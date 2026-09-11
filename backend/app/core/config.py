import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GiftWise"
    API_V1_STR: str = "/api"
    
    # Auto-detect local macOS user for postgresql or fallback to sqlite
    DEFAULT_USER: str = os.getenv("USER", "postgres")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"postgresql://{DEFAULT_USER}@localhost:5432/giftwise"
    )

    class Config:
        case_sensitive = True

settings = Settings()
