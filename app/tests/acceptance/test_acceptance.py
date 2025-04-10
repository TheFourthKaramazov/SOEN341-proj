
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.backend.database import SessionLocal, get_db, init_db
from app.backend.models import User, DirectMessage, ChannelMessage, Channel, UserChannel
from app.backend.api import app

# Prepare a test session factory using the same DB engine
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=SessionLocal.kw["bind"])

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
#overriding db
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def fresh_db():
    """
    This fixture runs before each test function,
    resetting the DB so we don't collide on unique usernames or leftover data.
    """
    init_db(force_reset=True)
    yield
    

@pytest.fixture(scope="function")
def db_session():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def create_users(db_session):
    """
    Creates a normal user and an admin user in the DB.
    Returns (normal_user, admin_user).
    """
    normal = User(username="normal_user", password_hash="testpass", is_admin=False)
    db_session.add(normal)
    db_session.commit()
    db_session.refresh(normal)

    admin = User(username="admin_user", password_hash="secretpass", is_admin=True)
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    return normal, admin

def test_debug_user_model():
    """
    Debug test to print out actual columns in the User model at runtime.
    """
    columns = User.__table__.columns.keys()
    print("\n[DEBUG] User model columns =>", list(columns))
    assert "password_hash" in columns, "Expected 'password_hash' in User columns."

def test_direct_messaging(db_session, create_users):
    """
    Acceptance test: direct messaging (/messages/).
    Expects 200 if the route finds both sender and receiver in the DB.
    """
    normal_user, _admin_user = create_users

    # create a second normal user
    second_user = User(username="second_user", password_hash="anotherpass", is_admin=False)
    db_session.add(second_user)
    db_session.commit()
    db_session.refresh(second_user)

    payload = {
        "sender_id": normal_user.id,
        "receiver_id": second_user.id,
        "text": "Hello from the acceptance test!"
    }
    response = client.post("/messages/", json=payload)
    print("Response from /messages/:", response.status_code, response.json())

    # We expect 200 if everything works
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["message"]["sender_id"] == normal_user.id
    assert data["message"]["receiver_id"] == second_user.id
    assert data["message"]["text"] == "Hello from the acceptance test!"

def test_channel_creation_requires_admin(db_session, create_users):
    """
    Acceptance test: channel creation (admin-only).
    The route expects 'User-Id' in headers for admin check.
    """
    normal_user, admin_user = create_users

    # normal tries,should fail 403
    payload = {"name": "NormalUserChannel", "is_public": True}
    resp_normal = client.post("/channels/", json=payload, headers={"User-Id": str(normal_user.id)})
    assert resp_normal.status_code == 403, f"Expected 403, got {resp_normal.status_code}"

    # admin tries, should succeed 200
    payload = {"name": "AdminChannel", "is_public": True}
    resp_admin = client.post("/channels/", json=payload, headers={"User-Id": str(admin_user.id)})
    assert resp_admin.status_code == 200, f"Expected 200, got {resp_admin.status_code}"
    data = resp_admin.json()
    assert data["name"] == "AdminChannel"

def test_channel_based_messaging(db_session, create_users):
    """
    1) Admin creates channel
    2) Normal user joins
    3) Normal user sends a channel message
    """
    normal_user, admin_user = create_users

    # Admin creates channel (need 'User-Id' = admin id)
    payload = {"name": "TestChannelMessaging", "is_public": True}
    resp = client.post("/channels/", json=payload, headers={"User-Id": str(admin_user.id)})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    channel_id = resp.json()["id"]

    # Normal user joins channel (this route uses query param for user_id, so no header needed)
    join_resp = client.post(f"/join_channel/{channel_id}", params={"user_id": normal_user.id})
    assert join_resp.status_code == 200, f"Expected 200, got {join_resp.status_code}"

    # Normal user sends channel message
    msg_payload = {
        "channel_id": channel_id,
        "sender_id": normal_user.id,
        "text": "Hello channel!"
    }
    post_resp = client.post("/channel-messages/", json=msg_payload)
    assert post_resp.status_code == 200, f"Expected 200, got {post_resp.status_code}"
    resp_data = post_resp.json()
    assert resp_data["channel_id"] == channel_id
    assert resp_data["text"] == "Hello channel!"

def test_message_deletion_requires_admin(db_session, create_users):
    """
    1) Admin creates channel
    2) Normal user joins and posts a message
    3) Normal user tries to delete => 403
    4) Admin deletes => 200
    """
    normal_user, admin_user = create_users

    # admin creates channel
    channel_payload = {"name": "DeleteTestChannel", "is_public": True}
    channel_resp = client.post("/channels/", json=channel_payload, headers={"User-Id": str(admin_user.id)})
    assert channel_resp.status_code == 200, f"Expected 200, got {channel_resp.status_code}"
    channel_id = channel_resp.json()["id"]

    # normal user joins channel
    join_resp = client.post(f"/join_channel/{channel_id}", params={"user_id": normal_user.id})
    assert join_resp.status_code == 200, f"Expected 200, got {join_resp.status_code}"

    # normal user posts a message
    msg_payload = {
        "channel_id": channel_id,
        "sender_id": normal_user.id,
        "text": "Message to be deleted"
    }
    post_resp = client.post("/channel-messages/", json=msg_payload)
    assert post_resp.status_code == 200
    msg_id = post_resp.json()["id"]

    # normal tries to delete => 403
    del_resp_normal = client.delete(
        f"/channel-messages/{msg_id}",
        headers={"User-Id": str(normal_user.id)}
    )
    assert del_resp_normal.status_code == 403, f"Expected 403, got {del_resp_normal.status_code}"

    # admin deletes => 200
    del_resp_admin = client.delete(
        f"/channel-messages/{msg_id}",
        headers={"User-Id": str(admin_user.id)}
    )
    assert del_resp_admin.status_code == 200, f"Expected 200, got {del_resp_admin.status_code}"
    assert del_resp_admin.json()["message"] == "Message deleted successfully"

def test_direct_message_deletion_requires_admin(db_session, create_users):
    """
    1) normal_user sends a direct message
    2) normal_user tries to delete => 403
    3) admin deletes => 200
    """
    normal_user, admin_user = create_users

    # normal sends DM to admin
    send_payload = {
        "sender_id": normal_user.id,
        "receiver_id": admin_user.id,
        "text": "DM to be deleted"
    }
    send_resp = client.post("/messages/", json=send_payload)
    assert send_resp.status_code == 200, f"Expected 200, got {send_resp.status_code}"
    dm_id = send_resp.json()["message"]["id"]

    # normal tries to delete => 403
    del_resp_normal = client.delete(
        f"/direct-messages/{dm_id}",
        headers={"User-Id": str(normal_user.id)}
    )
    assert del_resp_normal.status_code == 403, f"Expected 403, got {del_resp_normal.status_code}"

    # admin deletes => 200
    del_resp_admin = client.delete(
        f"/direct-messages/{dm_id}",
        headers={"User-Id": str(admin_user.id)}
    )
    assert del_resp_admin.status_code == 200, f"Expected 200, got {del_resp_admin.status_code}"
    assert del_resp_admin.json()["message"] == "Direct message deleted successfully"
