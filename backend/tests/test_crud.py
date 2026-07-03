import pytest
from sqlalchemy.orm import Session
import crud
import schemas

def test_create_user(db_session: Session):
    user_data = schemas.UserCreate(username="testuser", email="test@test.com", password="password")
    user = crud.create_user(db_session, user_data)
    assert user.username == "testuser"
    assert user.email == "test@test.com"
    assert user.id is not None
    assert user.hashed_password != "password"

def test_get_user_by_username(db_session: Session):
    user_data = schemas.UserCreate(username="testuser2", email="test2@test.com", password="password")
    crud.create_user(db_session, user_data)
    
    user = crud.get_user_by_username(db_session, "testuser2")
    assert user is not None
    assert user.email == "test2@test.com"

def test_create_database(db_session: Session):
    user_data = schemas.UserCreate(username="testuser3", email="test3@test.com", password="password")
    user = crud.create_user(db_session, user_data)
    
    db_data = schemas.DatabaseCreate(name="Test DB")
    database = crud.create_database(db_session, db_data, user.id)
    
    assert database.name == "Test DB"
    assert database.owner_id == user.id
    assert database.id is not None
    assert database.filename.endswith(".sqlite")

def test_get_databases(db_session: Session):
    user_data = schemas.UserCreate(username="testuser4", email="test4@test.com", password="password")
    user = crud.create_user(db_session, user_data)
    
    crud.create_database(db_session, schemas.DatabaseCreate(name="DB 1"), user.id)
    crud.create_database(db_session, schemas.DatabaseCreate(name="DB 2"), user.id)
    
    databases = crud.get_databases(db_session, user.id)
    assert len(databases) == 2
