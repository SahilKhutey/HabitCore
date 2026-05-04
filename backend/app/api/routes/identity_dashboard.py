from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.api.deps import get_db, auth_required
from app.models.user import User
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
    
    # 4. Calculate Discipline Score (Mock logic for now, should pull from analytics)
    # In a real app, this would query reflections and habit completion rates
    discipline_score = current_user.level * 10 # Just a placeholder
    
    return {
        "user_id": current_user.id,
        "journey_day": journey_day,
        "phase": phase,
        "identity_label": identity_label,
        "discipline_score": min(discipline_score, 100),
        "onboarding_stuck_reason": onboarding.get("stuck_reason"),
        "instant_insight": onboarding.get("instant_insight")
    }
