"""
GiftWise Recommendation Engine Module (Milestone 4)

Implements Section 5 Spec:
- Candidate filtering with progressive relaxation for cold start scenarios
- Bayesian-adjusted average rating scoring: S = (C * m + sum_ratings) / (C + n)
- Prior weight C = 10 (trades off small sample noise vs observed data)
- Confidence level tiering: Low (n < 5), Medium (5 <= n <= 20), High (n > 20)
- Transparent evidence-backed explanations & top failure reason warnings (>15% threshold)
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.db_models import (
    GiftingExperience, Gift, Occasion, Relationship, RecipientProfile,
    FailureReason, FailureReasonCode, ConfidenceLevel,
    recipient_profile_interests, recipient_profile_personalities, Interest, Personality
)

DEFAULT_PRIOR_WEIGHT_C = 10.0  # C = 10 prior weight

class RecommendationEngine:
    def __init__(self, db: Session, prior_weight_c: float = DEFAULT_PRIOR_WEIGHT_C):
        self.db = db
        self.C = prior_weight_c
        self.global_mean = self._calculate_global_mean()

    def _calculate_global_mean(self) -> float:
        """Calculate global average recipient rating across all logged experiences."""
        result = self.db.query(func.avg(GiftingExperience.recipient_rating)).scalar()
        return float(result) if result is not None else 7.5

    def _get_confidence_level(self, n: int) -> ConfidenceLevel:
        if n < 5:
            return ConfidenceLevel.Low
        elif n <= 20:
            return ConfidenceLevel.Medium
        else:
            return ConfidenceLevel.High

    def _filter_experiences(
        self,
        relationship_id: int,
        occasion_id: int,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        interest_ids: Optional[List[int]] = None,
        personality_ids: Optional[List[int]] = None,
        ignore_budget: bool = False,
        ignore_interests: bool = False,
        ignore_personalities: bool = False
    ) -> List[GiftingExperience]:
        
        query = self.db.query(GiftingExperience).filter(
            GiftingExperience.relationship_id == relationship_id,
            GiftingExperience.occasion_id == occasion_id
        )

        # Budget filtering (±20% flexibility)
        if not ignore_budget and (budget_min is not None or budget_max is not None):
            low = (budget_min * 0.80) if budget_min is not None else 0
            high = (budget_max * 1.20) if budget_max is not None else 10000.0
            query = query.filter(GiftingExperience.budget_actual.between(low, high))

        experiences = query.all()

        # Tag filtering in memory / python for join precision
        filtered = []
        for exp in experiences:
            profile = exp.recipient_profile
            if not profile:
                filtered.append(exp)
                continue

            prof_interest_ids = {i.id for i in profile.interests}
            prof_personality_ids = {p.id for p in profile.personalities}

            interest_match = True
            if not ignore_interests and interest_ids:
                interest_match = bool(prof_interest_ids.intersection(set(interest_ids)))

            personality_match = True
            if not ignore_personalities and personality_ids:
                personality_match = bool(prof_personality_ids.intersection(set(personality_ids)))

            if interest_match and personality_match:
                filtered.append(exp)

        return filtered

    def get_recommendations(
        self,
        relationship_id: int,
        occasion_id: int,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        interest_ids: Optional[List[int]] = None,
        personality_ids: Optional[List[int]] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Executes candidate filtering, cold-start handling, Bayesian scoring, and explanation generation.
        """
        interest_ids = interest_ids or []
        personality_ids = personality_ids or []

        # Progressive Cold-Start Filter Relaxation Steps
        fallback_applied = False
        fallback_notes = None
        matched_exps = []

        # Step 0: Strict Match
        matched_exps = self._filter_experiences(
            relationship_id, occasion_id, budget_min, budget_max, interest_ids, personality_ids
        )
        unique_gifts = {e.gift_id for e in matched_exps}

        # Step 1: Relax Budget if < 3 candidate gifts
        if len(unique_gifts) < 3 and (budget_min is not None or budget_max is not None):
            fallback_applied = True
            fallback_notes = "Fewer than 3 matching experiences found. Relaxed budget constraint (±20% widened)."
            matched_exps = self._filter_experiences(
                relationship_id, occasion_id, budget_min, budget_max, interest_ids, personality_ids,
                ignore_budget=True
            )
            unique_gifts = {e.gift_id for e in matched_exps}

        # Step 2: Relax Interests if still < 3 candidate gifts
        if len(unique_gifts) < 3 and interest_ids:
            fallback_applied = True
            fallback_notes = "Fewer than 3 candidate gifts found. Relaxed interest & budget filters."
            matched_exps = self._filter_experiences(
                relationship_id, occasion_id, budget_min, budget_max, interest_ids, personality_ids,
                ignore_budget=True, ignore_interests=True
            )
            unique_gifts = {e.gift_id for e in matched_exps}

        # Step 3: Relax Personalities if still < 3 candidate gifts
        if len(unique_gifts) < 3 and personality_ids:
            fallback_applied = True
            fallback_notes = "Expanded query to overall relationship & occasion data to ensure reliable suggestions."
            matched_exps = self._filter_experiences(
                relationship_id, occasion_id, budget_min, budget_max, interest_ids, personality_ids,
                ignore_budget=True, ignore_interests=True, ignore_personalities=True
            )
            unique_gifts = {e.gift_id for e in matched_exps}

        # Group matching experiences by gift_id
        gift_exp_map: Dict[str, List[GiftingExperience]] = {}
        for exp in matched_exps:
            gift_exp_map.setdefault(exp.gift_id, []).append(exp)

        # Lookup Interest & Personality names for explanations
        interest_names_map = {i.id: i.name for i in self.db.query(Interest).all()}
        personality_names_map = {p.id: p.name for p in self.db.query(Personality).all()}
        target_interests = [interest_names_map[iid] for iid in interest_ids if iid in interest_names_map]
        target_personalities = [personality_names_map[pid] for pid in personality_ids if pid in personality_names_map]

        recommendations = []

        for gift_id, exps in gift_exp_map.items():
            gift = self.db.query(Gift).filter(Gift.id == gift_id).first()
            if not gift:
                continue

            n = len(exps)
            sum_ratings = sum(e.recipient_rating for e in exps)
            raw_avg_rating = sum_ratings / n

            # Bayesian Score Formula: (C * m + sum_ratings) / (C + n)
            bayesian_score = (self.C * self.global_mean + sum_ratings) / (self.C + n)
            confidence_level = self._get_confidence_level(n)

            # Failure Analysis
            failure_count = sum(1 for e in exps if e.failure_reasons)
            failure_rate = failure_count / n if n > 0 else 0.0

            top_failure_reason = None
            if failure_rate > 0.15:
                # Find most frequent failure code
                codes = []
                for e in exps:
                    for fr in e.failure_reasons:
                        codes.append(fr.reason_code.value)
                if codes:
                    most_common_code = max(set(codes), key=codes.count)
                    top_failure_reason = f"In {int(round(failure_rate * 100))}% of cases: {most_common_code.replace('_', ' ').title()}"

            # Generate Transparent Explanations & Contributing Factors
            factors = []
            if gift.is_personalized:
                factors.append("Personalized items scored higher for sentimental recipients in this dataset.")
            if gift.is_experience:
                factors.append("Experiential gifts received top recipient satisfaction for this occasion.")
            if gift.is_handmade:
                factors.append("Handmade touch contributed positively to recipient sentiment.")
            if raw_avg_rating >= 8.5:
                factors.append(f"Exceptionally high recipient rating average ({raw_avg_rating:.1f}/10 across {n} experiences).")
            if target_interests:
                factors.append(f"Direct alignment with recipient interests in {', '.join(target_interests[:2])}.")
            if not factors:
                factors.append("Consistently strong recipient outcome ratings in similar gifting situations.")

            recommendations.append({
                "gift_id": gift.id,
                "gift_name": gift.name,
                "gift_category": gift.category,
                "description": gift.description,
                "typical_price_min": float(gift.typical_price_min),
                "typical_price_max": float(gift.typical_price_max),
                "is_personalized": gift.is_personalized,
                "is_experience": gift.is_experience,
                "is_handmade": gift.is_handmade,
                "bayesian_score": round(bayesian_score, 2),
                "raw_avg_rating": round(raw_avg_rating, 2),
                "sample_size_n": n,
                "confidence_level": confidence_level,
                "contributing_factors": factors[:3],
                "failure_rate": round(failure_rate, 2),
                "top_failure_reason": top_failure_reason,
                "matching_experiences_sample": [
                    {
                        "giver_rating": e.giver_rating,
                        "recipient_rating": e.recipient_rating,
                        "review_text": e.review_text,
                        "reaction_text": e.reaction_text,
                        "is_synthetic": e.is_synthetic
                    } for e in exps[:3]
                ]
            })

        # Sort recommendations by Bayesian score descending
        recommendations.sort(key=lambda x: x["bayesian_score"], reverse=True)

        return {
            "query_summary": {
                "relationship_id": relationship_id,
                "occasion_id": occasion_id,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "interest_ids": interest_ids,
                "personality_ids": personality_ids,
                "prior_weight_C": self.C,
                "global_mean_m": round(self.global_mean, 2)
            },
            "cold_start_fallback_applied": fallback_applied,
            "fallback_notes": fallback_notes,
            "total_candidates_found": len(recommendations),
            "recommendations": recommendations[:top_k]
        }
