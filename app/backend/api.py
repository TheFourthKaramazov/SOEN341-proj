import json
import logging
from contextlib import asynccontextmanager
from typing import Set
from urllib import request

from fastapi import FastAPI, Depends, Header, WebSocket, WebSocketDisconnect, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.backend.database import SessionLocal, init_db  
from app.backend.models import User, DirectMessage, Channel, ChannelMessage, UserChannel
from app.backend.schemas import ChannelResponse, UserCreate, DirectMessageCreate, ChannelCreate, ChannelMessageCreate

# Initialize FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield  

app = FastAPI(lifespan=lifespan) 
active_connections = {}
router = APIRouter()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from app.backend.database import get_db
from app.backend.models import ChannelMessage

channel_connections = {}

@app.websocket("/ws/channel/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    if channel_id not in channel_connections:
        channel_connections[channel_id] = []
    channel_connections[channel_id].append(websocket)
    print(f"Client connected to channel {channel_id}")

    try:
        while True:
            data = await websocket.receive_json()  # Receive message as JSON
            sender_id = data.get("sender_id")  # Extract sender ID
            message_text = data.get("text")
            if not sender_id or not message_text:
                continue
            print(f"Message in channel {channel_id}: {data}")
            
            #  Save message to the database
            message = ChannelMessage(
                channel_id=channel_id,
                sender_id=sender_id,  # Change this to the actual sender's ID (pass it from frontend)
                text=message_text
            )
            db.add(message)
            db.commit()

            for ws in channel_connections[channel_id]:
                await ws.send_json({"sender_id": sender_id, "text": message_text})
            if sender_id in active_connections:
                for ws in active_connections[sender_id]:
                    try:
                        await ws.send_json(data)

                    except Exception as e:
                        print(f"Failed to send message to {sender_id}: {e}")
    except WebSocketDisconnect:
        print(f"Client disconnected from channel {channel_id}")
        channel_connections[channel_id].remove(websocket)



@app.post("/test/channel-message/")
def test_channel_message(channel_id: int, sender_id: int, text: str, db: Session = Depends(get_db)):
    try:
        new_message = ChannelMessage(channel_id=channel_id, sender_id=sender_id, text=text)
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return {"message": "Message saved!", "id": new_message.id}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    """Handles login requests and authenticates users."""
    
    # Convert username to lowercase before checking in the database
    existing_user = db.query(User).filter(User.username.ilike(user.username)).first()

    # If user doesn't exist, return an error (instead of creating a new one)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User does not exist. Please check your username.")

    # Check password directly (no hashing)
    if existing_user.password_hash != user.password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {"id": existing_user.id, "username": existing_user.username, "is_admin": existing_user.is_admin}

@app.websocket("/realtime/direct/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """Handles real-time direct messaging."""
    await websocket.accept()

    if user_id not in active_connections:
        active_connections[user_id] = set()
    active_connections[user_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()  # Receive raw message

            # Try parsing the message (Handle bad JSON)
            try:
                message = json.loads(data)
                sender_id = user_id
                receiver_id = message.get("receiver_id")
                message_text = message.get("content")
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid JSON received: {data}, Error: {e}")
                continue  # Skip processing invalid data

            # Store the message in the database
            store_direct_message(db, sender_id, receiver_id, message_text)

            response_data = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": message_text
            }

            #  Send to all active connections of the receiver
            if receiver_id in active_connections:
                for ws in active_connections[receiver_id]:
                    try:
                        await ws.send_json(response_data)

                    except Exception as e:
                        print(f"Failed to send message to {receiver_id}: {e}")

            # Also send message back to sender (so their UI updates immediately)
            if sender_id in active_connections:
                for ws in active_connections[sender_id]:
                    try:
                        await ws.send_json(response_data)

                    except Exception as e:
                        print(f"Failed to send message to {sender_id}: {e}")

    except WebSocketDisconnect:
        print(f"[INFO] WebSocket disconnected: {user_id}")
        active_connections[user_id].remove(websocket)
        if not active_connections[user_id]:  # Remove user if no active connections remain
            del active_connections[user_id]

    except Exception as e:
        print(f"[ERROR] WebSocket crashed: {e}")

# webSocket for Channels
@app.websocket("/realtime/channel/{channel_id}/{user_id}")
async def websocket_channel_endpoint(
    websocket: WebSocket, channel_id: int, user_id: int, db: Session = Depends(get_db)
):
    """Handles real-time channel messaging."""
    user = db.query(User).filter_by(id=user_id).first()
    # if not user:
    #     await websocket.close(code=4001)
    #     return

    channel = db.query(Channel).filter_by(id=channel_id).first()
    # if not channel:
    #     await websocket.close(code=4002)
    #     return

    await websocket.accept()
    if channel_id not in active_connections:
        active_connections[channel_id] = set()
    active_connections[channel_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            sender_id = data.get("sender_id")
            message_text = data.get("text")

            if sender_id != user_id:
                await websocket.send_json({"error": "Unauthorized sender."})
                continue

            new_message = ChannelMessage(channel_id=channel_id, sender_id=sender_id, text=message_text)
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            response_data = {
                "channel_id": channel_id,
                "sender_id": sender_id,
                "text": message_text
            }

            for conn in active_connections[channel_id]:
                await conn.send_json(response_data)

    except WebSocketDisconnect:
        active_connections[channel_id].remove(websocket)
        if not active_connections[channel_id]:  
            del active_connections[channel_id]

# retrieve Users
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": user.id, "name": user.username} for user in users]

# store Direct Messages
def store_direct_message(db: Session, sender_id: int, receiver_id: int, text: str):
    sender = db.query(User).filter(User.id == sender_id).first()
    receiver = db.query(User).filter(User.id == receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")

    new_message = DirectMessage(sender_id=sender_id, receiver_id=receiver_id, text=text)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {
        "id": new_message.id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "text": new_message.text,
        "timestamp": new_message.timestamp  
    }

def store_channel_message(db: Session, sender_id: int, channel_id: int, text: str):
    sender = db.query(User).filter(User.id == sender_id).first()
    channel = db.query(User).filter(User.id == channel_id).first()

    if not sender or not channel:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")

    new_message = DirectMessage(sender_id=sender_id, channel_id=channel_id, text=text)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {
        "id": new_message.id,
        "sender_id": sender_id,
        "channel_id": channel_id,
        "text": new_message.text,
        "timestamp": new_message.timestamp  
    }

# get Messages Between Users
@app.get("/messages/{user1_id}/{user2_id}")
def get_messages(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(DirectMessage)
        .filter(
            ((DirectMessage.sender_id == user1_id) & (DirectMessage.receiver_id == user2_id))
            | ((DirectMessage.sender_id == user2_id) & (DirectMessage.receiver_id == user1_id))
        )
        .order_by(DirectMessage.timestamp.asc())
        .all()
    )

    user_map = {user.id: user.username for user in db.query(User).filter(User.id.in_([user1_id, user2_id])).all()}

    return [
        {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "sender_name": user_map.get(msg.sender_id, f"User {msg.sender_id}"),
            "receiver_name": user_map.get(msg.receiver_id, f"User {msg.receiver_id}"),
            "text": msg.text,
            "timestamp": msg.timestamp
        }
        for msg in messages
    ]

# get Channel Messages
@app.get("/channel-messages/{channel_id}")
def get_channel_messages(channel_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(ChannelMessage)
        .filter(ChannelMessage.channel_id == channel_id)
        .order_by(ChannelMessage.timestamp.asc())
        .all()
    )
    return [{"id": msg.id, "sender_id": msg.sender_id, "text": msg.text} for msg in messages]

global_channel_connections: Set[WebSocket] = set()

@app.websocket("/realtime/global/channels")
async def websocket_global_channels(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    global_channel_connections.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        global_channel_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        global_channel_connections.remove(websocket)

# Function to broadcast global channel updates
async def broadcast_channel_update(message: str):
    for connection in global_channel_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"Failed to send message to connection: {e}")
            global_channel_connections.remove(connection)

# create Channel
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/channels/")
async def create_channel(channel: ChannelCreate, db: Session = Depends(get_db), user_id: int = Header(None)):
    logger.debug(f"Received request to create channel. User ID: {user_id}")
    
    try:
        # checks if channel name is blank
        channel_name = channel.name.strip()
        if not channel_name:
            raise HTTPException(status_code=400, detail="Channel name cannot be blank")

        # check if another channel has the same name
        existing_channel = db.query(Channel).filter(Channel.name.ilike(channel_name)).first()
        if existing_channel:
            raise HTTPException(status_code=400, detail="Channel name already exists")

        # check if admin
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        if not current_user.is_admin:
            logger.error(f"User is not an admin: {user_id}")
            raise HTTPException(status_code=403, detail="Only admins can create channels")

        new_channel = Channel(name=channel.name, is_public=True)
        db.add(new_channel)
        db.commit()
        db.refresh(new_channel)
        logger.debug(f"Channel created successfully: {new_channel}")

        await broadcast_channel_update(json.dumps({
            "event": "channel_created",
            "channel": {
                "id": new_channel.id,
                "name": new_channel.name,
                "is_public": new_channel.is_public,
            },
        }))

        return new_channel
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating channel: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# delete channel
@app.delete("/delete_channel/{channel_id}")
async def delete_channel(channel_id: int, user_id: int = Header(...), db: Session = Depends(get_db)):
    current_user = db.query(User).filter(User.id == user_id).first()

    # check if user exists
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the user has admin role
    if not current_user or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete channels")

    # Find the channel that we will delete
    channel_to_delete = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel_to_delete:
        raise HTTPException(status_code=404, detail="Channel not found")

    db.delete(channel_to_delete)
    db.commit()

    await broadcast_channel_update(json.dumps({
        "event": "channel_deleted",
        "channel_id": channel_id,
    }))

    return {"message": "Channel deleted successfully"}


# join Channel
@app.post("/join_channel/{channel_id}")
def join_channel(channel_id: int, user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not user or not channel:
        raise HTTPException(status_code=404, detail="User or channel not found")

    membership = db.query(UserChannel).filter_by(user_id=user.id, channel_id=channel_id).first()
    if membership:
        return {"message": "Already a member"}

    new_membership = UserChannel(user_id=user.id, channel_id=channel_id)
    db.add(new_membership)
    db.commit()
    
    return {"message": "Successfully joined the channel"}
@app.get("/channels/", response_model=list[ChannelResponse])
def get_channels(user_id: int = Header(None), db: Session = Depends(get_db)):
    """Retrieve all available channels, including public channels and private channels the user is part of."""
    public_channels = db.query(Channel).filter(Channel.is_public == True).all()

    if user_id:  # Fetch private channels for logged-in users
        user_private_channels = (
            db.query(Channel)
            .join(UserChannel, Channel.id == UserChannel.channel_id)
            .filter(UserChannel.user_id == user_id)
            .all()
        )
        available_channels = public_channels + user_private_channels
    else:
        available_channels = public_channels  # Guests can only see public channels

    if not available_channels:
        raise HTTPException(status_code=404, detail="No channels found")

    return available_channels


@app.delete("/channel-messages/{message_id}")
async def delete_channel_message(
    message_id: int, 
    db: Session = Depends(get_db), 
    user_id: int = Header(None)
):
    # Check if admin
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete messages")

    # Find the message to delete
    message = db.query(ChannelMessage).filter(ChannelMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(message)
    db.commit()

    # Notify all clients in the channel
    await notify_message_deleted(message.channel_id, message_id)

    return {"message": "Message deleted successfully"}

async def notify_message_deleted(channel_id: int, message_id: int):
    if channel_id in active_connections:
        for websocket in active_connections[channel_id]:
            try:
                await websocket.send_json({
                    "action": "message_deleted",
                    "channel_id": channel_id,
                    "message_id": message_id,
                })
            except Exception as e:
                print(f"Failed to notify client: {e}")

@app.delete("/direct-messages/{message_id}")
async def delete_direct_message(
    message_id: int, 
    db: Session = Depends(get_db), 
    user_id: int = Header(None)
):
    # Check if admin
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete messages")

    # Find the message to delete
    message = db.query(DirectMessage).filter(DirectMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(message)
    db.commit()

    return {"message": "Direct message deleted successfully"}
