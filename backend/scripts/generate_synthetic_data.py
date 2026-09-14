"""
Synthetic Seed Data Generator for GiftWise (Milestone 2)

Generates ~750 synthetic gifting experiences clearly labeled `is_synthetic = True`.
Includes natural noise/variance, giver-vs-recipient satisfaction gaps, realistic review text,
and failure reasons for low-rated experiences.
"""

import sys
import os
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.db.session import engine, SessionLocal, Base
from backend.app.models.db_models import (
    User, Gift, Occasion, Relationship, Interest, Personality,
    RecipientProfile, GiftingExperience, FailureReason, FailureReasonCode
)
from backend.scripts.seed_scaffold import seed_scaffold

# Expanded catalog of gifts to ensure rich analytical spread
EXPANDED_GIFTS = [
    # Electronics
    {"name": "Wireless Noise-Canceling Headphones", "category": "Electronics", "description": "Over-ear bluetooth headphones with active noise cancellation.", "price_min": 120, "price_max": 250, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "Smart Fitness Watch", "category": "Electronics", "description": "Activity tracker with heart rate monitor and sleep tracking.", "price_min": 80, "price_max": 180, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "E-Reader Paperwhite Edition", "category": "Electronics", "description": "Glare-free digital book reader with adjustable warm light.", "price_min": 100, "price_max": 150, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "Instant Mini Photo Printer", "category": "Electronics", "description": "Pocket-sized wireless photo printer for smartphones.", "price_min": 70, "price_max": 120, "is_personalized": False, "is_experience": False, "is_handmade": False},
    
    # Home & Kitchen
    {"name": "Cast Iron Dutch Oven (5.5 Qt)", "category": "Home & Kitchen", "description": "Enameled heavy cast iron pot for braising and baking.", "price_min": 70, "price_max": 140, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "Espresso Machine with Milk Frother", "category": "Home & Kitchen", "description": "15-bar pump espresso maker for lattes and cappuccinos.", "price_min": 130, "price_max": 280, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "Aeropress Coffee & Espresso Maker", "category": "Home & Kitchen", "description": "Compact immersion coffee press ideal for home or camping.", "price_min": 35, "price_max": 50, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "Aromatherapy Essential Oil Diffuser Set", "category": "Home & Kitchen", "description": "Ultrasonic cool mist diffuser with 8 organic essential oils.", "price_min": 30, "price_max": 60, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "Weighted Blanket 15lbs", "category": "Home & Kitchen", "description": "Soft cooling glass-bead weighted blanket for deep sleep.", "price_min": 50, "price_max": 90, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "Indoor Herb Garden Kit", "category": "Home & Kitchen", "description": "Hydroponic countertop garden with LED grow light for fresh herbs.", "price_min": 60, "price_max": 110, "is_personalized": False, "is_experience": False, "is_handmade": False},

    # Personalized & Handmade
    {"name": "Custom Engraved Leather Journal", "category": "Personalized & Craft", "description": "Handcrafted leather binder with personalized initials.", "price_min": 30, "price_max": 55, "is_personalized": True, "is_experience": False, "is_handmade": True},
    {"name": "Custom Star Map Framed Print", "category": "Personalized & Craft", "description": "Custom night sky map of a meaningful date and coordinates.", "price_min": 35, "price_max": 75, "is_personalized": True, "is_experience": False, "is_handmade": True},
    {"name": "Custom Embroidered Family Portrait", "category": "Personalized & Craft", "description": "Hand-stitched minimalistic portrait based on photo.", "price_min": 50, "price_max": 120, "is_personalized": True, "is_experience": False, "is_handmade": True},
    {"name": "Personalized Recipe Cutting Board", "category": "Personalized & Craft", "description": "Walnut wood board laser-engraved with family handwritten recipe.", "price_min": 40, "price_max": 80, "is_personalized": True, "is_experience": False, "is_handmade": True},
    {"name": "Handmade Ceramic Mug Set", "category": "Personalized & Craft", "description": "Set of two wheel-thrown speckled stoneware coffee mugs.", "price_min": 35, "price_max": 65, "is_personalized": False, "is_experience": False, "is_handmade": True},

    # Experiences
    {"name": "Couples Cooking Class Workshop", "category": "Experiences", "description": "Hands-on Italian pasta making class guided by professional chef.", "price_min": 110, "price_max": 220, "is_personalized": False, "is_experience": True, "is_handmade": False},
    {"name": "Hot Air Balloon Ride Voucher", "category": "Experiences", "description": "Sunrise flight experience with champagne celebration.", "price_min": 200, "price_max": 350, "is_personalized": False, "is_experience": True, "is_handmade": False},
    {"name": "Specialty Coffee Roasting Workshop", "category": "Experiences", "description": "Interactive tasting and roasting class at local specialty roastery.", "price_min": 65, "price_max": 110, "is_personalized": False, "is_experience": True, "is_handmade": False},
    {"name": "Spa & Massage Day Package", "category": "Experiences", "description": "60-minute deep tissue massage and facial treatment pass.", "price_min": 90, "price_max": 180, "is_personalized": False, "is_experience": True, "is_handmade": False},
    {"name": "Concert / Theater Gift Ticket Voucher", "category": "Experiences", "description": "Flexible ticket voucher for live music or Broadway touring show.", "price_min": 80, "price_max": 200, "is_personalized": False, "is_experience": True, "is_handmade": False},

    # Outdoors & Games
    {"name": "Ultra-Lightweight Backpacking Hammock", "category": "Outdoors & Fitness", "description": "Compact double hammock with tree-friendly straps.", "price_min": 30, "price_max": 55, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "Insulated Stainless Steel Growler 64oz", "category": "Outdoors & Fitness", "description": "Vacuum-insulated carbonated beverage growler.", "price_min": 35, "price_max": 60, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "Strategic Board Game Catan 3D Edition", "category": "Games & Hobbies", "description": "Immersive 3D sculpted board game edition.", "price_min": 45, "price_max": 95, "is_personalized": False, "is_experience": False, "is_handmade": False},
    {"name": "1000-Piece Custom Photo Puzzle", "category": "Games & Hobbies", "description": "High-gloss cardboard puzzle made from personal memory photo.", "price_min": 25, "price_max": 45, "is_personalized": True, "is_experience": False, "is_handmade": False}
]

AGE_RANGES = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

REVIEWS_HIGH_RATING = [
    "They absolutely loved it! Used it immediately and praised how thoughtful it was.",
    "Brought tears to their eyes. Fits their personality perfectly and quality is fantastic.",
    "Super practical and well-made. They mention how much they use it every single week.",
    "Best gift of the occasion! Personalized touches made a huge impression.",
    "Surpassed expectations! Fantastic build quality and very memorable experience."
]

REVIEWS_MEDIUM_RATING = [
    "They liked it and thanked me warmly, though it was slightly different from what they expected.",
    "Nice overall quality, but they already had something similar sitting in their closet.",
    "Decent gift! They enjoyed it at first, but haven't used it much since.",
    "A bit generic, but served its purpose well for the occasion.",
    "They appreciated the gesture, but the size/color wasn't 100% their style."
]

REVIEWS_LOW_RATING = [
    "Unfortunately it missed the mark. They already owned a newer model.",
    "Build quality was disappointing and felt flimsy. They rarely touch it.",
    "Felt too impersonal and generic. Recipient seemed polite but unimpressed.",
    "Wrong sizing/style choice. Should have picked something more tailored to their tastes.",
    "Arrived late and didn't fit their apartment space well."
]

REACTIONS = [
    "Genuine excitement and huge smile upon unwrapping.",
    "Polite smile and thank you, but subtle confusion.",
    "Speechless and amazed at the personalization!",
    "Laughed and immediately showed it to everyone present.",
    "Pleasantly surprised and started using it right away."
]

FAILURE_FREE_TEXTS = {
    FailureReasonCode.ALREADY_OWNED: "Recipient already owned a similar item.",
    FailureReasonCode.WRONG_SIZE: "Sizing was off or didn't fit their physical space.",
    FailureReasonCode.TOO_GENERIC: "Felt like a mass-produced last-minute gift.",
    FailureReasonCode.POOR_QUALITY: "Materials felt cheap or broke easily.",
    FailureReasonCode.NOT_THEIR_STYLE: "Color/style didn't match recipient aesthetic.",
    FailureReasonCode.WRONG_TIMING: "Gifting timing wasn't ideal for their current situation.",
    FailureReasonCode.EXPRESSION_OF_DISLIKE: "Recipient explicitly preferred a different category.",
    FailureReasonCode.OTHER: "Misc issue during gifting event."
}

def generate_synthetic_dataset(db: Session, num_experiences: int = 750):
    print(f"🎲 Generating {num_experiences} synthetic gifting experiences (`is_synthetic = True`)...")

    # Ensure tables exist on the current session's engine
    target_engine = db.get_bind()
    Base.metadata.create_all(bind=target_engine)

    # 1. Seed base catalog first
    seed_scaffold(db)

    # 2. Add extra catalog items
    for gdata in EXPANDED_GIFTS:
        existing = db.query(Gift).filter(Gift.name == gdata["name"]).first()
        if not existing:
            g = Gift(
                name=gdata["name"],
                category=gdata["category"],
                description=gdata["description"],
                typical_price_min=gdata["price_min"],
                typical_price_max=gdata["price_max"],
                is_personalized=gdata["is_personalized"],
                is_experience=gdata["is_experience"],
                is_handmade=gdata["is_handmade"]
            )
            db.add(g)
    db.commit()

    # Retrieve lookups
    all_gifts = db.query(Gift).all()
    all_occasions = db.query(Occasion).all()
    all_relationships = db.query(Relationship).all()
    all_interests = db.query(Interest).all()
    all_personalities = db.query(Personality).all()

    # 3. Create ~25 Synthetic Giver Users
    users = []
    for i in range(1, 26):
        email = f"synthetic_giver_{i}@giftwise.demo"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                password_hash="pbkdf2_sha256$synthetic$hash",
                display_name=f"Giver {i}",
                contribution_count=0
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        users.append(user)

    # 4. Generate Synthetic Experiences
    experiences_added = 0
    now = datetime.utcnow()

    for _ in range(num_experiences):
        user = random.choice(users)
        gift = random.choice(all_gifts)
        occasion = random.choice(all_occasions)
        relationship = random.choice(all_relationships)

        # Create RecipientProfile
        profile = RecipientProfile(
            age_range=random.choice(AGE_RANGES)
        )
        # Select 1-3 interests, 1-2 personalities
        profile.interests = random.sample(all_interests, k=random.randint(1, 3))
        profile.personalities = random.sample(all_personalities, k=random.randint(1, 2))
        db.add(profile)
        db.flush()

        # Calculate budget (typical price ± 15%)
        base_price = float((gift.typical_price_min + gift.typical_price_max) / 2)
        variance = random.uniform(-0.15, 0.15)
        budget_actual = round(max(10.0, base_price * (1 + variance)), 2)

        # Ratings simulation:
        # Personalized/Experience gifts tend to score slightly higher on average,
        # but with natural noise & occasional giver/recipient satisfaction gaps.
        base_score = 7.5
        if gift.is_personalized:
            base_score += 0.8
        if gift.is_experience:
            base_score += 0.5
        if gift.is_handmade:
            base_score += 0.4

        # Recipient rating (primary signal) with normal noise
        recipient_rating = int(round(min(10, max(1, random.gauss(base_score, 1.8)))))
        
        # Giver rating (givers often over-estimate or under-estimate recipient satisfaction!)
        # Create satisfaction gap in ~30% of cases
        if random.random() < 0.30:
            giver_rating = min(10, max(1, recipient_rating + random.choice([2, 3, -2])))
        else:
            giver_rating = recipient_rating

        would_recommend = recipient_rating >= 7

        # Review & Reaction text selection
        if recipient_rating >= 8:
            review_text = random.choice(REVIEWS_HIGH_RATING)
        elif recipient_rating >= 5:
            review_text = random.choice(REVIEWS_MEDIUM_RATING)
        else:
            review_text = random.choice(REVIEWS_LOW_RATING)

        reaction_text = random.choice(REACTIONS)

        # Timestamp spread over past 365 days
        created_at = now - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))

        exp = GiftingExperience(
            user_id=user.id,
            gift_id=gift.id,
            occasion_id=occasion.id,
            relationship_id=relationship.id,
            recipient_profile_id=profile.id,
            budget_actual=budget_actual,
            giver_rating=giver_rating,
            recipient_rating=recipient_rating,
            would_recommend=would_recommend,
            review_text=review_text,
            reaction_text=reaction_text,
            is_synthetic=True,  # STRICT GUARDRAIL ENFORCED
            created_at=created_at
        )
        db.add(exp)
        db.flush()

        # Add Failure Reasons for low ratings or random failure events
        if recipient_rating <= 6 or (recipient_rating <= 7 and random.random() < 0.25):
            code = random.choice(list(FailureReasonCode))
            fr = FailureReason(
                gifting_experience_id=exp.id,
                reason_code=code,
                free_text=FAILURE_FREE_TEXTS.get(code, "Recipient reported an issue.")
            )
            db.add(fr)

        # Increment user contribution count
        user.contribution_count += 1
        experiences_added += 1

    db.commit()
    print(f"✅ Successfully generated {experiences_added} synthetic gifting experiences (all flagged `is_synthetic = True`)!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        generate_synthetic_dataset(db, num_experiences=750)
    finally:
        db.close()
