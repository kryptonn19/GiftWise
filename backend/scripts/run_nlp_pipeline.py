"""
Batch NLP Pipeline Execution Script (Milestone 5)

Processes all logged gifting experiences in the database and extracts:
- VADER sentiment scores
- Extracted gifting themes
- Sentence-level positive and negative reason tags
Populates review_nlp_insights table.
"""

import sys
import os
from sqlalchemy.orm import Session

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.db.session import SessionLocal
from backend.app.models.db_models import GiftingExperience
from backend.app.nlp.pipeline import process_experience_nlp

def run_batch_nlp(db: Session):
    experiences = db.query(GiftingExperience).all()
    total = len(experiences)
    print(f"🧠 Running NLP Pipeline on {total} gifting experiences...")

    processed = 0
    for exp in experiences:
        process_experience_nlp(db, exp.id)
        processed += 1
        if processed % 100 == 0:
            print(f"  Processed {processed}/{total} experiences...")

    print(f"✅ Successfully processed NLP insights for all {processed} experiences!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_batch_nlp(db)
    finally:
        db.close()
