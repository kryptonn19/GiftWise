import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GiftWise"
    API_V1_STR: str = "/api"
    
    # Database setting - defaults to local postgresql or sqlite fallback for test runs
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/giftwise"
    )

    class Config:
        case_sensitive = True

settings = Settings()
