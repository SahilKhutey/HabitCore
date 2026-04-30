from sqlalchemy import Column, String, Integer, JSON, Boolean, ForeignKey
from app.db.declarative import Base
import uuid

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id = Column(String, primary_key=True)
    mode = Column(String, default="Consistency") # Speed, Consistency, Competitive, Minimal
    progress_style = Column(String, default="bar") # bar, ring, streak
    engagement_level = Column(String, default="Balanced") # Chill, Balanced, Intense
    reward_type = Column(String, default="visual") # visual, coins, competitive
    identity_goal = Column(String, default="Productive") # Fit, Learner, Productive, Calm
    layout = Column(JSON, default=["xp", "habits", "quests"])

class UserRule(Base):
    __tablename__ = "user_rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    condition = Column(String) # miss_2_days, complete_all_habits, 5_day_streak
    action = Column(String) # reset_streak, bonus_xp, unlock_reward
    is_active = Column(Boolean, default=True)
