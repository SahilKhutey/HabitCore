import random
from sqlalchemy.orm import Session
from app.models.gamification import DailyChallenge
from app.models.habit_log import HabitLog
from datetime import date

class ChallengeService:
    @staticmethod
    def get_todays_challenge(db: Session):
        """
        Returns the challenge for today. In production, this would be 
        persisted or generated once per day per user.
        """
        challenge = db.query(DailyChallenge).order_by(DailyChallenge.created_at.desc()).first()
        if not challenge:
            # Seed a default challenge if none exists
            challenge = DailyChallenge(
                title="Consistency King",
                condition_type="complete_habits",
                condition_value=3,
                reward_xp=50
            )
            db.add(challenge)
            db.commit()
            db.refresh(challenge)
        return challenge

    @staticmethod
    def check_progress(db: Session, user_id: str, challenge: DailyChallenge):
        if challenge.condition_type == "complete_habits":
            completed_count = db.query(HabitLog).join(HabitLog.habit).filter(
                HabitLog.date == date.today(),
                HabitLog.habit.has(user_id=user_id)
            ).count()
            
            return {
                "current": completed_count,
                "target": challenge.condition_value,
                "is_completed": completed_count >= challenge.condition_value
            }
        return {"current": 0, "target": 1, "is_completed": False}
