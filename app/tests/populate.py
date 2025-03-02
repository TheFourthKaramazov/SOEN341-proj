from sqlalchemy.orm import Session
from app.backend.database import SessionLocal
from app.backend.models import User
from app.backend.models import Channel

db = SessionLocal()

users = [
    User(username="Alice Johnson", password_hash="hashedpassword1"),
    User(username="Bob Williams", password_hash="hashedpassword2"),
    User(username="Charlie Smith", password_hash="hashedpassword3"),
    User(username="Diana Rodriguez", password_hash="hashedpassword4"),
    User(username="Ethan Martinez", password_hash="hashedpassword5"),
]

db.add_all(users)
db.commit()
db.close()
print("Users added successfully!")

channels = [
    Channel(name="General Chat", is_public=True),
    Channel(name="Project Discussions", is_public=True),
    Channel(name="Casual Talks", is_public=True),
    Channel(name="Tech Support", is_public=True),
    Channel(name="Gaming Room", is_public=True),
]

db.add_all(channels)
db.commit()
db.close()
print("Channels added successfully!")