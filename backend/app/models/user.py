from sqlalchemy import Column, String, Integer, Boolean, DateTime
from app.db.base import Base
import uuid
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    is_premium = Column(Boolean, default=False)
    followers = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    streak_freeze = Column(Integer, default=1)
    referral_code = Column(String, unique=True)
    last_active_hour = Column(Integer, default=9)
    paywall_variant = Column(String, default="A")
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    social_id = Column(String, index=True, nullable=True)
    provider = Column(String, default="email") # email, google, apple
    
    # Customization & Mode
    mode = Column(String, default="Consistency") # Speed, Consistency, Competitive, Minimal
    progress_style = Column(String, default="bar") # bar, ring, streak
    engagement_level = Column(String, default="Balanced") # Chill, Balanced, Intense
    reward_type = Column(String, default="visual") # visual, coins, competitive
    identity_goal = Column(String, default="Productive") # Fit, Learner, Productive, Calm
    identity_level = Column(String, default="beginner") # beginner, builder, disciplined, elite
    archetype = Column(String, nullable=True) # warrior, monk, achiever, explorer
    daily_habit_goal = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

