"""
ML Engine — Probabilistic models (V2 Entry).
"""
try:
    from sklearn.linear_model import LogisticRegression
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class AvoidanceModel:
    """
    Predicts the probability of avoidance tomorrow based on recent features.
    """
    def __init__(self):
        self.model = None
        if SKLEARN_AVAILABLE:
            self.model = LogisticRegression(max_iter=1000)

    def train(self, X: List[List[float]], y: List[int]):
        """
        Trains the model on historical behavioral data.
        X: [[energy, stress, focus_ratio, avoidance_rate_7d], ...]
        y: [0, 1] (avoided or not)
        """
        if not SKLEARN_AVAILABLE or not self.model:
            return False
        
        if len(X) < 14: # Minimum training size
            return False
            
        try:
            self.model.fit(np.array(X), np.array(y))
            return True
        except Exception as e:
            print(f"ML Training Error: {e}")
            return False

    def predict_proba(self, x: List[float]) -> float:
        """
        Returns the probability (0.0-1.0) of avoidance.
        """
        if not SKLEARN_AVAILABLE or not self.model:
            return 0.0
            
        try:
            # sklearn predict_proba returns [prob_0, prob_1]
            probs = self.model.predict_proba(np.array([x]))[0]
            return float(probs[1])
        except:
            return 0.0

    def is_ready(self, history_len: int) -> bool:
        return SKLEARN_AVAILABLE and history_len >= 30
