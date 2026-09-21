# 🎁 GiftWise: Community-Driven Gift Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Pytest-22%20Passed-brightgreen.svg)](file:///Users/akshayaverma/GiftWise/backend/tests)

**GiftWise** is an intelligent, community-driven gift recommendation and analytics platform designed to solve gift-giving uncertainty. It uses empirical recipient outcome data, Bayesian confidence scoring, NLP sentiment analysis, and analytical SQL views to deliver transparent, data-backed gift recommendations.

---

## ✨ Features

- **🧠 Bayesian Recommendation Engine**:
  - Uses empirical recipient outcome ratings to rank candidates.
  - Applies Bayesian shrinkage towards global mean $m$ with prior weight $C=10.0$ to prevent small-sample bias.
  - Assigns confidence tiers (`High`, `Medium`, `Low`) based on sample size $n$.
  - Includes transparent explanations detailing *why* a gift is recommended or flagged for potential failure.
  - Automatically applies **Cold-Start Fallback** with relaxed constraints when exact query matches yield zero results.

- **💬 Natural Language Processing (NLP)**:
  - **Sentiment Analysis**: VADER sentiment scoring on user review and recipient reaction text.
  - **Theme Extraction**: spaCy entity and noun chunk extraction to identify key emotional and practical themes.
  - **Auto-Triggering**: Runs asynchronously whenever a new gifting experience is created.

- **📊 SQL Analytics Suite (7 Analytical Views)**:
  1. `view_rating_by_occasion_relationship`: Average ratings by occasion & relationship.
  2. `view_rating_by_budget_bucket`: Rating metrics grouped into price buckets.
  3. `view_giver_vs_recipient_satisfaction_gap`: Giver vs recipient perception gap.
  4. `view_personalized_vs_non_personalized`: Personalized vs standard gift performance.
  5. `view_failure_reason_frequency`: Frequency breakdown of failure reasons.
  6. `view_sample_size_vs_rating_variance`: Sample size vs variance for confidence validation.
  7. `view_reliable_vs_polarizing_gifts`: Categorization of gifts into Reliable Winners, Polarizing, or Consistently Low.

- **🎨 Modern Dark Glassmorphism Frontend**:
  - Served directly from `backend/app/static/index.html`.
  - Responsive design featuring tabbed views for Recommendation Search, Experience Logging, and Analytics Dashboard.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI, Pydantic V2, Uvicorn
- **Database**: SQLAlchemy ORM (Supports PostgreSQL & SQLite with automatic local fallback)
- **NLP**: VADER Sentiment (`nltk`), spaCy (`en_core_web_sm`)
- **Testing**: Pytest & FastAPI `TestClient`

---

## 🚀 Quick Start

### 1. Installation & Environment Setup

```bash
# Clone the repository
git clone https://github.com/kryptonn19/GiftWise.git
cd GiftWise

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Synthetic Seed Data

Populates reference lookups, gift catalog, and ~750 synthetic gifting experiences (`is_synthetic=True`):

```bash
PYTHONPATH=. python backend/scripts/generate_synthetic_data.py
```

### 3. Run Development Server

```bash
PYTHONPATH=. uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the application in your browser:
- **Interactive Web App**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run Automated Test Suite

```bash
PYTHONPATH=. pytest
```

---

## 📡 API Reference Overview

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/lookups` | `GET` | Fetches reference Occasions, Relationships, Interests, and Personalities. |
| `/api/gifts` | `GET` / `POST` | List all catalog gifts or register a new gift. |
| `/api/experiences` | `GET` / `POST` | Submit a gifting outcome experience or list logged experiences. |
| `/api/recommendations` | `POST` | Generate Bayesian gift recommendations for a recipient profile. |
| `/api/analytics/*` | `GET` | Retrieve analytical SQL views (satisfaction gap, failure rates, budget buckets). |

---

## 📄 License

Created by **Khushi** & maintained by the GiftWise team.
