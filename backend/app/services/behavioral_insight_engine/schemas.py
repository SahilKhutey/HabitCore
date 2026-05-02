"""
Schemas — Pydantic contracts for the Behavioral Insight Engine.

DailyBehaviorData: input contract normalizing checkin + habit data per day.
InsightOut: output contract for API responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class DailyBehaviorData(BaseModel):
    """
    Standardized per-day behavioral snapshot.
    Assembled by the service from HabitLog + DailyCheckin tables.
    """
    date: str                          # ISO date string e.g. "2026-05-02"
    habits_completed: int = 0
    habits_total: int = 0
    mood: int = 3                      # Normalized 1–5 (happy=5, sad=1, neutral=3)
    energy: int = 3                    # Normalized 1–3 (high=3, medium=2, low=1)
    sleep_hours: float = 7.0           # Estimated from sleep_quality * 1.5
    sleep_quality: int = 3             # Raw 1–5 from DailyCheckin
    reflection: Optional[str] = None   # Free-text reflection entry


class InsightOut(BaseModel):
    """API response shape for a single behavioral insight."""
    id: str
    type: str            # pattern | warning | growth | reflection
    category: str        # sleep | mood | consistency | energy | overload
    message: str
    action_hint: Optional[str] = None
    confidence: float
    impact_score: float
    rank_score: float
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True


class GrowthReportOut(BaseModel):
    """Weekly growth report: narrative summary of behavioral trends."""
    period_days: int
    avg_completion_rate: float
    trend: str              # "improving" | "stable" | "declining"
    top_pattern: Optional[str]
    top_warning: Optional[str]
    narrative: str          # 2–3 sentence plain-language behavioral summary
    insights_count: int
