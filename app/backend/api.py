from contextlib import asynccontextmanager
from typing import Dict, Union

from fastapi import FastAPI, Depends, Header, WebSocket, WebSocketDisconnect, HTTPException
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

    return {"id": existing_user.id, "username": existing_user.username}

# webSocket for Direct Messages
@app.websocket("/realtime/direct/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """Handles real-time direct messaging."""
    await websocket.accept()
    active_connections[user_id] = websocket  

    try:
        while True:
            data = await websocket.receive_json()
            sender_id = user_id
            receiver_id = data.get("receiver_id")
            message_text = data.get("content")

            print(f"[DEBUG] Received message: {message_text} from {sender_id} to {receiver_id}")

            store_direct_message(db, sender_id, receiver_id, message_text)

            response_data = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": message_text
            }

            if receiver_id in active_connections:
                await active_connections[receiver_id].send_json(response_data)
            else:
                print(f"[WARNING] User {receiver_id} is not connected.")

    except WebSocketDisconnect:
        print(f"[INFO] WebSocket disconnected: {user_id}")
        del active_connections[user_id]

# webSocket for Channels
@app.websocket("/realtime/channel/{channel_id}/{user_id}")
async def websocket_channel_endpoint(
    websocket: WebSocket, channel_id: int, user_id: int, db: Session = Depends(get_db)
):
    """Handles real-time channel messaging."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        await websocket.close(code=4001)
        return

    channel = db.query(Channel).filter_by(id=channel_id).first()
    if not channel:
        await websocket.close(code=4002)
        return

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
    return [{"sender_id": msg.sender_id, "text": msg.text} for msg in messages]

# create Channel
@app.post("/channels/")
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    new_channel = Channel(name=channel.name, is_public=channel.is_public)
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    return new_channel

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
