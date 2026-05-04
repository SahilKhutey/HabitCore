"""
Nudge Engine — Real-time behavioral intervention service.
"""
import uuid
import json
import threading
import logging
import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
from kafka import KafkaConsumer
from sqlalchemy import create_engine, text

# Adjust path for app imports
try:
    from app.core.config import settings
    from app.services.nudge_engine.decision import score_nudge
    from app.services.nudge_engine.templates import generate_nudge_content
    from app.services.context_store.manager import ContextManager
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
    from app.core.config import settings
    from app.services.nudge_engine.decision import score_nudge
    from app.services.nudge_engine.templates import generate_nudge_content
    from app.services.context_store.manager import ContextManager

from app.observability import setup_observability
from app.utils.priority import PriorityQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)
ctx_manager = ContextManager(host=os.environ.get("REDIS_HOST", "localhost"))

def handle_pattern(pattern):
    user_id = pattern.get("user_id")
    p_type = pattern.get("pattern_type") or pattern.get("event_type")
    
    if not user_id or not p_type:
        logger.warning(f"Incomplete event data received by nudge engine: {pattern}")
        return

    # 1. Get Real-time Context (Redis)
    context = ctx_manager.get_full_context(user_id)
    
    # 1.0 Get Journey Context (DB)
    journey_day = 0
    with engine.connect() as conn:
        res = conn.execute(
            text("SELECT created_at FROM users WHERE id = :u"),
            {"u": user_id}
        ).fetchone()
        if res:
            created_at = res[0]
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            journey_day = (datetime.now(timezone.utc) - created_at).days
    
    context["journey_day"] = journey_day
    
    # 1.1 Degraded Mode Check (Self-Healing)
    system_mode = ctx_manager.redis.get("system_mode")
    if system_mode == "degraded":
        # In degraded mode, only process high-priority patterns (e.g. pattern_type == 'burnout_risk')
        if p_type not in ["burnout_risk", "critical_deviation"]:
            logger.warning(f"DEGRADED MODE: Skipping non-critical nudge for {user_id} (Type: {p_type})")
            return
    
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
                "id": str(uuid.uuid4()),
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
    logger.info("Nudge Engine Priority Consumer starting...")
    pq = PriorityQueue(redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"))
    
    while True:
        try:
            item = pq.pop("nudge")
            if item:
                logger.info(f"Popped item from PQ with priority {item['priority']:.2f}")
                handle_pattern(item["data"])
            else:
                # Small sleep to prevent busy waiting if queues are empty
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in Nudge PQ loop: {e}")
            time.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    thread = threading.Thread(target=consume_patterns, daemon=True)
    thread.start()
    yield
    # Shutdown logic

app = FastAPI(title="HabitCore Nudge Engine", lifespan=lifespan)

# Initialize Observability
setup_observability(app, service_name="nudge_engine")

@app.get("/health")
def health():
    return {"status": "ok", "consumer_thread": "running"}
