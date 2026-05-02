"""
Intelligence V2 API — Real-time prediction and advanced analytics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.ml.models.avoidance_model import AvoidanceModel
from app.ml.features.feature_builder import build_daily_features
from app.models.intelligence_models import DailyLog, Event, ModelRegistry
from datetime import date, datetime

from app.ml.core.features import build_behavioral_features
from app.models.intelligence_models import DailyLog, Event, ModelRegistry, PredictionLog
import uuid

router = APIRouter()

@router.post("/predict/avoidance", summary="Predict avoidance risk (V2 Lifecycle)")
def predict_avoidance(
    user=Depends(auth_required),
    db: Session = Depends(get_db)
):
    # 1. Fetch only PRODUCTION-ready model
    model_info = db.query(ModelRegistry).filter(
        ModelRegistry.name == "avoidance_model",
        ModelRegistry.status == "production"
    ).order_by(ModelRegistry.version.desc()).first()
    
    if not model_info:
        # Fallback to latest staging if no production model
        model_info = db.query(ModelRegistry).filter(
            ModelRegistry.name == "avoidance_model"
        ).order_by(ModelRegistry.version.desc()).first()

    if not model_info:
        raise HTTPException(status_code=404, detail="Intelligence Engine initializing.")

    # 2. Get real-time signals
    today = date.today()
    log = db.query(DailyLog).filter(DailyLog.user_id == str(user.id), DailyLog.date == today).first()
    if not log:
        raise HTTPException(status_code=400, detail="Incomplete day log.")

    # 3. Standardized Feature Building (Parity with training)
    feat_input = {
        "energy": log.self_integrity_score or 5,
        "focus_ratio": 0.5, # Default if no events yet
        "distraction_minutes": 0.0,
        "integrity_score": log.self_integrity_score or 5
    }
    features = build_behavioral_features(feat_input)

    # 4. Predict
    import joblib
    model = joblib.load(model_info.path)
    risk = float(model.predict_proba([features])[0][1])

    # 5. LIFE CYCLE LOGGING
    pred_log = PredictionLog(
        user_id=str(user.id),
        model_id=model_info.id,
        input_features=feat_input,
        prediction=risk,
        created_at=datetime.now(timezone.utc)
    )
    db.add(pred_log)
    db.commit()

    return {
        "risk_score": risk,
        "model_v": model_info.version,
        "status": model_info.status,
        "directive": "Interrupt current loop" if risk > 0.7 else "Stable momentum"
    }
