from sqlalchemy import Boolean, Column, Integer, String
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
