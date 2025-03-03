from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.backend.database import get_db
from app.backend.models import ChannelMessage
from app.backend.auth import get_current_user  # Assuming authentification is implemented
from app.backend.database import get_past_messages_secure

router = APIRouter()

@router.get("/channels/{channel_id}/messages")
def fetch_channel_messages(
    channel_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Get user from authentification
):
    """Retrieve past messages for a channel, ensuring user has access."""
    messages = get_past_messages_secure(db, current_user["id"], channel_id, skip, limit)
    
    if not messages:
        raise HTTPException(status_code=403, detail="You don't have access to this channel.")

    return messages
