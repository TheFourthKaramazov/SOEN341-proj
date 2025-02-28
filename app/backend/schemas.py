from pydantic import BaseModel

class UserCreate(BaseModel):
    """Schema for creating a new user."""

    # entries for username and password
    username: str
    password: str


class DirectMessageCreate(BaseModel):
    """Schema for sending a direct message."""

    # entries for sender ID, receiver ID, and message text
    sender_id: int
    receiver_id: int
    text: str


class ChannelCreate(BaseModel):
    """Schema for creating a new chat channel."""

    # entry for channel name
    name: str
    admin_only: bool


class ChannelMessageCreate(BaseModel):
    """Schema for sending a message within a channel."""

    # entries for channel ID, sender ID, and message text
    channel_id: int
    sender_id: int
    text: str

#should I make a schema for joining a channel? Ask.
class ChannelMembershipCreate(BaseModel):
    """Schema for joining a channel. Therefore creating a membership."""

    # entries for user username, channel name
    user_id: int
    channel_id: int
