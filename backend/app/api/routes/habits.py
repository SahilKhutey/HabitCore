from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional, List
import uuid

from app.api.deps import get_db, auth_required
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.services.gamification_service import calculate_xp_reward, calculate_level_data, calculate_coin_reward
from app.services.habit_service import calculate_streak, adjust_habit_difficulty
from app.services.habit_engine import HabitEngine
from app.services.analytics_service import AnalyticsService

router = APIRouter()

class HabitCreate(BaseModel):
    name: str
    time: Optional[str] = None

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    time: Optional[str] = None

@router.post("/create")
def create_habit(data: HabitCreate, user=Depends(auth_required), db: Session = Depends(get_db)):
    habits_count = db.query(Habit).filter(Habit.user_id == user.id).count()
    if habits_count >= 3 and not user.is_premium:
        raise HTTPException(status_code=403, detail="Upgrade to premium")

    habit = Habit(user_id=user.id, name=data.name, time=data.time)
    db.add(habit)
    db.commit()
    return habit

@router.put("/{habit_id}")
def update_habit(habit_id: str, data: HabitUpdate, user=Depends(auth_required), db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit: raise HTTPException(404, "Habit not found")
    
    if data.name: habit.name = data.name
    if data.time: habit.time = data.time
    
    db.commit()
    return habit

@router.delete("/{habit_id}")
def delete_habit(habit_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit: raise HTTPException(404, "Habit not found")
    
    # Delete logs too
    db.query(HabitLog).filter(HabitLog.habit_id == habit_id).delete()
    db.delete(habit)
    db.commit()
    return {"status": "deleted"}

@router.get("/today/status")
def get_today_status(user=Depends(auth_required), db: Session = Depends(get_db)):
    today = date.today()
    logs = db.query(HabitLog.habit_id).join(Habit, Habit.id == HabitLog.habit_id).filter(
        Habit.user_id == user.id,
        HabitLog.date == today
    ).all()
    return [log[0] for log in logs]

@router.post("/complete")
def complete_habit(habit_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    try:
        result = HabitEngine.complete(db, habit_id, user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{habit_id}/history")
def get_habit_history(habit_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit: raise HTTPException(404, "Habit not found")
    
    logs = db.query(HabitLog.date).filter(HabitLog.habit_id == habit_id).all()
    return [log[0].isoformat() for log in logs]

@router.get("/{habit_id}/smart-time")
def get_smart_time(habit_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    logs = db.query(HabitLog).filter(HabitLog.habit_id == habit_id).all()
    if not logs:
        return {"hour": 9}
    
    hours = [log.completed_at.hour for log in logs if log.completed_at]
    if not hours:
        return {"hour": 9}
        
    # Most frequent hour (mode)
    smart_hour = max(set(hours), key=hours.count)
    
    # Nudge: 1 hour before the usual time
    nudge_hour = max(6, smart_hour - 1)
    
    return {"hour": nudge_hour}

@router.post("/{habit_id}/adjust")
def adjust_difficulty(habit_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit: raise HTTPException(404, "Habit not found")
    
    # Cooldown check: 3 days
    if habit.last_adjusted_at:
        if (datetime.utcnow() - habit.last_adjusted_at).days < 3:
            return {"status": "cooldown", "message": "Adjustment on cooldown"}

    logs = db.query(HabitLog).filter(HabitLog.habit_id == habit_id).all()
    change = adjust_habit_difficulty(habit, logs)
    
    if change:
        habit.last_adjusted_at = datetime.utcnow()
        db.commit()
    
    return {"status": "success", "change": change, "difficulty": habit.difficulty}

@router.put("/{habit_id}/difficulty")
def set_difficulty(habit_id: str, level: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if not habit: raise HTTPException(404, "Habit not found")
    
    if level not in ["easy", "medium", "hard"]:
        raise HTTPException(400, "Invalid difficulty level")
        
    habit.difficulty = level
    db.commit()
    return habit

from app.services.user_guardian import UserGuardian

@router.post("/{habit_id}/freeze")
def use_freeze(habit_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    if UserGuardian.apply_freeze(db, user, habit_id):
        return {"status": "streak saved", "remaining_freezes": user.streak_freeze}

    return {"status": "not needed or no freeze"}

@router.get("/{user_id}")
def get_user_habits(user_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    if user_id != user.id: raise HTTPException(403, "Forbidden")
    return db.query(Habit).filter(Habit.user_id == user.id).all()
