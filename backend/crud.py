from sqlalchemy.orm import Session
import models, schemas, auth

def get_user_by_username(db: Session, username: str):
    """
    Retrieve a user by their username.
    """
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user by their email address.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user in the database.
    1. Hash the password.
    2. Create a User model instance.
    3. Add to the session and commit.
    4. Refresh to get the ID and defaults.
    """
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
