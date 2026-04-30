from pydantic import BaseModel

class HabitCreate(BaseModel):
    title: str
