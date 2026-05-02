from pydantic import BaseModel
from typing import List, Optional

class TextInput(BaseModel):
    user_id: str
    text: str

class SignalOutput(BaseModel):
    user_id: str
    emotion: str
    state: str
    behaviors: List[str]
    distortions: List[str]
    events: List[dict]
