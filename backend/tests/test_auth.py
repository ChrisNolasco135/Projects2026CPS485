import pytest
from datetime import timedelta
from jose import jwt
import auth

def test_password_hashing():
    password = "secretpassword"
    hashed = auth.get_password_hash(password)
    assert hashed != password
    assert auth.verify_password(password, hashed) is True
    assert auth.verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    data = {"sub": "testuser"}
    token = auth.create_access_token(data)
    
    # Verify token decoding
    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    assert payload.get("sub") == "testuser"
    assert "exp" in payload

def test_create_access_token_with_expires_delta():
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=15)
    token = auth.create_access_token(data, expires_delta=expires_delta)
    
    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    assert payload.get("sub") == "testuser"
