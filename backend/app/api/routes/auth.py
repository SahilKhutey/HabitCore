from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.api.deps import get_db
from app.services.identity_orchestrator import IdentityOrchestrator

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        IdentityOrchestrator.register_email(db, user.email, user.password)
        return {"message": "User created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Registration failed")

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    session = IdentityOrchestrator.authenticate_email(db, user.email, user.password)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return session
