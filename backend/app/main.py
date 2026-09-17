from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.session import engine, Base
from backend.app.api.lookups import router as lookups_router
from backend.app.api.gifts import router as gifts_router
from backend.app.api.experiences import router as experiences_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.analytics import router as analytics_router
from backend.app.db.analytics_db import initialize_analytics_views
from backend.app.db.session import SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist on startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        initialize_analytics_views(db)
    finally:
        db.close()
    yield

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Community-Driven Gift Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for local Streamlit / Frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(lookups_router, prefix=settings.API_V1_STR)
app.include_router(gifts_router, prefix=settings.API_V1_STR)
app.include_router(experiences_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

import os
from fastapi.staticfiles import StaticFiles

# Mount static frontend application
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
