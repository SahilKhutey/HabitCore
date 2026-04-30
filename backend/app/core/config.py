from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "HabitHero"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./habithero.db"
    
    # Auth
    SECRET_KEY: str = "supersecretkey"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Monetization
    FREE_HABIT_LIMIT: int = 3

    class Config:
        case_sensitive = True

settings = Settings()
