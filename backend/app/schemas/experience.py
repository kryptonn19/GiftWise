from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from backend.app.models.db_models import FailureReasonCode

class FailureReasonCreate(BaseModel):
    reason_code: FailureReasonCode
    free_text: Optional[str] = None

class FailureReasonResponse(BaseModel):
    id: str
    reason_code: FailureReasonCode
    free_text: Optional[str] = None

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = ConfigDict(from_attributes=True)

class ReviewNLPInsightResponse(BaseModel):
    id: str
    sentiment_score: Optional[float] = None
    extracted_themes: Optional[List[str]] = []
    extracted_positive_reasons: Optional[List[str]] = []
    extracted_negative_reasons: Optional[List[str]] = []

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = ConfigDict(from_attributes=True)

class RecipientProfileCreate(BaseModel):
    age_range: str
    interest_ids: List[int] = []
    personality_ids: List[int] = []

class RecipientProfileResponse(BaseModel):
    id: str
    age_range: str
    interests: List[str] = []
    personalities: List[str] = []

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = ConfigDict(from_attributes=True)

class ExperienceCreate(BaseModel):
    gift_id: str
    occasion_id: int
    relationship_id: int
    recipient_profile: RecipientProfileCreate
    budget_actual: float = Field(..., ge=0)
    giver_rating: int = Field(..., ge=1, le=10)
    recipient_rating: int = Field(..., ge=1, le=10)
    would_recommend: bool
    review_text: Optional[str] = None
    reaction_text: Optional[str] = None
    failure_reasons: Optional[List[FailureReasonCreate]] = []

class ExperienceResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    gift_id: str
    gift_name: str
    gift_category: str
    occasion_id: int
    occasion_name: str
    relationship_id: int
    relationship_name: str
    recipient_profile: RecipientProfileResponse
    budget_actual: float
    giver_rating: int
    recipient_rating: int
    would_recommend: bool
    review_text: Optional[str] = None
    reaction_text: Optional[str] = None
    is_synthetic: bool
    created_at: datetime
    failure_reasons: List[FailureReasonResponse] = []
    nlp_insight: Optional[ReviewNLPInsightResponse] = None

    @field_validator("id", "user_id", "gift_id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = ConfigDict(from_attributes=True)
