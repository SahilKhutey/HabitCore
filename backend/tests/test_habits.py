import pytest

def get_auth_token(client):
    client.post(
        "/auth/register",
        json={"email": "habituser@example.com", "password": "securepassword"}
    )
    response = client.post(
        "/auth/login",
        json={"email": "habituser@example.com", "password": "securepassword"}
    )
    return response.json()["access_token"], response.json()["user_id"]

def test_create_habit(client):
    token, user_id = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/habits/create",
        json={"name": "Test Habit", "time": "Morning", "difficulty": "medium", "target_per_day": 1},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Habit"
    assert "id" in data
    
def test_complete_habit(client):
    token, user_id = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create
    create_resp = client.post(
        "/habits/create",
        json={"name": "Test Habit", "time": "Morning", "difficulty": "medium", "target_per_day": 1},
        headers=headers
    )
    habit_id = create_resp.json()["id"]
    
    # Complete
    response = client.post(
        "/habits/complete",
        json={"habit_id": habit_id},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["rewards"]["total_xp"] > 0
