from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.session import get_db
from backend.app.models.db_models import (
    GiftingExperience, RecipientProfile, FailureReason, Gift,
    Occasion, Relationship, Interest, Personality
)
from backend.app.schemas.experience import (
    ExperienceCreate, ExperienceResponse, RecipientProfileResponse, FailureReasonResponse, ReviewNLPInsightResponse
)
from backend.app.nlp.pipeline import process_experience_nlp

router = APIRouter(prefix="/experiences", tags=["experiences"])

def _format_experience_response(exp: GiftingExperience) -> ExperienceResponse:
    interests = [i.name for i in exp.recipient_profile.interests] if exp.recipient_profile else []
    personalities = [p.name for p in exp.recipient_profile.personalities] if exp.recipient_profile else []

    profile_resp = RecipientProfileResponse(
        id=exp.recipient_profile.id,
        age_range=exp.recipient_profile.age_range,
        interests=interests,
        personalities=personalities
    )

    failure_reasons_resp = [
        FailureReasonResponse(
            id=fr.id,
            reason_code=fr.reason_code,
            free_text=fr.free_text
        ) for fr in exp.failure_reasons
    ]

    nlp_resp = None
    if exp.nlp_insight:
        nlp_resp = ReviewNLPInsightResponse(
            id=exp.nlp_insight.id,
            sentiment_score=float(exp.nlp_insight.sentiment_score) if exp.nlp_insight.sentiment_score is not None else None,
            extracted_themes=exp.nlp_insight.extracted_themes or [],
            extracted_positive_reasons=exp.nlp_insight.extracted_positive_reasons or [],
            extracted_negative_reasons=exp.nlp_insight.extracted_negative_reasons or []
        )

    return ExperienceResponse(
        id=exp.id,
        user_id=exp.user_id,
        gift_id=exp.gift_id,
        gift_name=exp.gift.name if exp.gift else "Unknown Gift",
        gift_category=exp.gift.category if exp.gift else "Uncategorized",
        occasion_id=exp.occasion_id,
        occasion_name=exp.occasion.name if exp.occasion else "Unknown Occasion",
        relationship_id=exp.relationship_id,
        relationship_name=exp.relationship_obj.name if exp.relationship_obj else "Unknown Relationship",
        recipient_profile=profile_resp,
        budget_actual=float(exp.budget_actual),
        giver_rating=exp.giver_rating,
        recipient_rating=exp.recipient_rating,
        would_recommend=exp.would_recommend,
        review_text=exp.review_text,
        reaction_text=exp.reaction_text,
        is_synthetic=exp.is_synthetic,
        created_at=exp.created_at,
        failure_reasons=failure_reasons_resp,
        nlp_insight=nlp_resp
    )

@router.get("", response_model=List[ExperienceResponse])
def list_experiences(
    gift_id: Optional[str] = None,
    occasion_id: Optional[int] = None,
    relationship_id: Optional[int] = None,
    is_synthetic: Optional[bool] = None,
    user_id: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(GiftingExperience)
    if gift_id:
        query = query.filter(GiftingExperience.gift_id == gift_id)
    if occasion_id:
        query = query.filter(GiftingExperience.occasion_id == occasion_id)
    if relationship_id:
        query = query.filter(GiftingExperience.relationship_id == relationship_id)
    if is_synthetic is not None:
        query = query.filter(GiftingExperience.is_synthetic == is_synthetic)
    if user_id:
        query = query.filter(GiftingExperience.user_id == user_id)

    experiences = query.order_by(GiftingExperience.created_at.desc()).offset(offset).limit(limit).all()
    return [_format_experience_response(e) for e in experiences]

@router.post("", response_model=ExperienceResponse, status_code=201)
def create_experience(exp_in: ExperienceCreate, db: Session = Depends(get_db)):
    gift = db.query(Gift).filter(Gift.id == exp_in.gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    occasion = db.query(Occasion).filter(Occasion.id == exp_in.occasion_id).first()
    if not occasion:
        raise HTTPException(status_code=404, detail="Occasion not found")

    relationship_obj = db.query(Relationship).filter(Relationship.id == exp_in.relationship_id).first()
    if not relationship_obj:
        raise HTTPException(status_code=404, detail="Relationship not found")

    profile = RecipientProfile(age_range=exp_in.recipient_profile.age_range)
    if exp_in.recipient_profile.interest_ids:
        interests = db.query(Interest).filter(Interest.id.in_(exp_in.recipient_profile.interest_ids)).all()
        profile.interests = interests

    if exp_in.recipient_profile.personality_ids:
        personalities = db.query(Personality).filter(Personality.id.in_(exp_in.recipient_profile.personality_ids)).all()
        profile.personalities = personalities

    db.add(profile)
    db.flush()

    exp = GiftingExperience(
        gift_id=gift.id,
        occasion_id=occasion.id,
        relationship_id=relationship_obj.id,
        recipient_profile_id=profile.id,
        budget_actual=exp_in.budget_actual,
        giver_rating=exp_in.giver_rating,
        recipient_rating=exp_in.recipient_rating,
        would_recommend=exp_in.would_recommend,
        review_text=exp_in.review_text,
        reaction_text=exp_in.reaction_text,
        is_synthetic=False
    )
    db.add(exp)
    db.flush()

    if exp_in.failure_reasons:
        for fr_in in exp_in.failure_reasons:
            fr = FailureReason(
                gifting_experience_id=exp.id,
                reason_code=fr_in.reason_code,
                free_text=fr_in.free_text
            )
            db.add(fr)

    db.commit()
    
    # Process NLP extraction automatically
    process_experience_nlp(db, exp.id)

    db.refresh(exp)
    return _format_experience_response(exp)

@router.get("/{experience_id}", response_model=ExperienceResponse)
def get_experience(experience_id: str, db: Session = Depends(get_db)):
    exp = db.query(GiftingExperience).filter(GiftingExperience.id == experience_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Gifting experience not found")
    return _format_experience_response(exp)
