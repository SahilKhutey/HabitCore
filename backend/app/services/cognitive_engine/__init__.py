"""
CognitiveEngine — v2 Intelligence Layer

The system's true moat:
  Behavior Data × Cognitive Mapping × Insight Accuracy

Pipeline:
  CognitiveDayLog (raw input)
    → FeatureBuilder     (feature engineering)
    → BurnoutDetector    (dual-signal burnout: behavioral + cognitive)
    → ThoughtProcessor   (CBT distortion detection, 12 types)
    → DriverMapper       (energy accounting)
    → InsightBuilder     (human-level output)
    → CognitiveEngineService (orchestration)
"""
from .service import CognitiveEngineService
from .thought_processor import ThoughtProcessor
from .feature_builder import FeatureBuilder
from .burnout_detector import BurnoutDetector, BurnoutAssessment
from .driver_mapper import DriverMapper
from .insight_builder import InsightBuilder

__all__ = [
    "CognitiveEngineService",
    "ThoughtProcessor",
    "FeatureBuilder",
    "BurnoutDetector",
    "BurnoutAssessment",
    "DriverMapper",
    "InsightBuilder",
]
