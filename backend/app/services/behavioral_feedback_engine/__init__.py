"""
Behavioral Feedback Engine (BFE) — Runtime Layer.

Enforces:
  Self-awareness > dopamine
  Adaptation > static scoring
  Insight > engagement tricks

Identity: Behavioral Feedback System for Human Cognition.
"""
from .service import BehavioralFeedbackService
from .pattern_engine import PatternEngine
from .adaptive_engine import AdaptiveEngine
from .scoring_engine import BFEScoringEngine, RetentionSystem
from .insight_engine import InsightEngine

__all__ = [
    "BehavioralFeedbackService",
    "PatternEngine",
    "AdaptiveEngine",
    "BFEScoringEngine",
    "RetentionSystem",
    "InsightEngine",
]
