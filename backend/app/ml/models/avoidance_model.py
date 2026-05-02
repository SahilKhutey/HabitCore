"""
Avoidance Model — Logistic Regression for predicting behavioral friction.
"""
try:
    from sklearn.linear_model import LogisticRegression
    import joby # Using joblib for model serialization
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

import os

class AvoidanceModel:
    def __init__(self, model_path: str = None):
        self.model = None
        self.path = model_path
        if SKLEARN_AVAILABLE:
            if model_path and os.path.exists(model_path):
                try:
                    import joblib
                    self.model = joblib.load(model_path)
                except Exception:
                    self.model = LogisticRegression(max_iter=1000)
            else:
                self.model = LogisticRegression(max_iter=1000)

    def train(self, X: np.ndarray, y: np.ndarray):
        if not SKLEARN_AVAILABLE:
            return False
        try:
            self.model.fit(X, y)
            return True
        except Exception:
            return False

    def predict(self, X: np.ndarray) -> float:
        if not SKLEARN_AVAILABLE or self.model is None:
            return 0.5 # Neutral fallback
        try:
            # Predict probability of the positive class (avoidance)
            return float(self.model.predict_proba(X)[0][1])
        except Exception:
            return 0.5

    def save(self, path: str):
        if not SKLEARN_AVAILABLE or self.model is None:
            return
        import joblib
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
