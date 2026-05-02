import pandas as pd
import logging
from scripts.db import get_connection
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_patterns(run_date):
    """
    Detects behavioral patterns using a sliding window of derived signals.
    """
    logger.info(f"Detecting patterns for date: {run_date}")
    engine = get_connection()
    run_date_dt = pd.to_datetime(run_date)
    
    # Fetch window (last 14 days)
    query = """
        SELECT *
        FROM derived_signals
        WHERE date >= (DATE(:run_date) - INTERVAL '14 days')
        AND date <= DATE(:run_date)
    """
    
    try:
        df = pd.read_sql(text(query), engine, params={"run_date": run_date})
    except Exception as e:
        logger.error(f"Error reading signals: {e}")
        return

    if df.empty:
        logger.info("No signal data found in window. Skipping.")
        return

    patterns = []
    
    # Process per user
    for user_id, group in df.groupby("user_id"):
        recent = group.sort_values("date").tail(7) # Focus on last 7 days for current trigger
        
        if len(recent) < 3:
            continue

        # Trigger 1: Energy-Avoidance (Existing rule)
        # Using integrity_score as proxy for energy if not directly in signals
        low_integrity_count = (recent["integrity_score"] < 5).sum()
        high_avoidance_count = (recent["avoidance_score"] > 0.7).sum()

        if low_integrity_count >= 3 and high_avoidance_count >= 2:
            patterns.append({
                "user_id": user_id,
                "pattern_type": "energy_avoidance_loop",
                "description": "Low integrity/energy levels are preceding spikes in task avoidance.",
                "confidence": 0.85,
                "detected_at": run_date_dt
            })

        # Trigger 2: Focus Decay
        if len(recent) >= 5:
            focus_slope = (recent["execution_score"].iloc[-1] - recent["execution_score"].iloc[0]) / 5
            if focus_slope < -0.1:
                patterns.append({
                    "user_id": user_id,
                    "pattern_type": "focus_decay",
                    "description": "Systematic drop in focus efficiency over the last 5 days.",
                    "confidence": 0.75,
                    "detected_at": run_date_dt
                })

    if not patterns:
        logger.info("No patterns detected.")
        return

    df_patterns = pd.DataFrame(patterns)
    
    # Idempotency: delete for this date first (to allow backfills)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM patterns WHERE DATE(detected_at) = DATE(:run_date)"), {"run_date": run_date})

    # Load
    df_patterns.to_sql("patterns", engine, if_exists="append", index=False)
    logger.info(f"Successfully detected and saved {len(df_patterns)} patterns.")

if __name__ == "__main__":
    import sys
    date_arg = sys.argv[1] if len(sys.argv) > 1 else pd.Timestamp.now().date()
    detect_patterns(date_arg)
