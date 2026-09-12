import uuid
import enum
from datetime import datetime
from typing import List
from sqlalchemy import (
    Column, String, Text, Integer, Float, Numeric, Boolean, 
    DateTime, ForeignKey, Enum as SQLEnum, Table, JSON, ARRAY
)
from sqlalchemy.orm import relationship as sqla_relationship
from backend.app.db.session import Base

# Cross-DB type for Text Array (PostgreSQL TEXT[] with SQLite JSON fallback)
TextArrayType = ARRAY(Text).with_variant(JSON, "sqlite")

# ENUMS
class FailureReasonCode(str, enum.Enum):
    ALREADY_OWNED = "ALREADY_OWNED"
    WRONG_SIZE = "WRONG_SIZE"
    TOO_GENERIC = "TOO_GENERIC"
    POOR_QUALITY = "POOR_QUALITY"
    NOT_THEIR_STYLE = "NOT_THEIR_STYLE"
    WRONG_TIMING = "WRONG_TIMING"
    EXPRESSION_OF_DISLIKE = "EXPRESSION_OF_DISLIKE"
    OTHER = "OTHER"

class ConfidenceLevel(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"

# 1. USER MODEL
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    contribution_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    experiences = sqla_relationship("GiftingExperience", back_populates="user")
    queries = sqla_relationship("RecommendationQuery", back_populates="user")

# 2. GIFT MODEL
class Gift(Base):
    __tablename__ = "gifts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    typical_price_min = Column(Numeric(10, 2), nullable=False)
    typical_price_max = Column(Numeric(10, 2), nullable=False)
    is_personalized = Column(Boolean, default=False, nullable=False)
    is_experience = Column(Boolean, default=False, nullable=False)
    is_handmade = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    experiences = sqla_relationship("GiftingExperience", back_populates="gift")

# 3. OCCASION MODEL
class Occasion(Base):
    __tablename__ = "occasions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    experiences = sqla_relationship("GiftingExperience", back_populates="occasion")
    queries = sqla_relationship("RecommendationQuery", back_populates="occasion")

# 4. RELATIONSHIP MODEL
class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    experiences = sqla_relationship("GiftingExperience", back_populates="relationship_obj")
    queries = sqla_relationship("RecommendationQuery", back_populates="relationship_obj")

# 5. INTEREST MODEL
class Interest(Base):
    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

# 6. PERSONALITY MODEL
class Personality(Base):
    __tablename__ = "personalities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

# 7. RECIPIENT PROFILE JOIN TABLES
recipient_profile_interests = Table(
    "recipient_profile_interests",
    Base.metadata,
    Column("recipient_profile_id", String(36), ForeignKey("recipient_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("interest_id", Integer, ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True)
)

recipient_profile_personalities = Table(
    "recipient_profile_personalities",
    Base.metadata,
    Column("recipient_profile_id", String(36), ForeignKey("recipient_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("personality_id", Integer, ForeignKey("personalities.id", ondelete="CASCADE"), primary_key=True)
)

# 8. RECIPIENT PROFILE MODEL
class RecipientProfile(Base):
    __tablename__ = "recipient_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    age_range = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    interests = sqla_relationship("Interest", secondary=recipient_profile_interests)
    personalities = sqla_relationship("Personality", secondary=recipient_profile_personalities)
    experiences = sqla_relationship("GiftingExperience", back_populates="recipient_profile")

# 9. GIFTING EXPERIENCE MODEL
class GiftingExperience(Base):
    __tablename__ = "gifting_experiences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    gift_id = Column(String(36), ForeignKey("gifts.id", ondelete="CASCADE"), nullable=False, index=True)
    occasion_id = Column(Integer, ForeignKey("occasions.id", ondelete="RESTRICT"), nullable=False, index=True)
    relationship_id = Column(Integer, ForeignKey("relationships.id", ondelete="RESTRICT"), nullable=False, index=True)
    recipient_profile_id = Column(String(36), ForeignKey("recipient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    budget_actual = Column(Numeric(10, 2), nullable=False, index=True)
    giver_rating = Column(Integer, nullable=False)
    recipient_rating = Column(Integer, nullable=False)
    would_recommend = Column(Boolean, nullable=False)
    review_text = Column(Text, nullable=True)
    reaction_text = Column(Text, nullable=True)
    is_synthetic = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = sqla_relationship("User", back_populates="experiences")
    gift = sqla_relationship("Gift", back_populates="experiences")
    occasion = sqla_relationship("Occasion", back_populates="experiences")
    relationship_obj = sqla_relationship("Relationship", back_populates="experiences")
    recipient_profile = sqla_relationship("RecipientProfile", back_populates="experiences")
    failure_reasons = sqla_relationship("FailureReason", back_populates="gifting_experience", cascade="all, delete-orphan")
    nlp_insight = sqla_relationship("ReviewNLPInsight", back_populates="gifting_experience", uselist=False, cascade="all, delete-orphan")

# 10. FAILURE REASON MODEL
class FailureReason(Base):
    __tablename__ = "failure_reasons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gifting_experience_id = Column(String(36), ForeignKey("gifting_experiences.id", ondelete="CASCADE"), nullable=False, index=True)
    reason_code = Column(SQLEnum(FailureReasonCode), nullable=False, index=True)
    free_text = Column(Text, nullable=True)

    gifting_experience = sqla_relationship("GiftingExperience", back_populates="failure_reasons")

# 11. REVIEW NLP INSIGHT MODEL
class ReviewNLPInsight(Base):
    __tablename__ = "review_nlp_insights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gifting_experience_id = Column(String(36), ForeignKey("gifting_experiences.id", ondelete="CASCADE"), unique=True, nullable=False)
    sentiment_score = Column(Float, nullable=True)
    extracted_themes = Column(TextArrayType, nullable=True)
    extracted_positive_reasons = Column(TextArrayType, nullable=True)
    extracted_negative_reasons = Column(TextArrayType, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    gifting_experience = sqla_relationship("GiftingExperience", back_populates="nlp_insight")

# 12. RECOMMENDATION QUERY JOIN TABLES
recommendation_query_interests = Table(
    "recommendation_query_interests",
    Base.metadata,
    Column("query_id", String(36), ForeignKey("recommendation_queries.id", ondelete="CASCADE"), primary_key=True),
    Column("interest_id", Integer, ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True)
)

recommendation_query_personalities = Table(
    "recommendation_query_personalities",
    Base.metadata,
    Column("query_id", String(36), ForeignKey("recommendation_queries.id", ondelete="CASCADE"), primary_key=True),
    Column("personality_id", Integer, ForeignKey("personalities.id", ondelete="CASCADE"), primary_key=True)
)

# 13. RECOMMENDATION QUERY MODEL
class RecommendationQuery(Base):
    __tablename__ = "recommendation_queries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    relationship_id = Column(Integer, ForeignKey("relationships.id", ondelete="RESTRICT"), nullable=False)
    occasion_id = Column(Integer, ForeignKey("occasions.id", ondelete="RESTRICT"), nullable=False)
    budget_min = Column(Numeric(10, 2), nullable=True)
    budget_max = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    user = sqla_relationship("User", back_populates="queries")
    occasion = sqla_relationship("Occasion", back_populates="queries")
    relationship_obj = sqla_relationship("Relationship", back_populates="queries")
    interests = sqla_relationship("Interest", secondary=recommendation_query_interests)
    personalities = sqla_relationship("Personality", secondary=recommendation_query_personalities)
    results = sqla_relationship("RecommendationResult", back_populates="query", cascade="all, delete-orphan")

# 14. RECOMMENDATION RESULT MODEL
class RecommendationResult(Base):
    __tablename__ = "recommendation_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String(36), ForeignKey("recommendation_queries.id", ondelete="CASCADE"), nullable=False)
    gift_id = Column(String(36), ForeignKey("gifts.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    confidence_level = Column(SQLEnum(ConfidenceLevel), nullable=False)
    rank = Column(Integer, nullable=False)
    was_clicked = Column(Boolean, default=False, nullable=False)
    was_saved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    query = sqla_relationship("RecommendationQuery", back_populates="results")
    gift = sqla_relationship("Gift")
