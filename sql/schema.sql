-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. DROP TABLES & TYPES IF EXISTS (for clean development resets)
DROP TABLE IF EXISTS recommendation_results CASCADE;
DROP TABLE IF EXISTS recommendation_query_personalities CASCADE;
DROP TABLE IF EXISTS recommendation_query_interests CASCADE;
DROP TABLE IF EXISTS recommendation_queries CASCADE;
DROP TABLE IF EXISTS review_nlp_insights CASCADE;
DROP TABLE IF EXISTS failure_reasons CASCADE;
DROP TABLE IF EXISTS gifting_experiences CASCADE;
DROP TABLE IF EXISTS recipient_profile_personalities CASCADE;
DROP TABLE IF EXISTS recipient_profile_interests CASCADE;
DROP TABLE IF EXISTS recipient_profiles CASCADE;
DROP TABLE IF EXISTS personalities CASCADE;
DROP TABLE IF EXISTS interests CASCADE;
DROP TABLE IF EXISTS relationships CASCADE;
DROP TABLE IF EXISTS occasions CASCADE;
DROP TABLE IF EXISTS gifts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP TYPE IF EXISTS failure_reason_code CASCADE;
DROP TYPE IF EXISTS confidence_level CASCADE;

-- 2. FAILURE REASON ENUM
CREATE TYPE failure_reason_code AS ENUM (
    'ALREADY_OWNED',
    'WRONG_SIZE',
    'TOO_GENERIC',
    'POOR_QUALITY',
    'NOT_THEIR_STYLE',
    'WRONG_TIMING',
    'EXPRESSION_OF_DISLIKE',
    'OTHER'
);

-- 3. CONFIDENCE LEVEL ENUM
CREATE TYPE confidence_level AS ENUM (
    'Low',
    'Medium',
    'High'
);

-- 4. USERS TABLE
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    contribution_count INT DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5. GIFTS TABLE
CREATE TABLE gifts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    typical_price_min NUMERIC(10, 2) NOT NULL CHECK (typical_price_min >= 0),
    typical_price_max NUMERIC(10, 2) NOT NULL CHECK (typical_price_max >= typical_price_min),
    is_personalized BOOLEAN DEFAULT FALSE NOT NULL,
    is_experience BOOLEAN DEFAULT FALSE NOT NULL,
    is_handmade BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 6. OCCASIONS TABLE
CREATE TABLE occasions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- 7. RELATIONSHIPS TABLE
CREATE TABLE relationships (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- 8. INTERESTS TABLE
CREATE TABLE interests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- 9. PERSONALITIES TABLE
CREATE TABLE personalities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- 10. RECIPIENT PROFILES TABLE
CREATE TABLE recipient_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    age_range VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 11. RECIPIENT PROFILE INTERESTS (Join Table)
CREATE TABLE recipient_profile_interests (
    recipient_profile_id UUID NOT NULL REFERENCES recipient_profiles(id) ON DELETE CASCADE,
    interest_id INT NOT NULL REFERENCES interests(id) ON DELETE CASCADE,
    PRIMARY KEY (recipient_profile_id, interest_id)
);

-- 12. RECIPIENT PROFILE PERSONALITIES (Join Table)
CREATE TABLE recipient_profile_personalities (
    recipient_profile_id UUID NOT NULL REFERENCES recipient_profiles(id) ON DELETE CASCADE,
    personality_id INT NOT NULL REFERENCES personalities(id) ON DELETE CASCADE,
    PRIMARY KEY (recipient_profile_id, personality_id)
);

-- 13. GIFTING EXPERIENCES TABLE
CREATE TABLE gifting_experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    gift_id UUID NOT NULL REFERENCES gifts(id) ON DELETE CASCADE,
    occasion_id INT NOT NULL REFERENCES occasions(id) ON DELETE RESTRICT,
    relationship_id INT NOT NULL REFERENCES relationships(id) ON DELETE RESTRICT,
    recipient_profile_id UUID NOT NULL REFERENCES recipient_profiles(id) ON DELETE CASCADE,
    budget_actual NUMERIC(10, 2) NOT NULL CHECK (budget_actual >= 0),
    giver_rating INT NOT NULL CHECK (giver_rating BETWEEN 1 AND 10),
    recipient_rating INT NOT NULL CHECK (recipient_rating BETWEEN 1 AND 10),
    would_recommend BOOLEAN NOT NULL,
    review_text TEXT,
    reaction_text TEXT,
    is_synthetic BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 14. FAILURE REASONS TABLE
CREATE TABLE failure_reasons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gifting_experience_id UUID NOT NULL REFERENCES gifting_experiences(id) ON DELETE CASCADE,
    reason_code failure_reason_code NOT NULL,
    free_text TEXT
);

-- 15. REVIEW NLP INSIGHTS TABLE
CREATE TABLE review_nlp_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gifting_experience_id UUID UNIQUE NOT NULL REFERENCES gifting_experiences(id) ON DELETE CASCADE,
    sentiment_score NUMERIC(5, 4) CHECK (sentiment_score BETWEEN -1.0 AND 1.0),
    extracted_themes TEXT[],
    extracted_positive_reasons TEXT[],
    extracted_negative_reasons TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 16. RECOMMENDATION QUERIES TABLE
CREATE TABLE recommendation_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    relationship_id INT NOT NULL REFERENCES relationships(id) ON DELETE RESTRICT,
    occasion_id INT NOT NULL REFERENCES occasions(id) ON DELETE RESTRICT,
    budget_min NUMERIC(10, 2) CHECK (budget_min >= 0),
    budget_max NUMERIC(10, 2) CHECK (budget_max >= budget_min),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 17. RECOMMENDATION QUERY INTERESTS (Join Table)
CREATE TABLE recommendation_query_interests (
    query_id UUID NOT NULL REFERENCES recommendation_queries(id) ON DELETE CASCADE,
    interest_id INT NOT NULL REFERENCES interests(id) ON DELETE CASCADE,
    PRIMARY KEY (query_id, interest_id)
);

-- 18. RECOMMENDATION QUERY PERSONALITIES (Join Table)
CREATE TABLE recommendation_query_personalities (
    query_id UUID NOT NULL REFERENCES recommendation_queries(id) ON DELETE CASCADE,
    personality_id INT NOT NULL REFERENCES personalities(id) ON DELETE CASCADE,
    PRIMARY KEY (query_id, personality_id)
);

-- 19. RECOMMENDATION RESULTS TABLE
CREATE TABLE recommendation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID NOT NULL REFERENCES recommendation_queries(id) ON DELETE CASCADE,
    gift_id UUID NOT NULL REFERENCES gifts(id) ON DELETE CASCADE,
    score NUMERIC(6, 4) NOT NULL,
    confidence_level confidence_level NOT NULL,
    rank INT NOT NULL,
    was_clicked BOOLEAN DEFAULT FALSE NOT NULL,
    was_saved BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- INDEXES
CREATE INDEX idx_gifting_experiences_gift_id ON gifting_experiences(gift_id);
CREATE INDEX idx_gifting_experiences_occasion_id ON gifting_experiences(occasion_id);
CREATE INDEX idx_gifting_experiences_relationship_id ON gifting_experiences(relationship_id);
CREATE INDEX idx_gifting_experiences_recipient_profile_id ON gifting_experiences(recipient_profile_id);
CREATE INDEX idx_gifting_experiences_is_synthetic ON gifting_experiences(is_synthetic);
CREATE INDEX idx_gifting_experiences_budget ON gifting_experiences(budget_actual);
CREATE INDEX idx_gifts_category ON gifts(category);
CREATE INDEX idx_failure_reasons_experience_id ON failure_reasons(gifting_experience_id);
CREATE INDEX idx_failure_reasons_code ON failure_reasons(reason_code);
CREATE INDEX idx_rec_queries_created_at ON recommendation_queries(created_at);
