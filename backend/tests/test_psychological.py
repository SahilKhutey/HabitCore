import pytest
from app.models.user import User
from app.models.psychological import DailyCheckin

def test_daily_checkin(client, db_session):
    # Setup user
    from app.core.security import hash_password
    user = User(email="psy@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    
    # Login
    login_res = client.post("/auth/login", json={"email": "psy@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Checkin
    checkin_data = {
        "mood": "happy",
        "energy_morning": "high",
        "energy_evening": "medium",
        "sleep_quality": 4,
        "tags": ["productive"],
        "reflection": "Feeling great!"
    }
    res = client.post("/psychological/checkin", json=checkin_data, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] == True
    assert data["checkin"]["mood"] == "happy"
    assert len(data["insights"]["insights"]) > 0

def test_habit_completion_reward(client, db_session):
    # Setup user
    from app.core.security import hash_password
    user = User(email="reward@example.com", password_hash=hash_password("password123"), xp=0, level=1)
    db_session.add(user)
    db_session.commit()
    
    login_res = client.post("/auth/login", json={"email": "reward@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Complete habit
    res = client.post("/psychological/habits/complete", json={
        "habit_id": "123",
        "completed": True,
        "difficulty": "hard"
    }, headers=headers)
    
    assert res.status_code == 200
    data = res.json()
    assert data["reward"]["xp"] == 50 # Hard = 50 base XP
    
    # Verify user state
    db_session.refresh(user)
    assert user.xp == 50
    assert user.coins == 25
