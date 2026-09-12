import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_nlp.db"

from backend.app.db.session import Base
from backend.app.models.db_models import (
    Gift, Occasion, Relationship, RecipientProfile, GiftingExperience, ReviewNLPInsight
)
from backend.app.nlp.pipeline import analyze_review_text, process_experience_nlp

engine = create_engine("sqlite:///./test_nlp.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    occ = Occasion(name="Birthday")
    rel = Relationship(name="Partner")
    db.add_all([occ, rel])
    db.commit()

    gift = Gift(name="Personalized Photo Album", category="Personalized", typical_price_min=30, typical_price_max=60, is_personalized=True)
    db.add(gift)
    db.commit()

    prof = RecipientProfile(age_range="25-34")
    db.add(prof)
    db.commit()

    exp = GiftingExperience(
        gift_id=gift.id, occasion_id=occ.id, relationship_id=rel.id, recipient_profile_id=prof.id,
        budget_actual=45.0, giver_rating=9, recipient_rating=10, would_recommend=True,
        review_text="They loved the custom engraved initials! Build quality was exceptional and very practical.",
        reaction_text="Tears of joy upon unwrapping!",
        is_synthetic=True
    )
    db.add(exp)
    db.commit()

    yield
    db.close()
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_nlp.db"):
        os.remove("./test_nlp.db")

def test_analyze_review_text():
    review = "They loved the custom engraved initials! Build quality was exceptional and very practical."
    reaction = "Tears of joy upon unwrapping!"
    
    analysis = analyze_review_text(review, reaction)

    assert analysis["sentiment_score"] > 0.5
    assert "personalization" in analysis["extracted_themes"]
    assert "quality" in analysis["extracted_themes"]
    assert "usefulness" in analysis["extracted_themes"]
    assert len(analysis["extracted_positive_reasons"]) > 0

def test_process_experience_nlp():
    db = TestingSessionLocal()
    exp = db.query(GiftingExperience).first()
    assert exp is not None

    insight = process_experience_nlp(db, exp.id)
    assert insight is not None
    assert insight.gifting_experience_id == exp.id
    assert insight.sentiment_score > 0.5
    assert "personalization" in insight.extracted_themes

    db.close()
