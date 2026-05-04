"""
BehavioralInsightService — main orchestrator for the Behavioral Insight Engine.

Pipeline:
  1. Fetch raw data from DB (HabitLog + DailyCheckin for last N days)
  2. Build DailyBehaviorData records
  3. FeatureExtractor → per-day features + aggregated stats
  4. PatternRules → rule-based insights (deterministic, high-precision)
  5. BehaviorMLModel → correlation coefficients
  6. InsightGenerator → correlation-based insights (adaptive)
  7. Merge, rank, deduplicate, time-decay
  8. Persist to behavioral_insights table
  9. Return ranked insight list

Deduplication: insights with the same trigger_key are not re-saved
if one was created within DEDUP_WINDOW_DAYS days.

Time decay: older stored insights have their rank_score reduced so fresh
insights surface higher.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date, timezone
from sqlalchemy.orm import Session

from .models import BehavioralInsight
from .schemas import DailyBehaviorData, InsightOut, GrowthReportOut
from .feature_extractor import FeatureExtractor
from .pattern_rules import PatternRules
from .ml_model import BehaviorMLModel
from .insight_generator import InsightGenerator

from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.psychological import DailyCheckin


# ── Constants ────────────────────────────────────────────────────────────────

ANALYSIS_WINDOW_DAYS = 14    # days of history to analyze
DEDUP_WINDOW_DAYS    = 3     # min days before same trigger_key re-surfaces
MAX_INSIGHTS_STORED  = 50    # per-user cap to prevent unbounded growth
TIME_DECAY_DAILY     = 0.02  # rank_score reduction per day of age
FEED_LIMIT           = 10    # default max returned in /insights/behavioral


class BehavioralInsightService:
    """Main orchestrator. Instantiated with a DB session per request."""

    def __init__(self, db: Session):
        self.db = db

    # ── PUBLIC API ────────────────────────────────────────────────────────────

    def run_for_user(
        self,
        user_id: str,
        habit_count: int = 0,
        archetype: str = "pioneer"
    ) -> List[BehavioralInsight]:
        """
        Full pipeline: fetch → extract → detect → generate → persist.
        Returns list of newly created BehavioralInsight objects.
        Call this on habit completion and on daily check-in submission.
        """
        raw_data = self._fetch_user_data(user_id)
        if not raw_data:
            return []

        extra = {"habit_count": habit_count, "archetype": archetype}
        raw_insights = self._detect_insights(raw_data, extra)

        new_insights = []
        for raw in raw_insights:
            if self._should_save(user_id, raw.get("trigger_key")):
                insight = self._persist(user_id, raw)
                new_insights.append(insight)

        self._apply_time_decay(user_id)
        self._prune_old_insights(user_id)
        return new_insights

    def get_feed(
        self,
        user_id: str,
        limit: int = FEED_LIMIT,
        include_read: bool = False
    ) -> List[InsightOut]:
        """Return ranked, unread (or all) insights for a user."""
        query = self.db.query(BehavioralInsight).filter(
            BehavioralInsight.user_id == user_id,
            BehavioralInsight.is_dismissed == False,
        )
        if not include_read:
            query = query.filter(BehavioralInsight.is_read == False)

        insights = (
            query.order_by(BehavioralInsight.rank_score.desc())
                 .limit(limit)
                 .all()
        )
        return [self._to_schema(i) for i in insights]

    def mark_read(self, user_id: str, insight_id: str) -> bool:
        """Mark a single insight as read. Returns True if found."""
        insight = self.db.query(BehavioralInsight).filter(
            BehavioralInsight.id == insight_id,
            BehavioralInsight.user_id == user_id,
        ).first()
        if not insight:
            return False
        insight.is_read = True
        self.db.commit()
        return True

    def mark_dismissed(self, user_id: str, insight_id: str) -> bool:
        """Permanently dismiss an insight from the user's feed."""
        insight = self.db.query(BehavioralInsight).filter(
            BehavioralInsight.id == insight_id,
            BehavioralInsight.user_id == user_id,
        ).first()
        if not insight:
            return False
        insight.is_dismissed = True
        self.db.commit()
        return True

    def get_growth_report(self, user_id: str, days: int = 7) -> GrowthReportOut:
        """
        Build a weekly growth narrative from stored insights + aggregated features.
        Returns a GrowthReportOut with plain-language narrative summary.
        """
        raw_data = self._fetch_user_data(user_id, window_days=days)
        if not raw_data:
            return GrowthReportOut(
                period_days=days,
                avg_completion_rate=0.0,
                trend="insufficient_data",
                top_pattern=None,
                top_warning=None,
                narrative="Not enough behavioral data to generate a report yet. Complete at least 3 days of habits.",
                insights_count=0,
            )

        features = FeatureExtractor.extract(raw_data)
        agg      = FeatureExtractor.aggregate(features)

        # Trend: compare recent half vs. earlier half
        mid = len(features) // 2
        early_avg  = sum(f["completion_rate"] for f in features[:mid]) / max(1, mid)
        recent_avg = sum(f["completion_rate"] for f in features[mid:]) / max(1, len(features) - mid)
        delta      = recent_avg - early_avg

        if delta > 0.08:
            trend = "improving"
        elif delta < -0.08:
            trend = "declining"
        else:
            trend = "stable"

        # Pull top stored insights
        patterns = self.db.query(BehavioralInsight).filter(
            BehavioralInsight.user_id == user_id,
            BehavioralInsight.type == "pattern",
            BehavioralInsight.is_dismissed == False,
        ).order_by(BehavioralInsight.rank_score.desc()).first()

        warnings = self.db.query(BehavioralInsight).filter(
            BehavioralInsight.user_id == user_id,
            BehavioralInsight.type == "warning",
            BehavioralInsight.is_dismissed == False,
        ).order_by(BehavioralInsight.rank_score.desc()).first()

        total = self.db.query(BehavioralInsight).filter(
            BehavioralInsight.user_id == user_id,
            BehavioralInsight.is_dismissed == False,
        ).count()

        narrative = self._build_narrative(agg, trend, days)

        return GrowthReportOut(
            period_days=days,
            avg_completion_rate=round(agg["avg_completion"], 3),
            trend=trend,
            top_pattern=patterns.message if patterns else None,
            top_warning=warnings.message if warnings else None,
            narrative=narrative,
            insights_count=total,
        )

    # ── INTERNAL PIPELINE ─────────────────────────────────────────────────────

    def _fetch_user_data(
        self,
        user_id: str,
        window_days: int = ANALYSIS_WINDOW_DAYS
    ) -> List[DailyBehaviorData]:
        """
        Assembles per-day behavioral snapshots from HabitLog + DailyCheckin.
        Returns a list of DailyBehaviorData, one per day with activity.
        """
        cutoff = date.today() - timedelta(days=window_days)

        # All habit logs in the window
        logs = self.db.query(HabitLog).join(Habit, HabitLog.habit_id == Habit.id).filter(
            Habit.user_id == user_id,
            HabitLog.date >= cutoff,
        ).all()

        # All checkins in the window
        checkins = self.db.query(DailyCheckin).filter(
            DailyCheckin.user_id == user_id,
            DailyCheckin.date >= cutoff,
        ).all()

        # Habit count: total active habits for the user
        habit_count = self.db.query(Habit).filter(
            Habit.user_id == user_id,
            Habit.is_active == True,
        ).count()

        # Build per-day dicts
        days_with_logs = {}
        for log in logs:
            d = log.date.isoformat()
            if d not in days_with_logs:
                days_with_logs[d] = {"completed": 0, "total": habit_count}
            days_with_logs[d]["completed"] += 1

        # Enrich with checkin data
        checkin_map = {c.date.isoformat(): c for c in checkins}

        result: List[DailyBehaviorData] = []
        for day_str in sorted(days_with_logs.keys()):
            day_data = days_with_logs[day_str]
            checkin  = checkin_map.get(day_str)

            mood_raw        = 3
            energy_raw      = 2
            sleep_quality   = 3
            sleep_hours     = 6.5
            reflection      = None

            if checkin:
                mood_raw      = checkin.mood or "neutral"
                energy_raw    = checkin.energy_morning or "medium"
                sleep_quality = checkin.sleep_quality or 3
                reflection    = checkin.reflection

            result.append(DailyBehaviorData(
                date=day_str,
                habits_completed=day_data["completed"],
                habits_total=day_data["total"],
                mood=mood_raw,
                energy=energy_raw,
                sleep_quality=sleep_quality,
                sleep_hours=sleep_hours,
                reflection=reflection,
            ))

        return result

    def _detect_insights(
        self,
        raw_data: List[DailyBehaviorData],
        extra: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Run full detection pipeline: features → rules + ML → combined list."""
        features = FeatureExtractor.extract(raw_data)
        agg      = FeatureExtractor.aggregate(features)

        rule_insights = PatternRules.detect(agg, extra)
        correlations  = BehaviorMLModel.compute_correlations(features)
        ml_insights   = InsightGenerator.from_correlations(correlations)

        all_insights = rule_insights + ml_insights

        # Rank: confidence * impact
        for i in all_insights:
            i["rank_score"] = round(i["confidence"] * i["impact"], 4)

        # Sort by rank descending
        all_insights.sort(key=lambda x: x["rank_score"], reverse=True)
        return all_insights

    def _should_save(self, user_id: str, trigger_key: Optional[str]) -> bool:
        """
        Deduplication check: don't save an insight with the same trigger_key
        if one was created within DEDUP_WINDOW_DAYS days.
        """
        if not trigger_key:
            return True
        cutoff = datetime.now(timezone.utc) - timedelta(days=DEDUP_WINDOW_DAYS)
        existing = self.db.query(BehavioralInsight).filter(
            BehavioralInsight.user_id == user_id,
            BehavioralInsight.trigger_key == trigger_key,
            BehavioralInsight.created_at >= cutoff,
        ).first()
        return existing is None

    def _persist(self, user_id: str, raw: Dict[str, Any]) -> BehavioralInsight:
        """Save a raw insight dict to the DB as a BehavioralInsight record."""
        insight = BehavioralInsight(
            user_id=user_id,
            type=raw["type"],
            category=raw["category"],
            message=raw["message"],
            action_hint=raw.get("action_hint"),
            confidence=raw["confidence"],
            impact_score=raw["impact"],
            rank_score=raw["rank_score"],
            trigger_key=raw.get("trigger_key"),
            last_triggered_at=datetime.now(timezone.utc),
        )
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def _apply_time_decay(self, user_id: str) -> None:
        """
        Reduce rank_score for older insights so fresh ones surface higher.
        Applied in-place to all unread, undismissed insights older than 1 day.
        """
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        old_insights = self.db.query(BehavioralInsight).filter(
            BehavioralInsight.user_id == user_id,
            BehavioralInsight.created_at < yesterday,
            BehavioralInsight.is_dismissed == False,
        ).all()

        for ins in old_insights:
            age_days    = (datetime.now(timezone.utc) - ins.created_at).days
            decay       = age_days * TIME_DECAY_DAILY
            ins.rank_score = max(0.0, round(ins.rank_score - decay, 4))

        self.db.commit()

    def _prune_old_insights(self, user_id: str) -> None:
        """Keep only the top MAX_INSIGHTS_STORED insights per user (by rank_score)."""
        all_insights = (
            self.db.query(BehavioralInsight)
                   .filter(BehavioralInsight.user_id == user_id)
                   .order_by(BehavioralInsight.rank_score.desc())
                   .all()
        )
        if len(all_insights) > MAX_INSIGHTS_STORED:
            to_delete = all_insights[MAX_INSIGHTS_STORED:]
            for ins in to_delete:
                self.db.delete(ins)
            self.db.commit()

    def _build_narrative(
        self,
        agg: Dict[str, float],
        trend: str,
        days: int
    ) -> str:
        """Generate a 2–3 sentence plain-language behavioral narrative."""
        trend_phrase = {
            "improving":          "Your consistency has been improving over this period.",
            "stable":             "Your behavioral output has been stable over this period.",
            "declining":          "Completion has declined over this period — this warrants attention.",
            "insufficient_data":  "Insufficient data for a trend assessment.",
        }.get(trend, "Trend unclear.")

        completion_pct = round(agg["avg_completion"] * 100)
        sleep_str      = f"{agg['avg_sleep']:.1f} hours"
        mood_note      = (
            "Mood levels have been a contributing factor."
            if agg["avg_mood"] < 2.5 else
            "Mood has been within a functional range."
        )

        return (
            f"Over the last {days} days, your average habit completion was {completion_pct}%. "
            f"{trend_phrase} "
            f"Average sleep was {sleep_str}. {mood_note}"
        )

    def _to_schema(self, insight: BehavioralInsight) -> InsightOut:
        return InsightOut(
            id=insight.id,
            type=insight.type,
            category=insight.category,
            message=insight.message,
            action_hint=insight.action_hint,
            confidence=insight.confidence,
            impact_score=insight.impact_score,
            rank_score=insight.rank_score,
            is_read=insight.is_read,
            created_at=insight.created_at.isoformat(),
        )
