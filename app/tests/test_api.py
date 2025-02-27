import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session
from app.backend.database import SessionLocal, get_db
from app.backend.models import User, DirectMessage, Channel, ChannelMessage
from app.backend.api import app
from app.backend.database import init_db

# initialize the database before running tests
init_db()  # ensures all tables exist

# use the


# use the main database
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=SessionLocal.kw["bind"])

# override get_db dependency to use a rollback strategy
def override_get_db():
    """provides a session that rolls back changes after each test"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # undo any test changes
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    """creates a database session that rolls back after each test"""
    db = TestSessionLocal()
    yield db
    db.rollback()  # rollback changes after test
    db.close()

client = TestClient(app)

def test_create_user(test_db):
    """test creating a user"""
    response = client.post("/users/", json={"username": "TestUser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["username"] == "TestUser"

def test_send_message(test_db):
    """test sending a direct message"""
    response = client.post("/messages/", json={"sender_id": 1, "receiver_id": 2, "text": "Hello!"})
    assert response.status_code == 200
    assert response.json()["text"] == "Hello!"

def test_create_channel(test_db):
    """test creating a channel"""
    response = client.post("/channels/", json={"name": "General"})
    assert response.status_code == 200
    assert response.json()["name"] == "General"

@pytest.mark.asyncio
async def test_websocket_messaging():
    """Tests sending and receiving messages via WebSocket."""
    sender_id = 1
    receiver_id = 2
    message_text = f"This is a test message via WebSocket from user with id {sender_id} to user with id {receiver_id}"

    with client.websocket_connect(f"/realtime/direct/{sender_id}") as sender_websocket:
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