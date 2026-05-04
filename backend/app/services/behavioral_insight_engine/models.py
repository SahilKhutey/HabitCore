"""
BehavioralInsight — DB model for the Behavioral Insight Engine.

Stores generated insights in SQLite, compatible with HabitCore's
existing String-UUID pattern (no PostgreSQL dialect required).
"""
from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, Integer
from app.db.declarative import Base
from datetime import datetime, timezone
import uuid


class BehavioralInsight(Base):
    __tablename__ = "behavioral_insights"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)

    # Classification
    type = Column(String, nullable=False)      # "pattern" | "warning" | "growth" | "reflection"
    category = Column(String, nullable=False)  # "sleep" | "mood" | "consistency" | "energy" | "overload"

    # Content
    message = Column(Text, nullable=False)     # Human-readable, identity-framed, no hype
    action_hint = Column(Text, nullable=True)  # Specific suggested action (optional)

    # Scoring
    confidence = Column(Float, default=0.5)    # 0.0–1.0, from ML correlation or rule certainty
    impact_score = Column(Float, default=0.5)  # 0.0–1.0, behavioral importance weight
    rank_score = Column(Float, default=0.5)    # confidence * impact, used for ordering

    # Deduplication: don't surface the same insight twice within N days
    trigger_key = Column(String, nullable=True)  # e.g. "sleep_warning" | "growth_consistency"
    last_triggered_at = Column(DateTime, nullable=True)

    # Lifecycle
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
