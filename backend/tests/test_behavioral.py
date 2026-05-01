import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.behavioral import UserBehaviorLog
from app.services.behavior_memory_service import BehaviorMemoryService

def test_burnout_scoring(client, db_session):
    # Setup user
    from app.core.security import hash_password
    user = User(email="burnout@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    
    service = BehaviorMemoryService(db_session)
    
    # Create logs simulating burnout
    # 5 failed habits, 3 low energy days, 3 poor mood days over last 7 days
    now = datetime.utcnow()
    
    # Habit failures
    for i in range(5):
        log = UserBehaviorLog(
            user_id=user.id,
            event_type='habit_completed',
            event_data={'completed': False},
            timestamp=now - timedelta(days=i)
        )
        db_session.add(log)
    
    # Low energy/mood checkins
    for i in range(3):
        log = UserBehaviorLog(
            user_id=user.id,
            event_type='checkin',
            event_data={'energy_morning': 'low', 'mood': 'tired'},
            timestamp=now - timedelta(days=i)
        )
        db_session.add(log)
    
    db_session.commit()
    
    score = service.calculate_burnout_score(user.id)
    assert score > 0.5
    
    # Create recovery plan
    plan = service.create_recovery_plan(user.id, "burnout")
    assert plan is not None
    assert plan.plan_type == "habit_reduction"

def test_time_pattern_analysis(client, db_session):
    # Setup user
    from app.core.security import hash_password
    user = User(email="pattern@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    
    service = BehaviorMemoryService(db_session)
    
    # Log 3 successful habits at 8 AM
    for _ in range(3):
        log = UserBehaviorLog(
            user_id=user.id,
            event_type='habit_completed',
            event_data={'completed': True},
            timestamp=datetime(2026, 5, 1, 8, 30)
        )
        db_session.add(log)
    
    db_session.commit()
    
    patterns = service.analyze_time_patterns(user.id)
    assert len(patterns) == 1
    assert patterns[0].insight_value == "8:00"
    assert patterns[0].confidence_score == 1.0
