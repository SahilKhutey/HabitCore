import pytest
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.habit import Habit
from app.services.nudge_engine import NudgeEngine

def test_onboarding_submission(client, db_session):
    # Setup fresh user
    from app.core.security import hash_password
    user = User(email="onboarding_test@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    
    # Login
    login_res = client.post("/auth/login", json={"email": "onboarding_test@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Submit Onboarding
    onboarding_data = {
        "change_goal": "Stop procrastinating",
        "primary_struggle": "Distractions",
        "stuck_moment": "Scrolling social media at night",
        "archetype": "builder"
    }
    res = client.post("/users/onboarding", json=onboarding_data, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "onboarding_completed"
    
    # Verify DB update
    db_session.refresh(user)
    assert user.onboarding_state["change_goal"] == "Stop procrastinating"
    assert user.archetype == "builder"
    assert user.identity_goal == "Productive"
    
    # Verify habits seeded
    habits = db_session.query(Habit).filter(Habit.user_id == user.id).all()
    assert len(habits) > 0
    assert any(h.name == "Deep Work Session" for h in habits)

def test_journey_phase_progression(db_session):
    # Create test user
    user = User(
        email="progression@example.com", 
        identity_goal="Elite Athlete",
        current_streak=0
    )
    db_session.add(user)
    db_session.commit()
    
    habit = Habit(user_id=user.id, name="Morning Run", difficulty="hard")
    db_session.add(habit)
    db_session.commit()
    
    # Phase 1: Hook (Streak 1)
    user.current_streak = 1
    phase = NudgeEngine.get_user_phase(user)
    assert phase == "hook"
    nudge = NudgeEngine.generate_nudge(user, habit)
    assert any(word in nudge.lower() for word in ["pathway", "dopamine", "small wins", "neurological mapping", "first few days"])
    
    # Phase 2: Awareness (Streak 5)
    user.current_streak = 5
    phase = NudgeEngine.get_user_phase(user)
    assert phase == "awareness"
    nudge = NudgeEngine.generate_nudge(user, habit)
    assert any(word in nudge.lower() for word in ["observation", "energy peaks", "pattern", "awareness", "mastery"])
    
    # Phase 3: Intervention (Streak 10)
    user.current_streak = 10
    phase = NudgeEngine.get_user_phase(user)
    assert phase == "intervention"
    nudge = NudgeEngine.generate_nudge(user, habit)
    assert any(word in nudge.lower() for word in ["resilience", "friction", "intervene", "elite athlete", "in control"])
    
    # Phase 4: Identity (Streak 25)
    user.current_streak = 25
    phase = NudgeEngine.get_user_phase(user)
    assert phase == "identity"
    nudge = NudgeEngine.generate_nudge(user, habit)
    assert any(word in nudge.lower() for word in ["evidence", "embodying", "solidified", "elite athlete", "who you are"])

def test_identity_dashboard_summary(client, db_session):
    # Setup user with 15 days age
    from app.core.security import hash_password
    created_at = datetime.now(timezone.utc) - timedelta(days=15)
    user = User(
        email="identity_dash@example.com", 
        password_hash=hash_password("password123"),
        created_at=created_at,
        level=3,
        archetype="warrior",
        onboarding_state={"archetype": "warrior", "stuck_moment": "late night snacks"}
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    login_res = client.post("/auth/login", json={"email": "identity_dash@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get Summary
    res = client.get("/identity/summary", headers=headers)
    assert res.status_code == 200
    data = res.json()
    
    assert data["journey_day"] >= 15
    assert data["phase"] == "Identity"
    assert data["identity_label"] == "warrior"
    assert data["discipline_score"] == 30 # level 3 * 10
