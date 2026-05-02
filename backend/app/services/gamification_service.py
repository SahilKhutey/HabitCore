import random
from typing import Dict, Any, List
from datetime import datetime, date, timedelta
from app.models.user import User
from app.models.gamification import DailyChallenge
from app.models.habit_log import HabitLog
from app.models.habit import Habit
from sqlalchemy.orm import Session

class GamificationService:
    def __init__(self):
        self.mystery_rewards = [
            {"type": "xp", "value": 50, "message": "🎉 Bonus XP!"},
            {"type": "coins", "value": 25, "message": "💰 Coin shower!"},
            {"type": "streak", "value": 1, "message": "🔥 Streak shield!"},
            {"type": "badge", "value": "lucky", "message": "🍀 Lucky day badge!"}
        ]
        
        self.streak_tension_messages = [
            "⏰ Only {time_left} to save your {streak}-day streak!",
            "⚠️ Don't let your {streak}-day streak slip away!",
            "🔔 {time_left} remaining - you've got this!",
            "🎯 So close! Just {time_left} to keep your streak alive!"
        ]
    
    def generate_mystery_reward(self) -> Dict[str, Any]:
        reward = random.choice(self.mystery_rewards)
        return {**reward, 'reveal_animation': True, 'anticipation_message': "What could it be? 🎁"}
    
    def get_streak_tension_message(self, streak: int, time_left: str) -> str:
        message = random.choice(self.streak_tension_messages)
        return message.format(streak=streak, time_left=time_left)
    
    def calculate_time_until_streak_loss(self, last_activity: datetime) -> str:
        deadline = last_activity + timedelta(days=1)
        time_left = deadline - datetime.utcnow()
        if time_left.total_seconds() <= 0: return "0h 0m"
        hours, minutes = int(time_left.total_seconds() / 3600), int((time_left.total_seconds() % 3600) / 60)
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

    def create_anticipation_loop(self, user_progress: Dict[str, Any]) -> Dict[str, Any]:
        xp = user_progress.get('xp', 0)
        next_milestone = self._get_next_milestone(xp)
        habits_to_milestone = max(1, (next_milestone - xp) // 10)
        return {
            'next_milestone': next_milestone,
            'habits_needed': habits_to_milestone,
            'message': f"Complete {habits_to_milestone} more habits for a milestone reward!",
            'progress_percentage': (xp % 100) / 100 * 100
        }
    
    def _get_next_milestone(self, current_xp: int) -> int:
        milestones = [100, 250, 500, 1000, 2500, 5000]
        for milestone in milestones:
            if current_xp < milestone: return milestone
        return ((current_xp // 1000) + 1) * 1000

    def get_todays_challenge(self, db: Session) -> DailyChallenge:
        challenge = db.query(DailyChallenge).order_by(DailyChallenge.created_at.desc()).first()
        if not challenge:
            challenge = DailyChallenge(title="Consistency King", condition_type="complete_habits", condition_value=3, reward_xp=50)
            db.add(challenge)
            db.commit()
            db.refresh(challenge)
        return challenge

    def check_challenge_progress(self, db: Session, user_id: str, challenge: DailyChallenge) -> Dict[str, Any]:
        if challenge.condition_type == "complete_habits":
            completed_count = db.query(HabitLog).join(Habit).filter(
                HabitLog.date == date.today(),
                Habit.user_id == user_id
            ).count()
            return {"current": completed_count, "target": challenge.condition_value, "is_completed": completed_count >= challenge.condition_value}
        return {"current": 0, "target": 1, "is_completed": False}

    @staticmethod
    def get_leaderboard(db: Session, limit: int = 10) -> List[User]:
        return db.query(User).order_by(User.xp.desc()).limit(limit).all()

# Singleton instance
gamification_service = GamificationService()
