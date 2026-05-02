"""
CognitiveEngineService — Main Orchestrator.

Coordinates the full cognitive analysis pipeline:

  CognitiveDayLog (DB)
    → FeatureBuilder.build()
    → BurnoutDetector.assess()
    → DriverMapper.map_drivers()
    → InsightBuilder.generate()
    → StateEngine update signal
    → AICoachService context enrichment

Also handles:
  - Morning check-in save
  - Evening check-in save (per-step)
  - Post-entry immediate feedback
  - Computed field backfill (distortion, alignment_score, cognitive_load)
"""
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.cognitive_day_log import CognitiveDayLog
from app.services.cognitive_engine.schemas import (
    MorningCheckinRequest, EveningCheckinRequest, DailyCognitiveSummary
)
from app.services.cognitive_engine.thought_processor import ThoughtProcessor
from app.services.cognitive_engine.feature_builder import FeatureBuilder
from app.services.cognitive_engine.burnout_detector import BurnoutDetector, BurnoutAssessment
from app.services.cognitive_engine.driver_mapper import DriverMapper
from app.services.cognitive_engine.insight_builder import InsightBuilder


class CognitiveEngineService:
    """
    DB-session-scoped orchestrator for all cognitive engine operations.
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Morning Check-in ──────────────────────────────────────────────────────

    def submit_morning(
        self, user_id: str, req: MorningCheckinRequest
    ) -> Dict[str, Any]:
        """
        Submit or update today's morning check-in.
        Returns immediate feedback based on state.
        """
        today = date.today()
        log = self._get_or_create_today(user_id, today)

        log.mood             = req.mood
        log.energy           = req.energy
        log.stress           = req.stress
        log.dominant_emotion = req.dominant_emotion
        log.morning_intent   = req.morning_intent
        log.morning_completed = True

        self.db.commit()

        # Immediate feedback
        feedback = self._morning_feedback(log)
        return {
            "status":   "saved",
            "log_date": str(today),
            "feedback": feedback,
        }

    def _morning_feedback(self, log: CognitiveDayLog) -> Dict[str, Any]:
        """
        Instant feedback after morning check-in.
        Uses BurnoutDetector.quick_check() for real-time state.
        """
        # Minimal feature check from today's data only
        energy = log.energy or "medium"
        stress = log.stress or 3

        # Quick burnout signal from morning data
        recent_logs = self._get_recent_logs(str(log.user_id), days=3)
        if recent_logs:
            features = FeatureBuilder.build(recent_logs)
            quick_burnout = BurnoutDetector.quick_check(
                features["avg_energy"],
                features["stress_trend"],
                features["self_respect_score"],
            )
        else:
            quick_burnout = energy == "low" and stress >= 7

        message = None
        flag    = None

        if quick_burnout:
            flag    = "burnout_risk"
            message = (
                "Early depletion signals detected. "
                "Focus on 1–2 core behaviors today. Rest is a behavioral strategy."
            )
        elif energy == "low":
            flag    = "low_energy"
            message = "Low energy noted. Protect your one essential habit and allow flexibility on the rest."
        elif log.mood and log.mood >= 8:
            flag    = "high_readiness"
            message = "Strong readiness state. A good time to tackle your most demanding habit."

        return {"flag": flag, "message": message, "energy": energy}

    # ── Evening Check-in ──────────────────────────────────────────────────────

    def submit_evening(
        self, user_id: str, req: EveningCheckinRequest
    ) -> Dict[str, Any]:
        """
        Submit evening check-in (all steps, all optional).
        Processes thought entry through ThoughtProcessor automatically.
        Triggers full cognitive analysis after save.
        """
        today = date.today()
        log   = self._get_or_create_today(user_id, today)

        # Step 1 — Mood reflection
        if req.evening_mood is not None:
            log.evening_mood = req.evening_mood
            if log.mood:
                log.mood_shift = (
                    "better" if req.evening_mood > log.mood + 1
                    else "worse" if req.evening_mood < log.mood - 1
                    else "same"
                )
        if req.mood_cause:  log.mood_cause = req.mood_cause

        # Step 2 — Thought + Reframe (auto-classify)
        if req.thought:
            t = req.thought
            log.thought   = t.thought
            log.trigger   = t.trigger
            log.reframe   = t.reframe
            log.belief_strength_before = t.belief_strength_before
            log.belief_strength_after  = t.belief_strength_after

            # Auto-classify via ThoughtProcessor
            distortion = ThoughtProcessor.detect_distortion(t.thought)
            log.thought_type         = t.thought_type or ThoughtProcessor.classify_thought_type(t.thought)
            log.cognitive_distortion = distortion["type"] if distortion else None
            log.distortion_confidence = distortion["confidence"] if distortion else None

        # Step 3 — Behavior
        if req.behavior:
            b = req.behavior
            log.habits_completed    = b.habits_completed
            log.habits_skipped      = b.habits_skipped
            log.deep_work_minutes   = b.deep_work_minutes
            log.distraction_minutes = b.distraction_minutes
            log.avoided_task        = b.avoided_task

        # Step 4 — Drivers + Identity
        if req.drivers:
            d = req.drivers
            log.energy_drainers    = d.energy_drainers
            log.energy_givers      = d.energy_givers
            log.social_influence   = d.social_influence
            log.self_respect       = d.self_respect
            log.acted_as_intended  = d.acted_as_intended

            # Compute identity alignment score
            respect_map = {"yes": 1.0, "partial": 0.5, "no": 0.0}
            sr_score = respect_map.get(d.self_respect or "partial", 0.5)
            act_score = 1.0 if d.acted_as_intended else (0.5 if d.acted_as_intended is None else 0.0)
            log.identity_alignment_score = round((sr_score + act_score) / 2, 3)

        # Step 5 — Progress
        if req.progress:
            p = req.progress
            log.win               = p.win
            log.improvement       = p.improvement
            log.moved_forward     = p.moved_forward
            log.anxiety_dump      = p.anxiety_dump
            log.in_control        = p.in_control
            log.out_of_control    = p.out_of_control
            log.tomorrow_priority = p.tomorrow_priority

        # Compute cognitive load score
        log.cognitive_load_score = self._compute_load_score(log)
        log.evening_completed    = True

        self.db.commit()

        # Run full cognitive analysis
        insights   = self._run_analysis(user_id, days=7)
        burnout    = insights["burnout"]

        return {
            "status":     "saved",
            "log_date":   str(today),
            "insights":   insights["insights"][:3],   # top 3 for immediate display
            "burnout":    burnout.to_dict() if burnout else None,
            "tomorrow":   log.tomorrow_priority,
        }

    # ── Core Analysis Pipeline ────────────────────────────────────────────────

    def _run_analysis(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Full pipeline run: features → burnout → drivers → insights."""
        logs = self._get_recent_logs(user_id, days=days)
        if not logs:
            return {"insights": [], "burnout": None, "features": {}}

        features = FeatureBuilder.build(logs)
        driver_map = DriverMapper.map_drivers(logs)

        # Behavioral burnout from existing engine (if available)
        behavioral_burnout = 0.0
        try:
            from app.services.core.psychological_engine import PsychologicalEngine
            psych = PsychologicalEngine(self.db)
            behavioral_burnout = psych.calculate_burnout_score(user_id)
        except Exception:
            pass

        burnout = BurnoutDetector.assess(features, behavioral_burnout)
        insights = InsightBuilder.generate(features, driver_map, burnout)

        return {
            "insights":    insights,
            "burnout":     burnout,
            "features":    features,
            "driver_map":  driver_map,
        }

    def get_cognitive_summary(self, user_id: str, days: int = 7) -> DailyCognitiveSummary:
        """
        Build DailyCognitiveSummary for AI Coach context injection.
        This is the cognitive enrichment fed into AICoachService.
        """
        logs = self._get_recent_logs(user_id, days=days)
        features = FeatureBuilder.build(logs)
        driver_map = DriverMapper.map_drivers(logs)
        behavioral_burnout = 0.0

        try:
            from app.services.core.psychological_engine import PsychologicalEngine
            behavioral_burnout = PsychologicalEngine(self.db).calculate_burnout_score(user_id)
        except Exception:
            pass

        burnout = BurnoutDetector.assess(features, behavioral_burnout)

        return DailyCognitiveSummary(
            avg_mood=features["avg_mood"],
            avg_energy=features["avg_energy"],
            avg_stress=features["avg_stress"],
            negative_thought_ratio=features["negative_thought_ratio"],
            avoidance_rate=features["avoidance_rate"],
            deep_work_ratio=features["deep_work_ratio"],
            self_respect_score=features["self_respect_score"],
            distortions_detected=features["distortions_detected"],
            top_drainers=features["top_drainers"],
            top_givers=features["top_givers"],
            progress_ratio=features["progress_ratio"],
            burnout_risk=burnout.confidence if burnout.detected else burnout.behavioral_score,
            days_analyzed=len(logs),
        )

    def get_insights(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Public API — return generated insights for the feed."""
        result = self._run_analysis(user_id, days=days)
        return result["insights"]

    def get_today_log(self, user_id: str) -> Optional[CognitiveDayLog]:
        """Fetch today's log for prefilling morning/evening forms."""
        return self.db.query(CognitiveDayLog).filter(
            CognitiveDayLog.user_id == user_id,
            CognitiveDayLog.log_date == date.today(),
        ).first()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_or_create_today(self, user_id: str, today: date) -> CognitiveDayLog:
        log = self.db.query(CognitiveDayLog).filter(
            CognitiveDayLog.user_id == user_id,
            CognitiveDayLog.log_date == today,
        ).first()
        if not log:
            log = CognitiveDayLog(user_id=user_id, log_date=today)
            self.db.add(log)
            self.db.flush()
        return log

    def _get_recent_logs(self, user_id: str, days: int = 7) -> List[CognitiveDayLog]:
        cutoff = date.today() - timedelta(days=days)
        return self.db.query(CognitiveDayLog).filter(
            CognitiveDayLog.user_id == user_id,
            CognitiveDayLog.log_date >= cutoff,
        ).order_by(CognitiveDayLog.log_date).all()

    def _compute_load_score(self, log: CognitiveDayLog) -> float:
        """
        Cognitive load score 0.0–1.0 from today's entry signals.
        Higher = more cognitive burden.
        """
        score = 0.0
        if log.stress:            score += (log.stress / 10) * 0.3
        if log.anxiety_dump:      score += 0.2
        if log.thought_type == "harmful": score += 0.2
        if log.mood and log.mood <= 4:   score += 0.2
        if log.energy == "low":          score += 0.1
        return round(min(score, 1.0), 3)
