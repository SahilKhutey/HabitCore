import pandas as pd
import logging
from scripts.db import get_connection
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_insights(run_date):
    """
    Converts patterns detected on a specific date into actionable user insights.
    """
    logger.info(f"Generating insights for date: {run_date}")
    engine = get_connection()
    
    # 1. Fetch patterns for today
    query = "SELECT * FROM patterns WHERE DATE(detected_at) = DATE(:run_date)"
    
    try:
        patterns = pd.read_sql(text(query), engine, params={"run_date": run_date})
    except Exception as e:
        logger.error(f"Error reading patterns: {e}")
        return

    if patterns.empty:
        logger.info("No patterns found to convert.")
        return

    insights = []
    
    for _, row in patterns.iterrows():
        # Map pattern type to title/priority
        priority = 0.8
        title = "Behavior Insight"
        
        if row["pattern_type"] == "energy_avoidance_loop":
            title = "Energy-Avoidance Trigger"
            priority = 0.95
        elif row["pattern_type"] == "focus_decay":
            title = "Focus Alert"
            priority = 0.85
            
        insights.append({
            "user_id": row["user_id"],
            "type": "pattern",
            "title": title,
            "message": row["description"],
            "priority": priority,
            "created_at": pd.to_datetime(run_date)
        })

    if not insights:
        return

    df_insights = pd.DataFrame(insights)
    
    # Idempotency
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM insights WHERE DATE(created_at) = DATE(:run_date)"), {"run_date": run_date})

    # Load
    df_insights.to_sql("insights", engine, if_exists="append", index=False)
    logger.info(f"Successfully generated {len(df_insights)} insights.")

if __name__ == "__main__":
    import sys
    date_arg = sys.argv[1] if len(sys.argv) > 1 else pd.Timestamp.now().date()
    generate_insights(date_arg)
