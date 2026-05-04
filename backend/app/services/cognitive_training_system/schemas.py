"""
Pydantic schemas for the Cognitive Training System.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


# ── Skill State ───────────────────────────────────────────────────────────────

class CognitiveSkillOut(BaseModel):
    awareness:               float
    emotional_labeling:      float
    distortion_detection:    float
    reframing:               float
    control_focus:           float
    action_despite_emotion:  float
    avoidance_awareness:     float
    self_integrity:          float
    identity_alignment:      float
    progress_recognition:    float
    discomfort_tolerance:    float
    attention_control:       float
    validation_independence: float
    self_talk_quality:       float
    cognitive_level:         int
    overall_score:           float

    model_config = ConfigDict(from_attributes=True)


# ── Mental Scores (per day) ───────────────────────────────────────────────────

class MentalScores(BaseModel):
    """
    Daily computed mental metrics. NOT shown as XP.
    Shown as: "Your Clarity score today", "Control score this week".
    """
    clarity:   float   # 0.0–1.0 — quality of thought awareness
    control:   float   # 0.0–1.0 — locus-of-control filter usage
    integrity: float   # 0.0–1.0 — self-respect + acted-as-intended
    focus:     float   # 0.0–1.0 — deep work / (deep + distracted)


# ── Protocol ─────────────────────────────────────────────────────────────────

class DailyProtocol(BaseModel):
    """
    What the user sees in tonight's check-in.
    Determined by cognitive level. More fields unlock at higher levels.
    """
    level:       int
    level_label: str    # "Awareness", "Understanding", "Control", etc.
    steps:       List[str]   # ordered step keys to show
    max_steps:   int
    description: str    # short explanation of today's protocol


# ── Loop Detection ────────────────────────────────────────────────────────────

class DetectedLoop(BaseModel):
    type:        str     # "negative_thought_loop" | "avoidance_loop" | etc.
    label:       str     # human-readable label
    message:     str     # specific, evidence-based observation
    confidence:  float   # 0.0–1.0
    evidence:    List[str]  # what data triggered this
    days_active: int     # how many consecutive days this loop has been present


# ── Intervention ──────────────────────────────────────────────────────────────

class Intervention(BaseModel):
    loop_type:    str
    technique:    str    # name of the CBT/ACT technique used
    action:       str    # internal action key
    prompt:       str    # what the user sees
    duration_sec: Optional[int] = None   # e.g., 120 for "2 minutes"
    has_timer:    bool = False
    follow_up:    Optional[str] = None   # follow-up question after action


# ── Progression ───────────────────────────────────────────────────────────────

class LevelUpEvent(BaseModel):
    """Returned when user crosses a level threshold."""
    previous_level: int
    new_level:      int
    level_label:    str
    message:        str
    unlocked_steps: List[str]   # new check-in steps now available


# ── Full Training Response ────────────────────────────────────────────────────

class TrainingSessionOut(BaseModel):
    """Complete response after an evening CTS submission."""
    scores:           MentalScores
    loops_detected:   List[DetectedLoop]
    interventions:    List[Intervention]
    skill_deltas:     Dict[str, float]    # skill → change (+0.03 etc)
    level_up:         Optional[LevelUpEvent]
    thought_behavior_links: List[str]     # "Fatigue thoughts → avoidance"
    tomorrow_protocol: DailyProtocol
