from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, timedelta
from app.api.deps import get_db, auth_required
from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.user import User

from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/heatmap")
def get_heatmap(days: int = 90, user=Depends(auth_required), db: Session = Depends(get_db)):
    """
    Returns daily completion counts for the last N days.
    Format: { "2024-04-01": 2, "2024-04-02": 0, ... }
    Used by the HabitHeatmap calendar component.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    logs = db.query(
        HabitLog.date,
        func.count(HabitLog.id).label("count")
    ).join(Habit, Habit.id == HabitLog.habit_id).filter(
        Habit.user_id == user.id,
        HabitLog.date >= start_date,
        HabitLog.date <= end_date,
    ).group_by(HabitLog.date).all()

    # Build full dict with 0-filled gaps
    result: dict = {}
    for i in range(days + 1):
        d = (start_date + timedelta(days=i)).isoformat()
        result[d] = 0

    for log in logs:
        result[log.date.isoformat()] = log.count

    return {
        "success": True,
        "heatmap": result,
        "total_completions": sum(result.values()),
        "active_days": sum(1 for v in result.values() if v > 0),
    }

@router.get("/pulse")
def get_identity_pulse(user=Depends(auth_required), db: Session = Depends(get_db)):
    """
    Returns the user's behavioral alignment with their identity goal.
    """
    return AnalyticsService.get_identity_pulse(db, user.id)


@router.get("/weekly")
def get_weekly_report(user=Depends(auth_required), db: Session = Depends(get_db)):
    today = date.today()
    week_ago = today - timedelta(days=7)

    logs = db.query(HabitLog).join(Habit, Habit.id == HabitLog.habit_id).filter(
        Habit.user_id == user.id,
        HabitLog.date >= week_ago
    ).all()

    if not logs:
        return {
            "total_completed": 0,
            "best_day": None,
            "completion_rate": 0,
            "improvement_tip": "Start your first habit today!"
        }

    # Completion count per day
    daily_counts = {}
    for log in logs:
        daily_counts[log.date] = daily_counts.get(log.date, 0) + 1

    # Best day of week
    weekdays = [log.date.strftime("%A") for log in logs]
    best_day = max(set(weekdays), key=weekdays.count)

    # Worst day (theoretical)
    all_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    missing_days = set(all_weekdays) - set(weekdays)
    improvement_tip = f"Try focusing more on {list(missing_days)[0]}" if missing_days else "You are crushing it on every day!"

    return {
        "total_completed": len(logs),
        "unique_days": len(daily_counts),
        "best_day": best_day,
        "completion_rate": round((len(daily_counts) / 7) * 100, 1),
        "improvement_tip": improvement_tip
    }

@router.get("/leaderboard")
def get_leaderboard(user=Depends(auth_required), db: Session = Depends(get_db)):
    # Simple leaderboard: Total completions this week
    week_ago = date.today() - timedelta(days=7)
    
    results = db.query(
        User.id,
        User.email,
        func.count(HabitLog.id).label("score")
    ).join(Habit, Habit.user_id == User.id).join(HabitLog, HabitLog.habit_id == Habit.id).filter(
        HabitLog.date >= week_ago
    ).group_by(User.id).order_by(desc("score")).limit(10).all()

    leaderboard = []
    user_rank = 0
    for i, res in enumerate(results):
        display_name = res.email.split("@")[0]
        leaderboard.append({
            "id": res.id,
            "name": display_name,
            "score": res.score,
            "is_me": res.id == user.id
        })
        if res.id == user.id:
            user_rank = i + 1

    return {
        "top_users": leaderboard,
        "my_rank": user_rank
    }

@router.get("/recommendations")
def get_recommendations(user=Depends(auth_required), db: Session = Depends(get_db)):
    logs = db.query(HabitLog).join(Habit, Habit.id == HabitLog.habit_id).filter(
        Habit.user_id == user.id
    ).all()

    if not logs:
        return {
            "insights": ["Welcome! Start with one small habit to build momentum."],
            "suggestion": "Drink Water"
        }

    completion_rate = len(logs) / max(1, db.query(Habit).filter(Habit.user_id == user.id).count() * 7)
    
    insights = []
    if completion_rate < 0.4:
        insights.append("Focus on one habit at a time to stay consistent.")
    elif completion_rate > 0.8:
        insights.append("You are crushing it! Ready for a new challenge?")
        
    # Time insight
    hours = [log.completed_at.hour for log in logs if log.completed_at]
    if hours:
        best_hour = max(set(hours), key=hours.count)
        time_period = "morning" if best_hour < 12 else ("afternoon" if best_hour < 18 else "night")
        insights.append(f"You perform best during the {time_period}.")

    return {
        "insights": insights,
        "suggestion": "Meditation" if completion_rate > 0.6 else "Keep going with current habits"
    }
