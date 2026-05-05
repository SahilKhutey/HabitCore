"""
Nudge Engine — Real-time behavioral intervention service.
"""
import uuid
import json
import threading
import logging
import os
import time
import sys
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import create_engine, text

# Adjust path for app imports to pull from backend if needed
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

try:
    if BACKEND_PATH not in sys.path:
        sys.path.insert(0, BACKEND_PATH)
    from app.core.config import settings
    from app.utils.priority import PriorityQueue
    from app.services.context_store.manager import ContextManager
except ImportError:
    # Fallback or error if backend is missing
    logging.error("Backend components not found. Ensure backend directory is correctly linked.")
    raise

# Local imports from the nudge_engine/app directory
from .decision import score_nudge
from .templates import generate_nudge_content
from .observability import setup_observability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcode DB path for cross-service consistency during stress test
DB_PATH = os.path.abspath(os.path.join(BACKEND_PATH, 'habithero.db'))
DATABASE_URL = f"sqlite:///{DB_PATH}"

logger.info(f"Nudge Engine using DATABASE_URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)
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
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except ValueError:
                    created_at = datetime.strptime(created_at.split('.')[0], "%Y-%m-%d %H:%M:%S")
            
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            journey_day = (datetime.now(timezone.utc) - created_at).days
    
    context["journey_day"] = journey_day
    
    # 1.1 Degraded Mode Check (Self-Healing)
    system_mode = ctx_manager.r.get("system_mode")
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
        
    # 6. Real-time Broadcast (Redis Pub/Sub)
    try:
        nudge_payload = {
            "id": str(uuid.uuid4()), # Reuse or new
            "user_id": user_id,
            "type": nudge_data["type"],
            "message": nudge_data["message"],
            "priority": nudge_data["priority"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        ctx_manager.r.publish(f"nudges:{user_id}", json.dumps(nudge_payload))
        logger.info(f"Broadcasted nudge to Redis channel nudges:{user_id}")
    except Exception as e:
        logger.error(f"Failed to broadcast nudge: {e}")
        
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

