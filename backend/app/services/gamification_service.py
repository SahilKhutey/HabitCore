from app.core.constants import DIFFICULTY_XP, STREAK_BONUS_30, STREAK_BONUS_7, STREAK_BONUS_3, XP_LEVEL_BASE

def calculate_xp_reward(streak: int, difficulty: str = "Medium", user_mode: str = "Consistency"):
    base_xp = DIFFICULTY_XP.get(difficulty, 20)

    
    # Speed Runner mode gets +25% base XP but lower streak bonuses
    if user_mode == "Speed":
        base_xp = int(base_xp * 1.25)
    
    bonus_xp = 0
    # Streak rewards (Consistency King gets double streak bonuses)
    streak_mult = 2.0 if user_mode == "Consistency" else 1.0
    
    if streak >= 30:
        bonus_xp = STREAK_BONUS_30 * streak_mult
    elif streak >= 7:
        bonus_xp = STREAK_BONUS_7 * streak_mult
    elif streak >= 3:
        bonus_xp = STREAK_BONUS_3 * streak_mult

        
    total_xp = base_xp + bonus_xp
    
    # Random Bonus (10% chance)
    lucky_bonus = 0
    if random.random() < 0.1:
        lucky_bonus = 25
        
    return total_xp, lucky_bonus

def calculate_coin_reward(streak: int):
    base_coins = 5
    if streak >= 7:
        return base_coins + 10
    return base_coins

def xp_needed(level: int):
    """Calculates XP required to pass the given level."""
    return int(100 * (level ** 1.5))

def calculate_level_data(total_xp: int):
    """
    Returns (level, current_xp_in_level, xp_for_next_level)
    """
    level = 1
    remaining_xp = total_xp
    while remaining_xp >= xp_needed(level):
        remaining_xp -= xp_needed(level)
        level += 1
    return level, remaining_xp, xp_needed(level)

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.gamification import Badge, UserBadge

class HeroService:
    @staticmethod
    def check_milestones(db: Session, user: User, current_streak: int, total_logs: int):
        """
        Evaluates and grants badges based on user milestones.
        Deep interface for the premium gamification ecosystem.
        """
        # Streak Milestones
        if current_streak >= 30:
            HeroService._grant_badge(db, user, "The Immortal")
        elif current_streak >= 7:
            HeroService._grant_badge(db, user, "Consistency Rookie")
        elif current_streak >= 3:
            HeroService._grant_badge(db, user, "Early Starter")

        # Total Habit Milestones
        if total_logs >= 100:
            HeroService._grant_badge(db, user, "Century Hero")
        elif total_logs >= 10:
            HeroService._grant_badge(db, user, "Habit Ten")
        elif total_logs >= 1:
            HeroService._grant_badge(db, user, "First Step")

    @staticmethod
    def _grant_badge(db: Session, user: User, badge_name: str):
        badge = db.query(Badge).filter(Badge.name == badge_name).first()
        if not badge:
            return

        # Premium Check
        if badge.is_premium_exclusive and not user.is_premium:
            return

        # Check if already earned
        existing = db.query(UserBadge).filter(
            UserBadge.user_id == user.id,
            UserBadge.badge_id == badge.id
        ).first()

        if not existing:
            earned = UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(earned)
            db.commit()

    @staticmethod
    def get_leaderboard(db: Session, limit: int = 10):
        """
        Returns the top users by XP. 
        Premium users get a special flag in the response.
        """
        return db.query(User).order_by(User.xp.desc()).limit(limit).all()

