"""
BehavioralInsightEngine — HabitCore v2.0

Converts raw behavioral logs into actionable psychological intelligence.
Pipeline: BehaviorMemory → FeatureExtractor → PatternRules + MLModel → InsightGenerator → InsightStore
"""
from .service import BehavioralInsightService

__all__ = ["BehavioralInsightService"]
