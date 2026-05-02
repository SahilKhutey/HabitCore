"""
CognitiveDayLog — The core data moat of HabitCore v2

This is the richest behavioral record in the system.
One record per user per day, capturing the full human loop:
  State → Thought → Behavior → Driver → Progress → Insight → Adaptation

SQLite-compatible: String UUIDs, no PostgreSQL dialect.
All JSON fields stored as SQLAlchemy JSON (serialized dicts/lists).
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, Date, ForeignKey
from app.db.declarative import Base
from datetime import datetime, date
import uuid


class CognitiveDayLog(Base):
    __tablename__ = "cognitive_day_logs"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    log_date   = Column(Date, default=date.today, index=True)

    # ── MORNING CHECK-IN (30 sec, fast input) ──────────────────────────────

    # State
    mood            = Column(Integer, nullable=True)   # 1–10
    energy          = Column(String,  nullable=True)   # "low" | "medium" | "high"
    stress          = Column(Integer, nullable=True)   # 1–10
    dominant_emotion = Column(String, nullable=True)   # free text: "anxious", "calm", "excited"

    # Morning intent
    morning_intent  = Column(Text, nullable=True)      # "How do you want to show up today?"

    # ── EVENING CHECK-IN (≤2 min) ──────────────────────────────────────────

    # Step 1 — Mood reflection (evening)
    evening_mood    = Column(Integer, nullable=True)   # 1–10
    mood_shift      = Column(String,  nullable=True)   # "better" | "same" | "worse"
    mood_cause      = Column(Text,    nullable=True)   # free text

    # Step 2 — Thought + Reframe (core CBT loop)
    thought               = Column(Text,    nullable=True)  # raw thought logged
    thought_type          = Column(String,  nullable=True)  # "helpful" | "harmful" | "neutral"
    cognitive_distortion  = Column(String,  nullable=True)  # detected distortion type
    trigger               = Column(Text,    nullable=True)  # what triggered the thought
    reframe               = Column(Text,    nullable=True)  # user's reframe attempt
    belief_strength_before = Column(Integer, nullable=True) # 0–100
    belief_strength_after  = Column(Integer, nullable=True) # 0–100

    # Step 3 — Behavior audit
    habits_completed      = Column(Integer, nullable=True, default=0)
    habits_skipped        = Column(Integer, nullable=True, default=0)
    deep_work_minutes     = Column(Integer, nullable=True, default=0)
    distraction_minutes   = Column(Integer, nullable=True, default=0)
    avoided_task          = Column(Text,    nullable=True)  # what they avoided

    # Step 4 — Drivers (energy accounting)
    energy_drainers       = Column(JSON, nullable=True)   # ["meetings", "social media"]
    energy_givers         = Column(JSON, nullable=True)   # ["walk", "deep work"]
    social_influence      = Column(JSON, nullable=True)   # {"positive": [], "negative": []}

    # Step 4 — Identity alignment
    self_respect          = Column(String, nullable=True)  # "yes" | "partial" | "no"
    acted_as_intended     = Column(Boolean, nullable=True)

    # Step 5 — Progress
    win                   = Column(Text, nullable=True)    # one thing that went well
    improvement           = Column(Text, nullable=True)    # one thing to improve
    moved_forward         = Column(Boolean, nullable=True, default=False)

    # Step 5 — Mental load reduction
    anxiety_dump          = Column(Text, nullable=True)    # brain dump of worries

    # Step 5 — Locus of control filter
    in_control            = Column(JSON, nullable=True)    # list of controllables
    out_of_control        = Column(JSON, nullable=True)    # list of uncontrollables

    # Step 5 — Tomorrow
    tomorrow_priority     = Column(Text, nullable=True)    # single focus for tomorrow

    # ── Computed fields (populated by CognitiveEngine post-processing) ─────

    distortion_confidence = Column(Float, nullable=True)   # 0.0–1.0
    identity_alignment_score = Column(Float, nullable=True) # 0.0–1.0
    cognitive_load_score  = Column(Float, nullable=True)   # 0.0–1.0

    # Entry metadata
    morning_completed     = Column(Boolean, default=False)
    evening_completed     = Column(Boolean, default=False)
    created_at            = Column(DateTime, default=datetime.utcnow)
    updated_at            = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
