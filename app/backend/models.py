from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
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
    
    # channel ID and name and admin only status
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    admin_only = Column(Boolean, default=False)
    messages = relationship("ChannelMessage", back_populates="channel")


class ChannelMessage(Base):
    """Database model for storing messages within chat channels."""
    __tablename__ = "channel_messages" # table name
    
    # message ID, channel ID, sender ID, message text, and timestamp
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 

    
    # relationships to channel and sender
    channel = relationship("Channel", back_populates="messages")
    sender = relationship("User")

class ChannelMembership(Base):
    """Database model for storing members currently within chat channels."""
    __tablename__ = "channel_membership" # table name

     # user ID, channel ID 
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))

    # relationships to channel and user
    user = relationship("User")
    channel = relationship("Channel")