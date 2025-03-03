import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session
from app.backend.models import User, DirectMessage, Channel, ChannelMessage, UserChannel
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
    sender_id = 1
    receiver_id = 2
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

@pytest.mark.asyncio
async def test_websocket_channel_messaging():
    """Tests sending and receiving messages via WebSocket in a channel."""

    db = TestSessionLocal()

    try:
        user1, user2, test_channel = setup_users_and_channel(db)

        verify_user_in_channel(db, user1, test_channel)
        verify_user_in_channel(db, user2, test_channel)

        print(f"{user1.username} and {user2.username} are in {test_channel.name}")

        send_and_receive_message(user1, user2, test_channel)
    finally:
        db.close()

def setup_users_and_channel(db):
    """Make sure the test users and channel exist, creating them if needed."""

    username_1 = "testuser1"
    username_2 = "testuser2"
    test_channel_name = "test_channel"

    # Make sure user1 exists
    user1 = db.query(User).filter_by(username=username_1).first()
    if not user1:
        user1 = User(username=username_1, password_hash="password")
        db.add(user1)
        db.commit()
        db.refresh(user1)

    # Make sure user2 exists
    user2 = db.query(User).filter_by(username=username_2).first()
    if not user2:
        user2 = User(username=username_2, password_hash="password")
        db.add(user2)
        db.commit()
        db.refresh(user2)

    # Make sure channel exists
    test_channel = db.query(Channel).filter_by(name=test_channel_name).first()
    if not test_channel:
        test_channel = Channel(name=test_channel_name, is_public=True)
        db.add(test_channel)
        db.commit()
        db.refresh(test_channel)

    # Add the users to the channel if they're not already in it.
    if not db.query(UserChannel).filter_by(user_id=user1.id, channel_id=test_channel.id).first():
        db.add(UserChannel(user_id=user1.id, channel_id=test_channel.id))

    if not db.query(UserChannel).filter_by(user_id=user2.id, channel_id=test_channel.id).first():
        db.add(UserChannel(user_id=user2.id, channel_id=test_channel.id))

    db.commit()

    return user1, user2, test_channel


def verify_user_in_channel(db, user, channel):
    """Make sure a user is part of the channel."""
    assert db.query(UserChannel).filter_by(user_id=user.id, channel_id=channel.id).first() is not None, \
        f"User {user.username} is NOT in channel {channel.name}."


def send_and_receive_message(user1, user2, test_channel):
    """Send and receive the message over WebSocket."""

    with client.websocket_connect(f"/realtime/channel/{test_channel.id}/{user1.id}") as sender_ws, \
            client.websocket_connect(f"/realtime/channel/{test_channel.id}/{user2.id}") as receiver_ws:

        message_text = f"Hello people of {test_channel.name}!!"

        sender_ws.send_json({"text": message_text, "channel_id": test_channel.id, "sender_id": user1.id})
        print(f"{user1.username} sent message: {message_text}")

        # We simulate a delay to give time for the other user to receive the message
        time.sleep(1)

        response = receiver_ws.receive_json()
        print(f"📥 {user2.username} received message: {response}")

        assert response["text"] == message_text, "Received message does not match the sent message!"
        assert response["sender_id"] == user1.id, "Sender ID does not match!"
        assert response["channel_id"] == test_channel.id, "Channel ID does not match!"

        print("WebSocket messaging test passed!")
