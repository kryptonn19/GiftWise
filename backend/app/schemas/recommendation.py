from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from backend.app.models.db_models import ConfidenceLevel

class RecommendationQueryCreate(BaseModel):
    relationship_id: int
    occasion_id: int
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    interest_ids: List[int] = []
    personality_ids: List[int] = []
    top_k: int = Field(10, ge=1, le=50)

class MatchingExperienceSample(BaseModel):
    giver_rating: int
    recipient_rating: int
    review_text: Optional[str] = None
    reaction_text: Optional[str] = None
    is_synthetic: bool

class RecommendationItem(BaseModel):
    gift_id: str
    gift_name: str
    gift_category: str
    description: Optional[str] = None
    typical_price_min: float
    typical_price_max: float
    is_personalized: bool
    is_experience: bool
    is_handmade: bool
    bayesian_score: float
    raw_avg_rating: float
    sample_size_n: int
    confidence_level: ConfidenceLevel
    contributing_factors: List[str]
    failure_rate: float
    top_failure_reason: Optional[str] = None
    matching_experiences_sample: List[MatchingExperienceSample] = []

    model_config = ConfigDict(from_attributes=True)

class RecommendationQuerySummary(BaseModel):
    relationship_id: int
    occasion_id: int
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    interest_ids: List[int] = []
    personality_ids: List[int] = []
    prior_weight_C: float
    global_mean_m: float

class RecommendationResponse(BaseModel):
    query_id: str
    query_summary: RecommendationQuerySummary
    cold_start_fallback_applied: bool
    fallback_notes: Optional[str] = None
    total_candidates_found: int
    recommendations: List[RecommendationItem]
