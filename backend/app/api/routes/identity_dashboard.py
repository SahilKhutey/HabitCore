from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.api.deps import get_db, auth_required
from app.models.user import User
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from sqlalchemy import func
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

@router.get("/summary")
def get_identity_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_required)
):
    """Returns a high-level summary of the user's 30-day identity journey."""
    
    # 1. Calculate Journey Day
    created_at = current_user.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    journey_day = (datetime.now(timezone.utc) - created_at).days
    
    # 2. Determine Phase
    phase = "Hook"
    if journey_day > 14:
        phase = "Identity"
    elif journey_day > 7:
        phase = "Intervention"
    elif journey_day > 2:
        phase = "Awareness"
        
    # 3. Get Onboarding Insights
    onboarding = current_user.onboarding_state or {}
    identity_label = onboarding.get("archetype", "Seeker")
    
    # 4. Calculate Discipline Score
    seven_days_ago = datetime.now(timezone.utc).date() - timedelta(days=7)
    
    completions = db.query(func.count(HabitLog.id)).filter(
        HabitLog.user_id == current_user.id,
        HabitLog.date >= seven_days_ago
    ).scalar() or 0
    
    habit_count = db.query(func.count(Habit.id)).filter(
        Habit.user_id == current_user.id,
        Habit.is_active == True
    ).scalar() or 1
    
    expected = habit_count * 7
    discipline_score = (completions / expected) * 100
    
    return {
        "user_id": current_user.id,
        "journey_day": journey_day,
        "phase": phase,
        "identity_label": identity_label,
        "discipline_score": min(round(discipline_score, 1), 100),
        "onboarding_stuck_reason": onboarding.get("stuck_reason"),
        "instant_insight": onboarding.get("instant_insight")
    }

class IdentityShiftRequest(BaseModel):
    archetype: str
    level: int

@router.post("/shift")
def shift_identity(
    data: IdentityShiftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_required)
):
    """Manually shift user identity and level (Demo/Debug only)"""
    onboarding = current_user.onboarding_state or {}
    onboarding["archetype"] = data.archetype
    current_user.onboarding_state = onboarding
    current_user.archetype = data.archetype
    current_user.identity_level = "Monk" if data.archetype == "monk" else "Beginner"
    current_user.level = data.level
    
    # Also update user_behavior_state if it exists
    from app.models.user_behavior_state import UserBehaviorState
    state = db.query(UserBehaviorState).filter(UserBehaviorState.user_id == current_user.id).first()
    if state:
        # In this system, archetype is stored in user.onboarding_state or user.archetype
        # We update the state to reflect a 'stable' monk status
        state.current_state = "stable"
        state.last_score = 95.0 # High integrity for monk

    db.commit()
    return {"status": "identity shifted", "archetype": data.archetype}
