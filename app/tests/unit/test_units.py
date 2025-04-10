

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.backend.base import Base
from app.backend.models import User, Channel, DirectMessage, ChannelMessage
from app.backend.api import store_direct_message, store_channel_message


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Creates all tables in the in-memory DB once per session,
    then optionally drops them after tests (if desired).
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Each test gets its own transaction-scoped session.
    Rolls back changes after each test.
    """
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

def test_store_direct_message(db_session):
    """
    Tests store_direct_message to ensure it correctly saves
    a DirectMessage and returns the right dictionary.
    """
    # Create two users in the DB
    sender = User(username="Alice", password_hash="alicepass", is_admin=False)
    receiver = User(username="Bob", password_hash="bobpass", is_admin=False)
    db_session.add_all([sender, receiver])
    db_session.commit()

    # Call the function under test
    result = store_direct_message(
        db=db_session,
        sender_id=sender.id,
        receiver_id=receiver.id,
        text="Hello Bob!"
    )

    # Verify the returned dict
    assert result["sender_id"] == sender.id
    assert result["receiver_id"] == receiver.id
    assert result["text"] == "Hello Bob!"

    # Confirm the DB actually has the message
    dm = db_session.query(DirectMessage).first()
    assert dm is not None
    assert dm.sender_id == sender.id
    assert dm.receiver_id == receiver.id
    assert dm.text == "Hello Bob!"

def test_store_channel_message(db_session):
    """
    Tests store_channel_message to ensure it correctly saves
    a ChannelMessage and returns the right dictionary.
    """
    # Create a user and a channel
    user = User(username="TestUser", password_hash="testpass", is_admin=False)
    channel = Channel(name="TestChannel", is_public=True)
    db_session.add_all([user, channel])
    db_session.commit()

    # Call the function
    result = store_channel_message(
        db=db_session,
        sender_id=user.id,
        channel_id=channel.id,
        text="Hello, Channel!"
    )

    # Verify the returned dict
    assert result["sender_id"] == user.id
    assert result["channel_id"] == channel.id
    assert result["text"] == "Hello, Channel!"

    # Confirm the DB actually has the message
    ch_msg = db_session.query(ChannelMessage).first()
    assert ch_msg is not None
    assert ch_msg.sender_id == user.id
    assert ch_msg.channel_id == channel.id
    assert ch_msg.text == "Hello, Channel!"
