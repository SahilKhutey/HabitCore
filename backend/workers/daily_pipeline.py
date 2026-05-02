"""
Daily Pipeline Worker — The core batch processing unit.
"""
from datetime import date, timedelta, datetime, timezone
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.intelligence_models import DailyLog, Event, DerivedSignal, Pattern, Insight, Score
from app.ml.features.feature_builder import build_daily_features
from app.ml.features.rolling import compute_rolling
from app.ml.rules.rule_engine import detect_patterns
from app.ml.stats.correlation import compute_stats
from app.ml.pipelines.insight_generator import generate_insights

def run_daily_pipeline(user_id: str, target_date: date = None):
    """
    Executes the full intelligence pipeline for a specific user and date.
    """
    if target_date is None:
        target_date = date.today()
        
    db = SessionLocal()
    try:
        # 1. Fetch Raw Data
        log = db.query(DailyLog).filter(DailyLog.user_id == user_id, DailyLog.date == target_date).first()
        if not log:
            return # Skip if no log for today

        events = db.query(Event).filter(
            Event.user_id == user_id,
            Event.created_at >= datetime.combine(target_date, datetime.min.time()),
            Event.created_at <= datetime.combine(target_date, datetime.max.time())
        ).all()

        # 2. Feature Engineering
        daily_features = build_daily_features(events, log)
        
        # Fetch history for rolling features and patterns
        history_start = target_date - timedelta(days=14)
        history_logs = db.query(DailyLog).filter(
            DailyLog.user_id == user_id, 
            DailyLog.date >= history_start,
            DailyLog.date < target_date
        ).order_by(DailyLog.date.asc()).all()
        
        # Convert history to feature list
        history_features = []
        for h_log in history_logs:
            h_events = db.query(Event).filter(
                Event.user_id == user_id,
                Event.created_at >= datetime.combine(h_log.date, datetime.min.time()),
                Event.created_at <= datetime.combine(h_log.date, datetime.max.time())
            ).all()
            history_features.append(build_daily_features(h_events, h_log))
        
        # Add today to history for pattern detection
        all_features = history_features + [daily_features]
        
        rolling = compute_rolling(all_features)
        
        # 3. Pattern Detection
        patterns_data = detect_patterns(all_features)
        stats = compute_stats(all_features)
        
        # 4. Insight Generation
        insights_data = generate_insights(patterns_data, stats)

        # 5. Persistence
        # Save patterns
        for p_data in patterns_data:
            pattern = Pattern(
                user_id=user_id,
                pattern_type=p_data["type"],
                description=p_data["message"],
                confidence=p_data["confidence"],
                detected_at=datetime.now(timezone.utc)
            )
            db.add(pattern)

        # Save insights
        for i_data in insights_data:
            insight = Insight(
                user_id=user_id,
                type=i_data["type"],
                title=i_data["title"],
                message=i_data["message"],
                priority=i_data["priority"],
                created_at=datetime.now(timezone.utc)
            )
            db.add(insight)

        db.commit()
    finally:
        db.close()
