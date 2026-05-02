"""
Cognitive Training System (CBTS) — Production Layer

Input → Interpretation → Interruption → Reinforcement

Pipeline:
  CognitiveDayLog
    → ScoringEngine         (Clarity / Control / Integrity / Focus)
    → LoopDetector          (7 harmful loop types)
    → InterventionEngine    (CBT/ACT micro-interventions)
    → SkillTracker          (14 cognitive skill growth updates)
    → ProgressionEngine     (Level 1 Awareness → 5 Self-Mastery)
    → ProtocolEngine        (Adaptive UX: what user sees tomorrow)
"""
from .service import CognitiveTrainingService
from .scoring_engine import ScoringEngine
from .loop_detector import LoopDetector
from .intervention_engine import InterventionEngine
from .skill_tracker import SkillTracker, ProgressionEngine
from .protocol_engine import ProtocolEngine

__all__ = [
    "CognitiveTrainingService",
    "ScoringEngine",
    "LoopDetector",
    "InterventionEngine",
    "SkillTracker",
    "ProgressionEngine",
    "ProtocolEngine",
]
