import pandas as pd
import logging
from scripts.db import get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compute_daily_features(run_date):
    """
    Computes daily features from events and logs for a specific date.
    Ensures idempotency by deleting existing records for the date first.
    """
    logger.info(f"Running feature pipeline for date: {run_date}")
    engine = get_connection()
    
    # Format date for SQL
    run_date_str = pd.to_datetime(run_date).strftime('%Y-%m-%d')

    # 1. Fetch Data with Partitioning (Date Filter)
    query_events = f"SELECT * FROM events WHERE DATE(created_at) = '{run_date_str}'"
    query_logs = f"SELECT * FROM daily_logs WHERE date = '{run_date_str}'"

    try:
        events = pd.read_sql(query_events, engine)
        logs = pd.read_sql(query_logs, engine)
    except Exception as e:
        logger.error(f"Error reading from DB: {e}")
        return

    if logs.empty:
        logger.info(f"No logs found for {run_date_str}. Skipping.")
        return

    # 2. Process and Aggregate
    # Ensure date column for merging
    logs['date'] = pd.to_datetime(logs['date']).dt.date
    
    if not events.empty:
        events['date'] = pd.to_datetime(events['created_at']).dt.date
        
        # Aggregate metrics
        deep_work = events[events["event_type"] == "deep_work"] \
            .groupby(["user_id", "date"])["event_value"].sum().reset_index(name="deep_work_minutes")

        distraction = events[events["event_type"] == "distraction"] \
            .groupby(["user_id", "date"])["event_value"].sum().reset_index(name="distraction_minutes")

        # Merge with logs
        df = logs.merge(deep_work, on=["user_id", "date"], how="left") \
                 .merge(distraction, on=["user_id", "date"], how="left")
    else:
        df = logs.copy()
        df["deep_work_minutes"] = 0.0
        df["distraction_minutes"] = 0.0

    df.fillna(0, inplace=True)

    # 3. Feature Engineering
    df["focus_ratio"] = df["deep_work_minutes"] / (
        df["deep_work_minutes"] + df["distraction_minutes"] + 1
    )
    
    # Prepare for insert (column name mapping)
    # Mapping model fields: execution_score, avoidance_score, cognitive_score, integrity_score, etc.
    output_df = pd.DataFrame()
    output_df["user_id"] = df["user_id"]
    output_df["date"] = df["date"]
    output_df["execution_score"] = df["focus_ratio"]
    output_df["avoidance_score"] = df["avoidance_flag"].astype(float)
    output_df["cognitive_score"] = (df["thought_label"] == "negative").astype(float)
    output_df["integrity_score"] = df["self_integrity_score"]
    output_df["deep_work_minutes"] = df["deep_work_minutes"]
    output_df["distraction_minutes"] = df["distraction_minutes"]
    output_df["version"] = 2 # Mark as V2 processed

    # 4. IDEMPOTENCY: Delete existing records for the date
    with engine.connect() as conn:
        conn.execute(f"DELETE FROM derived_signals WHERE date = '{run_date_str}'")

    # 5. Load
    output_df.to_sql("derived_signals", engine, if_exists="append", index=False)
    logger.info(f"Successfully processed {len(output_df)} signal records for {run_date_str}")

if __name__ == "__main__":
    import sys
    date_arg = sys.argv[1] if len(sys.argv) > 1 else pd.Timestamp.now().date()
    compute_daily_features(date_arg)
