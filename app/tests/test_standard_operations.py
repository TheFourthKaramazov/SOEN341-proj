import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.backend.models import User, DirectMessage, Channel, ChannelMessage
from app.backend.api import app
from app.backend.database import get_db, SessionLocal

# use the main database session
def override_get_db():
    """provides a session for the main database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db  # force using the main database

@pytest.fixture(scope="function")
def main_db():
    """uses the main database session for testing"""
    db = SessionLocal()
    yield db
    db.close()

client = TestClient(app)

#  TEST ADDING A USER
def test_add_user():
    """adds a new user to the database"""
    response = client.post("/users/", json={"username": "TestUser", "password": "testpass"})
    assert response.status_code == 200
    print("✔️ user added successfully")

# TEST CREATING A CHANNEL
def test_create_channel():
    """creates a chat channel"""
    response = client.post("/channels/", json={"name": "TestChannel"})
    assert response.status_code == 200
    print("✔️ channel created successfully")

#  TEST SENDING A DIRECT MESSAGE
def test_send_direct_message():
    """sends a direct message between users"""
    
    # retrieve users
    with SessionLocal() as db:
        sender = db.query(User).filter_by(username="TestUser").first()
        receiver = User(username="ReceiverUser", password_hash="receiverpass")
        db.add(receiver)
        db.commit()
        receiver = db.query(User).filter_by(username="ReceiverUser").first()

    # send message
    response = client.post("/messages/", json={"sender_id": sender.id, "receiver_id": receiver.id, "text": "Hello!"})
    assert response.status_code == 200
    print("✔️ direct message sent successfully")

# ✅ TEST SENDING A MESSAGE IN A CHANNEL
def test_send_channel_message():
    """sends a message in a channel"""
    
    # retrieve channel and user
    with SessionLocal() as db:
        user = db.query(User).filter_by(username="TestUser").first()
        channel = db.query(Channel).filter_by(name="TestChannel").first()

    # send message
    response = client.post("/channel-messages/", json={"channel_id": channel.id, "sender_id": user.id, "text": "Hello Channel!"})
    assert response.status_code == 200
    print("✔️ channel message sent successfully")

# ✅ TEST RETRIEVING MESSAGES
def test_retrieve_messages():
    """retrieves messages from the database"""
    with SessionLocal() as db:
        sender = db.query(User).filter_by(username="TestUser").first()
        receiver = db.query(User).filter_by(username="ReceiverUser").first()
    
    # get direct messages
    response = client.post("/messages/", json={"sender_id": sender.id, "receiver_id": receiver.id, "text": "Hello!"})


