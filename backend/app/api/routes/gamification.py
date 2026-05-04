from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.services.gamification_service import gamification_service
from app.services.ai_service import get_ai_service

router = APIRouter()

@router.get("/today")
def get_today_challenge(db: Session = Depends(get_db)):
    return gamification_service.get_todays_challenge(db)

@router.get("/progress/{challenge_id}")
def get_challenge_progress(challenge_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    challenge = gamification_service.get_todays_challenge(db)
    return gamification_service.check_challenge_progress(db, user.id, challenge)

@router.get("/ai/insight")
def get_ai_insight(user=Depends(auth_required), db: Session = Depends(get_db)):
    from app.services.behavioral_insight_engine.service import BehavioralInsightService
    service = BehavioralInsightService(db)
    insights = service.get_feed(str(user.id), limit=1)
    
    if insights:
        return {"insight": insights[0].message}
        
    return {
        "insight": "Your behavioral engine is warming up. Complete more habits to unlock deep psychological insights."
    }
