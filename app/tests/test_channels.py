from sqlalchemy.orm import Session
from app.backend.database import SessionLocal, engine, init_db
from app.backend.models import Base, User, Channel

#  Initialize the database (Ensures tables are created)
print("⏳ Initializing database...")
init_db()  # This makes sure the database is set up
print("✅ Database initialized!")

#  Create tables if they don't exist
print("⏳ Creating tables if not exist...")
Base.metadata.create_all(engine)
print(" Tables are ready!")

#  Open a  database session
db = SessionLocal()

try:
    #  Insert users
    users = [
        User(username="Alice Johnson", password_hash="hashedpassword1"),
        User(username="Bob Williams", password_hash="hashedpassword2"),
        User(username="Charlie Smith", password_hash="hashedpassword3"),
        User(username="Diana Rodriguez", password_hash="hashedpassword4"),
        User(username="Ethan Martinez", password_hash="hashedpassword5"),
    ]

    db.add_all(users)
    db.commit()
    print(" Users added successfully!")

    # Insert channels
    channels = [
        Channel(name="General Chat", is_public=True),
        Channel(name="Project Discussions", is_public=True),
        Channel(name="Casual Talks", is_public=True),
        Channel(name="Tech Support", is_public=True),
        Channel(name="Gaming Room", is_public=True),
    ]

    db.add_all(channels)
    db.commit()
    print("✅ Channels added successfully!")



finally:
    db.close()  # Close session properly
    print(" Database session closed!")