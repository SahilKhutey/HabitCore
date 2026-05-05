import sys
import os
from contextlib import asynccontextmanager

# Add root project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, habits, users, payments, referrals, admin, preferences, shop, analytics, gamification, psychological, avatar_routes, identity_dashboard
from app.services.behavioral_insight_engine.routes import router as insights_router
from app.services.cognitive_engine.routes import router as cognitive_router
from app.services.cognitive_training_system.routes import router as cbts_router
from app.services.behavioral_feedback_engine.routes import router as bfe_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.intelligence_v2 import router as intelligence_v2_router
from app.services.reflection_engine.routes import router as reflection_router

from app.db.session import engine, SessionLocal
from app.db.declarative import Base
import app.db.base
from app.scheduler import scheduler
from app.services.websocket_service import manager
from app.services.nudge_engine import NudgeEngine
from app.api.routes.seed_shop import seed_shop_items
from app.observability import setup_observability
import redis
import time
from fastapi import Request
import logging

logger = logging.getLogger("backend")

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    scheduler.start()
    
    # Seed shop items if empty
    db = SessionLocal()
    try:
        seed_shop_items(db)
    finally:
        db.close()
    
    # Nudge Engine: Run every 6 hours
    @scheduler.scheduled_job("interval", hours=6)
    def run_nudges():
        db = SessionLocal()
        try:
            count = NudgeEngine.process_nudges(db)
            print(f"Nudge Engine: Sent {count} identity nudges.")
        finally:
            db.close()
            
    yield
    # Shutdown logic
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for easier cross-platform development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Observability
setup_observability(app, service_name="backend")

# Redis client for self-healing status
redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

# Throttling Middleware
@app.middleware("http")
async def throttling_middleware(request: Request, call_next):
    if request.url.path == "/habits/events":
        if redis_client.get("ingestion_rate_limit") == "enabled":
            logger.warning("THROTTLING ACTIVE: Slowing down ingestion...")
            time.sleep(0.5) # Add 500ms delay to demonstration backpressure
            
    response = await call_next(request)
    return response

# Routers
app.include_router(auth.router, prefix="/auth")
app.include_router(habits.router, prefix="/habits")
app.include_router(users.router, prefix="/users")
app.include_router(payments.router, prefix="/payments")
app.include_router(referrals.router, prefix="/referrals")
app.include_router(admin.router, prefix="/admin")
app.include_router(preferences.router, prefix="/preferences")
app.include_router(shop.router, prefix="/shop")
app.include_router(analytics.router, prefix="/analytics")
app.include_router(gamification.router, prefix="/gamification")
app.include_router(psychological.router, prefix="/psychological")
app.include_router(avatar_routes.router, prefix="/api/avatar", tags=["avatar"])
app.include_router(insights_router, prefix="/insights", tags=["behavioral-insights"])
app.include_router(cognitive_router, prefix="/cognitive", tags=["cognitive-engine"])
app.include_router(cbts_router, prefix="/cognitive-training", tags=["cognitive-training-system"])
app.include_router(bfe_router, prefix="/bfe", tags=["behavioral-feedback-engine"])
app.include_router(intelligence_router, prefix="/intelligence", tags=["behavioral-intelligence"])
app.include_router(intelligence_v2_router, prefix="/intelligence/v2", tags=["behavioral-intelligence-v2"])
app.include_router(reflection_router, prefix="/reflection", tags=["reflection-engine"])
app.include_router(identity_dashboard.router, prefix="/identity", tags=["identity-dashboard"])
from app.api.routes import notifications
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)

@app.get("/")
def root():
    return {"message": "HabitCore API running", "observability": "enabled"}
