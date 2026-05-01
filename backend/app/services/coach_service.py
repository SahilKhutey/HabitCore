from sqlalchemy.orm import Session
from app.models.habit_log import HabitLog
from app.models.user import User
from datetime import datetime, timedelta

class CoachService:
    @staticmethod
    def get_daily_insight(db: Session, user: User):
        # 1. Fetch recent logs
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        logs = db.query(HabitLog).filter(
            HabitLog.habit_id.in_(
                [h.id for h in user.habits] # assuming relationship exists
            ),
            HabitLog.date >= seven_days_ago.date()
        ).all()

        completion_rate = len(logs) / (len(user.habits) * 7) if user.habits and len(user.habits) > 0 else 0

        # 2. Logic for insights
        if completion_rate < 0.3:
            return {
                "message": "Focus on just one habit today. Small wins build momentum.",
                "action": "Complete your easiest habit"
            }
        
        if completion_rate > 0.8:
            return {
                "message": "Consistency Master! You're ready for a new challenge.",
                "action": "Add a new habit"
            }

        # 3. Time-based insight (simulated)
        if user.last_active_hour > 18:
            return {
                "message": "You perform best in the evening. Keep your hardest tasks for 7 PM.",
                "action": "Review evening goals"
            }

        return {
            "message": "You're building a solid foundation. Stay focused on your identity.",
            "action": "View progress"
        }
