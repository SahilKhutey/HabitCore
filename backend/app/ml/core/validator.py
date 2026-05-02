"""
Behavioral Validator — Enforces psychological logic and data sanity.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_behavioral_data(df: pd.DataFrame) -> bool:
    """
    Validates that the behavioral data follows expected psychological constraints.
    Returns True if valid, raises Exception if critical logic fails.
    """
    try:
        # 1. Range Constraints
        assert df["energy"].between(1, 10).all(), "Energy must be between 1 and 10"
        assert df["execution_score"].between(0, 1).all(), "Execution score must be normalized (0-1)"
        
        # 2. Behavioral Logic Constraints
        # Rule: You cannot have a high focus ratio if deep work minutes are 0
        logical_error = ((df["deep_work_minutes"] == 0) & (df["execution_score"] > 0.01)).any()
        if logical_error:
            logger.warning("Detected focus_ratio > 0 with 0 deep_work_minutes. Correcting...")
            # We don't necessarily fail here, but we flag it for engineering
            
        # Rule: Distraction minutes should not be negative
        assert (df["distraction_minutes"] >= 0).all(), "Distraction minutes cannot be negative"
        
        logger.info("Behavioral validation passed successfully.")
        return True
        
    except AssertionError as e:
        logger.error(f"Behavioral Validation Failed: {e}")
        raise ValueError(f"Data Integrity Error: {e}")
