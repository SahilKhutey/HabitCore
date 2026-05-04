from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Set
from pydantic import BaseModel

from app.models.user import User
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.analytics import AnalyticsEvent

class UserHealthReport(BaseModel):
    is_burnout: bool
    churn_risk_score: int
    streak_at_risk: bool
    remaining_freezes: int
    recommendation: str

class UserGuardian:
    @staticmethod
    def evaluate_health(db: Session, user: User) -> UserHealthReport:
        """
        Comprehensive health check for the user.
        Combines burnout detection, churn risk, and streak protection.
        """
        # 1. Burnout Detection (Completion Rate)
        today = date.today()
        seven_days_ago = today - timedelta(days=7)
        
        logs = db.query(HabitLog).join(Habit, HabitLog.habit_id == Habit.id).filter(
            Habit.user_id == user.id,
            HabitLog.date >= seven_days_ago
        ).all()
        
        unique_dates = {log.date for log in logs}
        completion_rate = len(unique_dates) / 7
        is_burnout = completion_rate < 0.3
        
        # 2. Churn Risk Calculation
        score = 0
        
        # Recency (Days since last app_open)
        last_open = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.user_id == user.id,
            AnalyticsEvent.event_type == "app_open"
        ).order_by(AnalyticsEvent.created_at.desc()).first()
        
        if not last_open:
            score += 50
        else:
            days_inactive = (datetime.now(timezone.utc) - last_open.created_at).days
            if days_inactive >= 3:
                score += 40
            elif days_inactive >= 1:
                score += 10
                
        # Engagement (Habits completed last 7 days)
        if len(logs) == 0:
            score += 30
        elif len(logs) < 3:
            score += 15
            
        # 3. Streak Protection Check
        # Check if any active habit missed yesterday
        yesterday = today - timedelta(days=1)
        habits = db.query(Habit).filter(Habit.user_id == user.id).all()
        streak_at_risk = False
        
        for habit in habits:
            yesterday_log = db.query(HabitLog).filter(
                HabitLog.habit_id == habit.id,
                HabitLog.date == yesterday
            ).first()
            if not yesterday_log:
                streak_at_risk = True
                break

        # 4. Recommendation Logic
        recommendation = "Keep it up!"
        if is_burnout:
            recommendation = "🧘 Let's slow down. Focus on just 1 habit today."
        elif streak_at_risk and user.streak_freeze > 0:
            recommendation = "❄️ Streak at risk! Use a freeze to save your progress."
        elif score > 50:
            recommendation = "🔥 You're losing momentum. Try a quick task to stay on track."

        return UserHealthReport(
            is_burnout=is_burnout,
            churn_risk_score=score,
            streak_at_risk=streak_at_risk,
            remaining_freezes=user.streak_freeze,
            recommendation=recommendation
        )

    @staticmethod
    def apply_freeze(db: Session, user: User, habit_id: str) -> bool:
        """
        Attempts to apply a streak freeze to a specific habit.
        Returns True if applied, False otherwise.
        """
        if user.streak_freeze <= 0:
            return False
            
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Check if yesterday was actually missed
        yesterday_log = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == yesterday
        ).first()
        
        if not yesterday_log:
            user.streak_freeze -= 1
            # We don't create a log for yesterday, but the streak calculation 
            # (which we should eventually deepen too) will need to know about freezes.
            # For now, we'll just deduct the freeze as per the user's initial snippet.
            db.commit()
            return True
            
        return False
