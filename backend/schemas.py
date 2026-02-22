from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict

# Base schema for Database
class DatabaseBase(BaseModel):
    name: str
    content: Dict[str, Any] = {} # Flexible JSON content

class DatabaseCreate(DatabaseBase):
    pass

class Database(DatabaseBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# Base schema for User
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Schema for creating a user (includes password)
class UserCreate(UserBase):
    password: str

# Schema for reading user data (excludes password, includes ID and status)
class User(UserBase):
    id: int
    is_active: bool
    databases: List[Database] = []

    # Enable ORM mode to read data from SQLAlchemy models
    class Config:
        from_attributes = True

# Schema for JWT Token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for Token payload data
class TokenData(BaseModel):
    username: Optional[str] = None
