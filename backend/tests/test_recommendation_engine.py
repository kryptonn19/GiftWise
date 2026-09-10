import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_rec_engine.db"

from backend.app.db.session import Base
from backend.app.models.db_models import (
    User, Gift, Occasion, Relationship, Interest, Personality,
    RecipientProfile, GiftingExperience, FailureReason, FailureReasonCode, ConfidenceLevel
)
from backend.app.engine.recommendation import RecommendationEngine

engine = create_engine("sqlite:///./test_rec_engine.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create lookups
    occ = Occasion(name="Birthday")
    rel = Relationship(name="Partner")
    interest = Interest(name="Coffee")
    personality = Personality(name="Practical")
    db.add_all([occ, rel, interest, personality])
    db.commit()

    # Create Gifts
    g1 = Gift(name="Gift A", category="Cat1", typical_price_min=50, typical_price_max=100, is_personalized=True)
    g2 = Gift(name="Gift B", category="Cat2", typical_price_min=40, typical_price_max=80, is_experience=True)
    g3 = Gift(name="Gift C", category="Cat3", typical_price_min=30, typical_price_max=60)
    db.add_all([g1, g2, g3])
    db.commit()

    # Create Recipient Profile
    prof = RecipientProfile(age_range="25-34")
    prof.interests = [interest]
    prof.personalities = [personality]
    db.add(prof)
    db.commit()

    # Add 10 experiences for Gift A with rating 10
    for _ in range(10):
        exp = GiftingExperience(
            gift_id=g1.id, occasion_id=occ.id, relationship_id=rel.id, recipient_profile_id=prof.id,
            budget_actual=75.0, giver_rating=10, recipient_rating=10, would_recommend=True,
            is_synthetic=True
        )
        db.add(exp)

    # Add 1 experience for Gift B with rating 10 (test prior weight pull)
    exp_b = GiftingExperience(
        gift_id=g2.id, occasion_id=occ.id, relationship_id=rel.id, recipient_profile_id=prof.id,
        budget_actual=60.0, giver_rating=10, recipient_rating=10, would_recommend=True,
        is_synthetic=True
    )
    db.add(exp_b)

    # Add 5 experiences for Gift C with rating 5 + failure reasons
    for _ in range(5):
        exp_c = GiftingExperience(
            gift_id=g3.id, occasion_id=occ.id, relationship_id=rel.id, recipient_profile_id=prof.id,
            budget_actual=45.0, giver_rating=5, recipient_rating=4, would_recommend=False,
            is_synthetic=True
        )
        db.add(exp_c)
        db.flush()
        fr = FailureReason(gifting_experience_id=exp_c.id, reason_code=FailureReasonCode.POOR_QUALITY)
        db.add(fr)

    db.commit()
    yield
    db.close()
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_rec_engine.db"):
        os.remove("./test_rec_engine.db")

def test_bayesian_scoring_and_confidence():
    db = TestingSessionLocal()
    rec_engine = RecommendationEngine(db=db, prior_weight_c=10.0)
    
    results = rec_engine.get_recommendations(
        relationship_id=1, occasion_id=1, budget_min=30, budget_max=100
    )

    assert results["total_candidates_found"] == 3
    recs = results["recommendations"]

    # Gift A (n=10, all 10s) vs Gift B (n=1, single 10)
    gift_a = next(r for r in recs if r["gift_name"] == "Gift A")
    gift_b = next(r for r in recs if r["gift_name"] == "Gift B")
    gift_c = next(r for r in recs if r["gift_name"] == "Gift C")

    assert gift_a["sample_size_n"] == 10
    assert gift_a["confidence_level"] == ConfidenceLevel.Medium
    assert gift_b["sample_size_n"] == 1
    assert gift_b["confidence_level"] == ConfidenceLevel.Low

    # Bayesian score of A (n=10) should be higher than B (n=1) because C=10 pulls single sample towards global mean
    assert gift_a["bayesian_score"] > gift_b["bayesian_score"]

    # Gift C should have top failure reason detected (>15% failure rate)
    assert gift_c["failure_rate"] == 1.0
    assert gift_c["top_failure_reason"] is not None
    assert "Poor Quality" in gift_c["top_failure_reason"]

    db.close()

def test_cold_start_fallback():
    db = TestingSessionLocal()
    rec_engine = RecommendationEngine(db=db, prior_weight_c=10.0)

    # Search with impossible budget range ($1000-$2000)
    results = rec_engine.get_recommendations(
        relationship_id=1, occasion_id=1, budget_min=1000, budget_max=2000
    )

    # Should trigger fallback
    assert results["cold_start_fallback_applied"] is True
    assert "Relaxed budget" in results["fallback_notes"]
    assert len(results["recommendations"]) > 0

    db.close()
