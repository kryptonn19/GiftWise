import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

test_db_url = "sqlite:///./test_analytics_suite.db"
engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from backend.app.main import app
from backend.app.db.session import Base, get_db
from backend.app.db.analytics_db import initialize_analytics_views
from backend.scripts.generate_synthetic_data import generate_synthetic_dataset

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        generate_synthetic_dataset(db, num_experiences=50)
        initialize_analytics_views(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    app.dependency_overrides.clear()
    if os.path.exists("./test_analytics_suite.db"):
        os.remove("./test_analytics_suite.db")

@pytest.fixture(scope="module")
def api_client(setup_test_db):
    with TestClient(app) as client:
        yield client

ANALYTICS_VIEWS = [
    "view_rating_by_occasion_relationship",
    "view_rating_by_budget_bucket",
    "view_giver_vs_recipient_satisfaction_gap",
    "view_personalized_vs_non_personalized",
    "view_failure_reason_frequency",
    "view_sample_size_vs_rating_variance",
    "view_reliable_vs_polarizing_gifts"
]

ANALYTICS_ENDPOINTS = [
    "/api/analytics/rating-by-occasion-relationship",
    "/api/analytics/rating-by-budget-bucket",
    "/api/analytics/giver-vs-recipient-gap",
    "/api/analytics/personalized-vs-non-personalized",
    "/api/analytics/failure-reasons",
    "/api/analytics/sample-size-vs-variance",
    "/api/analytics/reliable-vs-polarizing"
]

@pytest.mark.parametrize("view_name", ANALYTICS_VIEWS)
def test_sql_views_query_direct(view_name):
    """Verifies that all 7 SQL analytics views exist and return results directly via SQL query."""
    db = TestingSessionLocal()
    try:
        result = db.execute(text(f"SELECT * FROM {view_name}")).mappings().all()
        assert result is not None
        assert len(result) >= 0
    finally:
        db.close()

@pytest.mark.parametrize("endpoint", ANALYTICS_ENDPOINTS)
def test_analytics_api_endpoints(api_client, endpoint):
    """Verifies that all 7 FastAPI analytics endpoints respond with HTTP 200 and a JSON list."""
    response = api_client.get(endpoint)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
