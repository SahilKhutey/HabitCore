from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date
from app.api.deps import get_db, auth_required
from app.services.psychological_service import psychological_service
from app.services.reward_service import reward_service
from app.services.behavior_memory_service import BehaviorMemoryService
from app.services.ai_coach_service import AICoachService
from app.services.cached_ai_service import CachedAICoachService
from app.core.security import security_engine
from app.models.psychological import DailyCheckin

router = APIRouter()

# Global cached AI service instance
behavior_service_mock = None # Will be initialized per request or use a factory
cached_ai_service = None

def get_cached_ai_service(db: Session):
    global cached_ai_service
    if not cached_ai_service:
        behavior_service = BehaviorMemoryService(db)
        cached_ai_service = CachedAICoachService(behavior_service)
    return cached_ai_service

# Behavior routes
@router.post("/behavior/log")
def log_behavior(event_type: str, event_data: Dict, user=Depends(auth_required), db: Session = Depends(get_db)):
    # Security check
    if not security_engine.validate_event(user.id, event_type, event_data):
        raise HTTPException(status_code=429, detail="Too many requests or invalid data")
        
    service = BehaviorMemoryService(db)
    service.log_behavior(user.id, event_type, event_data)
    return {"success": True}

@router.get("/behavior/patterns")
def get_patterns(user=Depends(auth_required), db: Session = Depends(get_db)):
    service = BehaviorMemoryService(db)
    # Trigger analysis
    service.analyze_time_patterns(user.id)
    service.analyze_day_patterns(user.id)
    
    patterns = service.get_user_patterns(user.id)
    burnout_score = service.calculate_burnout_score(user.id)
    
    return {
        "success": True, 
        "patterns": patterns,
        "burnout_score": burnout_score
    }

@router.post("/ai-coach/advice")
def get_ai_advice(context: Dict, user=Depends(auth_required), db: Session = Depends(get_db)):
    # Security check
    if not security_engine.validate_event(user.id, "ai_coach", context):
        raise HTTPException(status_code=429, detail="Too many requests")
        
    service = get_cached_ai_service(db)
    advice = service.get_advice(user.id, context)
    return {"success": True, "advice": advice}

class CheckinRequest(BaseModel):
    mood: str
    energy_morning: str
    energy_evening: str
    sleep_quality: int
    tags: Optional[List[str]] = []
    reflection: Optional[str] = None

class HabitCompletionRequest(BaseModel):
    habit_id: str
    completed: bool
    difficulty: str

@router.post("/checkin")
def daily_checkin(request: CheckinRequest, user=Depends(auth_required), db: Session = Depends(get_db)):
    try:
        # Store checkin data
        checkin = DailyCheckin(
            user_id=user.id,
            mood=request.mood,
            energy_morning=request.energy_morning,
            energy_evening=request.energy_evening,
            sleep_quality=request.sleep_quality,
            tags=request.tags,
            reflection=request.reflection
        )
        db.add(checkin)
        db.commit()
        db.refresh(checkin)
        
        # Generate insights
        checkin_dict = {
            "mood": checkin.mood,
            "energy_morning": checkin.energy_morning,
            "energy_evening": checkin.energy_evening,
            "sleep_quality": checkin.sleep_quality
        }
        
        insights = psychological_service.calculate_daily_insights(
            checkin_dict, 
            {}  # Would include habit data in real implementation
        )
        
        return {
            "success": True,
            "checkin": {
                "id": checkin.id,
                "date": checkin.date.isoformat(),
                "mood": checkin.mood
            },
            "insights": insights,
            "message": psychological_service.generate_encouragement_message(True, {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkin error: {str(e)}")

@router.post("/habits/complete")
def complete_habit(request: HabitCompletionRequest, user=Depends(auth_required), db: Session = Depends(get_db)):
    try:
        # Calculate rewards
        xp_reward = psychological_service.calculate_xp_reward(
            request.difficulty, 
            user.current_streak if hasattr(user, 'current_streak') else 0
        )
        
        user.xp += xp_reward
        user.coins += xp_reward // 2
        
        # Check level up
        level_data = reward_service.calculate_level_up(user.xp, user.level)
        
        if level_data["level_up"]:
            user.level = level_data["level"]
            # Apply rewards
            user.coins += level_data["reward"].get("coins", 0)
            
        db.commit()
        
        return {
            "success": True,
            "reward": {
                "xp": xp_reward,
                "coins": xp_reward // 2,
                "message": psychological_service.generate_encouragement_message(request.completed, {})
            },
            "level_up_info": level_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Habit completion error: {str(e)}")

@router.get("/daily-challenge")
def get_daily_challenge():
    try:
        challenge = reward_service.generate_daily_challenge()
        return {
            "success": True,
            "challenge": challenge
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Challenge generation error: {str(e)}")

@router.get("/user-progress")
def get_user_progress(user=Depends(auth_required)):
    try:
        return {
            "success": True,
            "progress": {
                "xp": user.xp,
                "level": user.level,
                "coins": user.coins,
                "identity_level": user.identity_level,
                "archetype": user.archetype,
                # "badges" and "unlocked_features" would fetch from separate tables/logic
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Progress fetch error: {str(e)}")
