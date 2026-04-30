from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserSchema

from app.services.shop_service import ShopService

router = APIRouter()

@router.get("/leaderboard", response_model=List[UserSchema])
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.xp.desc()).limit(50).all()
    return users

@router.post("/shop/buy/{item_id}")
def buy_item(item_id: str, user_id: str, db: Session = Depends(get_db)):
    return ShopService.buy_item(db, user_id, item_id)
