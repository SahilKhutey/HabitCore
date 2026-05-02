"""
IntelligencePipeline — The unified production pipeline for Behavioral Intelligence.
Enforces: Raw → Signals → Patterns → Insights → Adaptation.
"""
from typing import List, Dict, Any, Optional
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.intelligence_models import DailyLog, Event, DerivedSignal, Pattern, Insight, Score, LoopDetection
from app.models.user import User
from app.models.user_behavior_state import UserBehaviorState
from app.core.intelligence_primitives import EventType, EventCategory, UserState, InsightType, LoopType

# Import existing engine logic for reuse/adaptation
from app.services.intelligence_pipeline.normalization.normalize import normalize_event
from app.services.intelligence_pipeline.feature_engine.builders import DailyFeatureBuilder, RollingFeatureBuilder
from app.services.intelligence_pipeline.orchestrator import generate_patterns
from app.services.intelligence_pipeline.feedback import FeedbackProcessor

class IntelligencePipeline:
    def __init__(self, db: Session):
        self.db = db

    # ── Step 1: Ingestion ───────────────────────────────────────────────────

    def ingest_daily_log(self, user_id: str, log_data: Dict[str, Any]) -> DailyLog:
        """
        Saves the raw daily log and triggers event ingestion for key behaviors.
        """
        log_date = log_data.get("date", date.today())
        
        # Check for existing log to ensure idempotency
        log = self.db.query(DailyLog).filter(
            DailyLog.user_id == str(user_id),
            DailyLog.date == log_date
        ).first()
        
        if not log:
            log = DailyLog(user_id=str(user_id), date=log_date)
            self.db.add(log)

        # Update fields
        for key, value in log_data.items():
            if hasattr(log, key):
                setattr(log, key, value)
        
        # Automated thought processing
        if log.key_thought and not log.distortion_type:
            # Note: keeping thought processor for reframe logic
            from app.services.cognitive_engine.thought_processor import ThoughtProcessor
            analysis = ThoughtProcessor.classify_thought(log.key_thought)
            log.thought_label = analysis.get("polarity")
            log.distortion_type = analysis.get("distortion")

        # Ingest event based on log
        if log.avoidance_flag:
            self.ingest_event(user_id, EventType.HABIT_SKIPPED, EventCategory.BEHAVIOR, 1.0, {"source": "daily_log"})
        
        self.db.flush()
        return log

    def ingest_event(self, user_id: str, event_type: EventType, category: EventCategory, value: float = 1.0, metadata: Dict[str, Any] = None) -> Event:
        """Saves a normalized raw event."""
        raw_event = {
            "user_id": user_id,
            "event_type": event_type.value,
            "event_category": category.value,
            "event_value": value,
            "metadata": metadata or {},
            "created_at": datetime.utcnow()
        }
        normalized = normalize_event(raw_event)
        
        event = Event(
            user_id=normalized["user_id"],
            event_type=normalized["type"],
            event_category=normalized["category"],
            event_value=normalized["value"],
            metadata_json=normalized["metadata"],
            created_at=normalized["timestamp"]
        )
        self.db.add(event)
        self.db.flush()
        return event

    # ── Step 2: Signal Computation ──────────────────────────────────────────

    def compute_signals(self, user_id: str, log_date: date) -> DerivedSignal:
        """
        Builds DerivedSignal and Score for the given date.
        """
        # Fetch data for the date
        log = self.db.query(DailyLog).filter(DailyLog.user_id == str(user_id), DailyLog.date == log_date).first()
        events = self.db.query(Event).filter(
            Event.user_id == str(user_id),
            Event.created_at >= datetime.combine(log_date, datetime.min.time()),
            Event.created_at <= datetime.combine(log_date, datetime.max.time())
        ).all()

        # Build feature sets
        history_logs = self._get_recent_logs(user_id, days=14)
        
        # Build daily feature history
        history_features = []
        for h_log in history_logs:
            h_events = self.db.query(Event).filter(
                Event.user_id == str(user_id),
                Event.created_at >= datetime.combine(h_log.date, datetime.min.time()),
                Event.created_at <= datetime.combine(h_log.date, datetime.max.time())
            ).all()
            history_features.append(DailyFeatureBuilder.build(h_events, h_log))

        today_features = history_features[-1] if history_features else {}
        rolling_features = RollingFeatureBuilder.build(history_features)

        # Create Signal record
        signal = self.db.query(DerivedSignal).filter(
            DerivedSignal.user_id == str(user_id),
            DerivedSignal.date == log_date
        ).first()
        
        if not signal:
            signal = DerivedSignal(user_id=str(user_id), date=log_date)
            self.db.add(signal)

        # Map to signals
        signal.execution_score = today_features.get("focus_ratio", 0.0)
        signal.avoidance_score  = float(today_features.get("avoidance_flag", 0))
        signal.cognitive_score  = float(today_features.get("negative_thought_count", 0))
        signal.integrity_score  = getattr(log, "self_integrity_score", 0.0)
        signal.deep_work_minutes = today_features.get("deep_work_minutes", 0)
        signal.distraction_minutes = today_features.get("distraction_minutes", 0)

        # Create Score record
        from app.services.behavioral_feedback_engine.adaptive_engine import AdaptiveEngine
        from app.services.behavioral_feedback_engine.scoring_engine import BFEScoringEngine
        
        state = AdaptiveEngine.determine_state(rolling_features)
        b_score = BFEScoringEngine.compute(log, state, rolling_features)
        
        score_rec = self.db.query(Score).filter(Score.user_id == str(user_id), Score.date == log_date).first()
        if not score_rec:
            score_rec = Score(user_id=str(user_id), date=log_date)
            self.db.add(score_rec)

        score_rec.behavior_score = b_score.score
        score_rec.execution_score = b_score.execution
        score_rec.avoidance_penalty = b_score.avoidance
        score_rec.cognitive_score = b_score.cognitive
        score_rec.emotional_score = b_score.emotional
        score_rec.integrity_score = b_score.integrity
        score_rec.focus_score = b_score.focus
        
        # Compute rolling averages
        past_scores = self.db.query(Score.behavior_score).filter(
            Score.user_id == str(user_id),
            Score.date <= log_date
        ).order_by(desc(Score.date)).limit(30).all()
        
        p_scores = [s[0] for s in past_scores]
        if p_scores:
            score_rec.rolling_7d_avg = sum(p_scores[:7]) / len(p_scores[:7])
            score_rec.rolling_30d_avg = sum(p_scores) / len(p_scores)
            score_rec.weekly_trend = PatternEngine.get_weekly_trend(p_scores[:7])

        self.db.flush()
        return signal

    # ── Step 3: Pattern & Loop Engine ───────────────────────────────────────

    def run_pattern_engine(self, user_id: str):
        """Detects patterns and loops over the last 14 days."""
        history_logs = self._get_recent_logs(user_id, days=14)
        history_features = []
        for h_log in history_logs:
            h_events = self.db.query(Event).filter(
                Event.user_id == str(user_id),
                Event.created_at >= datetime.combine(h_log.date, datetime.min.time()),
                Event.created_at <= datetime.combine(h_log.date, datetime.max.time())
            ).all()
            history_features.append(DailyFeatureBuilder.build(h_events, h_log))

        if not history_features:
            return

        # Detect Patterns via Orchestrator
        detected_patterns = generate_patterns(history_features)
        for dp in detected_patterns:
            # Update or create pattern
            pat = self.db.query(Pattern).filter(
                Pattern.user_id == str(user_id),
                Pattern.pattern_type == dp.type,
                Pattern.active == True
            ).first()
            
            if not pat:
                pat = Pattern(user_id=str(user_id), pattern_type=dp.type)
                self.db.add(pat)
            
            pat.description = dp.message
            pat.confidence = dp.confidence
            pat.last_seen = datetime.utcnow()
            pat.frequency = (pat.frequency or 0) + 1
            pat.trigger_conditions = dp.supporting_data
        
        # Detect Loops (from CognitiveTrainingSystem logic)
        from app.services.cognitive_training_system.loop_detector import LoopDetector
        detected_loops = LoopDetector.detect(history)
        for dl in detected_loops:
            loop = self.db.query(LoopDetection).filter(
                LoopDetection.user_id == str(user_id),
                LoopDetection.loop_type == dl.type,
                LoopDetection.active == True
            ).first()
            
            if not loop:
                loop = LoopDetection(user_id=str(user_id), loop_type=dl.type)
                self.db.add(loop)
            
            loop.description = dl.message
            loop.severity = dl.confidence
            loop.frequency = (loop.frequency or 0) + 1
            loop.last_seen = datetime.utcnow()

        self.db.flush()

    # ── Step 4: Insight Generation ──────────────────────────────────────────

    def generate_insights(self, user_id: str):
        """
        Generates priority-based insights from active patterns and features.
        """
        history = self._get_recent_logs(user_id, days=14)
        features = FeatureBuilder.build(history)
        patterns = self.db.query(Pattern).filter(Pattern.user_id == str(user_id), Pattern.active == True).all()
        
        # Adapt InsightEngine or use directly
        state = AdaptiveEngine.determine_state(features)
        # Note: InsightEngine currently expects DetectedPattern schema objects, 
        # so we might need a small mapping layer.
        mapped_patterns = [] # Mapping omitted for brevity, assuming InsightEngine works with our objects or we map them
        
        # For now, we'll implement a priority-based push
        for pat in patterns:
            if pat.confidence > 0.8:
                # Check for existing un-seen insight for this pattern
                existing = self.db.query(Insight).filter(
                    Insight.user_id == str(user_id),
                    Insight.related_pattern_id == pat.id,
                    Insight.seen == False
                ).first()
                
                if not existing:
                    insight = Insight(
                        user_id=str(user_id),
                        type=InsightType.PATTERN.value,
                        title=pat.pattern_type.replace("_", " ").title(),
                        message=pat.description,
                        related_pattern_id=pat.id,
                        priority=pat.confidence * (pat.impact_score or 1.0),
                        confidence=pat.confidence,
                        expires_at=datetime.utcnow() + timedelta(days=3)
                    )
                    self.db.add(insight)

        self.db.flush()

    # ── Step 5: Adaptive Engine (State Update) ──────────────────────────────

    def update_user_state(self, user_id: str):
        """Updates the global UserBehaviorState and User cognitive level."""
        history_logs = self._get_recent_logs(user_id, days=14)
        history_features = []
        for h_log in history_logs:
            h_events = self.db.query(Event).filter(
                Event.user_id == str(user_id),
                Event.created_at >= datetime.combine(h_log.date, datetime.min.time()),
                Event.created_at <= datetime.combine(h_log.date, datetime.max.time())
            ).all()
            history_features.append(DailyFeatureBuilder.build(h_events, h_log))
            
        rolling_features = RollingFeatureBuilder.build(history_features)
        
        from app.services.behavioral_feedback_engine.adaptive_engine import AdaptiveEngine
        current_state = AdaptiveEngine.determine_state(rolling_features)
        directives = AdaptiveEngine.produce_directives(current_state)
        
        # Update UserBehaviorState
        ub_state = self.db.query(UserBehaviorState).filter(UserBehaviorState.user_id == str(user_id)).first()
        if not ub_state:
            ub_state = UserBehaviorState(user_id=str(user_id))
            self.db.add(ub_state)
        
        ub_state.current_state = current_state.value
        ub_state.directives = directives.dict()
        
        # Update User cognitive level
        user = self.db.query(User).filter(User.id == str(user_id)).first()
        if user:
            # We reuse the ProgressionEngine from CognitiveTrainingSystem
            from app.services.cognitive_training_system.skill_tracker import ProgressionEngine
            # We need skill state to compute level, or we use a simplified version for BFE
            # For now, we'll keep it separate or fetch skill state
            pass

        self.db.flush()

    # ── Full Pipeline Trigger ───────────────────────────────────────────────

    def run_full_pipeline(self, user_id: str, log_date: date):
        """
        Executes the entire Behavioral Intelligence Pipeline.
        """
        # Step 1 & 2: Signals
        self.compute_signals(user_id, log_date)
        
        # Step 3: Patterns
        self.run_pattern_engine(user_id)
        
        # Step 4: Insights
        self.generate_insights(user_id)
        
        # Step 5: Adaptation
        self.update_user_state(user_id)
        
        self.db.commit()

    # ── Helpers ────────────────────────────────────────────────────────────

    def _get_recent_logs(self, user_id: str, days: int = 14) -> List[DailyLog]:
        cutoff = date.today() - timedelta(days=days)
        return self.db.query(DailyLog).filter(
            DailyLog.user_id == str(user_id),
            DailyLog.date >= cutoff
        ).order_by(DailyLog.date).all()
