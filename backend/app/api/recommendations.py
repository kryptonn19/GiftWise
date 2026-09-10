from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.engine.recommendation import RecommendationEngine
from backend.app.models.db_models import (
    RecommendationQuery, RecommendationResult, Interest, Personality
)
from backend.app.schemas.recommendation import (
    RecommendationQueryCreate, RecommendationResponse
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.post("", response_model=RecommendationResponse)
def get_recommendations(
    query_in: RecommendationQueryCreate,
    db: Session = Depends(get_db)
):
    # 1. Log query
    rec_query = RecommendationQuery(
        relationship_id=query_in.relationship_id,
        occasion_id=query_in.occasion_id,
        budget_min=query_in.budget_min,
        budget_max=query_in.budget_max
    )
    if query_in.interest_ids:
        interests = db.query(Interest).filter(Interest.id.in_(query_in.interest_ids)).all()
        rec_query.interests = interests
    if query_in.personality_ids:
        personalities = db.query(Personality).filter(Personality.id.in_(query_in.personality_ids)).all()
        rec_query.personalities = personalities

    db.add(rec_query)
    db.flush()

    # 2. Run Recommendation Engine
    engine = RecommendationEngine(db=db)
    results_data = engine.get_recommendations(
        relationship_id=query_in.relationship_id,
        occasion_id=query_in.occasion_id,
        budget_min=query_in.budget_min,
        budget_max=query_in.budget_max,
        interest_ids=query_in.interest_ids,
        personality_ids=query_in.personality_ids,
        top_k=query_in.top_k
    )

    # 3. Log results into database
    for rank, item in enumerate(results_data["recommendations"], start=1):
        res_row = RecommendationResult(
            query_id=rec_query.id,
            gift_id=item["gift_id"],
            score=item["bayesian_score"],
            confidence_level=item["confidence_level"],
            rank=rank
        )
        db.add(res_row)

    db.commit()

    return RecommendationResponse(
        query_id=rec_query.id,
        query_summary=results_data["query_summary"],
        cold_start_fallback_applied=results_data["cold_start_fallback_applied"],
        fallback_notes=results_data["fallback_notes"],
        total_candidates_found=results_data["total_candidates_found"],
        recommendations=results_data["recommendations"]
    )
