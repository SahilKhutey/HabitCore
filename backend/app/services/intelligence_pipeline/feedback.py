"""
Feedback Processor — Manages the user feedback loop for patterns and insights.
"""
from typing import Any
from sqlalchemy.orm import Session
from app.models.intelligence_models import Pattern, Insight

class FeedbackProcessor:
    @staticmethod
    def process_feedback(db: Session, user_id: str, pattern_id: str, feedback: str):
        """
        Adjusts pattern and insight confidence based on user feedback.
        feedback: 'accurate' | 'inaccurate'
        """
        pattern = db.query(Pattern).filter(
            Pattern.id == pattern_id,
            Pattern.user_id == str(user_id)
        ).first()
        
        if not pattern:
            return False

        # Identity-level reinforcement: If accurate, increase confidence and impact
        if feedback == "accurate":
            pattern.confidence = min(0.99, (pattern.confidence or 0.5) + 0.05)
            pattern.impact_score = (pattern.impact_score or 1.0) + 0.1
        
        # Self-correction: If inaccurate, decrease confidence rapidly
        elif feedback == "inaccurate":
            pattern.confidence = max(0.1, (pattern.confidence or 0.5) - 0.15)
            # If confidence drops too low, deactivate pattern
            if pattern.confidence < 0.3:
                pattern.active = False

        db.commit()
        return True
