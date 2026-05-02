"""
Behavioral Intelligence Models — The core data architecture for HabitCore V2.
Enforces the pipeline: Raw → Signals → Patterns → Insights → Adaptation.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, JSON, ForeignKey, CheckConstraint, Index, Double
from sqlalchemy.orm import relationship
from app.db.declarative import Base
import datetime
import uuid

# ── 1. DAILY_LOGS (UX Entry Point) ──────────────────────────────────────────

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    date    = Column(Date, index=True, nullable=False)

    mood    = Column(Integer, CheckConstraint("mood BETWEEN 1 AND 10"))
    energy  = Column(Integer, CheckConstraint("energy BETWEEN 1 AND 10"))
    stress  = Column(Integer)
    dominant_emotion = Column(String)

    key_thought    = Column(String)
    thought_label  = Column(String)
    distortion_type = Column(String)

    reframe = Column(String)

    wins     = Column(JSON) # Array of strings
    failures = Column(JSON) # Array of strings

    avoidance_flag = Column(Boolean, default=False)

    self_integrity_score = Column(Float, CheckConstraint("self_integrity_score BETWEEN 0 AND 1"))

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        Index("idx_daily_logs_user_date", "user_id", "date", unique=True),
    )


# ── 2. EVENTS (Core Engine — Time-series Optimized) ─────────────────────────

class Event(Base):
    __tablename__ = "events"

    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id        = Column(String, index=True, nullable=False)

    event_type     = Column(String, nullable=False) # Enum from core.intelligence_primitives
    event_category = Column(String) # behavior / cognitive / system

    event_value    = Column(Double)
    metadata_json  = Column(JSON) # Renamed from 'metadata' to avoid SQL keywords

    source         = Column(String)

    created_at     = Column(DateTime, nullable=False, index=True, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        Index("idx_events_user_time", "user_id", "created_at"),
    )


# ── 3. DERIVED_SIGNALS (Versioned) ──────────────────────────────────────────

class DerivedSignal(Base):
    __tablename__ = "derived_signals"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String, index=True, nullable=False)
    date       = Column(Date, index=True, nullable=False)

    version    = Column(Integer, default=1)

    execution_score      = Column(Float)
    avoidance_score      = Column(Float)
    focus_score          = Column(Float)
    cognitive_score      = Column(Float)
    emotional_stability  = Column(Float)
    integrity_score      = Column(Float)

    distraction_minutes  = Column(Integer)
    deep_work_minutes    = Column(Integer)

    computed_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        Index("idx_signals_user_date", "user_id", "date"),
    )


# ── 4. PATTERNS (Core Moat — Versioned) ─────────────────────────────────────

class Pattern(Base):
    __tablename__ = "patterns"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String, index=True, nullable=False)

    pattern_type = Column(String) # e.g. energy_avoidance_link
    version      = Column(Integer, default=1)

    description  = Column(String)

    confidence   = Column(Float)
    impact_score = Column(Float)

    frequency    = Column(Integer)
    last_seen    = Column(DateTime)

    trigger_conditions = Column(JSON)

    active       = Column(Boolean, default=True)

    detected_at  = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_updated = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        Index("idx_patterns_user_active", "user_id", "active"),
    )


# ── 5. INSIGHTS (Priority System) ───────────────────────────────────────────

class Insight(Base):
    __tablename__ = "insights"

    id      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)

    type    = Column(String) # pattern, contradiction, progress, warning
    title   = Column(String)
    message = Column(String)

    related_pattern_id = Column(String, ForeignKey("patterns.id"), nullable=True)

    priority    = Column(Float) # 0.0 - 1.0
    confidence  = Column(Float)

    seen        = Column(Boolean, default=False)

    expires_at  = Column(DateTime)
    created_at  = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        Index("idx_insights_user_priority", "user_id", "priority"),
    )


# ── 6. SCORES (Trend-first Design) ──────────────────────────────────────────

class Score(Base):
    __tablename__ = "scores"

    id      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    date    = Column(Date, index=True, nullable=False)

    behavior_score = Column(Float)

    execution_score   = Column(Float)
    avoidance_penalty = Column(Float)
    cognitive_score   = Column(Float)
    emotional_score   = Column(Float)
    integrity_score   = Column(Float)
    focus_score       = Column(Float)

    rolling_7d_avg  = Column(Float)
    rolling_30d_avg = Column(Float)

    weekly_trend    = Column(String) # improving, stable, declining

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


# ── 7. IDENTITY_TRACKING (Enriched) ─────────────────────────────────────────

class IdentityTracking(Base):
    __tablename__ = "identity_tracking"

    id      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    date    = Column(Date, index=True, nullable=False)

    desired_identity = Column(String)

    acted_in_alignment = Column(Boolean)
    alignment_score    = Column(Float)

    notes = Column(String)


# ── 8. LOOP_DETECTIONS (Real-time Intervention) ──────────────────────────────

class LoopDetection(Base):
    __tablename__ = "loop_detections"

    id      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)

    loop_type   = Column(String) # avoidance_loop, negative_thought_loop
    description = Column(String)

    severity    = Column(Float)
    frequency   = Column(Integer)

    active      = Column(Boolean, default=True)

    detected_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_seen   = Column(DateTime)
