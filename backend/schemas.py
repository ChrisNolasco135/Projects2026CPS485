from pydantic import BaseModel, EmailStr
from typing import Optional

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
