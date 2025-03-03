from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from app.backend.base import Base 
from sqlalchemy.orm import Session
from app.backend.models import ChannelMessage





# SQLite database URL
DATABASE_URL = "sqlite:///./app/backend/database.db" 



engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.backend.models import User, DirectMessage, Channel, ChannelMessage

def get_db():
    """Provides a database session to API endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def init_db(force_reset=False):
    """Initializes the database without dropping tables unless explicitly requested."""
    if force_reset:
        print(" WARNING: Resetting database!")
        Base.metadata.drop_all(bind=engine)  # deletes all tables (only if requested)
    
    print("Ensuring tables exist...")
    Base.metadata.create_all(bind=engine)  # creates tables only if missing

    # DEBUG: Print existing tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in database:", tables)

    if not tables:
        print("⚠️ ERROR: No tables were created. Something is wrong.")

def get_past_messages(db: Session, channel_id: int, skip: int = 0, limit: int = 10):
    """Fetch paginated past messages from a given channel, chronological order."""
    return (
        db.query(ChannelMessage)
        .filter(ChannelMessage.channel_id == channel_id)
        .order_by(ChannelMessage.timestamp.asc())  # Oldest messages first
        .offset(skip)
        .limit(limit)
        .all()
    )
