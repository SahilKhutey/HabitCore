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


# ── 9. MODEL_REGISTRY (ML Ops) ──────────────────────────────────────────────

class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name    = Column(String, index=True) # e.g. avoidance_model
    version = Column(Integer, default=1)
    feature_version = Column(String, default="v2.0_behavior_aware")
    
    path    = Column(String) # path to serialized model file
    
    # Metrics
    accuracy = Column(Float)
    recall   = Column(Float, default=0.0)
    precision = Column(Float, default=0.0)
    
    status = Column(String, default="staging") # staging, production, archived
    metadata_json = Column(JSON) # model parameters, training date range
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    model_id = Column(String, ForeignKey("model_registry.id"))
    
    input_features = Column(JSON) # Snapshot of features used
    prediction = Column(Float) # The probability output
    actual_outcome = Column(Boolean, nullable=True) # Filled later for retraining
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class InsightFeedback(Base):
    __tablename__ = "insight_feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    insight_id = Column(String, ForeignKey("insights.id"))
    user_id = Column(String, index=True)
    
    is_helpful = Column(Boolean)
    action_taken = Column(Boolean, default=False)
    feedback_text = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String)
    subcategory = Column(String)
    
    text = Column(String, nullable=False)
    intent = Column(String)
    
    depth_level = Column(Integer, default=1) # 1-3
    emotional_intensity = Column(Float, default=0.5)
    
    trigger_types = Column(JSON) # ["avoidance_high", "low_energy", etc.]
    
    # NEW: Semantic Intelligence Fields
    semantic_tags = Column(JSON) # ["avoidance", "fear", "discomfort"]
    cognitive_type = Column(String) # "awareness", "distortion", "behavioral_probe"
    emotional_weight = Column(Integer, default=1) # 1-5
    novelty_score = Column(Float, default=1.0)
    cooldown_days = Column(Integer, default=3)
    
    difficulty_weight = Column(Float, default=0.5)
    base_priority = Column(Float, default=0.5)
    
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class QuestionStats(Base):
    __tablename__ = "question_stats"

    question_id = Column(String, ForeignKey("questions.id"), primary_key=True)
    
    times_shown = Column(Integer, default=0)
    times_answered = Column(Integer, default=0)
    times_skipped = Column(Integer, default=0)
    
    avg_response_time = Column(Float, default=0.0)
    effectiveness_score = Column(Float, default=0.0) # Behavior improvement metric
    
    last_shown_at = Column(DateTime)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class UserQuestionHistory(Base):
    __tablename__ = "user_question_history"

    user_id = Column(String, index=True, primary_key=True)
    question_id = Column(String, ForeignKey("questions.id"), primary_key=True)
    
    last_shown_at = Column(DateTime)
    times_seen = Column(Integer, default=0)

class QuestionUsageLog(Base):
    __tablename__ = "question_usage_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    question_id = Column(String, ForeignKey("questions.id"))
    date = Column(Date)
    response = Column(String, nullable=True)
    response_time_seconds = Column(Integer, nullable=True)
    skipped = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class CognitiveSignal(Base):
    __tablename__ = "cognitive_signals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    date = Column(Date, index=True)
    
    # Extracted Insights
    emotion = Column(String) # low_energy, anxiety, etc.
    state = Column(String) # avoidance, rumination, flow
    distortions = Column(JSON) # ["overgeneralization", "catastrophizing"]
    behaviors = Column(JSON) # ["distraction", "deep_work"]
    
    raw_text = Column(String)
    usage_log_id = Column(String, ForeignKey("question_usage_logs.id"))
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class Nudge(Base):
    __tablename__ = "nudges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    type = Column(String) # interrupt, redirect, reflective, reinforcement
    trigger_pattern = Column(String)
    message = Column(String)
    priority = Column(Integer, default=1)
    
    delivered = Column(Boolean, default=False)
    acted = Column(Boolean, default=False)
    
    metadata = Column(JSON, nullable=True) # { "pattern_id": "...", "confidence": 0.9 }
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class NudgeFeedback(Base):
    __tablename__ = "nudge_feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nudge_id = Column(String, ForeignKey("nudges.id"))
    user_id = Column(String, index=True)
    
    action_taken = Column(Boolean, default=False)
    dismissed = Column(Boolean, default=False)
    response_time_ms = Column(Integer, nullable=True)
    
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
