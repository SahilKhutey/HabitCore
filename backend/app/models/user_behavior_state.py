"""
UserBehaviorState — Persists the output of the Adaptive Engine.
This determines how the app interface behaves for a specific user.
"""
from sqlalchemy import Column, String, Float, DateTime, JSON
from app.db.declarative import Base
from datetime import datetime
import uuid

class UserBehaviorState(Base):
    __tablename__ = "user_behavior_state"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, unique=True, index=True, nullable=False)
    
    current_state = Column(String, default="stable") # stable, struggling, overwhelmed, improving
    last_score = Column(Float, default=0.0)
    
    # Store the full directives as JSON for the frontend
    directives = Column(JSON, nullable=True)
    
    # Store weekly meta for the dashboard
    weekly_meta = Column(JSON, nullable=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
