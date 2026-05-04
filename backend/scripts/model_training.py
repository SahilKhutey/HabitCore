import pandas as pd
import logging
from sklearn.linear_model import LogisticRegression
import joblib
import os
from datetime import datetime, timezone
from scripts.db import get_connection
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_behavioral_models():
    """
    Trains user-specific behavioral models using the last 30 days of data.
    Registers models in the ModelRegistry.
    """
    logger.info("Starting behavioral model training cycle...")
    engine = get_connection()
    
    # 1. Fetch training data (partitioned by date)
    query = """
        SELECT user_id, execution_score, integrity_score, distraction_minutes, avoidance_score
        FROM derived_signals
        WHERE date >= date('now', '-30 days')
    """
    
    try:
        df = pd.read_sql(text(query), engine)
    except Exception as e:
        logger.error(f"Error fetching training data: {e}")
        return

    if len(df) < 50:
        logger.info("Insufficient system-wide data for training. Skipping.")
        return

    # Process per user (or global model if sparse)
    for user_id, group in df.groupby("user_id"):
        if len(group) < 14: # Minimum 2 weeks of data per user
            continue
            
        logger.info(f"Training avoidance model for user {user_id}")
        
        X = group[["execution_score", "integrity_score", "distraction_minutes"]].fillna(0)
        y = (group["avoidance_score"] > 0.5).astype(int) # Target: high avoidance

        if y.nunique() < 2:
            logger.info(f"Not enough class variance for user {user_id}. Skipping.")
            continue

        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)

        # 2. Versioned Storage
        os.makedirs("models", exist_ok=True)
        model_name = f"avoidance_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        model_path = os.path.join("models", model_name)
        joblib.dump(model, model_path)

        # 3. Register in DB
        with engine.connect() as conn:
            # Get latest version
            v_query = text("SELECT COUNT(*) FROM model_registry WHERE name = 'avoidance_model'")
            version = conn.execute(v_query).scalar() + 1
            
            insert_query = text("""
                INSERT INTO model_registry (name, version, path, accuracy, metadata_json, created_at)
                VALUES (:name, :version, :path, :accuracy, :meta, :created_at)
            """)
            conn.execute(insert_query, {
                "name": "avoidance_model",
                "version": version,
                "path": model_path,
                "accuracy": float(model.score(X, y)),
                "meta": {"user_id": str(user_id), "samples": len(group)},
                "created_at": datetime.now(timezone.utc)
            })
            
    logger.info("Model training cycle complete.")

if __name__ == "__main__":
    train_behavioral_models()
