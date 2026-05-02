from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from app.api.deps import get_db, auth_required
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.behavioral import UserBehaviorLog
from app.core.habit_orchestrator import get_habit_orchestrator
from app.services.reward_service import reward_service
from app.services.analytics_service import AnalyticsService
from app.services.behavioral_insight_engine.service import BehavioralInsightService

router = APIRouter()

@router.post("/seed")
def seed_habits(user=Depends(auth_required), db: Session = Depends(get_db)):
    """Seed initial habits for a new user"""
    existing = db.query(Habit).filter(Habit.user_id == user.id).first()
    if existing:
        return {"status": "already seeded"}
        
    habits = [
        Habit(user_id=user.id, name="Morning Meditation", time="07:00", difficulty="medium"),
        Habit(user_id=user.id, name="Deep Work Session", time="09:00", difficulty="hard"),
        Habit(user_id=user.id, name="Evening Review", time="21:00", difficulty="easy"),
    ]
    db.add_all(habits)
    db.commit()
    return {"status": "seeded", "habits": len(habits)}

@router.post("/reset-burnout")
def reset_burnout(user=Depends(auth_required), db: Session = Depends(get_db)):
    """Simulate a neural reset to reduce burnout score"""
    # Reduce burnout score impact
    reset_log = UserBehaviorLog(
        user_id=user.id,
        event_type="neural_reset",
        event_data={"impact": -0.2, "source": "manual_trigger"},
        context={"timestamp": datetime.utcnow().isoformat()}
    )
    db.add(reset_log)
    db.commit()
    return {"status": "reset success", "new_burnout_impact": -0.2}

class HabitCreate(BaseModel):
    name: str
    time: Optional[str] = None

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    time: Optional[str] = None

class HabitCompletionRequest(BaseModel):
    habit_id: str
    habit_name: Optional[str] = None
    difficulty: str = "medium"
    completed: bool = True
    current_streak: int = 0
    metadata: Dict[str, Any] = {}

@router.post("/create")
def create_habit(data: HabitCreate, user=Depends(auth_required), db: Session = Depends(get_db)):
    habits_count = db.query(Habit).filter(Habit.user_id == user.id).count()
    if habits_count >= 3 and not user.is_premium:
        raise HTTPException(status_code=403, detail="Upgrade to premium")

    habit = Habit(user_id=user.id, name=data.name, time=data.time)
    db.add(habit)
    db.commit()
    db.refresh(habit)
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
async def complete_habit(
    request: HabitCompletionRequest,
    background_tasks: BackgroundTasks,
    user = Depends(auth_required),
    db: Session = Depends(get_db)
):
    """Complete a habit — triggers reward orchestration and behavioral insight generation."""
    try:
        orchestrator = get_habit_orchestrator(db)
        result = await orchestrator.process_habit_completion(
            user.id,
            request.dict()
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        # Fire behavioral insight generation in background (non-blocking)
        def _run_insights(user_id: str):
            from app.db.session import SessionLocal
            bg_db = SessionLocal()
            try:
                habit_count = bg_db.query(Habit).filter(
                    Habit.user_id == user_id,
                    Habit.is_active == True,
                ).count()
                svc = BehavioralInsightService(bg_db)
                svc.run_for_user(user_id=user_id, habit_count=habit_count)
            except Exception as e:
                print(f"[InsightEngine] Background run error: {e}")
            finally:
                bg_db.close()

        background_tasks.add_task(_run_insights, str(user.id))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    change = reward_service.adjust_habit_difficulty(habit, logs)
    
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

@router.get("/state")
async def get_habit_state(user=Depends(auth_required), db: Session = Depends(get_db)):
    """
    Unified Command Center endpoint for the frontend.
    Returns synchronized state for Dashboard, Intelligence, and Wellness centers.
    """
    try:
        orchestrator = get_habit_orchestrator(db)
        user_state = await orchestrator._update_user_state(user.id)
    except Exception:
        user_state = {
            "burnout_score": 0.0,
            "mode": "normal",
            "identity_pulse": 0
        }
    
    # Get pulse from analytics
    try:
        pulse = AnalyticsService.get_identity_pulse(db, user.id)
        pulse_score = pulse.get("score", 0)
    except Exception:
        pulse_score = 0

    # Compute current streak from HabitLog
    try:
        streak = 0
        check_date = date.today()
        while True:
            completed = db.query(HabitLog).filter(
                HabitLog.user_id == user.id,
                HabitLog.date == check_date
            ).first()
            if completed:
                streak += 1
                check_date = check_date - timedelta(days=1)
            else:
                break
    except Exception:
        streak = 0

    # Get daily habits status
    today = date.today()
    completed_ids = db.query(HabitLog.habit_id).filter(
        HabitLog.user_id == user.id,
        HabitLog.date == today
    ).all()
    
    return {
        "success": True,
        "user_state": {
            **user_state,
            "level": user.level,
            "xp": user.xp,
            "coins": user.coins,
            "identity_goal": user.identity_goal,
            "archetype": user.archetype,
            "current_streak": streak,
            "identity_pulse": pulse_score,
            "daily_habit_goal": getattr(user, 'daily_habit_goal', 3),
        },
        "habits_completed_today": [log[0] for log in completed_ids],
        "server_time": datetime.utcnow().isoformat()
    }

@router.get("/")
def get_user_habits(user=Depends(auth_required), db: Session = Depends(get_db)):
    return db.query(Habit).filter(Habit.user_id == user.id).all()

@router.get("/activity")
def get_activity_feed(limit: int = 10, user=Depends(auth_required), db: Session = Depends(get_db)):
    """Returns the last N habit completion events for the activity feed."""
    logs = db.query(HabitLog, Habit).join(
        Habit, HabitLog.habit_id == Habit.id
    ).filter(
        Habit.user_id == user.id
    ).order_by(
        HabitLog.completed_at.desc()
    ).limit(limit).all()
    
    feed = []
    for log, habit in logs:
        completed_at = log.completed_at or datetime.utcnow()
        # Compute how long ago
        delta = datetime.utcnow() - completed_at
        if delta.seconds < 3600:
            time_ago = f"{delta.seconds // 60}m ago"
        elif delta.days == 0:
            time_ago = f"{delta.seconds // 3600}h ago"
        else:
            time_ago = f"{delta.days}d ago"
        
        feed.append({
            "id": str(log.id),
            "habit_name": habit.name,
            "xp_earned": habit.difficulty == "hard" and 150 or (habit.difficulty == "medium" and 80 or 40),
            "time_ago": time_ago,
            "completed_at": completed_at.isoformat(),
            "difficulty": habit.difficulty,
        })
    
    return {"feed": feed, "total": len(feed)}

