from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from app.db.declarative import Base
import uuid
import datetime

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
    provider = Column(String, default="email")
    
    mode = Column(String, default="Consistency")
    progress_style = Column(String, default="bar")
    engagement_level = Column(String, default="Balanced")
    reward_type = Column(String, default="visual")
    identity_goal = Column(String, default="Productive")
    identity_level = Column(String, default="beginner")
    archetype = Column(String, nullable=True)
    daily_habit_goal = Column(Integer, default=3)
    
    timezone         = Column(String, default='UTC')
    onboarding_state = Column(JSON)
    identity_profile = Column(JSON)
    cognitive_level  = Column(Integer, default=1)

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
