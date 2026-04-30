from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.models.user_preferences import UserPreferences

router = APIRouter()

@router.get("/")
def get_preferences(user=Depends(auth_required), db: Session = Depends(get_db)):
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
    if not prefs:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs

@router.post("/")
def update_preferences(data: dict, user=Depends(auth_required), db: Session = Depends(get_db)):
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
    if not prefs:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)
        
    for key, value in data.items():
        if hasattr(prefs, key):
            setattr(prefs, key, value)
            
    db.commit()
    return prefs
