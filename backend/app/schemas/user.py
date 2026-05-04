from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserSchema(BaseModel):
    id: str
    email: str
    xp: int = 0
    level: int = 1
    is_premium: bool = False
    identity_goal: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
