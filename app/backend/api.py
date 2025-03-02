
from contextlib import asynccontextmanager
from typing import Dict, Union

from fastapi import FastAPI, Depends, Header, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.backend.database import SessionLocal, init_db  
from app.backend.models import User, DirectMessage, Channel, ChannelMessage, UserChannel
from app.backend.schemas import ChannelResponse, UserCreate, DirectMessageCreate, ChannelCreate, ChannelMessageCreate
from fastapi.middleware.cors import CORSMiddleware



# create a FastAPI instance
@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.backend.database import init_db
    init_db()
    yield  # continue serving requests

app = FastAPI(lifespan=lifespan)  # fix: use lifespan instead of `@app.on_event("startup")`
active_connections = {}

# add CORS Middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend URL (change "*" to specific domain in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

def get_db(): 
    """Provides a database session to API endpoints."""
    db = SessionLocal() # create a new session
    try: 
        yield db
    finally:
        db.close()

@app.websocket("/realtime/direct/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """WebSocket route for realtime messaging"""

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            print(f"Received from {user_id}: {data}")

            sender_id = user_id
            receiver_id = data.get("receiver_id")
            message_text = data.get("text")

            store_direct_message(db, sender_id, receiver_id, message_text)

            response_data = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "text": message_text
            }

            if receiver_id in active_connections:
                await active_connections[receiver_id].send_json(response_data)
                response_data["status"] = "delivered"
            else:
                response_data["status"] = "recipient_offline"
                response_data["message"] = "Message stored but recipient is offline."

            # Send response back to sender
            await websocket.send_json(response_data)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {user_id}")

@app.websocket("/realtime/channel/{channel_id}/{user_id}")
async def websocket_channel_endpoint(
    websocket: WebSocket, channel_id: int, user_id: int, db: Session = Depends(get_db)
):
    """WebSocket route for real-time messaging in channels with user authentication."""

    # Validate the user
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        await websocket.close(code=4001)
        return

    # Validate the channel
    channel = db.query(Channel).filter_by(id=channel_id).first()
    if not channel:
        await websocket.close(code=4002)
        return

    # Check if the user is in the channel
    user_in_channel = db.query(UserChannel).filter_by(user_id=user_id, channel_id=channel_id).first()
    if not user_in_channel:
        await websocket.close(code=4003)
        return

    await websocket.accept()

    # Track active WebSocket connections per channel
    if channel_id not in active_connections:
        active_connections[channel_id] = set()
    active_connections[channel_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            sender_id = data.get("sender_id")
            message_text = data.get("text")

            # Validate sender
            if sender_id != user_id:
                await websocket.send_json({"error": "Unauthorized sender."})
                continue

            # Store the message in the database
            new_message = ChannelMessage(channel_id=channel_id, sender_id=sender_id, text=message_text)
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            # Prepare and broadcast response
            response_data = {
                "channel_id": channel_id,
                "sender_id": sender_id,
                "text": message_text
            }

            for conn in active_connections[channel_id]:
                await conn.send_json(response_data)

    except WebSocketDisconnect:
        active_connections[channel_id].remove(websocket)
        if not active_connections[channel_id]:  # Remove channel if no users are left
            del active_connections[channel_id]

@app.post("/users/") # create new endpoint
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Creates a new user in the database."""

    # create new user
    new_user = User(username=user.username, password_hash=user.password)

    # add user to database
    db.add(new_user)

    # commit changes to database
    db.commit()

    # refresh the user to get updated information
    db.refresh(new_user)
    return new_user

@app.post("/messages/") # create new endpoint
def send_message(message: DirectMessageCreate, db: Session = Depends(get_db)):
    """Sends a direct message between users by calling store_direct_message"""
    return store_direct_message(db, message.sender_id, message.receiver_id, message.text)

def store_direct_message(db: Session, sender_id: int, receiver_id: int, text: str):
    """Stores a direct message in the database and returns the message"""

    # Make sure both the sender and receiver
    sender = db.query(User).filter_by(id=sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail=f"Sender with id {sender_id} does not exist")

    receiver = db.query(User).filter_by(id=receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail=f"Receiver with id {receiver_id} does not exist")

    new_message = DirectMessage(sender_id=sender_id, receiver_id=receiver_id, text=text)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    response = {
        "message": new_message,
        "status_code": 200
    }

    return response

@app.post("/channels/") # create new endpoint
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    """Creates a new chat channel."""
    new_channel = Channel(name=channel.name, is_public=channel.is_public) # create new channel

    # add channel to database
    db.add(new_channel)

    # commit changes to database
    db.commit()

    # refresh the channel to get updated information
    db.refresh(new_channel)
    return new_channel

@app.post("/channel-messages/") # create new endpoint
def send_channel_message(message: ChannelMessageCreate, db: Session = Depends(get_db)):
    """Sends a message within a chat channel."""

    # create new message
    new_message = ChannelMessage(
        channel_id=message.channel_id,
        sender_id=message.sender_id,
        text=message.text
    )

    # add message to database
    db.add(new_message)

    # commit changes to database
    db.commit()

    # refresh the message to get updated information
    db.refresh(new_message)
    return new_message

@app.get("/channels/", response_model=list[ChannelResponse])
def get_channels(user_id: int = Header(None), db: Session = Depends(get_db)):
    """
    Returns all available channels.
    If user_id is provided, return both public and private channels the user has access to.
    If user_id is missing, return only public channels.
    """
    # Get public channels
    public_channels = db.query(Channel).filter(Channel.is_public == True).all()

    if user_id:  # Only fetch private channels if user_id exists
        user_private_channels = (
            db.query(Channel)
            .join(UserChannel, Channel.id == UserChannel.channel_id)
            .filter(UserChannel.user_id == user_id)
            .all()
        )
        available_channels = public_channels + user_private_channels
    else:
        available_channels = public_channels

    if not available_channels:
        raise HTTPException(status_code=404, detail="No channels found")

    return available_channels

@app.post("/join_channel/{channel_id}")
def join_channel(channel_id: int, user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if user is already a member
    membership = db.query(UserChannel).filter_by(user_id=user.id, channel_id=channel_id).first()
    if membership:
        return {"message": "Already a member"}
    
    # Check to see if the channel is in Admin Only mode. 
    if not channel.is_public:
        raise HTTPException(status_code=403, detail="Cannot join an admin only channel without permission")
    
    # Add user to channel
    new_membership = UserChannel(user_id=user.id, channel_id=channel_id)
    db.add(new_membership)
    db.commit()
    
    return {"message": "Successfully joined the channel"}

@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    """Fetch all users."""
    users = db.query(User).all()
    return [{"id": user.id, "name": user.username} for user in users]

def store_direct_message(db: Session, sender_id: int, receiver_id: int, text: str):
    """Stores a direct message in the database and returns the message"""

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
        "text": new_message.text
    }

@app.get("/messages/{user1_id}/{user2_id}")
def get_messages(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    """Retrieve stored messages between two users."""
    messages = (
        db.query(DirectMessage)
        .filter(
            ((DirectMessage.sender_id == user1_id) & (DirectMessage.receiver_id == user2_id))
            | ((DirectMessage.sender_id == user2_id) & (DirectMessage.receiver_id == user1_id))
        )
        .order_by(DirectMessage.timestamp.asc())
        .all()
    )

    return [
        {"sender_id": msg.sender_id, "receiver_id": msg.receiver_id, "text": msg.text}
        for msg in messages
    ]

@app.websocket("/realtime/channel/{channel_id}/{user_id}")
async def websocket_channel_endpoint(
    websocket: WebSocket, channel_id: int, user_id: int, db: Session = Depends(get_db)
):
    """WebSocket for real-time messaging in channels with user authentication."""
    
    # Validate user and channel
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        await websocket.close(code=4001)
        return
    channel = db.query(Channel).filter_by(id=channel_id).first()
    if not channel:
        await websocket.close(code=4002)
        return

    # Track WebSocket connection
    await websocket.accept()
    if channel_id not in active_connections:
        active_connections[channel_id] = set()
    active_connections[channel_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            sender_id = data.get("sender_id")
            message_text = data.get("text")

            # Validate sender
            if sender_id != user_id:
                await websocket.send_json({"error": "Unauthorized sender."})
                continue

            # Store message in database
            new_message = ChannelMessage(channel_id=channel_id, sender_id=sender_id, text=message_text)
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            # Broadcast message to all users in the channel
            response_data = {
                "channel_id": channel_id,
                "sender_id": sender_id,
                "text": message_text
            }

            for conn in active_connections[channel_id]:
                await conn.send_json(response_data)

    except WebSocketDisconnect:
        active_connections[channel_id].remove(websocket)
        if not active_connections[channel_id]:  # Remove channel if empty
            del active_connections[channel_id]

@app.get("/channel-messages/{channel_id}")
def get_channel_messages(channel_id: int, db: Session = Depends(get_db)):
    """Retrieve all messages in a channel."""
    messages = (
        db.query(ChannelMessage)
        .filter(ChannelMessage.channel_id == channel_id)
        .order_by(ChannelMessage.timestamp.asc())
        .all()
    )
    return [{"sender_id": msg.sender_id, "text": msg.text} for msg in messages]