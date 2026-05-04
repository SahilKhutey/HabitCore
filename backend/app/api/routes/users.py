from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from app.models.user import User
from app.models.habit_log import HabitLog
from app.schemas.user import UserSchema
from app.api.deps import get_db, auth_required
from app.services.shop_service import ShopService
from app.services.user_guardian import UserGuardian

from app.models.habit import Habit

router = APIRouter()
from app.services.reward_service import reward_service
from app.services.gamification_service import gamification_service

@router.get("/level")
def get_level(user=Depends(auth_required)):
    level_data = reward_service.calculate_level_up(user.xp, user.level)
    return {
        "level": level_data["level"],
        "current_xp": user.xp, # Total XP
        "next_level_xp": 100 * ((level_data["level"] + 1) ** 1.5), # Calculation logic
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
    return gamification_service.get_leaderboard(db)

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


# ─── ARCHETYPE / IDENTITY ──────────────────────────────────────────────────────

ARCHETYPE_HABITS = {
    "warrior": [
        {"name": "Morning Workout", "time": "06:00", "difficulty": "hard"},
        {"name": "Cold Shower", "time": "06:30", "difficulty": "medium"},
        {"name": "Evening Review", "time": "21:00", "difficulty": "easy"},
    ],
    "monk": [
        {"name": "Morning Meditation", "time": "07:00", "difficulty": "medium"},
        {"name": "Gratitude Journal", "time": "08:00", "difficulty": "easy"},
        {"name": "Evening Wind Down", "time": "21:30", "difficulty": "easy"},
    ],
    "builder": [
        {"name": "Deep Work Session", "time": "09:00", "difficulty": "hard"},
        {"name": "Learning Block", "time": "19:00", "difficulty": "medium"},
        {"name": "Daily Review", "time": "22:00", "difficulty": "easy"},
    ],
    "explorer": [
        {"name": "Morning Walk", "time": "08:00", "difficulty": "easy"},
        {"name": "Read & Explore", "time": "20:00", "difficulty": "medium"},
        {"name": "Connect with Someone", "time": "18:00", "difficulty": "easy"},
    ],
}

from pydantic import BaseModel
class ArchetypeRequest(BaseModel):
    archetype: str
    seed_habits: bool = True

class OnboardingInput(BaseModel):
    change_goal: str
    primary_struggle: str
    stuck_moment: str
    archetype: Optional[str] = None

@router.post("/onboarding", summary="Submit initial onboarding data to seed PsychEngine")
def submit_onboarding(data: OnboardingInput, user=Depends(auth_required), db: Session = Depends(get_db)):
    """
    Captures initial psychological state and seeds the behavioral journey.
    """
    user.onboarding_state = {
        "change_goal": data.change_goal,
        "primary_struggle": data.primary_struggle,
        "stuck_moment": data.stuck_moment,
        "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    if data.archetype:
        # Reuse existing archetype logic if provided
        set_archetype(ArchetypeRequest(archetype=data.archetype), user=user, db=db)
    
    db.commit()
    return {
        "status": "onboarding_completed",
        "message": "Let's understand how you think, not just what you do."
    }

@router.post("/set-archetype")
def set_archetype(data: ArchetypeRequest, user=Depends(auth_required), db: Session = Depends(get_db)):
    """Sets user archetype and optionally seeds archetype-appropriate starter habits."""
    valid = ["warrior", "monk", "builder", "explorer"]
    if data.archetype not in valid:
        from fastapi import HTTPException
        raise HTTPException(400, f"Invalid archetype. Choose from: {valid}")

    # Update user model
    user.archetype = data.archetype
    # Map archetype to identity goal
    archetype_to_goal = {
        "warrior": "Fit", "monk": "Calm", "builder": "Productive", "explorer": "Learner"
    }
    user.identity_goal = archetype_to_goal.get(data.archetype, "Productive")
    db.commit()

    seeded = []
    if data.seed_habits:
        existing_count = db.query(Habit).filter(Habit.user_id == user.id).count()
        # Only seed if user has < 2 habits (fresh account)
        if existing_count < 2:
            for h in ARCHETYPE_HABITS.get(data.archetype, []):
                habit = Habit(user_id=user.id, **h)
                db.add(habit)
                seeded.append(h["name"])
            db.commit()

    return {
        "status": "archetype_set",
        "archetype": data.archetype,
        "identity_goal": user.identity_goal,
        "habits_seeded": seeded
    }
