"""
HabitEngine — v2 Core Layer

Pure habit business logic: CRUD, scheduling, streak management,
completion validation, and load balancing.

Architecture rule: HabitEngine is a pure behavioral service.
It has NO knowledge of rewards, gamification, or XP.
Those concerns live in services/experience/reward_engine.py.
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.habit import Habit
from app.models.habit_log import HabitLog


# ── Streak edge cases ─────────────────────────────────────────────────────────
#
# Streak rules:
#   - A streak continues if the habit was completed on consecutive calendar days
#   - Missing ONE day resets streak to 0
#   - "Today" grace: if habit not yet completed today, streak is NOT broken
#     (evaluated on completion, not at midnight)
#   - Recovery mode exception: in BURNOUT/RECOVERY, streak freeze can be applied
#     (controlled by StateEngine via allow_streak_freeze flag)


class HabitEngine:
    """
    Stateful service — requires a DB session.
    All streak computations are edge-safe.
    """

    def __init__(self, db: Session):
        self.db = db

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def create(self, user_id: str, name: str, time: str = None, difficulty: str = "medium") -> Habit:
        habit = Habit(user_id=user_id, name=name, time=time, difficulty=difficulty)
        self.db.add(habit)
        self.db.commit()
        self.db.refresh(habit)
        return habit

    def get_active(self, user_id: str) -> List[Habit]:
        return (
            self.db.query(Habit)
            .filter(Habit.user_id == user_id, Habit.is_active == True)
            .order_by(Habit.created_at)
            .all()
        )

    def archive(self, user_id: str, habit_id: str) -> bool:
        """Soft-delete: sets is_active=False. Preserves logs."""
        habit = self._get_owned(user_id, habit_id)
        if not habit:
            return False
        habit.is_active = False
        self.db.commit()
        return True

    # ── Completion ────────────────────────────────────────────────────────────

    def complete(self, user_id: str, habit_id: str) -> Tuple[HabitLog, Dict[str, Any]]:
        """
        Record a habit completion. Returns (log_entry, completion_context).
        completion_context includes streak data for StateEngine + RewardEngine.
        """
        habit = self._get_owned(user_id, habit_id)
        if not habit:
            raise ValueError(f"Habit {habit_id} not found for user {user_id}")

        # Idempotency: don't double-log same habit same day
        today = date.today()
        existing = self.db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == today,
        ).first()
        if existing:
            streak = self._compute_streak(habit_id)
            return existing, self._build_context(habit, streak, already_done=True)

        log = HabitLog(
            habit_id=habit_id,
            user_id=user_id,
            completed=True,
            completed_at=datetime.now(timezone.utc),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        streak = self._compute_streak(habit_id)
        return log, self._build_context(habit, streak)

    # ── Streak Computation (edge-safe) ────────────────────────────────────────

    def _compute_streak(self, habit_id: str) -> int:
        """
        Compute current streak for a habit.
        Edge cases handled:
          - Gaps of > 1 day reset the streak
          - Today counts if completed; if not completed yet, streak is still live
          - Deduplication: only one log per day counts
        """
        logs = (
            self.db.query(HabitLog.date)
            .filter(HabitLog.habit_id == habit_id, HabitLog.completed == True)
            .order_by(HabitLog.date.desc())
            .all()
        )

        if not logs:
            return 0

        # Deduplicate dates
        dates = sorted(set(log.date for log in logs), reverse=True)
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Streak must include today or yesterday to be "alive"
        if dates[0] not in (today, yesterday):
            return 0

        streak = 1
        for i in range(1, len(dates)):
            expected = dates[i - 1] - timedelta(days=1)
            if dates[i] == expected:
                streak += 1
            else:
                break

        return streak

    def get_streak(self, habit_id: str) -> int:
        return self._compute_streak(habit_id)

    def get_completion_rate(self, habit_id: str, days: int = 14) -> float:
        """Completion rate over last N days (0.0–1.0)."""
        cutoff = date.today() - timedelta(days=days)
        completed = self.db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date >= cutoff,
            HabitLog.completed == True,
        ).count()
        return round(completed / days, 4)

    def get_today_status(self, user_id: str) -> Dict[str, bool]:
        """Returns {habit_id: completed_today} map for all active habits."""
        today = date.today()
        active = self.get_active(user_id)

        completed_today = set(
            log.habit_id
            for log in self.db.query(HabitLog.habit_id).filter(
                HabitLog.user_id == user_id,
                HabitLog.date == today,
                HabitLog.completed == True,
            ).all()
        )
        return {h.id: (h.id in completed_today) for h in active}

    # ── Load Balancing ────────────────────────────────────────────────────────

    def get_load_assessment(self, user_id: str) -> Dict[str, Any]:
        """
        Assess current habit load vs. state capacity.
        Returns recommendation for the Adaptive Layer.
        """
        active_count  = len(self.get_active(user_id))
        completion_rates = [
            self.get_completion_rate(h.id)
            for h in self.get_active(user_id)
        ]
        avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0.0

        if avg_completion < 0.4 and active_count > 3:
            assessment = "overloaded"
            recommendation = f"Consider archiving {active_count - 2} lower-priority habits."
        elif avg_completion > 0.9 and active_count < 5:
            assessment = "underloaded"
            recommendation = "Capacity exists for one additional habit aligned to your archetype."
        else:
            assessment = "balanced"
            recommendation = "Current load is appropriate."

        return {
            "active_count":    active_count,
            "avg_completion":  round(avg_completion, 3),
            "assessment":      assessment,
            "recommendation":  recommendation,
        }

    # ── Difficulty Adjustment ─────────────────────────────────────────────────

    def auto_adjust_difficulty(self, habit_id: str) -> Optional[str]:
        """
        Adaptive difficulty: adjusts based on 7-day completion rate.
        Returns new difficulty string if changed, None if unchanged.
        Cooldown: 3 days between adjustments.
        """
        habit = self.db.query(Habit).filter(Habit.id == habit_id).first()
        if not habit:
            return None

        if habit.last_adjusted_at:
            now = datetime.now(timezone.utc)
            last_at = habit.last_adjusted_at
            if last_at.tzinfo is None:
                now = now.replace(tzinfo=None)
            days_since = (now - last_at).days
            if days_since < 3:
                return None

        rate = self.get_completion_rate(habit_id, days=7)
        old_difficulty = habit.difficulty

        if rate > 0.90:
            if habit.difficulty == "easy":   habit.difficulty = "medium"
            elif habit.difficulty == "medium": habit.difficulty = "hard"
        elif rate < 0.30:
            if habit.difficulty == "hard":   habit.difficulty = "medium"
            elif habit.difficulty == "medium": habit.difficulty = "easy"

        if habit.difficulty != old_difficulty:
            habit.last_adjusted_at = datetime.now(timezone.utc)
            self.db.commit()
            return habit.difficulty

        return None

    # ── Internals ─────────────────────────────────────────────────────────────

    def _get_owned(self, user_id: str, habit_id: str) -> Optional[Habit]:
        return self.db.query(Habit).filter(
            Habit.id == habit_id,
            Habit.user_id == user_id,
            Habit.is_active == True,
        ).first()

    def _build_context(self, habit: Habit, streak: int, already_done: bool = False) -> Dict[str, Any]:
        return {
            "habit_id":    habit.id,
            "habit_name":  habit.name,
            "difficulty":  habit.difficulty,
            "streak":      streak,
            "already_done": already_done,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
