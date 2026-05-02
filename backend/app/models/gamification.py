from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.sql import func
from app.db.declarative import Base
import uuid

class Badge(Base):
    __tablename__ = "badges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True)
    description = Column(String)
    icon_name = Column(String)
    is_premium_exclusive = Column(Boolean, default=False)

class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    badge_id = Column(String, ForeignKey("badges.id"), index=True)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

class DailyChallenge(Base):
    __tablename__ = "daily_challenges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    condition_type = Column(String) # e.g. "complete_habits"
    condition_value = Column(Integer)
    reward_xp = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    referrer_id = Column(String, ForeignKey("users.id"), index=True)
    referred_id = Column(String, ForeignKey("users.id"), index=True)
    reward_given = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
