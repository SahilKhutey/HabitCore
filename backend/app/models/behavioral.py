from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, ForeignKey
from app.db.base import Base
from datetime import datetime
import uuid

class BehaviorPattern(Base):
    __tablename__ = "behavior_patterns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    pattern_type = Column(String)  # 'time_preference', 'day_pattern', 'mood_correlation'
    insight_key = Column(String)    # 'best_time', 'worst_day', 'mood_habit_correlation'
    insight_value = Column(String)
    confidence_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, name="metadata")  # Use metadata_json to avoid conflict with Base.metadata

class UserBehaviorLog(Base):
    __tablename__ = "user_behavior_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)  # 'habit_completed', 'checkin', 'mood_change'
    event_data = Column(JSON)
    context = Column(JSON)  # time_of_day, day_of_week, etc.

class RecoveryPlan(Base):
    __tablename__ = "recovery_plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    trigger_type = Column(String)  # 'burnout', 'failure_streak', 'low_mood'
    plan_type = Column(String)     # 'habit_reduction', 'micro_habits', 'rest_day'
    actions = Column(JSON)         # Specific recovery actions
    active = Column(Integer, default=1)  # 0 or 1
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
