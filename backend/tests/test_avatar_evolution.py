import pytest
from sqlalchemy.orm import Session
from app.services.avatar_service import AvatarService
from app.models.avatar_models import Archetype, EvolutionStage, AvatarItem
from app.core.habit_orchestrator import HabitOrchestrator

def test_avatar_initialization(db_session: Session):
    service = AvatarService(db_session)
    user_id = "test_user_avatar"
    avatar = service.get_avatar(user_id)
    
    assert avatar.user_id == user_id
    assert avatar.level == 1
    assert avatar.xp == 0
    assert avatar.archetype == Archetype.BEGINNER

def test_archetype_progression(db_session: Session):
    service = AvatarService(db_session)
    user_id = "test_user_archetype"
    
    # Simulate fitness focus
    habit_data = {
        "category_distribution": {"fitness": 0.8},
        "consistency_score": 0.9,
        "current_streak": 5,
        "mood": "energetic"
    }
    
    avatar = service.update_avatar_progress(user_id, 100, habit_data)
    
    # Archetype should shift to Warrior due to fitness focus > 0.6
    assert avatar.archetype == Archetype.WARRIOR

def test_evolution_milestone(db_session: Session):
    service = AvatarService(db_session)
    user_id = "test_user_evolution"
    
    # Boost XP to trigger Apprentice stage (threshold 500)
    habit_data = {"category_distribution": {}, "consistency_score": 0.5}
    avatar = service.update_avatar_progress(user_id, 550, habit_data)
    
    assert avatar.evolution_stage == EvolutionStage.APPRENTICE
    assert avatar.total_xp == 550

def test_orchestrator_avatar_integration(db_session: Session):
    orchestrator = HabitOrchestrator(db_session)
    user_id = "test_user_orch"
    
    habit_data = {
        "habit_id": "habit_1",
        "name": "Heavy Lifting",
        "difficulty": "hard",
        "category": "fitness",
        "completed": True
    }
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(orchestrator.process_habit_completion(user_id, habit_data))
    
    assert result["success"] is True
    assert "avatar_update" in result
    assert result["avatar_update"]["level"] >= 1
    assert result["avatar_update"]["archetype"] == Archetype.WARRIOR
