import pytest

def test_user_registration(client):
    response = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User created"

def test_user_login(client):
    # Register first
    client.post(
        "/auth/register",
        json={"email": "loginuser@example.com", "password": "securepassword"}
    )
    
    # Then login
    response = client.post(
        "/auth/login",
        json={"email": "loginuser@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user_id" in data

def test_invalid_login(client):
    # Try logging in without registering
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
