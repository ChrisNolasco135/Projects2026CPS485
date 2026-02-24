from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    """
    __tablename__ = "users"

    # Primary key, indexed for faster lookups
    id = Column(Integer, primary_key=True, index=True)
    
    # Username must be unique
    username = Column(String, unique=True, index=True)
    
    # Email must be unique
    email = Column(String, unique=True, index=True)
    
    # Store hashed password, not plain text
    hashed_password = Column(String)
    
    # User status
    is_active = Column(Boolean, default=True)

    # Relationship to user's databases
    databases = relationship("Database", back_populates="owner")

class Database(Base):
    """
    SQLAlchemy model for user databases.
    """
    __tablename__ = "databases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    filename = Column(String, unique=True, index=True) # Stores the filename of the SQLite DB
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="databases")
