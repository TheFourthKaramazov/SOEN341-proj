
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.backend.database import SessionLocal, init_db  
from app.backend.models import User, DirectMessage, Channel, ChannelMessage  
from app.backend.schemas import UserCreate, DirectMessageCreate, ChannelCreate, ChannelMessageCreate

# create a FastAPI instance
@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.backend.database import init_db
    init_db()
    yield  # continue serving requests

app = FastAPI(lifespan=lifespan)  # fix: use lifespan instead of `@app.on_event("startup")`

def get_db(): 
    """Provides a database session to API endpoints."""
    db = SessionLocal() # create a new session
    try: 
        yield db
    finally:
        db.close()

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
    """Sends a direct message between users."""
    new_message = DirectMessage(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        text=message.text
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@app.post("/channels/") # create new endpoint
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    """Creates a new chat channel."""
    new_channel = Channel(name=channel.name) # create new channel

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