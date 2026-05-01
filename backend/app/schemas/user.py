from pydantic import BaseModel
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

    class Config:
        from_attributes = True
