import pytest
from fastapi.testclient import TestClient
from app.backend.api import app 
from app.backend.database import SessionLocal, init_db
from app.backend.models import Channel, UserChannel, User

init_db(force_reset=True)

client = TestClient(app)

def test_get_channels():
    db = SessionLocal()

    try:
        # Create a test user
        test_user = User(username="testuser", password_hash="testpass")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create a public channel
        public_channel = Channel(name="public-channel", is_public=True)
        db.add(public_channel)
        db.commit()
        db.refresh(public_channel)

        # Create a private channel
        private_channel = Channel(name="private-channel", is_public=False)
        db.add(private_channel)
        db.commit()
        db.refresh(private_channel)

        # Grant the test user access to the private channel
        user_channel = UserChannel(user_id=test_user.id, channel_id=private_channel.id)
        db.add(user_channel)
        db.commit()

        # Test the /channels/ endpoint
        response = client.get("/channels/", headers={"user-id": str(test_user.id)})
        assert response.status_code == 200

        # Verify the response contains the expected channels
        channels = response.json()
        assert len(channels) == 2  # Public channel + private channel the user has access to
        assert any(channel["name"] == "public-channel" for channel in channels)
        assert any(channel["name"] == "private-channel" for channel in channels)

    finally:
        # Clean up the database
        db.query(UserChannel).delete()
        db.query(Channel).delete()
        db.query(User).delete()
        db.commit()
        db.close()

def test_get_channels_no_channels():
    init_db(force_reset=True)

    # Create a test user
    db = SessionLocal()
    test_user = User(username="testuser", password_hash="testpass")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    db.close()

    # Test the /channels/ endpoint
    response = client.get("/channels/", headers={"user-id": str(test_user.id)})
    assert response.status_code == 404
    assert response.json() == {"detail": "No channels found"}