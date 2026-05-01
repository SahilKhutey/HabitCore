import pytest
import asyncio
from app.core.habit_orchestrator import HabitOrchestrator
from app.models.user import User
from app.core.security import security_engine

@pytest.mark.asyncio
async def test_orchestrator_pipeline(db_session):
    security_engine.reset()
    # Setup user
    from app.core.security import hash_password
    user = User(email="orchestrator@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    
    orchestrator = HabitOrchestrator(db_session)
    
    habit_data = {
        "habit_id": "habit_1",
        "habit_name": "Test Habit",
        "difficulty": "hard",
        "completed": True,
        "current_streak": 4 # Next will be 5, triggering mystery reward tease
    }
    
    # Process completion
    result = await orchestrator.process_habit_completion(user.id, habit_data)
    
    assert result["success"] == True
    assert "rewards" in result
    assert result["rewards"]["total_xp"] > 0
    assert result["user_state"]["mode"] == "normal"
    assert "ai_advice" in result
    assert "gamification" in result
    
    # Verify behavior log was created
    from app.models.behavioral import UserBehaviorLog
    logs = db_session.query(UserBehaviorLog).filter(UserBehaviorLog.user_id == user.id).all()
    assert len(logs) == 1
    assert logs[0].event_type == "habit_completed"

@pytest.mark.asyncio
async def test_orchestrator_burnout_detection(db_session):
    security_engine.reset()
    # Setup user
    from app.core.security import hash_password
    user = User(email="burnout_orch@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    
    # Simulate high burnout in logs
    from app.models.behavioral import UserBehaviorLog
    from datetime import datetime, timedelta
    for i in range(5):
        # Failed habits
        log1 = UserBehaviorLog(
            user_id=user.id,
            event_type="habit_completed",
            event_data={"completed": False},
            timestamp=datetime.utcnow() - timedelta(hours=i)
        )
        # Low energy/mood checkins
        log2 = UserBehaviorLog(
            user_id=user.id,
            event_type="checkin",
            event_data={"energy_morning": "low", "mood": "tired"},
            timestamp=datetime.utcnow() - timedelta(hours=i)
        )
        db_session.add(log1)
        db_session.add(log2)
    db_session.commit()
    
    orchestrator = HabitOrchestrator(db_session)
    
    result = await orchestrator.process_habit_completion(user.id, {
        "habit_id": "burnout_test",
        "difficulty": "easy",
        "completed": True
    })
    
    assert result["success"] == True
    assert result["user_state"]["burnout_score"] > 0.7
    assert result["recovery_plan"] is not None
    assert result["user_state"]["mode"] == "burnout"
