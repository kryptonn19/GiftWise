from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/rating-by-occasion-relationship", response_model=List[Dict[str, Any]])
def get_rating_by_occasion_relationship(db: Session = Depends(get_db)):
    """Returns average recipient and giver ratings broken down by occasion and relationship."""
    result = db.execute(text("SELECT * FROM view_rating_by_occasion_relationship")).mappings().all()
    return [dict(row) for row in result]

@router.get("/rating-by-budget-bucket", response_model=List[Dict[str, Any]])
def get_rating_by_budget_bucket(db: Session = Depends(get_db)):
    """Returns rating metrics and giver-recipient satisfaction gap grouped into budget buckets."""
    result = db.execute(text("SELECT * FROM view_rating_by_budget_bucket")).mappings().all()
    return [dict(row) for row in result]

@router.get("/giver-vs-recipient-gap", response_model=List[Dict[str, Any]])
def get_giver_vs_recipient_satisfaction_gap(db: Session = Depends(get_db)):
    """Returns headline satisfaction gap breakdown comparing giver rating to recipient rating."""
    result = db.execute(text("SELECT * FROM view_giver_vs_recipient_satisfaction_gap")).mappings().all()
    return [dict(row) for row in result]

@router.get("/personalized-vs-non-personalized", response_model=List[Dict[str, Any]])
def get_personalized_vs_non_personalized(db: Session = Depends(get_db)):
    """Compares personalized vs non-personalized gift performance and recommend rate by relationship type."""
    result = db.execute(text("SELECT * FROM view_personalized_vs_non_personalized")).mappings().all()
    return [dict(row) for row in result]

@router.get("/failure-reasons", response_model=List[Dict[str, Any]])
def get_failure_reason_frequency(db: Session = Depends(get_db)):
    """Returns failure reason frequency overall and grouped by gift category."""
    result = db.execute(text("SELECT * FROM view_failure_reason_frequency")).mappings().all()
    return [dict(row) for row in result]

@router.get("/sample-size-vs-variance", response_model=List[Dict[str, Any]])
def get_sample_size_vs_rating_variance(db: Session = Depends(get_db)):
    """Returns sample size vs rating variance metrics per gift for confidence scoring validation."""
    result = db.execute(text("SELECT * FROM view_sample_size_vs_rating_variance")).mappings().all()
    return [dict(row) for row in result]

@router.get("/reliable-vs-polarizing", response_model=List[Dict[str, Any]])
def get_reliable_vs_polarizing_gifts(db: Session = Depends(get_db)):
    """Classifies gifts into Reliable Winners, Polarizing, Consistently Low, or Moderate performance."""
    result = db.execute(text("SELECT * FROM view_reliable_vs_polarizing_gifts")).mappings().all()
    return [dict(row) for row in result]
