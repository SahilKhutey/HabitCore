from pydantic import BaseModel

class EventInput(BaseModel):
    user_id: str
    event_type: str
    value: float = 0

class ContextResponse(BaseModel):
    user_id: str
    focus_score: float
    distraction_minutes: int
    last_event: str

class NudgeResponse(BaseModel):
    message: str
    priority: int
