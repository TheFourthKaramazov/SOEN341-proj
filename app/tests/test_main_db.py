from sqlalchemy.orm import Session
from app.backend.database import SessionLocal, init_db
from app.backend.models import User, DirectMessage, Channel, ChannelMessage, ChannelMembership

# initialize the database without resetting it
init_db(force_reset=True)

# start a session
db = SessionLocal()

# add a user
user1 = User(username="TestUser1", password_hash="password1")
user2 = User(username="TestUser2", password_hash="password2")
db.add(user1)
db.add(user2)
db.commit()

# send a direct message
message = DirectMessage(sender_id=user1.id, receiver_id=user2.id, text="Hello from user1 to user2")
db.add(message)
db.commit()

# create a channel
channel = Channel(name="TestChannel", admin_only=False)
db.add(channel)
db.commit()

#Have a user join a channel
channel_membership = ChannelMembership(user_id = user1.id, channel_id = channel.id)
db.add(channel_membership)
db.commit();

# send a message in the channel
channel_message = ChannelMessage(channel_id=channel.id, sender_id=user1.id, text="Hello in channel")
db.add(channel_message)
db.commit()

# query and print database contents for verification
users = db.query(User).all()
messages = db.query(DirectMessage).all()
channels = db.query(Channel).all()
channel_messages = db.query(ChannelMessage).all()

print("users in database:")
for user in users:
    print(f"id: {user.id}, username: {user.username}")

print("direct messages in database:")
for msg in messages:
    print(f"id: {msg.id}, sender_id: {msg.sender_id}, receiver_id: {msg.receiver_id}, text: {msg.text}")

print("channels in database:")
for ch in channels:
    print(f"id: {ch.id}, name: {ch.name}")

print("channel messages in database:")
for ch_msg in channel_messages:
    print(f"id: {ch_msg.id}, channel_id: {ch_msg.channel_id}, sender_id: {ch_msg.sender_id}, text: {ch_msg.text}")

# close session
db.close() 