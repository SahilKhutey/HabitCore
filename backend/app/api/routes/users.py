from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.user import User
from app.models.habit_log import HabitLog
from app.schemas.user import UserSchema
from app.api.deps import get_db, auth_required
from app.services.shop_service import ShopService
from app.services.user_guardian import UserGuardian

from app.models.habit import Habit

router = APIRouter()
from app.services.gamification_service import calculate_level_data

@router.get("/level")
def get_level(user=Depends(auth_required)):
    level, current_xp, next_xp = calculate_level_data(user.xp)
    return {
        "level": level,
        "current_xp": current_xp,
        "next_level_xp": next_xp,
        "total_xp": user.xp
    }

@router.get("/status")
def get_user_status(user=Depends(auth_required), db: Session = Depends(get_db)):
    """
    Returns a unified health report for the user.
    """
    return UserGuardian.evaluate_health(db, user)

@router.get("/burnout")
def burnout(user=Depends(auth_required), db: Session = Depends(get_db)):
    # Deprecated in favor of /status, but kept for compatibility
    report = UserGuardian.evaluate_health(db, user)
    return {"burnout": report.is_burnout}

@router.get("/badges")
def get_badges(user=Depends(auth_required), db: Session = Depends(get_db)):
    from app.models.gamification import UserBadge, Badge
    badges = db.query(Badge).join(UserBadge).filter(UserBadge.user_id == user.id).all()
    return badges

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    from app.services.gamification_service import HeroService
    return HeroService.get_leaderboard(db)

@router.post("/shop/buy/{item_id}")
def buy_item(item_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    return ShopService.buy_item(db, user.id, item_id)

@router.get("/inventory")
def get_inventory(user=Depends(auth_required), db: Session = Depends(get_db)):
    from app.models.shop import UserInventory, ShopItem
    results = db.query(ShopItem, UserInventory.is_active, UserInventory.id.label("inventory_id")).join(UserInventory).filter(UserInventory.user_id == user.id).all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "description": item.description,
            "is_active": is_active,
            "inventory_id": inventory_id
        }
        for item, is_active, inventory_id in results
    ]

@router.put("/preferences")
def update_preferences(data: dict, user=Depends(auth_required), db: Session = Depends(get_db)):
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    return {"status": "updated"}

@router.post("/subscribe")
def subscribe(user=Depends(auth_required), db: Session = Depends(get_db)):
    user.is_premium = True
    db.commit()
    return {"status": "premium_activated"}

@router.post("/referral/apply")
def apply_referral(code: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    referrer = db.query(User).filter(User.referral_code == code).first()

    if not referrer or referrer.id == user.id:
        return {"error": "Invalid code"}

    # Check if already referred
    from app.models.gamification import Referral
    existing = db.query(Referral).filter(Referral.referred_id == user.id).first()
    if existing:
        return {"error": "Already referred"}

    db.add(Referral(
        referrer_id=referrer.id,
        referred_id=user.id
    ))

    # Reward both
    referrer.coins += 50
    user.coins += 50

    db.commit()

    return {"status": "applied", "referrer": referrer.email}
