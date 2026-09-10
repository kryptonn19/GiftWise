import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_api.db"

from backend.app.main import app
from backend.app.db.session import Base, get_db
from backend.scripts.seed_scaffold import seed_scaffold

engine = create_engine("sqlite:///./test_api.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_scaffold(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_api.db"):
        os.remove("./test_api.db")

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_lookups():
    response = client.get("/api/lookups")
    assert response.status_code == 200
    data = response.json()
    assert len(data["occasions"]) > 0
    assert len(data["relationships"]) > 0
    assert len(data["interests"]) > 0
    assert len(data["personalities"]) > 0

def test_create_and_get_gift():
    gift_payload = {
        "name": "Smart Coffee Warmer",
        "category": "Home & Kitchen",
        "description": "Temperature-controlled beverage plate.",
        "typical_price_min": 20.0,
        "typical_price_max": 40.0,
        "is_personalized": False,
        "is_experience": False,
        "is_handmade": False
    }
    create_resp = client.post("/api/gifts", json=gift_payload)
    assert create_resp.status_code == 201
    gift_data = create_resp.json()
    assert gift_data["name"] == "Smart Coffee Warmer"
    assert "id" in gift_data

    get_resp = client.get(f"/api/gifts/{gift_data['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == gift_data["id"]

def test_create_experience():
    # Fetch lookups & gifts first
    lookups = client.get("/api/lookups").json()
    gifts = client.get("/api/gifts").json()

    occ_id = lookups["occasions"][0]["id"]
    rel_id = lookups["relationships"][0]["id"]
    gift_id = gifts[0]["id"]

    exp_payload = {
        "gift_id": gift_id,
        "occasion_id": occ_id,
        "relationship_id": rel_id,
        "recipient_profile": {
            "age_range": "25-34",
            "interest_ids": [lookups["interests"][0]["id"]],
            "personality_ids": [lookups["personalities"][0]["id"]]
        },
        "budget_actual": 35.0,
        "giver_rating": 9,
        "recipient_rating": 10,
        "would_recommend": True,
        "review_text": "Great gift overall!",
        "reaction_text": "Loved it!",
        "failure_reasons": []
    }

    response = client.post("/api/experiences", json=exp_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["gift_id"] == gift_id
    assert data["recipient_rating"] == 10
    assert data["is_synthetic"] is False

    # List experiences
    list_resp = client.get("/api/experiences")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1
