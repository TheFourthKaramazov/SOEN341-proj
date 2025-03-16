from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, TIMESTAMP, text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.backend.base import Base 


class User(Base):
    """Database model for storing user information."""
    __tablename__ = "users" # table name
    
    # user ID, username, and password hash
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # relationships to direct messages sent and received
    sent_messages = relationship("DirectMessage", foreign_keys="DirectMessage.sender_id", back_populates="sender")
    received_messages = relationship("DirectMessage", foreign_keys="DirectMessage.receiver_id", back_populates="receiver")

    # relationship to channels the user has access to
    channels = relationship("UserChannel", back_populates="user")

    sent_channel_messages = relationship(
        "ChannelMessage",
        foreign_keys="ChannelMessage.sender_id",  # Explicit FK reference
        back_populates="sender"
    )


class DirectMessage(Base):
    """ Database model for storing direct messages between users."""
    __tablename__ = "direct_messages" # table name
    
    # message ID, sender ID, receiver ID, message text, and timestamp
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))  

    # relationships to sender and receiver
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    
class Channel(Base):
    """Database model for storing chat channels."""
    __tablename__ = "channels" # table name
    
    # channel ID and name, and public/private flag
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_public = Column(Boolean, default=True)  # public by default
    messages = relationship("ChannelMessage", back_populates="channel", cascade="all, delete")

    # relationship to users who have access to the channel
    users = relationship("UserChannel", back_populates="channel")

# class ChannelMessage(Base):
#     """Database model for storing messages within chat channels."""
#     __tablename__ = "channel_messages" # table name
    
#     # message ID, channel ID, sender ID, message text, and timestamp
#     id = Column(Integer, primary_key=True, index=True)
#     channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
#     sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     text = Column(Text, nullable=False)
#     timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 

    
#     # relationships to channel and sender
#     channel = relationship("Channel", back_populates="messages")
#     sender = relationship("User")



class ChannelMessage(Base):
    __tablename__ = "channel_messages"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 

    sender = relationship("User", back_populates="sent_channel_messages")
    channel = relationship("Channel", back_populates="messages")



class UserChannel(Base):
    """Database model for tracking which users have access to which channels."""
    __tablename__ = "user_channels"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), primary_key=True)

    # relationships to user and channel
    user = relationship("User", back_populates="channels")
    channel = relationship("Channel", back_populates="users")