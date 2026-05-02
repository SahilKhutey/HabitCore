"""
HabitOrchestrator v2 — Central Pipeline Coordinator

Data flow (exact):
  User Action
    → HabitEngine.complete()           [Core Layer]
    → BehaviorMemoryService.log()      [Core Layer]
    → PsychologicalEngine.burnout()    [Core Layer]
    → StateEngine.compute()            [Core Layer]
    → RewardEngine.calculate_xp()      [Experience Layer] (state-modulated)
    → AICoachService.get_guidance()    [Intelligence Layer] (state-calibrated)
    → BehavioralInsightEngine.run()    [Intelligence Layer] (BackgroundTask)
    → Response assembled

Architecture rules enforced here:
  1. StateEngine output controls Experience Layer (no direct reward overrides)
  2. Intelligence Layer receives StateEngine output as mandatory context
  3. Experience Layer cannot trigger mode changes (read-only access to state)
  4. All messages follow v2 language standard
"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.core.habit_engine import HabitEngine
from app.services.core.state_engine import StateEngine
from app.services.core.psychological_engine import PsychologicalEngine
from app.services.experience.reward_engine import RewardEngine, reward_engine
from app.services.intelligence.ai_coach_service import ai_coach_service
from app.services.behavioral_insight_engine.service import BehavioralInsightService
from app.services.behavior_memory_service import BehaviorMemoryService
from app.services.live_ops.config_engine import config_engine
from app.models.user import User
from app.core.security import security_engine
from app.utils.logging import structured_logger


class HabitOrchestratorV2:
    """
    v2 Master Pipeline — coordinates all layers for habit completion.
    Synchronous core processing; background tasks for intelligence generation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.habit_engine      = HabitEngine(db)
        self.psych_engine      = PsychologicalEngine(db)
        self.behavior_memory   = BehaviorMemoryService(db)
        self.logger            = structured_logger

    async def process_habit_completion(
        self,
        user_id: str,
        habit_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        v2 Master Pipeline for habit completion.
        Returns structured response consumed by the frontend.
        """
        try:
            # ── 1. Security Validation ─────────────────────────────────────
            if not security_engine.validate_event(user_id, "habit_completed", habit_data):
                return {"success": False, "error": "Rate limit exceeded or invalid event."}

            # ── 2. Core: Complete habit (idempotent) ───────────────────────
            habit_id = habit_data.get("habit_id")
            log, completion_ctx = self.habit_engine.complete(user_id, habit_id)

            if completion_ctx.get("already_done"):
                return {"success": True, "message": "Already completed today.", "duplicate": True}

            # ── 3. Core: Behavior Memory Log ───────────────────────────────
            self.behavior_memory.log_behavior(
                user_id,
                "habit_completed",
                {**habit_data, "streak": completion_ctx["streak"]},
                context={
                    "hour":        datetime.utcnow().hour,
                    "day_of_week": datetime.utcnow().strftime("%A"),
                }
            )

            # ── 4. Core: Compute User State ────────────────────────────────
            burnout_score = self.psych_engine.calculate_burnout_score(user_id)
            completion_rate = self.habit_engine.get_completion_rate(habit_id)
            streak = completion_ctx["streak"]

            user_state = StateEngine.compute(
                burnout_score=burnout_score,
                completion_rate=completion_rate,
                streak=streak,
            )

            # ── 5. Experience Layer: Calculate Rewards (state-modulated) ───
            xp_data = RewardEngine.calculate_xp(
                difficulty=habit_data.get("difficulty", "medium"),
                streak=streak,
                consistency_rate=completion_rate,
                user_state=user_state,
            )

            # Check streak milestone for coins
            milestone = RewardEngine.check_streak_milestone(streak)
            coins_earned = milestone["coins"] if milestone else xp_data["xp_earned"] // 10

            # Identity-framed completion message
            user = self.db.query(User).filter(User.id == user_id).first()
            archetype = getattr(user, "identity_goal", None) or "pioneer"
            completion_message = RewardEngine.get_completion_message(
                archetype, streak, habit_data.get("difficulty", "medium")
            )

            # ── 6. Update User XP/Coins/Level ─────────────────────────────
            if user:
                user.xp    = (user.xp or 0) + xp_data["xp_earned"]
                user.coins = (user.coins or 0) + coins_earned

                level_data = RewardEngine.calculate_level_up(user.xp, user.level or 1)
                if level_data["leveled_up"]:
                    user.level  = level_data["level"]
                    user.coins += level_data["coins_awarded"]

                self.db.commit()
            else:
                level_data = {"leveled_up": False, "level": 1}

            # ── 7. Intelligence Layer: AI Guidance (cached) ────────────────
            ai_guidance = {"message": None, "source": "disabled"}
            if config_engine.feature("ai_coach"):
                try:
                    ai_guidance = ai_coach_service.get_guidance(
                        user_id=str(user_id),
                        user_state=user_state,
                        habit_completion_context=completion_ctx,
                    )
                except Exception as e:
                    self.logger.warning("AI guidance failed", error=str(e))

            # ── 8. Recovery Plan Check ─────────────────────────────────────
            recovery_plan = None
            if burnout_score >= config_engine.get("burnout_threshold", 0.60):
                plan = self.psych_engine.create_recovery_plan(user_id, trigger="habit_completion")
                if plan:
                    recovery_plan = {
                        "active":   True,
                        "message":  plan.actions.get("message"),
                        "actions":  plan.actions.get("suggestions", []),
                        "max_habits": plan.actions.get("max_habits", 3),
                    }

            # ── 9. Assemble Response ───────────────────────────────────────
            self.logger.info(
                "Habit completion processed",
                user_id=str(user_id),
                xp=xp_data["xp_earned"],
                streak=streak,
                mode=user_state.mode.value,
            )

            return {
                "success":    True,
                "duplicate":  False,

                # v2 completion message (identity-framed)
                "message":    completion_message,
                "milestone":  milestone,

                # Rewards (deterministic, state-modulated)
                "rewards": {
                    "xp_earned":    xp_data["xp_earned"],
                    "coins_earned": coins_earned,
                    "streak":       streak,
                    "xp_label":     RewardEngine.get_xp_display_label(archetype),
                },

                # Level progression
                "level": {
                    "current":      level_data.get("level", user.level if user else 1),
                    "leveled_up":   level_data["leveled_up"],
                    "level_message": level_data.get("level_message"),
                },

                # User state (consumed by frontend for UX mode)
                "user_state":  user_state.to_dict(),

                # Intelligence layer
                "ai_guidance":    ai_guidance,
                "recovery_plan":  recovery_plan,

                "timestamp": datetime.utcnow().isoformat(),
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            self.logger.error("Orchestration failed", error=str(e), user_id=str(user_id))
            return {"success": False, "error": "Processing failed. Please retry."}


def get_habit_orchestrator(db: Session) -> HabitOrchestratorV2:
    """Factory function — drop-in replacement for v1 orchestrator."""
    return HabitOrchestratorV2(db)
