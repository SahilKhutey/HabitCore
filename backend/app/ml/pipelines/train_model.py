"""
Training Pipeline — Orchestrates model training and registration.
"""
import numpy as np
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.ml.models.avoidance_model import AvoidanceModel
from app.models.intelligence_models import ModelRegistry

def train_avoidance_model(db: Session, user_id: str, historical_data: list):
    """
    Trains a personalized avoidance model for a user and registers the version.
    """
    if len(historical_data) < 30:
        return None # Require 30 days of data

    # Prepare features: energy, stress, focus_ratio
    X = np.array([
        [d.get("energy", 5), d.get("stress", 5), d.get("focus_ratio", 0.5)]
        for d in historical_data
    ])
    # Target: avoidance_flag
    y = np.array([d.get("avoidance_flag", 0) for d in historical_data])

    model = AvoidanceModel()
    success = model.train(X, y)

    if success:
        # Versioning and Storage
        version = db.query(ModelRegistry).filter(ModelRegistry.name == "avoidance_model").count() + 1
        model_filename = f"models/avoidance_{user_id}_v{version}.joblib"
        model_path = f"artifacts/{model_filename}"
        
        model.save(model_path)

        # Register in DB
        registry_entry = ModelRegistry(
            name="avoidance_model",
            version=version,
            path=model_path,
            accuracy=0.0, # To be calculated with validation set in next iteration
            metadata_json={
                "user_id": user_id,
                "training_date": datetime.now(timezone.utc).isoformat(),
                "samples": len(historical_data)
            }
        )
        db.add(registry_entry)
        db.commit()
        return registry_entry
    
    return None
