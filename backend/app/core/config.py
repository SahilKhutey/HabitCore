import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "HabitHero"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    APP_ENV: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./habithero.db"
    
    # Auth
    SECRET_KEY: str = "supersecretkey"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Monetization
    FREE_HABIT_LIMIT: int = 3
    OPENAI_API_KEY: str = "" # Add your key in .env

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), f".env.{os.getenv('APP_ENV', 'development')}"),
        env_file_encoding='utf-8',
        case_sensitive=True
    )

settings = Settings()
