from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from app.backend.base import Base 




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