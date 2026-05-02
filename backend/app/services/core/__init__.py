"""
HabitCore v2 — Core Layer
services/core/__init__.py

The Core Layer is the behavioral truth engine of the system.
All other layers derive state from this layer — never the reverse.

Services:
  HabitEngine           — CRUD, scheduling, completion, streak management
  BehaviorMemoryService — already in services/, re-exported here for layer clarity
  PsychologicalService  — mood/energy/sleep, domain scoring
  StateEngine           — global user mode (Normal/Burnout/Recovery/HighPerformance)
"""
from .habit_engine import HabitEngine
from .state_engine import StateEngine, UserMode, UserState
from .psychological_engine import PsychologicalEngine

__all__ = [
    "HabitEngine",
    "StateEngine",
    "UserMode",
    "UserState",
    "PsychologicalEngine",
]
