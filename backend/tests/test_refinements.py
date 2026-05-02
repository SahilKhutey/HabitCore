import pytest
from app.core.security import security_engine
from app.core.state_engine import user_state_engine, UserMode

def test_security_rate_limiting():
    user_id = "test_user_123"
    # Flood with habit completion events
    for _ in range(30):
        assert security_engine.validate_event(user_id, "habit_completed", {"habit_id": "1", "completed": True}) == True
    
    # 31st should fail
    assert security_engine.validate_event(user_id, "habit_completed", {"habit_id": "1", "completed": True}) == False

def test_user_state_transitions():
    # Normal state
    normal_data = {
        'current_streak': 5,
        'completion_rate': 0.7,
        'session_frequency': 3,
        'recent_activity': 4,
        'burnout_score': 0.2
    }
    assert user_state_engine.determine_user_mode(normal_data) == UserMode.NORMAL
    
    # Hyper state
    hyper_data = {
        'current_streak': 15,
        'completion_rate': 0.95,
        'session_frequency': 7,
        'recent_activity': 10,
        'burnout_score': 0.1
    }
    assert user_state_engine.determine_user_mode(hyper_data) == UserMode.HYPER
    
    # Burnout state
    burnout_data = {
        'current_streak': 10,
        'completion_rate': 0.5,
        'session_frequency': 2,
        'recent_activity': 1,
        'burnout_score': 0.8
    }
    assert user_state_engine.determine_user_mode(burnout_data) == UserMode.BURNOUT

def test_cached_ai_service():
    from app.services.ai_service import AIService
    from unittest.mock import MagicMock
    
    behavior_mock = MagicMock()
    behavior_mock.calculate_burnout_score.return_value = 0.2
    behavior_mock.get_user_patterns.return_value = {"best_time": {"value": "Morning"}}
    service = AIService(behavior_mock)
    service.client = MagicMock() # Ensure it doesn't hit fallback before call
    
    user_id = "user_cache_test"
    context = {"current_streak": 5, "recent_failures": 0}
    
    # Mock AIService advice
    service._call_ai_api = MagicMock(return_value="Take a walk")
    
    # First call - cache miss
    advice1 = service.get_personalized_advice(user_id, context)
    assert advice1 == "Take a walk"
    assert service._call_ai_api.call_count == 1
    
    # Second call - cache hit
    advice2 = service.get_personalized_advice(user_id, context)
    assert advice2 == "Take a walk"
    assert service._call_ai_api.call_count == 1
