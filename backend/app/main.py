from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, habits, users, payments, referrals, admin, preferences, shop, analytics, gamification, psychological, avatar_routes
from app.db.session import engine
from app.db.declarative import Base
import app.db.base
from app.scheduler import scheduler
from app.services.websocket_service import manager

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:8082",
        "http://localhost:5173",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:8082",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.services.nudge_engine import NudgeEngine
from app.db.session import SessionLocal
from app.api.routes.seed_shop import seed_shop_items

@app.on_event("startup")
def startup_event():
    scheduler.start()
    
    # Seed shop items if empty
    db = SessionLocal()
    try:
        seed_shop_items(db)
    finally:
        db.close()
    
    # Nudge Engine: Run every 6 hours to identify sliding users
    @scheduler.scheduled_job("interval", hours=6)
    def run_nudges():
        db = SessionLocal()
        try:
            count = NudgeEngine.process_nudges(db)
            print(f"Nudge Engine: Sent {count} identity nudges.")
        finally:
            db.close()


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
    return {"message": "HabitHero API running"}
