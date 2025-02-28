
from contextlib import asynccontextmanager
from typing import Dict, Union

from fastapi import FastAPI, Depends, Header, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.backend.database import SessionLocal, init_db  
from app.backend.models import User, DirectMessage, Channel, ChannelMessage, UserChannel
from app.backend.schemas import ChannelResponse, UserCreate, DirectMessageCreate, ChannelCreate, ChannelMessageCreate

# create a FastAPI instance
@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.backend.database import init_db
    init_db()
    yield  # continue serving requests

app = FastAPI(lifespan=lifespan)  # fix: use lifespan instead of `@app.on_event("startup")`
active_connections = {}

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
    new_channel = Channel(name=channel.name, admin_only=channel.admin_only) # create new channel

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
def get_channels(user_id: int = Header(...), db: Session = Depends(get_db)):
    """
    Returns all available channels.
    Only public channels and private channels the user has access to are returned.
    """
    # Get public channels
    public_channels = db.query(Channel).filter(Channel.is_public == True).all()

    # Get private channels the user has access to
    user_private_channels = (
        db.query(Channel)
        .join(UserChannel, Channel.id == UserChannel.channel_id)
        .filter(UserChannel.user_id == user_id)
        .all()
    )

    available_channels = public_channels + user_private_channels

    if not available_channels:
        raise HTTPException(status_code=404, detail="No channels found")

    return available_channels