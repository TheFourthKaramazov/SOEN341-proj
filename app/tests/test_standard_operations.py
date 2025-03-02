import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session
from app.backend.models import User, DirectMessage, Channel, ChannelMessage
from app.backend.api import app, store_direct_message
from app.backend.database import get_db, SessionLocal

# use the main database
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=SessionLocal.kw["bind"])

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

def test_send_direct_message():
    """sends a direct message between users"""

    sender_id = 2
    receiver_id = 3
    message_text = "Direct message test!"

    with TestSessionLocal() as db:
        response = store_direct_message(db, sender_id, receiver_id, message_text)
        assert response["status_code"] == 200

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


@pytest.mark.asyncio
async def test_websocket_messaging():
    """Tests sending and receiving messages via WebSocket."""
    sender_id = 2
    receiver_id = 3
    message_text = f"This is a test message via WebSocket from user with id {sender_id} to user with id {receiver_id}"

    with client.websocket_connect(f"/messages/{sender_id}") as sender_websocket:
        print("WebSocket connection established.")

        sender_websocket.send_json({"receiver_id": receiver_id, "text": message_text})
        print("Message sent.")

        try:
            response = sender_websocket.receive_json()
            print(f"The Message was received!: {response}")

            assert response["sender_id"] == sender_id
            assert response["receiver_id"] == receiver_id
            assert response["text"] == message_text

        except Exception as e:
            print(f"Error receiving message: {e}")
            assert False, "WebSocket response not received."
