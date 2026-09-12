"""
GiftWise Rule-Based & Lexicon NLP Pipeline (Milestone 5)

Performs:
1. VADER Sentiment Scoring (-1.0 to 1.0)
2. spaCy Noun-Phrase & Gifting Theme Keyword Extraction
3. Sentence-level positive and negative reason tagging
4. Database persistence into review_nlp_insights
"""

import spacy
from typing import Dict, Any, List, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.orm import Session
from backend.app.models.db_models import GiftingExperience, ReviewNLPInsight

# Initialize VADER Analyzer
vader_analyzer = SentimentIntensityAnalyzer()

# Load spaCy English model (with fallback)
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = spacy.blank("en")

# Curated Gifting Theme Taxonomy
THEME_TAXONOMY = {
    "personalization": ["personal", "custom", "engraved", "initials", "monogram", "touch", "thoughtful", "name", "personalized"],
    "usefulness": ["practical", "useful", "everyday", "use", "handy", "functional", "daily", "workhorse"],
    "sentimentality": ["tears", "emotional", "meaningful", "memories", "sentimental", "special", "heartfelt"],
    "surprise": ["surprise", "shocked", "unexpected", "amazed", "unwrapping", "excitement", "thrilled"],
    "quality": ["quality", "durable", "sturdy", "flimsy", "craftsmanship", "materials", "well-made", "cheap", "broken"],
    "size_and_fit": ["size", "fit", "space", "too big", "too small", "sizing", "closet", "apartment", "dimension"],
    "timing": ["late", "arrived", "shipping", "timing", "delay", "on time", "quick"],
    "packaging": ["packaging", "box", "presentation", "wrapped", "gift box", "unboxing"]
}

def analyze_review_text(review_text: Optional[str], reaction_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes review and reaction text to extract sentiment score, gifting themes, and positive/negative reasons.
    """
    full_text = " ".join([t for t in [review_text, reaction_text] if t and t.strip()])
    if not full_text:
        return {
            "sentiment_score": 0.0,
            "extracted_themes": [],
            "extracted_positive_reasons": [],
            "extracted_negative_reasons": []
        }

    # 1. VADER Sentiment Scoring
    vader_scores = vader_analyzer.polarity_scores(full_text)
    sentiment_score = round(vader_scores["compound"], 4)

    # 2. spaCy Parsing & Theme Extraction
    doc = nlp(full_text)
    lower_text = full_text.lower()
    
    extracted_themes = set()
    for theme, keywords in THEME_TAXONOMY.items():
        if any(kw in lower_text for kw in keywords):
            extracted_themes.add(theme)

    # Extract additional noun phrases from spaCy if available
    if hasattr(doc, "noun_chunks"):
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            if len(chunk_text) > 3 and chunk_text not in ["they", "it", "this", "that"]:
                for theme, keywords in THEME_TAXONOMY.items():
                    if any(kw in chunk_text for kw in keywords):
                        extracted_themes.add(theme)

    # 3. Sentence-level Reason Tagging
    positive_reasons = []
    negative_reasons = []

    # Split by sentence
    sentences = [sent.text.strip() for sent in doc.sents] if hasattr(doc, "sents") else full_text.split(".")
    
    for sentence in sentences:
        if not sentence:
            continue
        sent_scores = vader_analyzer.polarity_scores(sentence)
        sent_compound = sent_scores["compound"]
        
        # Check if sentence contains theme keywords
        matched_themes = [
            theme for theme, kws in THEME_TAXONOMY.items() 
            if any(kw in sentence.lower() for kw in kws)
        ]

        if matched_themes:
            reason_entry = f"[{', '.join(matched_themes)}] {sentence}"
            if sent_compound >= 0.10:
                positive_reasons.append(reason_entry)
            elif sent_compound <= -0.10:
                negative_reasons.append(reason_entry)

    return {
        "sentiment_score": sentiment_score,
        "extracted_themes": sorted(list(extracted_themes)),
        "extracted_positive_reasons": positive_reasons[:5],
        "extracted_negative_reasons": negative_reasons[:5]
    }

def process_experience_nlp(db: Session, gifting_experience_id: str) -> Optional[ReviewNLPInsight]:
    """
    Extracts NLP insights for a given gifting experience and persists to review_nlp_insights table.
    """
    exp = db.query(GiftingExperience).filter(GiftingExperience.id == gifting_experience_id).first()
    if not exp:
        return None

    analysis = analyze_review_text(exp.review_text, exp.reaction_text)

    nlp_insight = db.query(ReviewNLPInsight).filter(
        ReviewNLPInsight.gifting_experience_id == exp.id
    ).first()

    if not nlp_insight:
        nlp_insight = ReviewNLPInsight(gifting_experience_id=exp.id)
        db.add(nlp_insight)

    nlp_insight.sentiment_score = analysis["sentiment_score"]
    nlp_insight.extracted_themes = analysis["extracted_themes"]
    nlp_insight.extracted_positive_reasons = analysis["extracted_positive_reasons"]
    nlp_insight.extracted_negative_reasons = analysis["extracted_negative_reasons"]

    db.commit()
    db.refresh(nlp_insight)
    return nlp_insight
