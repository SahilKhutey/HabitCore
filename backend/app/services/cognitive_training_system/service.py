"""
CognitiveTrainingService — Master CBTS Orchestrator.

Full pipeline per evening session:
  CognitiveDayLog (saved by CognitiveEngineService)
    → ScoringEngine.compute_daily()    [mental scores]
    → LoopDetector.detect()            [harmful loop detection, 7 days]
    → InterventionEngine.prescribe()   [CBT/ACT micro-interventions]
    → SkillTracker.update()            [14 skill growth updates]
    → ProgressionEngine.update_level() [level-up check]
    → ThoughtBehaviorLinker            [thought → behavior correlations]
    → ProtocolEngine.get_daily_protocol() [tomorrow's protocol]

Real-time feedback loop:
  Morning check-in → quick_burnout + protocol → shown on home screen
  Evening entry    → full pipeline → TrainingSessionOut → shown immediately

Database writes per session:
  CognitiveSkillState — updated 14 skills + level
  CognitiveDayLog — computed fields already written by CognitiveEngineService
"""
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.cognitive_day_log import CognitiveDayLog
from app.models.cognitive_skill_state import CognitiveSkillState
from app.services.cognitive_training_system.schemas import TrainingSessionOut, MentalScores
from app.services.cognitive_training_system.scoring_engine import ScoringEngine
from app.services.cognitive_training_system.loop_detector import LoopDetector
from app.services.cognitive_training_system.intervention_engine import InterventionEngine
from app.services.cognitive_training_system.skill_tracker import SkillTracker, ProgressionEngine
from app.services.cognitive_training_system.protocol_engine import ProtocolEngine


class CognitiveTrainingService:
    """DB-session-scoped CBTS orchestrator."""

    def __init__(self, db: Session):
        self.db = db

    # ── Main Pipeline ─────────────────────────────────────────────────────────

    def run_training_session(self, user_id: str) -> TrainingSessionOut:
        """
        Full CBTS pipeline. Called after evening check-in is saved.
        Returns TrainingSessionOut shown immediately to user.
        """
        today_log = self._get_today_log(user_id)
        recent_logs = self._get_recent_logs(user_id, days=7)

        # ── Step 1: Mental Scores ──────────────────────────────────────────
        if today_log:
            scores = ScoringEngine.compute_daily(today_log)
        else:
            scores = MentalScores(clarity=0.0, control=0.0, integrity=0.0, focus=0.0)

        # ── Step 2: Loop Detection ─────────────────────────────────────────
        loops = LoopDetector.detect(recent_logs, window_days=7)

        # ── Step 3: Interventions ──────────────────────────────────────────
        interventions = InterventionEngine.prescribe(loops)

        # ── Step 4: Skill Growth ───────────────────────────────────────────
        skill_state = ProgressionEngine.get_or_create(user_id, self.db)
        skill_deltas: Dict[str, float] = {}
        level_up_event = None

        if today_log:
            skill_deltas = SkillTracker.update(skill_state, today_log)
            level_up_event = ProgressionEngine.update_level(skill_state)
            self.db.commit()

        # ── Step 5: Thought-Behavior Links ────────────────────────────────
        links = self._link_thought_behavior(recent_logs)

        # ── Step 6: Tomorrow's Protocol ───────────────────────────────────
        tomorrow_protocol = ProtocolEngine.get_daily_protocol(
            skill_state.cognitive_level or 1
        )

        return TrainingSessionOut(
            scores=scores,
            loops_detected=loops,
            interventions=interventions,
            skill_deltas=skill_deltas,
            level_up=level_up_event,
            thought_behavior_links=links,
            tomorrow_protocol=tomorrow_protocol,
        )

    def get_morning_context(self, user_id: str) -> Dict[str, Any]:
        """
        Returns context needed for the home screen on morning open.
        Fast — no heavy analysis. Just protocol + quick state.
        """
        skill_state = ProgressionEngine.get_or_create(user_id, self.db)
        self.db.commit()

        protocol    = ProtocolEngine.get_daily_protocol(skill_state.cognitive_level or 1)
        morning_fields = ProtocolEngine.get_morning_fields(skill_state.cognitive_level or 1)

        # Quick burnout check from last 3 days
        recent = self._get_recent_logs(user_id, days=3)
        energy_trend = "medium"
        if recent:
            low_count = sum(1 for l in recent if l.energy == "low")
            if low_count >= 2:
                energy_trend = "low"
            elif all(l.energy == "high" for l in recent if l.energy):
                energy_trend = "high"

        return {
            "cognitive_level":    skill_state.cognitive_level or 1,
            "level_label":        protocol.level_label,
            "tonight_steps":      protocol.steps,
            "morning_fields":     morning_fields,
            "energy_trend":       energy_trend,
            "overall_skill_score": round(skill_state.overall_score or 0.0, 3),
        }

    def get_skill_state(self, user_id: str) -> Optional[CognitiveSkillState]:
        """Get the user's current cognitive skill state."""
        return ProgressionEngine.get_or_create(user_id, self.db)

    def get_weekly_scores(self, user_id: str) -> Dict[str, Any]:
        """Weekly mental score aggregation."""
        logs = self._get_recent_logs(user_id, days=7)
        return ScoringEngine.compute_weekly(logs)

    # ── Thought-Behavior Linker ───────────────────────────────────────────────

    def _link_thought_behavior(self, logs: List[CognitiveDayLog]) -> List[str]:
        """
        Surface specific thought → behavior correlations from log history.
        Returns plain-language observations: "Fatigue thoughts → avoidance."
        """
        links = []
        KEYWORDS = {
            "tired":     ("low energy", "avoidance"),
            "can't":     ("pessimism", "habit skipping"),
            "stressed":  ("stress",    "distraction"),
            "worthless": ("labeling",  "reduced completion"),
            "fail":      ("failure thought", "avoidance"),
            "behind":    ("comparison", "paralysis"),
        }

        for log in logs:
            if not log.thought:
                continue
            for keyword, (thought_label, behavior_label) in KEYWORDS.items():
                if keyword in log.thought.lower():
                    skipped = (log.habits_skipped or 0) > 0
                    distracted = (log.distraction_minutes or 0) > (log.deep_work_minutes or 0)
                    if skipped or distracted:
                        link = f"{thought_label.title()} thoughts correlate with {behavior_label} in your logs."
                        if link not in links:
                            links.append(link)

        return links[:5]  # max 5 links shown

    # ── DB Helpers ────────────────────────────────────────────────────────────

    def _get_today_log(self, user_id: str) -> Optional[CognitiveDayLog]:
        return self.db.query(CognitiveDayLog).filter(
            CognitiveDayLog.user_id == str(user_id),
            CognitiveDayLog.log_date == date.today(),
        ).first()

    def _get_recent_logs(self, user_id: str, days: int = 7) -> List[CognitiveDayLog]:
        cutoff = date.today() - timedelta(days=days)
        return self.db.query(CognitiveDayLog).filter(
            CognitiveDayLog.user_id == str(user_id),
            CognitiveDayLog.log_date >= cutoff,
        ).order_by(CognitiveDayLog.log_date).all()
