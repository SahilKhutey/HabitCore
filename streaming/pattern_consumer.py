"""
Pattern Consumer — Persists Flink-detected patterns and triggers real-time nudges.
"""
import sys
import os
import json
from kafka import KafkaConsumer
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

# Path for app config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

consumer = KafkaConsumer(
    "patterns_stream",
    bootstrap_servers="localhost:9092",
    group_id="pattern-insight-group",
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

def trigger_nudge(user_id, pattern_type, message):
    """
    In a real system, this would call a notification service (Firebase/APNS).
    For now, we log it as a high-priority system signal.
    """
    print(f"!!! REAL-TIME NUDGE for {user_id}: {message} !!!")

print("Pattern Insight Consumer starting...")
for msg in consumer:
    pattern = msg.value
    user_id = pattern["user_id"]
    p_type = pattern["pattern_type"]
    
    print(f"Detected pattern {p_type} for user {user_id}")
    
    # 1. Persist to DB
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO patterns (user_id, pattern_type, confidence, metadata, created_at)
                VALUES (:user_id, :p_type, :confidence, :metadata, :created_at)
            """),
            {
                "user_id": user_id,
                "p_type": p_type,
                "confidence": pattern.get("confidence", 0.0),
                "metadata": json.dumps(pattern.get("metadata", {})),
                "created_at": datetime.now(timezone.utc)
            }
        )
        conn.commit()
    
    # 2. Real-time Action Logic
    if p_type == "high_distraction_spike":
        trigger_nudge(user_id, p_type, "Focus detected slipping. Time for a 2-minute breath reset?")
    elif p_type == "active_avoidance_cycle":
        trigger_nudge(user_id, p_type, "You've hit an avoidance loop. What's the smallest possible action you can take now?")
