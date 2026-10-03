import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "GiftWise"
    API_V1_STR: str = "/api"
    
    # Auto-detect local database URL from environment or fallback to local SQLite DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./giftwise.db"
    )

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()

