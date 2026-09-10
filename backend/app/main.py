from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.session import engine, Base
from backend.app.api.lookups import router as lookups_router
from backend.app.api.gifts import router as gifts_router
from backend.app.api.experiences import router as experiences_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist on startup
    Base.metadata.create_all(bind=engine)
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

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
