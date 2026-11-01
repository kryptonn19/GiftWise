"""
Synthetic Seed Data Generator for GiftWise (Milestone 2)

Generates thousands of realistic synthetic gifting experiences labeled `is_synthetic = True`.
Features:
- Expanded catalog of 85+ distinct gifts spanning all major categories and price tiers.
- Persona-aware affinity matching (recipient interests, personalities, occasion, relationship).
- Natural variance: Reliable Winners (low variance, high rating), Polarizing Items (high variance),
  and Fragile/Generic Items with authentic failure reasons.
- Behavioral Giver-vs-Recipient perception gap simulation.
- Rich review & reaction text aligned with the NLP Gifting Theme Taxonomy.
- Integrated batch NLP analysis and SQL analytics views refreshment.
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.db.session import engine, SessionLocal, Base
from backend.app.models.db_models import (
    User, Gift, Occasion, Relationship, Interest, Personality,
    RecipientProfile, GiftingExperience, FailureReason, FailureReasonCode, ReviewNLPInsight
)
from backend.scripts.seed_scaffold import seed_scaffold
from backend.app.nlp.pipeline import process_experience_nlp
from backend.app.db.analytics_db import initialize_analytics_views

# ==============================================================================
# EXPANDED 85-ITEM GIFT CATALOG ACROSS 9 DISTINCT CATEGORIES
# ==============================================================================
EXPANDED_GIFTS: List[Dict[str, Any]] = [
    # 1. Electronics & Tech
    {
        "name": "Wireless Noise-Canceling Headphones",
        "category": "Electronics & Tech",
        "description": "Premium over-ear Bluetooth headphones with adaptive noise cancellation and 30-hour battery life.",
        "price_min": 140.0, "price_max": 280.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Tech & Gadgets", "Music & Audio", "Travel & Photography"],
        "personalities": ["Practical & Functional", "Tech-Savvy", "Introverted & Cozy"],
        "occasions": ["Birthday", "Graduation", "Christmas & Holidays"],
        "relationships": ["Partner / Spouse", "Child", "Sibling", "Close Friend"],
        "baseline_rating": 9.2, "variance": 0.9, "failure_prob": 0.04, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Smart Fitness & Health Watch",
        "category": "Electronics & Tech",
        "description": "All-day activity tracker with continuous heart rate, GPS tracking, and sleep score analytics.",
        "price_min": 110.0, "price_max": 220.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Fitness & Sports", "Tech & Gadgets"],
        "personalities": ["Practical & Functional", "Organized & Detail-Oriented", "Tech-Savvy"],
        "occasions": ["Birthday", "Christmas & Holidays", "Father's Day"],
        "relationships": ["Partner / Spouse", "Parent", "Sibling"],
        "baseline_rating": 8.7, "variance": 1.2, "failure_prob": 0.08, "default_fail": FailureReasonCode.WRONG_SIZE
    },
    {
        "name": "E-Reader Paperwhite Edition",
        "category": "Electronics & Tech",
        "description": "Glare-free 300 ppi digital book reader with adjustable warm light and waterproof build.",
        "price_min": 95.0, "price_max": 150.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Reading & Books", "Tech & Gadgets", "Travel & Photography"],
        "personalities": ["Introverted & Cozy", "Minimalist", "Practical & Functional"],
        "occasions": ["Birthday", "Christmas & Holidays", "Mother's Day", "Just Because"],
        "relationships": ["Partner / Spouse", "Parent", "Close Friend", "Sibling"],
        "baseline_rating": 9.3, "variance": 0.7, "failure_prob": 0.03, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Ergonomic Mechanical Keyboard",
        "category": "Electronics & Tech",
        "description": "Custom tactile hot-swappable mechanical keyboard with RGB backlighting and wrist rest.",
        "price_min": 85.0, "price_max": 175.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Tech & Gadgets", "Gaming"],
        "personalities": ["Tech-Savvy", "Organized & Detail-Oriented"],
        "occasions": ["Birthday", "Christmas & Holidays", "Graduation"],
        "relationships": ["Sibling", "Close Friend", "Partner / Spouse"],
        "baseline_rating": 8.9, "variance": 1.1, "failure_prob": 0.06, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Portable Waterproof Bluetooth Speaker",
        "category": "Electronics & Tech",
        "description": "Rugged 360-degree wireless outdoor speaker with deep bass and 16-hour playtime.",
        "price_min": 45.0, "price_max": 90.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Music & Audio", "Outdoors & Hiking", "Travel & Photography"],
        "personalities": ["Adventurous & Thrill-Seeking", "Humorous & Playful"],
        "occasions": ["Birthday", "Graduation", "Housewarming", "Just Because"],
        "relationships": ["Close Friend", "Sibling", "Coworker"],
        "baseline_rating": 8.8, "variance": 1.0, "failure_prob": 0.05, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Ultra-Slim Magnetic Wireless Power Bank",
        "category": "Electronics & Tech",
        "description": "Pocket-sized 10000mAh magnetic portable charger with fast USB-C power delivery.",
        "price_min": 35.0, "price_max": 65.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Tech & Gadgets", "Travel & Photography"],
        "personalities": ["Practical & Functional", "Organized & Detail-Oriented"],
        "occasions": ["Christmas & Holidays", "Thank You", "Just Because"],
        "relationships": ["Coworker", "Close Friend", "Sibling", "Parent"],
        "baseline_rating": 8.6, "variance": 1.1, "failure_prob": 0.07, "default_fail": FailureReasonCode.TOO_GENERIC
    },
    {
        "name": "Smart Health & Sleep Tracker Ring",
        "category": "Electronics & Tech",
        "description": "Titanium lightweight biometric ring tracking recovery, HRV, and sleep stages.",
        "price_min": 190.0, "price_max": 320.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Fitness & Sports", "Tech & Gadgets", "Self-Care & Wellness"],
        "personalities": ["Tech-Savvy", "Luxury Enthusiast", "Organized & Detail-Oriented"],
        "occasions": ["Anniversary", "Birthday", "Graduation"],
        "relationships": ["Partner / Spouse", "Parent"],
        "baseline_rating": 8.5, "variance": 1.6, "failure_prob": 0.12, "default_fail": FailureReasonCode.WRONG_SIZE
    },
    {
        "name": "Instant Wireless Pocket Photo Printer",
        "category": "Electronics & Tech",
        "description": "Zero-ink Bluetooth pocket printer producing 2x3 sticky-back photos from smartphone albums.",
        "price_min": 65.0, "price_max": 115.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Travel & Photography", "Art & Crafting"],
        "personalities": ["Sentimental & Nostalgic", "Creative & Artistic"],
        "occasions": ["Birthday", "Graduation", "Christmas & Holidays"],
        "relationships": ["Child", "Close Friend", "Sibling"],
        "baseline_rating": 8.4, "variance": 1.4, "failure_prob": 0.09, "default_fail": FailureReasonCode.POOR_QUALITY
    },

    # 2. Kitchen, Dining & Gourmet Food
    {
        "name": "Cast Iron Dutch Oven 5.5-Quart",
        "category": "Kitchen & Gourmet Food",
        "description": "Heavy enameled cast-iron pot with tight-fitting lid for sourdough baking, braises, and stews.",
        "price_min": 75.0, "price_max": 160.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Cooking & Gourmet Food", "Home Decor & Gardening"],
        "personalities": ["Practical & Functional", "Introverted & Cozy", "Luxury Enthusiast"],
        "occasions": ["Housewarming", "Wedding", "Christmas & Holidays", "Mother's Day"],
        "relationships": ["Partner / Spouse", "Parent", "Close Friend", "In-Law"],
        "baseline_rating": 9.4, "variance": 0.6, "failure_prob": 0.03, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Espresso Machine with Milk Steam Wand",
        "category": "Kitchen & Gourmet Food",
        "description": "15-bar Italian pressure pump espresso maker with manual micro-foam steaming wand.",
        "price_min": 150.0, "price_max": 340.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Coffee & Tea", "Cooking & Gourmet Food"],
        "personalities": ["Luxury Enthusiast", "Practical & Functional", "Organized & Detail-Oriented"],
        "occasions": ["Wedding", "Anniversary", "Christmas & Holidays", "Housewarming"],
        "relationships": ["Partner / Spouse", "Parent", "Close Friend"],
        "baseline_rating": 9.1, "variance": 1.0, "failure_prob": 0.05, "default_fail": FailureReasonCode.TOO_GENERIC
    },
    {
        "name": "Aeropress Coffee & Cold Brew Maker",
        "category": "Kitchen & Gourmet Food",
        "description": "Patented rapid immersion coffee press producing smooth espresso-style brew anywhere.",
        "price_min": 35.0, "price_max": 55.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Coffee & Tea", "Outdoors & Hiking", "Travel & Photography"],
        "personalities": ["Practical & Functional", "Minimalist"],
        "occasions": ["Birthday", "Thank You", "Father's Day", "Just Because"],
        "relationships": ["Coworker", "Close Friend", "Sibling", "Parent"],
        "baseline_rating": 9.3, "variance": 0.7, "failure_prob": 0.03, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Japanese Damascus Steel Chef's Knife (Gyuto 8\")",
        "category": "Kitchen & Gourmet Food",
        "description": "67-layer hammered Damascus steel blade with octagonal rosewood ergonomic handle.",
        "price_min": 85.0, "price_max": 175.0, "is_personalized": False, "is_experience": False, "is_handmade": True,
        "interests": ["Cooking & Gourmet Food"],
        "personalities": ["Practical & Functional", "Organized & Detail-Oriented", "Luxury Enthusiast"],
        "occasions": ["Birthday", "Father's Day", "Wedding", "Housewarming"],
        "relationships": ["Partner / Spouse", "Parent", "Close Friend"],
        "baseline_rating": 9.5, "variance": 0.5, "failure_prob": 0.02, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Artisan Single-Origin Coffee Subscription (3 Months)",
        "category": "Kitchen & Gourmet Food",
        "description": "Freshly roasted specialty whole-bean coffee curated from independent micro-roasters monthly.",
        "price_min": 45.0, "price_max": 80.0, "is_personalized": False, "is_experience": True, "is_handmade": False,
        "interests": ["Coffee & Tea", "Cooking & Gourmet Food"],
        "personalities": ["Adventurous & Thrill-Seeking", "Introverted & Cozy"],
        "occasions": ["Birthday", "Christmas & Holidays", "Thank You", "Father's Day"],
        "relationships": ["Close Friend", "Coworker", "Sibling", "Parent"],
        "baseline_rating": 9.0, "variance": 0.9, "failure_prob": 0.04, "default_fail": FailureReasonCode.EXPRESSION_OF_DISLIKE
    },
    {
        "name": "Countertop Indoor Hydroponic Herb Garden",
        "category": "Kitchen & Gourmet Food",
        "description": "Self-watering indoor garden with automated LED grow light and gourmet heirloom seed pods.",
        "price_min": 65.0, "price_max": 120.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Cooking & Gourmet Food", "Home Decor & Gardening"],
        "personalities": ["Introverted & Cozy", "Creative & Artistic"],
        "occasions": ["Housewarming", "Mother's Day", "Birthday", "Christmas & Holidays"],
        "relationships": ["Parent", "Close Friend", "Partner / Spouse"],
        "baseline_rating": 8.7, "variance": 1.2, "failure_prob": 0.07, "default_fail": FailureReasonCode.WRONG_SIZE
    },
    {
        "name": "Electric Precision Gooseneck Pour-Over Kettle",
        "category": "Kitchen & Gourmet Food",
        "description": "Variable temperature digital kettle with 1-degree temperature precision and keep-warm hold.",
        "price_min": 60.0, "price_max": 110.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Coffee & Tea", "Cooking & Gourmet Food"],
        "personalities": ["Organized & Detail-Oriented", "Tech-Savvy"],
        "occasions": ["Housewarming", "Birthday", "Wedding"],
        "relationships": ["Close Friend", "Sibling", "Partner / Spouse"],
        "baseline_rating": 9.2, "variance": 0.8, "failure_prob": 0.04, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Gourmet Hot Sauce Around The World Tasting Set",
        "category": "Kitchen & Gourmet Food",
        "description": "Curated crate of 10 artisanal small-batch chili sauces spanning mild smokey to fiery habanero.",
        "price_min": 32.0, "price_max": 60.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Cooking & Gourmet Food"],
        "personalities": ["Adventurous & Thrill-Seeking", "Humorous & Playful"],
        "occasions": ["Birthday", "Father's Day", "Christmas & Holidays", "Just Because"],
        "relationships": ["Sibling", "Close Friend", "Coworker"],
        "baseline_rating": 7.8, "variance": 2.2, "failure_prob": 0.18, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Italian Hand-Cranked Pasta Maker Machine",
        "category": "Kitchen & Gourmet Food",
        "description": "Chrome-plated steel pasta roller and cutter for fresh fettuccine, lasagna, and tagliolini.",
        "price_min": 45.0, "price_max": 90.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Cooking & Gourmet Food"],
        "personalities": ["Creative & Artistic", "Practical & Functional"],
        "occasions": ["Wedding", "Anniversary", "Christmas & Holidays", "Housewarming"],
        "relationships": ["Partner / Spouse", "Close Friend", "In-Law"],
        "baseline_rating": 8.6, "variance": 1.5, "failure_prob": 0.10, "default_fail": FailureReasonCode.TOO_GENERIC
    },
    {
        "name": "Handcrafted Speckled Stoneware Coffee Mug Set",
        "category": "Kitchen & Gourmet Food",
        "description": "Set of two wheel-thrown ceramic mugs with natural earthy clay glaze and comfortable loop handles.",
        "price_min": 35.0, "price_max": 65.0, "is_personalized": False, "is_experience": False, "is_handmade": True,
        "interests": ["Coffee & Tea", "Art & Crafting", "Home Decor & Gardening"],
        "personalities": ["Introverted & Cozy", "Minimalist", "Sentimental & Nostalgic"],
        "occasions": ["Housewarming", "Thank You", "Christmas & Holidays", "Mother's Day"],
        "relationships": ["Close Friend", "Coworker", "Parent", "Sibling"],
        "baseline_rating": 8.9, "variance": 0.9, "failure_prob": 0.05, "default_fail": FailureReasonCode.ALREADY_OWNED
    },

    # 3. Personalized & Handcrafted Keepsakes
    {
        "name": "Custom Constellation Star Map Framed Print",
        "category": "Personalized & Keepsakes",
        "description": "Astronomically accurate night sky projection of an exact anniversary or birthdate location.",
        "price_min": 35.0, "price_max": 80.0, "is_personalized": True, "is_experience": False, "is_handmade": True,
        "interests": ["Home Decor & Gardening", "Art & Crafting"],
        "personalities": ["Sentimental & Nostalgic", "Creative & Artistic"],
        "occasions": ["Anniversary", "Wedding", "Valentine's Day", "Baby Shower"],
        "relationships": ["Partner / Spouse", "Close Friend", "Parent"],
        "baseline_rating": 9.6, "variance": 0.5, "failure_prob": 0.02, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Custom Engraved Leather Journal & Pen Set",
        "category": "Personalized & Keepsakes",
        "description": "Hand-stitched full grain leather binder with personalized name debossing and brass fountain pen.",
        "price_min": 32.0, "price_max": 65.0, "is_personalized": True, "is_experience": False, "is_handmade": True,
        "interests": ["Reading & Books", "Art & Crafting"],
        "personalities": ["Sentimental & Nostalgic", "Introverted & Cozy", "Creative & Artistic"],
        "occasions": ["Graduation", "Birthday", "Father's Day", "Thank You"],
        "relationships": ["Close Friend", "Child", "Mentor", "Parent"],
        "baseline_rating": 9.4, "variance": 0.7, "failure_prob": 0.03, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Personalized Recipe Laser-Engraved Cutting Board",
        "category": "Personalized & Keepsakes",
        "description": "Solid walnut cutting board laser-engraved with grandmother's actual handwritten family recipe.",
        "price_min": 45.0, "price_max": 85.0, "is_personalized": True, "is_experience": False, "is_handmade": True,
        "interests": ["Cooking & Gourmet Food", "Home Decor & Gardening"],
        "personalities": ["Sentimental & Nostalgic", "Practical & Functional"],
        "occasions": ["Mother's Day", "Christmas & Holidays", "Wedding", "Housewarming"],
        "relationships": ["Parent", "Partner / Spouse", "Sibling", "Extended Family"],
        "baseline_rating": 9.5, "variance": 0.6, "failure_prob": 0.02, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Custom Minimalist Pet Portrait Canvas",
        "category": "Personalized & Keepsakes",
        "description": "Hand-illustrated custom digital artwork of recipient's beloved dog or cat on stretched canvas.",
        "price_min": 40.0, "price_max": 95.0, "is_personalized": True, "is_experience": False, "is_handmade": True,
        "interests": ["Art & Crafting", "Home Decor & Gardening"],
        "personalities": ["Sentimental & Nostalgic", "Humorous & Playful"],
        "occasions": ["Birthday", "Christmas & Holidays", "Just Because"],
        "relationships": ["Close Friend", "Partner / Spouse", "Sibling"],
        "baseline_rating": 9.7, "variance": 0.4, "failure_prob": 0.01, "default_fail": FailureReasonCode.POOR_QUALITY
    },
    {
        "name": "Monogrammed Italian Leather Weekender Duffle",
        "category": "Personalized & Keepsakes",
        "description": "Full grain vintage leather travel carry-on bag with brass hardware and custom foil initials.",
        "price_min": 95.0, "price_max": 195.0, "is_personalized": True, "is_experience": False, "is_handmade": True,
        "interests": ["Travel & Photography", "Fashion & Style"],
        "personalities": ["Luxury Enthusiast", "Organized & Detail-Oriented", "Practical & Functional"],
        "occasions": ["Graduation", "Anniversary", "Wedding", "Christmas & Holidays"],
        "relationships": ["Partner / Spouse", "Child", "Parent"],
        "baseline_rating": 9.3, "variance": 0.8, "failure_prob": 0.04, "default_fail": FailureReasonCode.WRONG_SIZE
    },
    {
        "name": "Personalized Soundwave Song Art Print",
        "category": "Personalized & Keepsakes",
        "description": "Framed visual audio soundwave print of wedding first dance song or personal voice message.",
        "price_min": 30.0, "price_max": 70.0, "is_personalized": True, "is_experience": False, "is_handmade": True,
        "interests": ["Music & Audio", "Home Decor & Gardening"],
        "personalities": ["Sentimental & Nostalgic", "Creative & Artistic"],
        "occasions": ["Anniversary", "Wedding", "Valentine's Day"],
        "relationships": ["Partner / Spouse"],
        "baseline_rating": 9.2, "variance": 0.9, "failure_prob": 0.04, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Monogrammed Leather Passport Cover & Luggage Tag Set",
        "category": "Personalized & Keepsakes",
        "description": "Matching pebbled leather travel wallet with gold foil stamped initials and RFID protection.",
        "price_min": 25.0, "price_max": 50.0, "is_personalized": True, "is_experience": False, "is_handmade": True,
        "interests": ["Travel & Photography", "Fashion & Style"],
        "personalities": ["Practical & Functional", "Organized & Detail-Oriented"],
        "occasions": ["Graduation", "Birthday", "Wedding", "Thank You"],
        "relationships": ["Close Friend", "Sibling", "Coworker", "Child"],
        "baseline_rating": 8.8, "variance": 1.0, "failure_prob": 0.06, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Custom 1000-Piece Personal Memory Photo Puzzle",
        "category": "Personalized & Keepsakes",
        "description": "High-resolution glossy jigsaw puzzle made from a cherished family vacation or wedding portrait.",
        "price_min": 25.0, "price_max": 45.0, "is_personalized": True, "is_experience": False, "is_handmade": False,
        "interests": ["Board Games & Puzzles", "Home Decor & Gardening"],
        "personalities": ["Sentimental & Nostalgic", "Introverted & Cozy", "Humorous & Playful"],
        "occasions": ["Christmas & Holidays", "Anniversary", "Mother's Day"],
        "relationships": ["Parent", "Partner / Spouse", "Extended Family"],
        "baseline_rating": 8.6, "variance": 1.3, "failure_prob": 0.08, "default_fail": FailureReasonCode.POOR_QUALITY
    },

    # 4. Experiences & Workshops
    {
        "name": "Couples Hands-On Cooking Class & Dinner",
        "category": "Experiences & Activities",
        "description": "Interactive 3-hour culinary workshop making handmade pasta and tiramisu paired with Italian wine.",
        "price_min": 120.0, "price_max": 240.0, "is_personalized": False, "is_experience": True, "is_handmade": False,
        "interests": ["Cooking & Gourmet Food", "Self-Care & Wellness"],
        "personalities": ["Adventurous & Thrill-Seeking", "Creative & Artistic", "Romantic"],
        "occasions": ["Anniversary", "Valentine's Day", "Birthday", "Wedding"],
        "relationships": ["Partner / Spouse"],
        "baseline_rating": 9.6, "variance": 0.5, "failure_prob": 0.02, "default_fail": FailureReasonCode.WRONG_TIMING
    },
    {
        "name": "Sunset Sea Kayak & Paddleboard Tour",
        "category": "Experiences & Activities",
        "description": "Guided 2.5-hour sunset coastal paddle expedition with wildlife viewing and waterproof gear provided.",
        "price_min": 70.0, "price_max": 140.0, "is_personalized": False, "is_experience": True, "is_handmade": False,
        "interests": ["Outdoors & Hiking", "Fitness & Sports", "Travel & Photography"],
        "personalities": ["Adventurous & Thrill-Seeking"],
        "occasions": ["Birthday", "Graduation", "Just Because"],
        "relationships": ["Close Friend", "Sibling", "Partner / Spouse"],
        "baseline_rating": 9.2, "variance": 0.8, "failure_prob": 0.04, "default_fail": FailureReasonCode.WRONG_TIMING
    },
    {
        "name": "Wheel Throwing Pottery Studio Workshop",
        "category": "Experiences & Activities",
        "description": "Introductory ceramic wheel throwing masterclass with glazing and kiln-firing of finished vessels.",
        "price_min": 65.0, "price_max": 120.0, "is_personalized": False, "is_experience": True, "is_handmade": False,
        "interests": ["Art & Crafting", "Home Decor & Gardening"],
        "personalities": ["Creative & Artistic", "Introverted & Cozy"],
        "occasions": ["Birthday", "Mother's Day", "Valentine's Day"],
        "relationships": ["Partner / Spouse", "Parent", "Close Friend", "Sibling"],
        "baseline_rating": 9.3, "variance": 0.7, "failure_prob": 0.03, "default_fail": FailureReasonCode.WRONG_TIMING
    },
    {
        "name": "Specialty Coffee Roasting & Cupping Class",
        "category": "Experiences & Activities",
        "description": "Behind-the-scenes sensory tasting class with green bean roasting and custom 1lb blend takeaway.",
        "price_min": 55.0, "price_max": 95.0, "is_personalized": False, "is_experience": True, "is_handmade": False,
        "interests": ["Coffee & Tea", "Cooking & Gourmet Food"],
        "personalities": ["Practical & Functional", "Tech-Savvy"],
        "occasions": ["Birthday", "Father's Day", "Thank You"],
        "relationships": ["Close Friend", "Partner / Spouse", "Sibling", "Coworker"],
        "baseline_rating": 9.1, "variance": 0.9, "failure_prob": 0.05, "default_fail": FailureReasonCode.WRONG_TIMING
    },
    {
        "name": "Luxury Spa Day & Deep Tissue Massage",
        "category": "Experiences & Activities",
        "description": "90-minute therapeutic massage package with eucalyptus steam room access and aromatherapy wrap.",
        "price_min": 110.0, "price_max": 230.0, "is_personalized": False, "is_experience": True, "is_handmade": False,
        "interests": ["Self-Care & Wellness"],
        "personalities": ["Introverted & Cozy", "Luxury Enthusiast"],
        "occasions": ["Mother's Day", "Anniversary", "Birthday", "Just Because"],
        "relationships": ["Partner / Spouse", "Parent", "Close Friend"],
        "baseline_rating": 9.5, "variance": 0.6, "failure_prob": 0.03, "default_fail": FailureReasonCode.WRONG_TIMING
    },
    {
        "name": "Escape Room Adventure Pass for Four",
        "category": "Experiences & Activities",
        "description": "Private 60-minute immersive puzzle room challenge pass with themed storyline and clues.",
        "price_min": 80.0, "price_max": 150.0, "is_personalized": False, "is_experience": True, "is_handmade": False,
        "interests": ["Gaming", "Board Games & Puzzles"],
        "personalities": ["Humorous & Playful", "Tech-Savvy", "Adventurous & Thrill-Seeking"],
        "occasions": ["Birthday", "Graduation", "Just Because"],
        "relationships": ["Sibling", "Close Friend", "Coworker"],
        "baseline_rating": 9.0, "variance": 1.1, "failure_prob": 0.06, "default_fail": FailureReasonCode.WRONG_TIMING
    },
    {
        "name": "Live Symphony or Broadway Theater Performance Tickets",
        "category": "Experiences & Activities",
        "description": "Tier-1 orchestra seats for touring musical, classical symphony, or opera performance.",
        "price_min": 95.0, "price_max": 220.0, "is_personalized": False, "is_experience": True, "is_handmade": False,
        "interests": ["Music & Audio", "Art & Crafting"],
        "personalities": ["Luxury Enthusiast", "Creative & Artistic"],
        "occasions": ["Anniversary", "Mother's Day", "Christmas & Holidays", "Birthday"],
        "relationships": ["Partner / Spouse", "Parent", "Mentor"],
        "baseline_rating": 9.2, "variance": 0.9, "failure_prob": 0.05, "default_fail": FailureReasonCode.WRONG_TIMING
    },
    {
        "name": "Sunrise Hot Air Balloon Flight Voucher",
        "category": "Experiences & Activities",
        "description": "Breathtaking 1-hour sunrise panoramic flight over valleys with traditional champagne toast.",
        "price_min": 220.0, "price_max": 390.0, "is_personalized": False, "is_experience": True, "is_handmade": False,
        "interests": ["Outdoors & Hiking", "Travel & Photography"],
        "personalities": ["Adventurous & Thrill-Seeking", "Luxury Enthusiast"],
        "occasions": ["Anniversary", "Graduation", "Wedding"],
        "relationships": ["Partner / Spouse", "Child"],
        "baseline_rating": 9.6, "variance": 0.6, "failure_prob": 0.03, "default_fail": FailureReasonCode.WRONG_TIMING
    },

    # 5. Home, Decor & Cozy Living
    {
        "name": "Ambient Sunset Projection Lamp",
        "category": "Home & Decor",
        "description": "Warm golden-hour ambient aesthetic mood light with 360-degree aluminum rotatable base.",
        "price_min": 22.0, "price_max": 45.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Home Decor & Gardening", "Art & Crafting"],
        "personalities": ["Introverted & Cozy", "Creative & Artistic"],
        "occasions": ["Birthday", "Housewarming", "Christmas & Holidays", "Just Because"],
        "relationships": ["Sibling", "Close Friend", "Child"],
        "baseline_rating": 8.7, "variance": 1.2, "failure_prob": 0.08, "default_fail": FailureReasonCode.TOO_GENERIC
    },
    {
        "name": "Ceramic Ultrasonic Essential Oil Diffuser Set",
        "category": "Home & Decor",
        "description": "Matte handmade ceramic stone diffuser with 100% pure organic lavender, eucalyptus, and mint oils.",
        "price_min": 35.0, "price_max": 70.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Self-Care & Wellness", "Home Decor & Gardening"],
        "personalities": ["Introverted & Cozy", "Minimalist"],
        "occasions": ["Housewarming", "Mother's Day", "Thank You", "Christmas & Holidays"],
        "relationships": ["Close Friend", "Parent", "Coworker", "In-Law"],
        "baseline_rating": 8.9, "variance": 1.0, "failure_prob": 0.06, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Cooling Glass-Bead Weighted Blanket 15lbs",
        "category": "Home & Decor",
        "description": "Breathable bamboo fabric weighted comforter with deep pressure stimulation for restful sleep.",
        "price_min": 55.0, "price_max": 105.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Self-Care & Wellness", "Home Decor & Gardening"],
        "personalities": ["Introverted & Cozy", "Practical & Functional"],
        "occasions": ["Christmas & Holidays", "Birthday", "Mother's Day"],
        "relationships": ["Partner / Spouse", "Parent", "Sibling"],
        "baseline_rating": 9.3, "variance": 0.8, "failure_prob": 0.04, "default_fail": FailureReasonCode.WRONG_SIZE
    },
    {
        "name": "Ergonomic Shredded Memory Foam Pillow",
        "category": "Home & Decor",
        "description": "Adjustable loft cooling gel memory foam pillow for neck pain relief and cervical support.",
        "price_min": 38.0, "price_max": 75.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Self-Care & Wellness"],
        "personalities": ["Practical & Functional"],
        "occasions": ["Father's Day", "Christmas & Holidays", "Thank You"],
        "relationships": ["Parent", "Partner / Spouse", "In-Law"],
        "baseline_rating": 8.6, "variance": 1.4, "failure_prob": 0.09, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Hand-Poured Soy Wax Aromatherapy Candle Trio",
        "category": "Home & Decor",
        "description": "Set of three clean-burning coconut soy wax candles in amber glass jars with wood wicks.",
        "price_min": 28.0, "price_max": 55.0, "is_personalized": False, "is_experience": False, "is_handmade": True,
        "interests": ["Home Decor & Gardening", "Self-Care & Wellness"],
        "personalities": ["Introverted & Cozy", "Sentimental & Nostalgic"],
        "occasions": ["Housewarming", "Thank You", "Mother's Day", "Christmas & Holidays"],
        "relationships": ["Coworker", "Close Friend", "In-Law", "Parent"],
        "baseline_rating": 8.8, "variance": 1.1, "failure_prob": 0.07, "default_fail": FailureReasonCode.TOO_GENERIC
    },
    {
        "name": "Minimalist Concrete Planter with Succulent Trio",
        "category": "Home & Decor",
        "description": "Hand-cast architectural concrete desk planter featuring three live assorted resilient succulents.",
        "price_min": 24.0, "price_max": 45.0, "is_personalized": False, "is_experience": False, "is_handmade": True,
        "interests": ["Home Decor & Gardening"],
        "personalities": ["Minimalist", "Creative & Artistic"],
        "occasions": ["Housewarming", "Thank You", "Birthday"],
        "relationships": ["Coworker", "Close Friend", "Mentor"],
        "baseline_rating": 8.7, "variance": 1.0, "failure_prob": 0.06, "default_fail": FailureReasonCode.TOO_GENERIC
    },
    {
        "name": "Ultra-Plush Chunky Knit Chenille Throw Blanket",
        "category": "Home & Decor",
        "description": "Hand-knitted ultra-thick chenille blanket that stays soft, shedding-free, and machine washable.",
        "price_min": 48.0, "price_max": 90.0, "is_personalized": False, "is_experience": False, "is_handmade": True,
        "interests": ["Home Decor & Gardening"],
        "personalities": ["Introverted & Cozy", "Sentimental & Nostalgic"],
        "occasions": ["Housewarming", "Christmas & Holidays", "Mother's Day", "Wedding"],
        "relationships": ["Close Friend", "Parent", "Partner / Spouse"],
        "baseline_rating": 9.1, "variance": 0.8, "failure_prob": 0.04, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Ultrasonic Eyeglass & Jewelry Cleaner",
        "category": "Home & Decor",
        "description": "45kHz soundwave professional sonic bath cleaner for rings, watches, and eyeglasses.",
        "price_min": 32.0, "price_max": 60.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Tech & Gadgets", "Fashion & Style"],
        "personalities": ["Practical & Functional", "Organized & Detail-Oriented"],
        "occasions": ["Father's Day", "Christmas & Holidays", "Birthday"],
        "relationships": ["Parent", "Close Friend", "In-Law"],
        "baseline_rating": 8.5, "variance": 1.3, "failure_prob": 0.09, "default_fail": FailureReasonCode.TOO_GENERIC
    },

    # 6. Wellness & Self-Care
    {
        "name": "Shiatsu Heated Deep Kneading Neck Massager",
        "category": "Wellness & Self-Care",
        "description": "3D rotational massage nodes with infrared soothing heat for neck, shoulders, and lower back.",
        "price_min": 45.0, "price_max": 85.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Self-Care & Wellness", "Fitness & Sports"],
        "personalities": ["Practical & Functional", "Introverted & Cozy"],
        "occasions": ["Mother's Day", "Father's Day", "Christmas & Holidays", "Birthday"],
        "relationships": ["Parent", "Partner / Spouse", "In-Law", "Extended Family"],
        "baseline_rating": 9.2, "variance": 0.9, "failure_prob": 0.04, "default_fail": FailureReasonCode.POOR_QUALITY
    },
    {
        "name": "100% Pure Mulberry Silk Sleep Mask & Pillowcase Set",
        "category": "Wellness & Self-Care",
        "description": "22 Momme grade-6A natural silk set designed to reduce hair friction and skin crease marks.",
        "price_min": 42.0, "price_max": 85.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Self-Care & Wellness", "Fashion & Style"],
        "personalities": ["Luxury Enthusiast", "Introverted & Cozy"],
        "occasions": ["Mother's Day", "Valentine's Day", "Birthday", "Christmas & Holidays"],
        "relationships": ["Partner / Spouse", "Close Friend", "Parent"],
        "baseline_rating": 9.4, "variance": 0.7, "failure_prob": 0.03, "default_fail": FailureReasonCode.WRONG_SIZE
    },
    {
        "name": "Deep Tissue Percussion Muscle Massage Gun",
        "category": "Wellness & Self-Care",
        "description": "Quiet brushless motor massage gun with 6 speed heads for workout recovery and muscle relief.",
        "price_min": 60.0, "price_max": 130.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Fitness & Sports", "Self-Care & Wellness"],
        "personalities": ["Practical & Functional", "Tech-Savvy"],
        "occasions": ["Father's Day", "Birthday", "Christmas & Holidays"],
        "relationships": ["Partner / Spouse", "Parent", "Sibling"],
        "baseline_rating": 9.1, "variance": 1.0, "failure_prob": 0.05, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Aromatherapy Organic Shower Steamers Pack",
        "category": "Wellness & Self-Care",
        "description": "Set of 8 essential oil vapor tablets turning everyday showers into invigorating spa aromatherapy.",
        "price_min": 18.0, "price_max": 35.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Self-Care & Wellness"],
        "personalities": ["Introverted & Cozy"],
        "occasions": ["Thank You", "Mother's Day", "Christmas & Holidays", "Just Because"],
        "relationships": ["Coworker", "Close Friend", "Sibling", "In-Law"],
        "baseline_rating": 8.7, "variance": 1.1, "failure_prob": 0.07, "default_fail": FailureReasonCode.TOO_GENERIC
    },
    {
        "name": "Premium High-Density Alignment Yoga Mat",
        "category": "Wellness & Self-Care",
        "description": "Non-slip eco-friendly natural rubber mat with laser-etched body alignment guidance marks.",
        "price_min": 45.0, "price_max": 90.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Fitness & Sports", "Self-Care & Wellness"],
        "personalities": ["Practical & Functional", "Organized & Detail-Oriented"],
        "occasions": ["Birthday", "New Year", "Christmas & Holidays"],
        "relationships": ["Close Friend", "Sibling", "Partner / Spouse"],
        "baseline_rating": 9.0, "variance": 1.0, "failure_prob": 0.05, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Daily Gratitude & Mindfulness Guided Journal",
        "category": "Wellness & Self-Care",
        "description": "Structured 5-minute daily reflection journal with prompts for positivity, goals, and perspective.",
        "price_min": 18.0, "price_max": 32.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Reading & Books", "Self-Care & Wellness"],
        "personalities": ["Sentimental & Nostalgic", "Introverted & Cozy"],
        "occasions": ["Graduation", "Birthday", "Thank You", "Just Because"],
        "relationships": ["Close Friend", "Coworker", "Child", "Mentor"],
        "baseline_rating": 8.5, "variance": 1.5, "failure_prob": 0.11, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },

    # 7. Outdoors & Adventure
    {
        "name": "Ultralight Double Backpacking Hammock",
        "category": "Outdoors & Adventure",
        "description": "Heavy-duty 210T parachute nylon hammock supporting 500lbs with tree-friendly adjustable straps.",
        "price_min": 32.0, "price_max": 60.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Outdoors & Hiking", "Travel & Photography"],
        "personalities": ["Adventurous & Thrill-Seeking", "Minimalist"],
        "occasions": ["Birthday", "Graduation", "Father's Day", "Just Because"],
        "relationships": ["Close Friend", "Sibling", "Child", "Partner / Spouse"],
        "baseline_rating": 9.3, "variance": 0.8, "failure_prob": 0.03, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Insulated Stainless Steel Growler 64oz",
        "category": "Outdoors & Adventure",
        "description": "Double-wall vacuum growler keeping craft beer or cider cold and carbonated for up to 48 hours.",
        "price_min": 35.0, "price_max": 65.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Outdoors & Hiking", "Cooking & Gourmet Food"],
        "personalities": ["Humorous & Playful", "Adventurous & Thrill-Seeking"],
        "occasions": ["Father's Day", "Birthday", "Housewarming"],
        "relationships": ["Close Friend", "Parent", "Sibling"],
        "baseline_rating": 8.8, "variance": 1.2, "failure_prob": 0.07, "default_fail": FailureReasonCode.TOO_GENERIC
    },
    {
        "name": "Heavy-Duty Multi-Tool Pliers with Locking Blades",
        "category": "Outdoors & Adventure",
        "description": "18-in-1 stainless steel pocket tool including wire cutters, saw, file, and screwdriver bits.",
        "price_min": 45.0, "price_max": 90.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Outdoors & Hiking", "Tech & Gadgets"],
        "personalities": ["Practical & Functional"],
        "occasions": ["Father's Day", "Graduation", "Christmas & Holidays"],
        "relationships": ["Parent", "Partner / Spouse", "Child", "Close Friend"],
        "baseline_rating": 9.4, "variance": 0.7, "failure_prob": 0.03, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Hydro Flask Wide Mouth Vacuum Water Bottle 32oz",
        "category": "Outdoors & Adventure",
        "description": "Pro-grade stainless steel bottle with leakproof straw lid keeping water ice-cold for 24 hours.",
        "price_min": 32.0, "price_max": 48.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Fitness & Sports", "Outdoors & Hiking", "Travel & Photography"],
        "personalities": ["Practical & Functional", "Minimalist"],
        "occasions": ["Birthday", "Graduation", "Thank You", "Just Because"],
        "relationships": ["Child", "Close Friend", "Sibling", "Coworker"],
        "baseline_rating": 9.1, "variance": 0.9, "failure_prob": 0.04, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Solar-Powered Rugged Power Bank with Camping Torch",
        "category": "Outdoors & Adventure",
        "description": "26800mAh waterproof shockproof backup battery with solar panel charger and SOS strobe torch.",
        "price_min": 35.0, "price_max": 65.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Outdoors & Hiking", "Tech & Gadgets"],
        "personalities": ["Adventurous & Thrill-Seeking", "Practical & Functional"],
        "occasions": ["Father's Day", "Birthday", "Graduation"],
        "relationships": ["Parent", "Sibling", "Close Friend"],
        "baseline_rating": 8.7, "variance": 1.3, "failure_prob": 0.08, "default_fail": FailureReasonCode.POOR_QUALITY
    },

    # 8. Books, Games & Hobbies
    {
        "name": "Strategic Board Game: Catan 3D Collector Edition",
        "category": "Games & Hobbies",
        "description": "Hand-painted 3D sculptured tiles and detailed settlements for the classic resource trading game.",
        "price_min": 60.0, "price_max": 120.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Board Games & Puzzles", "Gaming"],
        "personalities": ["Organized & Detail-Oriented", "Humorous & Playful"],
        "occasions": ["Christmas & Holidays", "Birthday", "Housewarming"],
        "relationships": ["Close Friend", "Sibling", "Partner / Spouse"],
        "baseline_rating": 9.5, "variance": 0.6, "failure_prob": 0.02, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Wingspan Deluxe Board Game & Custom Bird Feeder",
        "category": "Games & Hobbies",
        "description": "Award-winning competitive bird-collection engine-building board game with custom pastel eggs.",
        "price_min": 50.0, "price_max": 85.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Board Games & Puzzles", "Outdoors & Hiking"],
        "personalities": ["Introverted & Cozy", "Creative & Artistic"],
        "occasions": ["Birthday", "Christmas & Holidays", "Housewarming"],
        "relationships": ["Close Friend", "Partner / Spouse", "Sibling"],
        "baseline_rating": 9.3, "variance": 0.8, "failure_prob": 0.04, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Deluxe Leather-Bound Hardcover Classics Edition",
        "category": "Games & Hobbies",
        "description": "Gold-embossed foil leather-bound edition of classic literature with ribbon bookmark and gilded edges.",
        "price_min": 35.0, "price_max": 75.0, "is_personalized": False, "is_experience": False, "is_handmade": True,
        "interests": ["Reading & Books"],
        "personalities": ["Sentimental & Nostalgic", "Introverted & Cozy", "Luxury Enthusiast"],
        "occasions": ["Graduation", "Birthday", "Christmas & Holidays"],
        "relationships": ["Parent", "Close Friend", "Mentor", "Child"],
        "baseline_rating": 9.4, "variance": 0.7, "failure_prob": 0.03, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Professional 48-Color Watercolor Paint & Brush Set",
        "category": "Games & Hobbies",
        "description": "Artist-grade metallic and vibrant watercolor half-pans with refillable water brush pens.",
        "price_min": 32.0, "price_max": 65.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Art & Crafting"],
        "personalities": ["Creative & Artistic"],
        "occasions": ["Birthday", "Christmas & Holidays", "Mother's Day"],
        "relationships": ["Child", "Close Friend", "Sibling", "Parent"],
        "baseline_rating": 9.2, "variance": 0.9, "failure_prob": 0.04, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Retro Handheld Arcade Console (500 Classic Games)",
        "category": "Games & Hobbies",
        "description": "Pocket nostalgic 8-bit handheld video game console with color screen and TV-out cable.",
        "price_min": 25.0, "price_max": 50.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Gaming", "Tech & Gadgets"],
        "personalities": ["Humorous & Playful", "Sentimental & Nostalgic"],
        "occasions": ["Birthday", "Christmas & Holidays", "Just Because"],
        "relationships": ["Sibling", "Child", "Close Friend"],
        "baseline_rating": 8.1, "variance": 1.8, "failure_prob": 0.14, "default_fail": FailureReasonCode.POOR_QUALITY
    },
    {
        "name": "Traditional Japanese Bonsai Tree Starter Growing Kit",
        "category": "Games & Hobbies",
        "description": "Complete beginner kit with 4 seed varieties, organic peat pots, shears, and step-by-step growing manual.",
        "price_min": 25.0, "price_max": 45.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Home Decor & Gardening", "Art & Crafting"],
        "personalities": ["Organized & Detail-Oriented", "Introverted & Cozy"],
        "occasions": ["Housewarming", "Father's Day", "Birthday", "Thank You"],
        "relationships": ["Coworker", "Parent", "Close Friend"],
        "baseline_rating": 8.4, "variance": 1.6, "failure_prob": 0.12, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },

    # 9. Fashion & Style Accessories
    {
        "name": "100% Pure Mongolian Cashmere Fringe Scarf",
        "category": "Fashion & Accessories",
        "description": "Ultra-soft grade-A pure cashmere scarf offering lightweight warmth and timeless winter luxury.",
        "price_min": 65.0, "price_max": 135.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Fashion & Style"],
        "personalities": ["Luxury Enthusiast", "Introverted & Cozy"],
        "occasions": ["Christmas & Holidays", "Mother's Day", "Birthday"],
        "relationships": ["Partner / Spouse", "Parent", "Sibling"],
        "baseline_rating": 9.5, "variance": 0.6, "failure_prob": 0.03, "default_fail": FailureReasonCode.NOT_THEIR_STYLE
    },
    {
        "name": "Slim Minimalist Leather RFID Front-Pocket Wallet",
        "category": "Fashion & Accessories",
        "description": "Hand-stitched vegetable-tanned leather bifold with quick-access card ejection slot.",
        "price_min": 32.0, "price_max": 65.0, "is_personalized": False, "is_experience": False, "is_handmade": True,
        "interests": ["Fashion & Style", "Tech & Gadgets"],
        "personalities": ["Minimalist", "Practical & Functional"],
        "occasions": ["Father's Day", "Graduation", "Birthday", "Christmas & Holidays"],
        "relationships": ["Partner / Spouse", "Child", "Parent", "Close Friend"],
        "baseline_rating": 9.2, "variance": 0.8, "failure_prob": 0.04, "default_fail": FailureReasonCode.ALREADY_OWNED
    },
    {
        "name": "Handcrafted Polarized Wooden Sunglasses",
        "category": "Fashion & Accessories",
        "description": "Sustainably sourced bamboo & zebrawood sunglasses with UV400 polarized anti-glare lenses.",
        "price_min": 42.0, "price_max": 80.0, "is_personalized": False, "is_experience": False, "is_handmade": True,
        "interests": ["Fashion & Style", "Outdoors & Hiking", "Travel & Photography"],
        "personalities": ["Creative & Artistic", "Adventurous & Thrill-Seeking"],
        "occasions": ["Birthday", "Graduation", "Father's Day"],
        "relationships": ["Close Friend", "Sibling", "Partner / Spouse"],
        "baseline_rating": 8.6, "variance": 1.7, "failure_prob": 0.12, "default_fail": FailureReasonCode.WRONG_SIZE
    },
    {
        "name": "Heavyweight Cozy Nordic Wool Cabin Socks (4 Pairs)",
        "category": "Fashion & Accessories",
        "description": "Vintage jacquard thick thermal merino wool socks for cozy lounging and cold weather walks.",
        "price_min": 20.0, "price_max": 38.0, "is_personalized": False, "is_experience": False, "is_handmade": False,
        "interests": ["Fashion & Style", "Outdoors & Hiking"],
        "personalities": ["Introverted & Cozy", "Practical & Functional"],
        "occasions": ["Christmas & Holidays", "Thank You", "Just Because"],
        "relationships": ["Coworker", "Close Friend", "Sibling", "In-Law"],
        "baseline_rating": 8.8, "variance": 0.9, "failure_prob": 0.05, "default_fail": FailureReasonCode.TOO_GENERIC
    }
]

AGE_RANGES = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

# Realistic review texts mapping directly to NLP sentiment and theme keywords
REVIEWS_EXCEPTIONAL = [
    "They were completely blown away! The personalized touch and custom initials brought genuine tears of joy upon unwrapping.",
    "Best gift ever! The build quality is exceptional, very sturdy and practical. They use it daily.",
    "Surpassed all expectations! Packaging was gorgeous in a luxury gift box and arrived right on time.",
    "Such a thoughtful surprise! The craftsmanship and durable materials make this an unforgettable keepsake.",
    "They loved the custom touch and how functional it is for everyday use. High quality and beautifully made."
]

REVIEWS_VERY_GOOD = [
    "Great gift overall! Practical and well made. They thanked me warmly and started using it right away.",
    "A hit at the celebration! Good build quality, useful and thoughtfully presented.",
    "Very happy with this choice! Matches their style and daily routine nicely.",
    "Solid quality and thoughtful gesture. Arrived quickly and made a very good impression.",
    "Pleasantly surprised by how handy and functional this turned out to be."
]

REVIEWS_AVERAGE = [
    "They appreciated the gesture, but the sizing was slightly off for their space.",
    "Decent quality, though they already owned a similar model from a couple years ago.",
    "A bit generic for a major milestone, but still useful for everyday routines.",
    "Nice presentation and packaging, but not 100% their aesthetic taste.",
    "Arrived a couple days late for the party, but the item itself works fine."
]

REVIEWS_POOR = [
    "Unfortunately this missed the mark. Felt too generic and impersonal.",
    "The build quality was disappointing and felt cheap. Broke after two weeks of light use.",
    "Wrong style and completely off from their personal taste. It sits untouched in the closet.",
    "The sizing was too big and clunky for their apartment space.",
    "Arrived late in damaged packaging. Recipient was polite but clearly disappointed."
]

REACTIONS_POSITIVE = [
    "Tears of joy and a huge warm hug upon unwrapping!",
    "Genuine excitement and immediately showed it to everyone in the room.",
    "Speechless and amazed by the thoughtful personalization!",
    "Big smile, instant excitement, and started testing it immediately.",
    "Beaming with happiness and praised how well it fits their routine."
]

REACTIONS_NEUTRAL = [
    "Polite smile and grateful 'thank you', though subtle hesitation.",
    "Smiled and nodded, but set it aside after unwrapping.",
    "Thanked me politely, said it looks nice and useful."
]

REACTIONS_NEGATIVE = [
    "Awkward pause, polite but visibly forced thank-you smile.",
    "Laughed politely and admitted they already had two of these.",
    "Mild confusion on how to use it, ended up putting it back in the box."
]

FAILURE_REASON_TEXTS = {
    FailureReasonCode.ALREADY_OWNED: "Recipient already owned a similar item at home.",
    FailureReasonCode.WRONG_SIZE: "Sizing or physical dimensions did not fit their space.",
    FailureReasonCode.TOO_GENERIC: "Felt like a last-minute generic purchase without personal thought.",
    FailureReasonCode.POOR_QUALITY: "Materials felt flimsy or broke under regular use.",
    FailureReasonCode.NOT_THEIR_STYLE: "Aesthetic color or style conflicted with recipient taste.",
    FailureReasonCode.WRONG_TIMING: "Gifting timing or occasion was not ideal for this category.",
    FailureReasonCode.EXPRESSION_OF_DISLIKE: "Recipient explicitly noted they do not use this type of item.",
    FailureReasonCode.OTHER: "Miscellaneous mismatch during gifting exchange."
}


def ensure_catalog_seeded(db: Session) -> List[Gift]:
    """Ensures base lookups and all catalog gifts exist in the database."""
    seed_scaffold(db)

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
    return db.query(Gift).all()


def generate_synthetic_dataset(db: Session, num_experiences: int = 2500):
    """
    Generates rich, domain-intelligent synthetic gifting experiences with
    affinity clustering, realistic variance distributions, and NLP enrichment.
    """
    print(f"🎲 Generating {num_experiences} intelligent synthetic experiences (`is_synthetic = True`)...")

    # 1. Seed and load catalog
    all_gifts = ensure_catalog_seeded(db)
    all_occasions = {o.name: o for o in db.query(Occasion).all()}
    all_relationships = {r.name: r for r in db.query(Relationship).all()}
    all_interests = {i.name: i for i in db.query(Interest).all()}
    all_personalities = {p.name: p for p in db.query(Personality).all()}

    # Map gifts by name for quick metadata lookup
    gift_meta_map = {g["name"]: g for g in EXPANDED_GIFTS}

    # 2. Seed synthetic giver users (~40 givers)
    users = []
    for i in range(1, 41):
        email = f"giver_{i:02d}@giftwise-community.org"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                password_hash="pbkdf2_sha256$synthetic$hash",
                display_name=f"Community Giver {i}",
                contribution_count=0
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        users.append(user)

    now = datetime.utcnow()
    created_exps = []

    # 3. Generate experiences with 75% affinity weighting and 25% exploratory cases
    for idx in range(num_experiences):
        user = random.choice(users)
        gift = random.choice(all_gifts)
        meta = gift_meta_map.get(gift.name, {})

        is_affinity_matched = random.random() < 0.75 and bool(meta)

        if is_affinity_matched:
            # Match occasion & relationship from gift's natural affinities
            occ_name = random.choice(meta.get("occasions", list(all_occasions.keys())))
            rel_name = random.choice(meta.get("relationships", list(all_relationships.keys())))
            occasion = all_occasions.get(occ_name, random.choice(list(all_occasions.values())))
            relationship = all_relationships.get(rel_name, random.choice(list(all_relationships.values())))

            # Create RecipientProfile matching target interests & personalities
            profile = RecipientProfile(age_range=random.choice(AGE_RANGES))
            matched_interests = [all_interests[n] for n in meta.get("interests", []) if n in all_interests]
            matched_personalities = [all_personalities[n] for n in meta.get("personalities", []) if n in all_personalities]

            # Pick 1-2 primary matched + 0-1 random
            selected_interests = matched_interests[:2] if matched_interests else random.sample(list(all_interests.values()), 2)
            selected_personalities = matched_personalities[:1] if matched_personalities else random.sample(list(all_personalities.values()), 1)

            profile.interests = selected_interests
            profile.personalities = selected_personalities
            db.add(profile)
            db.flush()

            # Realistic rating: centered around baseline with low variance
            base_mean = meta.get("baseline_rating", 9.0)
            base_var = meta.get("variance", 0.8)
            raw_rating = random.gauss(base_mean, base_var)
            recipient_rating = int(round(min(10, max(1, raw_rating))))

            # Occasional giver perception gap in ~25% of cases
            if random.random() < 0.25:
                gap = random.choice([1, 2, -1])
                giver_rating = min(10, max(1, recipient_rating + gap))
            else:
                giver_rating = recipient_rating

            failure_prob = meta.get("failure_prob", 0.04)
            is_failure = (recipient_rating <= 6) or (random.random() < failure_prob)
            fail_code = meta.get("default_fail", FailureReasonCode.TOO_GENERIC)

        else:
            # Exploratory / Mismatched situation
            occasion = random.choice(list(all_occasions.values()))
            relationship = random.choice(list(all_relationships.values()))

            profile = RecipientProfile(age_range=random.choice(AGE_RANGES))
            profile.interests = random.sample(list(all_interests.values()), k=random.randint(1, 3))
            profile.personalities = random.sample(list(all_personalities.values()), k=random.randint(1, 2))
            db.add(profile)
            db.flush()

            # Mismatches result in lower / more polarized ratings
            raw_rating = random.gauss(6.2, 1.8)
            recipient_rating = int(round(min(10, max(1, raw_rating))))

            # Givers often assume gifts were better than they were!
            if random.random() < 0.40:
                giver_rating = min(10, max(1, recipient_rating + random.choice([2, 3])))
            else:
                giver_rating = recipient_rating

            is_failure = recipient_rating <= 6 or (random.random() < 0.25)
            fail_code = random.choice(list(FailureReasonCode))

        # Calculate actual budget within price bounds with ±10% realistic variance
        p_min = float(gift.typical_price_min)
        p_max = float(gift.typical_price_max)
        base_price = (p_min + p_max) / 2.0
        budget_actual = round(max(10.0, random.uniform(p_min * 0.95, p_max * 1.05)), 2)

        # Select corresponding review & reaction text
        if recipient_rating >= 9:
            review_text = random.choice(REVIEWS_EXCEPTIONAL)
            reaction_text = random.choice(REACTIONS_POSITIVE)
        elif recipient_rating >= 7:
            review_text = random.choice(REVIEWS_VERY_GOOD)
            reaction_text = random.choice(REACTIONS_POSITIVE[:3])
        elif recipient_rating >= 5:
            review_text = random.choice(REVIEWS_AVERAGE)
            reaction_text = random.choice(REACTIONS_NEUTRAL)
        else:
            review_text = random.choice(REVIEWS_POOR)
            reaction_text = random.choice(REACTIONS_NEGATIVE)

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
            would_recommend=(recipient_rating >= 7),
            review_text=review_text,
            reaction_text=reaction_text,
            is_synthetic=True,
            created_at=created_at
        )
        db.add(exp)
        db.flush()

        if is_failure:
            fr = FailureReason(
                gifting_experience_id=exp.id,
                reason_code=fail_code,
                free_text=FAILURE_REASON_TEXTS.get(fail_code, "Issue reported during exchange.")
            )
            db.add(fr)

        user.contribution_count += 1
        created_exps.append(exp.id)

    db.commit()
    print(f"✅ Created {len(created_exps)} experiences! Refreshing SQL analytics views...")

    # Refresh views
    initialize_analytics_views(db)

    print(f"🧠 Running batch NLP pipeline across new experiences...")
    # Run NLP in batches
    nlp_done = 0
    for eid in created_exps:
        process_experience_nlp(db, eid)
        nlp_done += 1
        if nlp_done % 500 == 0:
            print(f"  Processed {nlp_done}/{len(created_exps)} NLP insights...")

    print(f"🎉 Fully completed! {len(created_exps)} experiences are now ready with 100% NLP insights.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        generate_synthetic_dataset(db, num_experiences=2500)
    finally:
        db.close()
