"""
Master Reference Seed Script Scaffold for GiftWise.
Populates standard Occasions, Relationships, Interests, Personalities, and initial Gift Catalog items.
Does NOT generate synthetic gifting experiences (that belongs in Milestone 2).
"""
import sys
import os
from sqlalchemy.orm import Session

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.db.session import engine, SessionLocal, Base
from backend.app.models.db_models import (
    Occasion, Relationship, Interest, Personality, Gift
)

SEED_OCCASIONS = [
    "Birthday",
    "Anniversary",
    "Graduation",
    "Christmas & Holidays",
    "Housewarming",
    "Wedding",
    "Baby Shower",
    "Valentine's Day",
    "Mother's Day",
    "Father's Day",
    "Thank You",
    "Just Because"
]

SEED_RELATIONSHIPS = [
    "Partner / Spouse",
    "Parent",
    "Child",
    "Sibling",
    "Close Friend",
    "Coworker",
    "In-Law",
    "Mentor",
    "Extended Family"
]

SEED_INTERESTS = [
    "Tech & Gadgets",
    "Reading & Books",
    "Cooking & Gourmet Food",
    "Outdoors & Hiking",
    "Gaming",
    "Art & Crafting",
    "Fitness & Sports",
    "Music & Audio",
    "Travel & Photography",
    "Coffee & Tea",
    "Home Decor & Gardening",
    "Board Games & Puzzles",
    "Fashion & Style",
    "Self-Care & Wellness"
]

SEED_PERSONALITIES = [
    "Practical & Functional",
    "Sentimental & Nostalgic",
    "Adventurous & Thrill-Seeking",
    "Introverted & Cozy",
    "Creative & Artistic",
    "Tech-Savvy",
    "Minimalist",
    "Luxury Enthusiast",
    "Humorous & Playful",
    "Organized & Detail-Oriented"
]

SEED_GIFTS = [
    {
        "name": "Custom Engraved Leather Journal",
        "category": "Stationery & Personalization",
        "description": "High-quality refillable leather journal with custom name or quote engraved on the cover.",
        "typical_price_min": 25.00,
        "typical_price_max": 50.00,
        "is_personalized": True,
        "is_experience": False,
        "is_handmade": True
    },
    {
        "name": "Noise-Canceling Wireless Earbuds",
        "category": "Electronics & Tech",
        "description": "Compact Bluetooth earbuds with active noise cancellation and long battery life.",
        "typical_price_min": 80.00,
        "typical_price_max": 200.00,
        "is_personalized": False,
        "is_experience": False,
        "is_handmade": False
    },
    {
        "name": "Artisan Coffee Subscription (3 Months)",
        "category": "Food & Beverage / Experience",
        "description": "Monthly delivery of fresh single-origin coffee beans roasted by specialty roasters.",
        "typical_price_min": 45.00,
        "typical_price_max": 75.00,
        "is_personalized": False,
        "is_experience": True,
        "is_handmade": False
    },
    {
        "name": "E-Reader Paperwhite Edition",
        "category": "Electronics & Reading",
        "description": "Waterproof e-reader with glare-free display and adjustable warm light.",
        "typical_price_min": 110.00,
        "typical_price_max": 160.00,
        "is_personalized": False,
        "is_experience": False,
        "is_handmade": False
    },
    {
        "name": "Custom Star Map Poster of a Special Date",
        "category": "Home Decor & Art",
        "description": "Framed high-definition print showing the exact night sky alignment of a specific date and location.",
        "typical_price_min": 30.00,
        "typical_price_max": 70.00,
        "is_personalized": True,
        "is_experience": False,
        "is_handmade": True
    },
    {
        "name": "Cast Iron Dutch Oven 5.5-Quart",
        "category": "Kitchen & Dining",
        "description": "Heavy-duty enameled cast iron cookware ideal for braising, baking, and soups.",
        "typical_price_min": 60.00,
        "typical_price_max": 150.00,
        "is_personalized": False,
        "is_experience": False,
        "is_handmade": False
    },
    {
        "name": "Couples Cooking Class Workshop",
        "category": "Experiences",
        "description": "Interactive hands-on culinary workshop guided by a professional chef.",
        "typical_price_min": 100.00,
        "typical_price_max": 220.00,
        "is_personalized": False,
        "is_experience": True,
        "is_handmade": False
    },
    {
        "name": "Cozy Merino Wool Throw Blanket",
        "category": "Home & Comfort",
        "description": "Ultra-soft breathable 100% Merino wool blanket for living rooms and bedrooms.",
        "typical_price_min": 70.00,
        "typical_price_max": 130.00,
        "is_personalized": False,
        "is_experience": False,
        "is_handmade": False
    },
    {
        "name": "Custom Recipe Book Memory Binder",
        "category": "DIY & Family History",
        "description": "Custom bound binder with recipe cards to collect and preserve family cooking traditions.",
        "typical_price_min": 35.00,
        "typical_price_max": 65.00,
        "is_personalized": True,
        "is_experience": False,
        "is_handmade": True
    },
    {
        "name": "Portable Camping Hammock with Tree Straps",
        "category": "Outdoors & Travel",
        "description": "Lightweight parachute nylon hammock setup for hiking, camping, or backyard relaxation.",
        "typical_price_min": 25.00,
        "typical_price_max": 45.00,
        "is_personalized": False,
        "is_experience": False,
        "is_handmade": False
    }
]

def seed_scaffold(db: Session):
    print("🌱 Initializing master schema and populating lookup reference data...")

    # 1. Occasions
    for name in SEED_OCCASIONS:
        if not db.query(Occasion).filter(Occasion.name == name).first():
            db.add(Occasion(name=name))
    
    # 2. Relationships
    for name in SEED_RELATIONSHIPS:
        if not db.query(Relationship).filter(Relationship.name == name).first():
            db.add(Relationship(name=name))

    # 3. Interests
    for name in SEED_INTERESTS:
        if not db.query(Interest).filter(Interest.name == name).first():
            db.add(Interest(name=name))

    # 4. Personalities
    for name in SEED_PERSONALITIES:
        if not db.query(Personality).filter(Personality.name == name).first():
            db.add(Personality(name=name))

    # 5. Gift catalog scaffold
    for gift_data in SEED_GIFTS:
        if not db.query(Gift).filter(Gift.name == gift_data["name"]).first():
            db.add(Gift(**gift_data))

    db.commit()
    print("✅ Master lookup data successfully seeded!")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    try:
        seed_scaffold(db_session)
    finally:
        db_session.close()
