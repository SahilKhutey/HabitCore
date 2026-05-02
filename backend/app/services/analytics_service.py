from sqlalchemy.orm import Session
from app.models.analytics import AnalyticsEvent
from app.models.user import User
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.services.websocket_service import manager
import asyncio
from datetime import datetime, timedelta
from app.core.constants import IDENTITY_WEIGHTS

class AnalyticsService:
    @staticmethod
    def log_event(db: Session, user_id: str, event_type: str, metadata: dict = {}):
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=event_type,
            metadata_json=metadata
        )
        db.add(event)
        db.commit()
        
        # Broadcast via WebSockets (async)
        event_data = {
            "user_id": user_id,
            "event_type": event_type,
            "metadata": metadata,
            "created_at": str(event.created_at)
        }
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(manager.broadcast(event_data))
        except RuntimeError:
            # Called from a thread without an event loop
            pass

    @staticmethod
    def get_identity_pulse(db: Session, user_id: str):
        """
        Calculates how aligned a user's recent actions are with their stated identity goal.
        Deep analysis of habit categories vs. identity mapping.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}

        # 1. Fetch completions from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        completions = db.query(HabitLog.id, Habit.name).join(Habit, HabitLog.habit_id == Habit.id).filter(
            Habit.user_id == user_id,
            HabitLog.completed_at >= thirty_days_ago
        ).all()

        # 2. Score based on identity goal
        target_categories = IDENTITY_WEIGHTS.get(user.identity_goal, [])

        score = 0
        total = len(completions)
        
        if total == 0:
            return {"score": 0, "status": "Inactive", "total_completions": 0}

        for log_id, habit_name in completions:
            # We check if the habit name contains a target category keyword
            if any(cat.lower() in habit_name.lower() for cat in target_categories):
                score += 1

        pulse_percentage = (score / total) * 100
        
        return {
            "score": int(pulse_percentage),
            "goal": user.identity_goal,
            "total_completions": total,
            "status": "Aligned" if pulse_percentage > 70 else "Wandering"
        }

