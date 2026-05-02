"""
Upgraded Training Pipeline — Feature-aware and metric-gated.
"""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import recall_score, precision_score
import joblib
import os
from datetime import datetime, timezone
from app.ml.core.features import build_behavioral_features, get_feature_version
from app.ml.core.validator import validate_behavioral_data
from scripts.db import get_connection
from sqlalchemy import text

def train_avoidance_v2():
    engine = get_connection()
    
    # 1. Fetch data
    df = pd.read_sql("SELECT * FROM derived_signals WHERE date >= (CURRENT_DATE - INTERVAL '60 days')", engine)
    
    if len(df) < 50:
        return {"status": "skipped", "reason": "insufficient_data"}

    # 2. Behavioral Validation
    validate_behavioral_data(df)

    # 3. Feature Building (Unified Source of Truth)
    # Map raw signals to the feature builder input format
    X_raw = df.apply(lambda row: {
        "energy": row.get("integrity_score", 5), # Using integrity as energy proxy
        "focus_ratio": row.get("execution_score", 0.5),
        "distraction_minutes": row.get("distraction_minutes", 0),
        "integrity_score": row.get("integrity_score", 5)
    }, axis=1)
    
    X = pd.DataFrame([build_behavioral_features(r) for r in X_raw])
    y = (df["avoidance_score"] > 0.6).astype(int)

    # 4. Training with recall gate
    model = LogisticRegression()
    model.fit(X, y)
    
    preds = model.predict(X)
    recall = float(recall_score(y, preds))
    precision = float(precision_score(y, preds))
    accuracy = float(model.score(X, y))

    # CRITICAL: Recall Gate
    # We must catch avoidance! If we miss more than 40% of cases, don't deploy.
    status = "production" if recall >= 0.6 else "staging"

    # 5. Save & Register
    os.makedirs("models", exist_ok=True)
    model_name = f"avoidance_v2_{datetime.now().strftime('%Y%m%d')}.pkl"
    path = os.path.join("models", model_name)
    joblib.dump(model, path)

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO model_registry (name, version, feature_version, path, accuracy, recall, precision, status, created_at)
            VALUES (:name, :version, :feat_v, :path, :acc, :rec, :prec, :status, :created_at)
        """), {
            "name": "avoidance_model",
            "version": int(datetime.now().timestamp()),
            "feat_v": get_feature_version(),
            "path": path,
            "acc": accuracy,
            "rec": recall,
            "prec": precision,
            "status": status,
            "created_at": datetime.now(timezone.utc)
        })

    return {
        "status": "success",
        "recall": recall,
        "deployment": status,
        "path": path
    }
