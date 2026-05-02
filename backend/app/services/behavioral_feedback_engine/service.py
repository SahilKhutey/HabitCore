"""
BehavioralFeedbackService — Master Orchestrator for the BFE.

Pipeline:
1. Fetch recent logs (7-14 days).
2. Extract features from CognitiveEngine or direct logs.
3. Run PatternEngine to detect temporal/causal patterns.
4. Run AdaptiveEngine to determine UserSystemState and Directives.
5. Run ScoringEngine to compute the internal BehaviorScore.
6. Run InsightEngine to generate top 2 meaningful insights.
7. Apply RetentionSystem logic (flexible streaks, identity hooks).
8. Persist state in UserBehaviorState.
"""
from typing import List, Dict, Any, Optional
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session

from app.models.cognitive_day_log import CognitiveDayLog
from app.models.user_behavior_state import UserBehaviorState
from app.services.behavioral_feedback_engine.schemas import (
    BFESessionOut, DailyInput, UserSystemState, BFEInsight,
    DetectedPattern, SystemDirectives, BehaviorScore
)
from app.services.behavioral_feedback_engine.pattern_engine import PatternEngine
from app.services.behavioral_feedback_engine.adaptive_engine import AdaptiveEngine
from app.services.behavioral_feedback_engine.scoring_engine import BFEScoringEngine, RetentionSystem
from app.services.behavioral_feedback_engine.insight_engine import InsightEngine
from app.services.cognitive_engine.feature_builder import FeatureBuilder

class BehavioralFeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def process_daily_input(self, user_id: str, input_data: DailyInput) -> BFESessionOut:
        """
        Main entry point for daily behavioral processing.
        Called after a user submits their daily check-in.
        """
        # 1. Fetch history for pattern detection
        recent_logs = self._get_recent_logs(user_id, days=14)
        
        # 2. Extract features (merging current input with history)
        # We use the FeatureBuilder from CognitiveEngine for consistency
        features = FeatureBuilder.build(recent_logs)
        
        # 3. Determine User State & Directives
        current_state = AdaptiveEngine.determine_state(features)
        directives = AdaptiveEngine.produce_directives(current_state)
        
        # 4. Detect Patterns
        patterns = PatternEngine.detect_all(recent_logs, window_days=14)
        
        # 5. Compute Internal Score
        # Note: We pass the last log (the one just submitted)
        today_log = recent_logs[-1] if recent_logs else None
        score = BFEScoringEngine.compute(today_log, current_state, features)
        
        # 6. Generate Insights
        insights = InsightEngine.generate(patterns, features, current_state)
        top_insight = InsightEngine.select_top_insight(insights)
        
        # 7. Retention & Meta
        score_history = [
            BFEScoringEngine.compute(l, current_state, features).score 
            for l in recent_logs
        ]
        
        weekly_meta = BFEScoringEngine.compute_weekly_meta(
            score_history, recent_logs, current_state, 
            top_insight.message if top_insight else None
        )
        weekly_meta.pattern_count = len(patterns)
        
        streak_data = RetentionSystem.compute_flexible_streak(recent_logs)
        retention_signal = RetentionSystem.get_identity_signal(
            streak_data["consistency_ratio"], weekly_meta.trend
        )
        
        # 8. Persist State
        self._persist_state(user_id, current_state, score.score, directives, weekly_meta)
        
        return BFESessionOut(
            state=current_state,
            directives=directives,
            score=score,
            patterns=patterns,
            insights=insights[:2], # UX rule: max 2
            top_insight=top_insight,
            retention_signal=retention_signal,
            weekly_meta=weekly_meta
        )

    def get_user_state(self, user_id: str) -> Optional[UserBehaviorState]:
        return self.db.query(UserBehaviorState).filter(
            UserBehaviorState.user_id == str(user_id)
        ).first()

    def _persist_state(self, user_id: str, state: UserSystemState, score: float, directives: SystemDirectives, meta: Any):
        db_state = self.get_user_state(user_id)
        if not db_state:
            db_state = UserBehaviorState(user_id=str(user_id))
            self.db.add(db_state)
        
        db_state.current_state = state.value
        db_state.last_score = score
        db_state.directives = directives.dict()
        db_state.weekly_meta = meta.dict()
        
        self.db.commit()

    def _get_recent_logs(self, user_id: str, days: int = 14) -> List[CognitiveDayLog]:
        cutoff = date.today() - timedelta(days=days)
        return self.db.query(CognitiveDayLog).filter(
            CognitiveDayLog.user_id == str(user_id),
            CognitiveDayLog.log_date >= cutoff
        ).order_by(CognitiveDayLog.log_date).all()
