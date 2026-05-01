from sqlalchemy.orm import Session
from app.models.user import User
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.services.analytics_service import AnalyticsService
from app.core.constants import IDENTITY_WEIGHTS
from datetime import datetime, timedelta, timezone

class NudgeEngine:
    @staticmethod
    def identify_sliding_users(db: Session):
        """
        Identifies users who haven't completed a habit in the last 24-48 hours.
        These users are at high risk of losing momentum (the 'Sliding' state).
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        risk_cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
        
        # Find habits that were active recently but missed today
        sliding_habits = db.query(Habit).filter(
            Habit.done == False,
            Habit.created_at < cutoff
        ).all()
        
        return sliding_habits

    @staticmethod
    def generate_identity_nudge(user: User, habit: Habit):
        """
        Generates a nudge message based on the user's identity goal.
        Example: 'A "Fit" person wouldn't miss a Gym session today. Keep it going!'
        """
        identity = user.identity_goal or "Hero"
        messages = [
            f"A '{identity}' person stays consistent. Don't forget your {habit.name} today!",
            f"Momentum is your superpower. Your '{identity}' identity is growing—keep it up!",
            f"One small action for a '{identity}' hero. Your {habit.name} is waiting."
        ]
        
        import random
        return random.choice(messages)

    @staticmethod
    def process_nudges(db: Session):
        """
        Main loop to identify sliding users and queue notifications.
        """
        sliding_habits = NudgeEngine.identify_sliding_users(db)
        nudges_sent = 0
        
        for habit in sliding_habits:
            user = db.query(User).filter(User.id == habit.user_id).first()
            if not user:
                continue
                
            message = NudgeEngine.generate_identity_nudge(user, habit)
            
            # Log event for notification service to pick up
            AnalyticsService.log_event(db, user.id, "nudge_generated", {
                "habit_id": str(habit.id),
                "message": message,
                "identity": user.identity_goal
            })
            nudges_sent += 1
            
        return nudges_sent
