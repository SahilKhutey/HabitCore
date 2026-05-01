from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.user import User
from app.services.habit_service import calculate_streak, adjust_habit_difficulty
from app.services.gamification_service import calculate_xp_reward, calculate_level_data, calculate_coin_reward, HeroService

class HabitCompletionResponse(BaseModel):
    status: str
    streak: int
    xp: int
    current_xp: int
    next_level_xp: int
    level: int
    xp_gained: int
    coins_gained: int
    difficulty_change: Optional[str] = None
    new_difficulty: Optional[str] = None

class HabitEngine:
    @staticmethod
    def complete(db: Session, habit_id: str, user: User) -> HabitCompletionResponse:
        """
        Processes a habit completion.
        Deep interface that orchestrates logs, streaks, rewards, and difficulty adjustments.
        """
        today = date.today()
        
        # 1. Check for existing log today
        existing = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id, 
            HabitLog.date == today
        ).first()
        
        if existing:
            level, current_xp, next_xp = calculate_level_data(user.xp)
            return HabitCompletionResponse(
                status="already_completed",
                streak=calculate_streak(db.query(HabitLog).filter(HabitLog.habit_id == habit_id).all()),
                xp=user.xp,
                current_xp=current_xp,
                next_level_xp=next_xp,
                level=user.level,
                xp_gained=0,
                coins_gained=0
            )

        # 2. Fetch Habit
        habit = db.query(Habit).filter(Habit.id == habit_id).first()
        if not habit:
            raise ValueError("Habit not found")

        # 3. Create Log
        log = HabitLog(habit_id=habit_id, date=today)
        db.add(log)
        
        # 4. Calculate Streak
        # We need all logs to calculate streak correctly
        all_logs = db.query(HabitLog).filter(HabitLog.habit_id == habit_id).all()
        streak = calculate_streak(all_logs)

        # 5. Calculate Rewards
        xp_gain, lucky_bonus = calculate_xp_reward(streak, habit.difficulty, user.mode)
        coin_gain = calculate_coin_reward(streak)
        total_xp_gain = xp_gain + lucky_bonus
        
        # 6. Update User State (Locality)
        user.xp += total_xp_gain
        user.coins += coin_gain
        level, current_xp, next_xp = calculate_level_data(user.xp)
        user.level = level
        
        # 7. Adaptive Difficulty Adjustment
        difficulty_change = adjust_habit_difficulty(habit, all_logs)
        if difficulty_change:
            habit.last_adjusted_at = datetime.utcnow()

        # 8. Premium Milestones
        total_logs = db.query(HabitLog).join(Habit).filter(Habit.user_id == user.id).count()
        HeroService.check_milestones(db, user, streak, total_logs)

        # 9. Commit Changes
        db.commit()
        
        return HabitCompletionResponse(
            status="completed",
            streak=streak,
            xp=user.xp,
            current_xp=current_xp,
            next_level_xp=next_xp,
            level=user.level,
            xp_gained=total_xp_gain,
            coins_gained=coin_gain,
            difficulty_change=difficulty_change,
            new_difficulty=habit.difficulty if difficulty_change else None
        )
