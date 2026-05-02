import sys
import os
import json
from kafka import KafkaConsumer
from sqlalchemy import create_engine, text

# Adjust path for app models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.core.config import settings

from app.services.context_store.manager import ContextManager

engine = create_engine(settings.DATABASE_URL)
ctx_manager = ContextManager(host=os.environ.get("REDIS_HOST", "localhost"))

consumer = KafkaConsumer(
    "behavioral_events",
    bootstrap_servers="localhost:9092",
    group_id="db-writer-group",
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Event DB Writer + Context Updater starting...")
for msg in consumer:
    event = msg.value
    user_id = event["user_id"]
    e_type = event["event_type"]
    e_val = event.get("event_value", 1.0)
    
    print(f"Processing event {e_type} for user {user_id}...")
    
    # 1. Update Real-time Context Store (Redis)
    ctx_manager.update_event_context(user_id, e_type, e_val)
    
    # 2. Persist to DB
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO events (user_id, event_type, event_value) VALUES (:user_id, :event_type, :event_value)"),
            {
                "user_id": user_id,
                "event_type": e_type,
                "event_value": e_val
            }
        )
        conn.commit()
