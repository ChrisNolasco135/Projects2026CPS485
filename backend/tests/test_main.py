import pytest
from conftest import client, auth_headers

def test_register_and_login(client):
    # Register
    response = client.post("/register", json={
        "username": "api_user",
        "email": "api@test.com",
        "password": "apipassword"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "api_user"
    
    # Duplicate register
    response2 = client.post("/register", json={
        "username": "api_user",
        "email": "api@test.com",
        "password": "apipassword"
    })
    assert response2.status_code == 400
    
    # Login
    login_resp = client.post("/login", data={
        "username": "api_user",
        "password": "apipassword"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

def test_unauthorized_access(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_database_crud(client, auth_headers):
    # Create a user in the test db first using register
    client.post("/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "password"
    })
    
    # Create DB
    create_resp = client.post("/databases/", json={"name": "My API DB"}, headers=auth_headers)
    assert create_resp.status_code == 200
    db_id = create_resp.json()["id"]
    
    # List DBs
    list_resp = client.get("/databases/", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    
    # Get DB
    get_resp = client.get(f"/databases/{db_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "My API DB"
    
    # Delete DB
    del_resp = client.delete(f"/databases/{db_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    
    # Verify deleted
    get_after_del = client.get(f"/databases/{db_id}", headers=auth_headers)
    assert get_after_del.status_code == 404

def test_ask_ai_endpoint(client, auth_headers):
    client.post("/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "password"
    })
    
    db_resp = client.post("/databases/", json={"name": "AI Test DB"}, headers=auth_headers)
    db_id = db_resp.json()["id"]
    
    client.post(f"/databases/{db_id}/tables", json={
        "name": "people",
        "columns": [
            {"name": "name", "type": "TEXT"}
        ]
    }, headers=auth_headers)
    
    client.post(f"/databases/{db_id}/tables/people/rows", json={
        "data": {"id": 1, "name": "John"}
    }, headers=auth_headers)
    
    # Real API request
    ask_resp = client.post(f"/databases/{db_id}/ask", json={
        "question": "How many people are there?"
    }, headers=auth_headers)
    
    assert ask_resp.status_code == 200
    assert "results" in ask_resp.json()
