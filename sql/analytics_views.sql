-- SQL Analytics Views for GiftWise (Milestone 6)

-- 1. Average recipient rating by occasion x relationship
CREATE OR REPLACE VIEW view_rating_by_occasion_relationship AS
SELECT 
    o.id AS occasion_id,
    o.name AS occasion_name,
    r.id AS relationship_id,
    r.name AS relationship_name,
    COUNT(ge.id) AS total_experiences,
    ROUND(AVG(ge.recipient_rating), 2) AS avg_recipient_rating,
    ROUND(AVG(ge.giver_rating), 2) AS avg_giver_rating
FROM gifting_experiences ge
JOIN occasions o ON ge.occasion_id = o.id
JOIN relationships r ON ge.relationship_id = r.id
GROUP BY o.id, o.name, r.id, r.name;

-- 2. Average recipient rating by budget bucket
CREATE OR REPLACE VIEW view_rating_by_budget_bucket AS
SELECT 
    CASE 
        WHEN budget_actual < 25 THEN '1. Under $25'
        WHEN budget_actual BETWEEN 25 AND 50 THEN '2. $25 - $50'
        WHEN budget_actual BETWEEN 50 AND 100 THEN '3. $50 - $100'
        WHEN budget_actual BETWEEN 100 AND 200 THEN '4. $100 - $200'
        ELSE '5. Over $200'
    END AS budget_bucket,
    COUNT(id) AS total_experiences,
    ROUND(AVG(recipient_rating), 2) AS avg_recipient_rating,
    ROUND(AVG(giver_rating), 2) AS avg_giver_rating,
    ROUND(AVG(giver_rating - recipient_rating), 2) AS avg_satisfaction_gap
FROM gifting_experiences
GROUP BY budget_bucket
ORDER BY budget_bucket;

-- 3. Giver rating vs recipient rating (Headline Gap View)
CREATE OR REPLACE VIEW view_giver_vs_recipient_satisfaction_gap AS
SELECT 
    giver_rating,
    recipient_rating,
    COUNT(id) AS experience_count,
    ROUND(AVG(giver_rating - recipient_rating), 2) AS avg_gap
FROM gifting_experiences
GROUP BY giver_rating, recipient_rating
ORDER BY giver_rating DESC, recipient_rating DESC;

-- 4. Personalized vs non-personalized gift performance by relationship type
CREATE OR REPLACE VIEW view_personalized_vs_non_personalized AS
SELECT 
    r.name AS relationship_name,
    g.is_personalized,
    COUNT(ge.id) AS total_experiences,
    ROUND(AVG(ge.recipient_rating), 2) AS avg_recipient_rating,
    ROUND(AVG(ge.giver_rating), 2) AS avg_giver_rating,
    ROUND(CAST(SUM(CASE WHEN ge.would_recommend THEN 1 ELSE 0 END) AS NUMERIC) / COUNT(ge.id) * 100, 1) AS recommend_rate_pct
FROM gifting_experiences ge
JOIN gifts g ON ge.gift_id = g.id
JOIN relationships r ON ge.relationship_id = r.id
GROUP BY r.name, g.is_personalized
ORDER BY r.name, g.is_personalized;

-- 5. Failure reason frequency overall and by gift category
CREATE OR REPLACE VIEW view_failure_reason_frequency AS
SELECT 
    g.category AS gift_category,
    fr.reason_code,
    COUNT(fr.id) AS failure_count
FROM failure_reasons fr
JOIN gifting_experiences ge ON fr.gifting_experience_id = ge.id
JOIN gifts g ON ge.gift_id = g.id
GROUP BY g.category, fr.reason_code
ORDER BY failure_count DESC;

-- 6. Sample size vs rating variance (Confidence scoring validation)
CREATE OR REPLACE VIEW view_sample_size_vs_rating_variance AS
SELECT 
    g.id AS gift_id,
    g.name AS gift_name,
    g.category AS gift_category,
    COUNT(ge.id) AS sample_size_n,
    ROUND(AVG(ge.recipient_rating), 2) AS mean_recipient_rating,
    ROUND(COALESCE(STDDEV_SAMP(ge.recipient_rating), 0), 2) AS rating_stddev,
    ROUND(COALESCE(VARIANCE(ge.recipient_rating), 0), 2) AS rating_variance
FROM gifts g
JOIN gifting_experiences ge ON g.id = ge.gift_id
GROUP BY g.id, g.name, g.category
HAVING COUNT(ge.id) > 0;

-- 7. Reliable vs Polarizing gifts
CREATE OR REPLACE VIEW view_reliable_vs_polarizing_gifts AS
SELECT 
    g.id AS gift_id,
    g.name AS gift_name,
    g.category AS gift_category,
    COUNT(ge.id) AS sample_size_n,
    ROUND(AVG(ge.recipient_rating), 2) AS mean_recipient_rating,
    ROUND(COALESCE(STDDEV_SAMP(ge.recipient_rating), 0), 2) AS rating_stddev,
    CASE 
        WHEN AVG(ge.recipient_rating) >= 7.5 AND COALESCE(STDDEV_SAMP(ge.recipient_rating), 0) <= 1.5 THEN 'Reliable Winner'
        WHEN COALESCE(STDDEV_SAMP(ge.recipient_rating), 0) > 2.0 THEN 'Polarizing (High Variance)'
        WHEN AVG(ge.recipient_rating) < 5.5 THEN 'Consistently Low'
        ELSE 'Moderate / Balanced'
    END AS gift_performance_classification
FROM gifts g
JOIN gifting_experiences ge ON g.id = ge.gift_id
GROUP BY g.id, g.name, g.category
HAVING COUNT(ge.id) >= 5
ORDER BY mean_recipient_rating DESC, rating_stddev ASC;
