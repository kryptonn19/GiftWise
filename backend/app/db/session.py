from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings
from backend.app.db.analytics_db import register_sqlite_aggregates

# Engine configuration
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

@event.listens_for(Engine, "connect")
def _receive_connect(dbapi_connection, connection_record):
    register_sqlite_aggregates(dbapi_connection)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
