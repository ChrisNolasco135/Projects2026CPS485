from sqlalchemy.orm import Session
import models, schemas, auth
import uuid
import dynamic_db

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

def get_databases(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Retrieve all databases for a specific user.
    """
    return db.query(models.Database).filter(models.Database.owner_id == user_id).offset(skip).limit(limit).all()

def get_database(db: Session, database_id: int, user_id: int):
    """
    Retrieve a specific database by ID and ensure it belongs to the user.
    """
    return db.query(models.Database).filter(models.Database.id == database_id, models.Database.owner_id == user_id).first()

def create_database(db: Session, database: schemas.DatabaseCreate, user_id: int):
    """
    Create a new database for a user.
    Generates a unique filename and creates the SQLite file.
    """
    # Generate a unique filename: user_id_uuid.sqlite
    filename = f"{user_id}_{uuid.uuid4()}.sqlite"
    
    db_database = models.Database(name=database.name, filename=filename, owner_id=user_id)
    db.add(db_database)
    db.commit()
    db.refresh(db_database)
    
    # Create the physical file
    dynamic_db.create_db_file(filename)
    
    return db_database

def delete_database(db: Session, database_id: int, user_id: int):
    """
    Delete a database and its file.
    """
    db_database = get_database(db, database_id, user_id)
    if db_database:
        # Delete physical file
        dynamic_db.delete_db_file(db_database.filename)
        
        db.delete(db_database)
        db.commit()
        return True
    return False
