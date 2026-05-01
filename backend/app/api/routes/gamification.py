from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.services.challenge_service import ChallengeService

router = APIRouter()

@router.get("/today")
def get_today_challenge(db: Session = Depends(get_db)):
    return ChallengeService.get_todays_challenge(db)

@router.get("/progress/{challenge_id}")
def get_challenge_progress(challenge_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    challenge = ChallengeService.get_todays_challenge(db) # In production, find by ID
    return ChallengeService.check_progress(db, user.id, challenge)

@router.get("/ai/insight")
def get_ai_insight(user=Depends(auth_required), db: Session = Depends(get_db)):
    from app.services.coach_service import CoachService
    return CoachService.get_daily_insight(db, user)
