from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, habits, users, payments, referrals, admin, preferences, shop, analytics
from app.db.session import engine
from app.db.base import Base
from app.scheduler import scheduler
from app.services.websocket_service import manager

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    scheduler.start()

app.include_router(auth.router, prefix="/auth")
app.include_router(habits.router, prefix="/habits")
app.include_router(users.router, prefix="/users")
app.include_router(payments.router, prefix="/payments")
app.include_router(referrals.router, prefix="/referrals")
app.include_router(admin.router, prefix="/admin")
app.include_router(preferences.router, prefix="/preferences")
app.include_router(shop.router, prefix="/shop")
app.include_router(analytics.router, prefix="/analytics")

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
