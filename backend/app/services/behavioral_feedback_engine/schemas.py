"""
Behavioral Feedback Engine — Pydantic contracts.

DailyInput: the strict fast-input contract.
≤ 60 seconds. Mostly taps. No typing overload.

System response shapes for frontend consumption.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ── System States ─────────────────────────────────────────────────────────────

class UserSystemState(str, Enum):
    STABLE      = "stable"
    STRUGGLING  = "struggling"
    OVERWHELMED = "overwhelmed"
    IMPROVING   = "improving"


# ── Input Contract ────────────────────────────────────────────────────────────

class DailyInput(BaseModel):
    """
    The fast daily behavioral input.
    Every field is designed for ≤ 60-second completion.
    Mostly tap-based — no long text required.

    UX contract:
      mood, energy, self_integrity → slider/tap
      emotion                      → emotion selector (predefined list)
      thought                      → short text (optional, 1 sentence)
      action_taken, avoided_task   → yes/no toggle
      distraction_minutes          → number slider or tap
      win                          → short text (optional, 1 sentence)
    """
    # State (taps)
    mood:                int   = Field(..., ge=1, le=10)
    energy:              int   = Field(..., ge=1, le=10)
    emotion:             str   = Field(..., description="Primary emotion label")

    # Behavior (toggles)
    action_taken:        bool  = Field(..., description="Did you execute your primary intention today?")
    avoided_task:        bool  = Field(False, description="Did you avoid something you intended to do?")

    # Focus (number or slider)
    distraction_minutes: int   = Field(0, ge=0)

    # Thought (1 sentence, optional)
    thought:             Optional[str] = None

    # Win (1 sentence, optional)
    win:                 Optional[str] = None

    # Identity (0 or 1 tap)
    self_integrity:      int   = Field(..., ge=0, le=1,
                                       description="0=acted against values, 1=acted aligned")

    timestamp:           Optional[datetime] = None


# ── Detected Pattern ──────────────────────────────────────────────────────────

class DetectedPattern(BaseModel):
    type:       str     # "energy_avoidance_link" | "relapse" | "thought_behavior" | etc.
    label:      str
    message:    str     # specific, evidence-based
    confidence: float
    window_days: int
    supporting_data: Optional[Dict[str, Any]] = None


# ── Insight ───────────────────────────────────────────────────────────────────

class BFEInsight(BaseModel):
    type:       str    # "pattern" | "contradiction" | "progress" | "warning"
    message:    str    # 1–2 sentences, v2 language
    confidence: float
    action:     Optional[str] = None   # micro-intervention (1 sentence)
    curiosity_hook: Optional[str] = None  # ethical retention: "2 more days to confirm"


# ── System Response (Adaptive Engine output) ──────────────────────────────────

class SystemDirectives(BaseModel):
    """
    What the app does differently based on user state.
    Frontend reads these flags to adjust its behavior.
    """
    state:                UserSystemState

    # Input layer controls
    reduce_inputs:         bool = False   # overwhelmed: simplify check-in
    max_input_fields:      int  = 8       # how many fields to show tonight

    # Pressure controls
    disable_streak_pressure: bool = False
    disable_notifications:   bool = False
    disable_challenges:      bool = False

    # Guidance level
    increase_guidance:     bool = False   # struggling: more AI coaching
    show_intervention:     bool = True    # show CBT/ACT technique

    # Challenge level
    increase_challenge:    bool = False   # improving: suggest harder behaviors

    # Focus directive
    focus_mode:            str  = "reflection"   # "reflection" | "action" | "recovery" | "growth"

    # Protocol override
    micro_tasks_only:      bool = False   # struggling: 2-minute tasks only


# ── Behavior Score (internal) ─────────────────────────────────────────────────

class BehaviorScore(BaseModel):
    """
    Internal composite score. NOT displayed as XP or points.
    Used for trend analysis and state determination only.
    """
    score:        float   # 0.0–1.0 composite
    execution:    float
    avoidance:    float   # penalty (inverted)
    cognitive:    float
    emotional:    float
    integrity:    float
    focus:        float
    state_label:  UserSystemState


# ── Weekly Meta ───────────────────────────────────────────────────────────────

class WeeklyMeta(BaseModel):
    trend:              str    # "improving" | "declining" | "stable"
    avg_score:          float
    peak_day:           Optional[str]
    lowest_day:         Optional[str]
    dominant_state:     UserSystemState
    pattern_count:      int
    top_insight:        Optional[str]
    identity_consistency: float   # % of days self_integrity=1


# ── Full BFE Session Response ─────────────────────────────────────────────────

class BFESessionOut(BaseModel):
    """Complete BFE response per session. Max 2 insights shown to user."""
    state:            UserSystemState
    directives:       SystemDirectives
    score:            BehaviorScore
    patterns:         List[DetectedPattern]
    insights:         List[BFEInsight]       # max 2 shown in UX
    top_insight:      Optional[BFEInsight]   # the single highest-confidence insight
    retention_signal: Optional[str]          # ethical retention hook
    weekly_meta:      Optional[WeeklyMeta]
