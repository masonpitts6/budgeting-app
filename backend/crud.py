from sqlalchemy.orm import Session
from models import User

# Create a new user
def create_user(
        db: Session,
        username: str,
        email: str,
        password: str
):
    user = User(username=username, email=email, password=password)  # Hash password in real app
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Retrieve a user by username
def get_user(
        db: Session,
        username: str
):
    return db.query(User).filter(User.username == username).first()