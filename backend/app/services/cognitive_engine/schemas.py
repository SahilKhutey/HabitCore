"""
Schemas — Pydantic contracts for the CognitiveEngine.

Two entry points:
  MorningCheckinRequest  — 30 seconds, minimal friction
  EveningCheckinRequest  — ≤2 minutes, 5 structured steps

One output:
  CognitiveDayLogOut     — full day record for frontend
  CognitiveInsightOut    — single insight from InsightBuilder
  DailyCognitiveSummary  — lightweight summary for AI context injection
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date


# ── Morning Input (30 sec, minimal friction) ──────────────────────────────────

class MorningCheckinRequest(BaseModel):
    """
    Fast morning entry. Mood + energy + single intent sentence.
    UX rule: no more than 3 fields shown at once.
    """
    mood:            int   = Field(..., ge=1, le=10, description="Overall mood 1–10")
    energy:          str   = Field(..., description="low | medium | high")
    stress:          Optional[int] = Field(None, ge=1, le=10)
    dominant_emotion: Optional[str] = None  # "calm", "anxious", "motivated", etc.
    morning_intent:  Optional[str] = None   # "How do you want to show up today?"


# ── Evening Input (≤2 min, 5 steps) ─────────────────────────────────────────

class ThoughtEntry(BaseModel):
    """Step 2 — Thought + Reframe (core CBT loop)"""
    thought:                str
    thought_type:           Optional[str] = None   # "helpful" | "harmful" | "neutral"
    trigger:                Optional[str] = None
    reframe:                Optional[str] = None
    belief_strength_before: Optional[int] = Field(None, ge=0, le=100)
    belief_strength_after:  Optional[int] = Field(None, ge=0, le=100)


class BehaviorEntry(BaseModel):
    """Step 3 — Behavior audit"""
    habits_completed:    int   = 0
    habits_skipped:      int   = 0
    deep_work_minutes:   int   = 0
    distraction_minutes: int   = 0
    avoided_task:        Optional[str] = None


class DriverEntry(BaseModel):
    """Step 4 — Energy drivers + identity alignment"""
    energy_drainers:   Optional[List[str]] = None
    energy_givers:     Optional[List[str]] = None
    social_influence:  Optional[Dict[str, List[str]]] = None  # {"positive":[], "negative":[]}
    self_respect:      Optional[str] = None   # "yes" | "partial" | "no"
    acted_as_intended: Optional[bool] = None


class ProgressEntry(BaseModel):
    """Step 5 — Win, improvement, tomorrow focus, mental load"""
    win:               Optional[str] = None
    improvement:       Optional[str] = None
    moved_forward:     Optional[bool] = None
    anxiety_dump:      Optional[str] = None
    in_control:        Optional[List[str]] = None
    out_of_control:    Optional[List[str]] = None
    tomorrow_priority: Optional[str] = None


class EveningCheckinRequest(BaseModel):
    """
    Full evening check-in. All steps optional — system accepts partial logs.
    UX rule: each step is a separate screen, never shown all at once.
    """
    # Step 1 — Mood reflection
    evening_mood:  Optional[int]  = Field(None, ge=1, le=10)
    mood_shift:    Optional[str]  = None   # "better" | "same" | "worse"
    mood_cause:    Optional[str]  = None

    # Steps 2–5
    thought:    Optional[ThoughtEntry]  = None
    behavior:   Optional[BehaviorEntry] = None
    drivers:    Optional[DriverEntry]   = None
    progress:   Optional[ProgressEntry] = None


# ── API Responses ─────────────────────────────────────────────────────────────

class CognitiveInsightOut(BaseModel):
    type:       str    # "cognitive" | "driver" | "identity" | "behavior" | "burnout"
    category:   str    # "distortion" | "energy" | "consistency" | "alignment"
    message:    str    # v2 language: calm, specific, evidence-based
    confidence: float  # 0.0–1.0
    action_hint: Optional[str] = None


class CognitiveDayLogOut(BaseModel):
    id:           str
    log_date:     str
    morning_completed: bool
    evening_completed: bool

    mood:           Optional[int]
    energy:         Optional[str]
    stress:         Optional[int]
    dominant_emotion: Optional[str]
    morning_intent: Optional[str]

    evening_mood:    Optional[int]
    thought_type:    Optional[str]
    cognitive_distortion: Optional[str]
    habits_completed: Optional[int]
    self_respect:    Optional[str]
    moved_forward:   Optional[bool]
    tomorrow_priority: Optional[str]

    identity_alignment_score: Optional[float]
    cognitive_load_score:     Optional[float]

    model_config = ConfigDict(from_attributes=True)


class DailyCognitiveSummary(BaseModel):
    """Lightweight summary injected into AICoachService context."""
    avg_mood:             float
    avg_energy:           str
    avg_stress:           float
    negative_thought_ratio: float
    avoidance_rate:       float
    deep_work_ratio:      float
    self_respect_score:   float
    distortions_detected: List[str]
    top_drainers:         List[str]
    top_givers:           List[str]
    progress_ratio:       float
    burnout_risk:         float
    days_analyzed:        int
