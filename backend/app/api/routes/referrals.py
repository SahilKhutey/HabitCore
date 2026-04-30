from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.models.user import User

router = APIRouter()

@router.post("/apply/{code}")
def apply_referral(code: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    if user.referral_code == code:
        raise HTTPException(status_code=400, detail="Cannot refer yourself")
        
    referrer = db.query(User).filter(User.referral_code == code).first()
    if not referrer:
        raise HTTPException(status_code=404, detail="Invalid referral code")

    # Reward both users
    user.xp += 100
    user.coins += 50
    
    referrer.xp += 100
    referrer.coins += 50
    
    db.commit()
    return {"status": "success", "message": "Rewards granted!"}
