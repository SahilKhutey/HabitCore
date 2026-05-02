"""
Nudge Engine — Real-time behavioral intervention service.
"""
import threading
import json
import logging
import sys
import os
from fastapi import FastAPI
from kafka import KafkaConsumer
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

# Adjust path for app imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
from app.core.config import settings
from app.services.nudge_engine.decision import score_nudge, should_skip_nudge
from app.services.nudge_engine.templates import generate_nudge_content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.services.context_store.manager import ContextManager

app = FastAPI(title="HabitCore Nudge Engine")
engine = create_engine(settings.DATABASE_URL)
ctx_manager = ContextManager(host=os.environ.get("REDIS_HOST", "localhost"))

def handle_pattern(pattern):
    user_id = pattern["user_id"]
    p_type = pattern["pattern_type"]
    
    # 1. Get Real-time Context (Redis)
    context = ctx_manager.get_full_context(user_id)
    
    # 2. Cooldown check (Redis-based)
    if context.get("is_on_cooldown"):
        logger.info(f"Skipping nudge for {user_id} (cooldown active in Redis)")
        return

    # 3. Decision Logic
    score = score_nudge(pattern, context)
    if score < 0.5:
        logger.info(f"Nudge score too low ({score}) for {user_id}")
        return
        
    # 4. Generation
    nudge_data = generate_nudge_content(p_type, context)
    
    # 5. Delivery (DB + Simulation)
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO nudges (id, user_id, type, trigger_pattern, message, priority, metadata_json, created_at)
                VALUES (:id, :u, :t, :tp, :m, :p, :meta, :ca)
            """),
            {
                "id": str(datetime.now().timestamp()), # Simple ID for mock
                "u": user_id,
                "t": nudge_data["type"],
                "tp": p_type,
                "m": nudge_data["message"],
                "p": nudge_data["priority"],
                "meta": json.dumps({"score": score, "confidence": pattern.get("confidence")}),
                "ca": datetime.now(timezone.utc)
            }
        )
        conn.commit()
        
    logger.info(f"!!! [NUDGE DELIVERED] to {user_id}: {nudge_data['message']} !!!")

def consume_patterns():
    logger.info("Nudge Engine Consumer starting...")
    consumer = KafkaConsumer(
        "patterns_stream",
        bootstrap_servers="localhost:9092",
        group_id="nudge-engine-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    for msg in consumer:
        try:
            handle_pattern(msg.value)
        except Exception as e:
            logger.error(f"Error handling pattern: {e}")

@app.on_event("startup")
def start_worker():
    thread = threading.Thread(target=consume_patterns, daemon=True)
    thread.start()

@app.get("/health")
def health():
    return {"status": "ok"}
