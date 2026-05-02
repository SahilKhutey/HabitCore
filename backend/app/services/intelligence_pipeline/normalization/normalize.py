"""
Normalization Layer — Standardizes raw event data.
"""
from datetime import datetime
from typing import Dict, Any

def normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a raw event into a standard dictionary.
    Ensures correct types and field names.
    """
    created_at = event.get("created_at")
    if isinstance(created_at, datetime):
        timestamp = created_at
    elif isinstance(created_at, str):
        try:
            timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except:
            timestamp = datetime.utcnow()
    else:
        timestamp = datetime.utcnow()

    return {
        "user_id": str(event["user_id"]),
        "type": str(event["event_type"]).lower(),
        "category": str(event.get("event_category", "behavior")).lower(),
        "value": float(event.get("event_value", 0.0)),
        "metadata": event.get("metadata", {}),
        "timestamp": timestamp
    }
