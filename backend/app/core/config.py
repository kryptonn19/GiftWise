import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GiftWise"
    API_V1_STR: str = "/api"
    
    # Auto-detect local database URL from environment or fallback to local SQLite DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./giftwise.db"
    )

    class Config:
        case_sensitive = True

settings = Settings()
