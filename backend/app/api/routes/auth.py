from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import hash_password, create_access_token
from app.api.deps import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        return {"error": "Invalid credentials"}

    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    # Update active hour & log event
    db_user.last_active_hour = datetime.utcnow().hour
    db.commit()
    AnalyticsService.log_event(db, db_user.id, "app_open")
    
    return {"access_token": access_token, "token_type": "bearer"}
