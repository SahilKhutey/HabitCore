"""
Intelligence Primitives — Standardized Enums and Constants for the Behavioral Intelligence Pipeline.
"""
from enum import Enum

class EventType(str, Enum):
    DEEP_WORK       = "deep_work"
    DISTRACTION     = "distraction"
    HABIT_COMPLETED = "habit_completed"
    HABIT_SKIPPED   = "habit_skipped"
    THOUGHT_LOGGED  = "thought_logged"
    REFRAME_DONE    = "reframe_done"
    APP_OPEN        = "app_open"
    SESSION_END     = "session_end"

class EventCategory(str, Enum):
    BEHAVIOR  = "behavior"
    COGNITIVE = "cognitive"
    SYSTEM    = "system"

class UserState(str, Enum):
    STABLE      = "stable"
    STRUGGLING  = "struggling"
    OVERWHELMED = "overwhelmed"
    IMPROVING   = "improving"

class InsightType(str, Enum):
    PATTERN       = "pattern"
    CONTRADICTION = "contradiction"
    PROGRESS      = "progress"
    WARNING       = "warning"

class LoopType(str, Enum):
    AVOIDANCE_LOOP        = "avoidance_loop"
    NEGATIVE_THOUGHT_LOOP = "negative_thought_loop"
    ENERGY_DRAIN_LOOP     = "energy_drain_loop"
    SOCIAL_STRESS_LOOP    = "social_stress_loop"
