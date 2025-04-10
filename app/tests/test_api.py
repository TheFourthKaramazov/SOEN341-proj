import pytest
from fastapi.testclient import TestClient
from app.backend.models import User, DirectMessage, Channel, ChannelMessage
from app.backend.database import init_db
from sqlalchemy.orm import sessionmaker
from app.backend.database import engine, get_db
from app.backend.api import app
from app.backend.models import Base

# initialize the database before running tests
init_db()  # ensures all tables exist

# use the main database
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

    # Drop and recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

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

    # Promote to admin if needed
    user = test_db.query(User).filter_by(username="TestUser").first()
    user.is_admin = True
    test_db.commit()



def test_send_message(test_db):
    """test sending a direct message"""

    # Setup: create sender and receiver
    test_db.add_all([
        User(id=1, username="User1", password_hash="pass"),
        User(id=2, username="User2", password_hash="pass")
    ])
    test_db.commit()

    response = client.post("/messages/", json={"sender_id": 1, "receiver_id": 2, "text": "Hello!"})
    assert response.status_code == 200
    assert response.json()["message"]["text"] == "Hello!"

def test_create_channel(test_db):
    """test creating a channel"""

    test_db.add(User(id=1, username="Admin", password_hash="pass", is_admin=True))
    test_db.commit()

    response = client.post("/channels/", json={"name": "General", "is_public": True}, headers={"User-Id": "1"})
    assert response.status_code == 200
    assert response.json()["name"] == "General"

def test_join_channel(test_db):
    """test joining a channel"""

    test_db.add_all([
        User(id=1, username="Joiner", password_hash="pass"),
        Channel(id=1, name="TestChannel", is_public=True)
    ])
    test_db.commit()

    response = client.post("/join_channel/1", params={"user_id": 1})
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully joined the channel"}