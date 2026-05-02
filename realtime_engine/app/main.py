from fastapi import FastAPI
from app.schemas import EventInput, ContextResponse, NudgeResponse
from app.context_service import update_user_context, get_user_context
from app.nudge_engine import generate_nudge

app = FastAPI(title="HabitCore Real-Time Engine")


@app.post("/event")
def ingest_event(event: EventInput):
    update_user_context(event.user_id, event.event_type, event.value)
    return {"status": "event processed"}


@app.get("/context/{user_id}", response_model=ContextResponse)
def fetch_context(user_id: str):
    return get_user_context(user_id)


@app.get("/nudge/{user_id}", response_model=NudgeResponse)
def get_nudge(user_id: str):
    context = get_user_context(user_id)
    nudge = generate_nudge(context)
    return nudge
