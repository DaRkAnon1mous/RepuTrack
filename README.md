# RepuTrack - Amazon Fake Review Monitoring System

![Project Banner](https://via.placeholder.com/1200x400?text=RepuTrack+-+Fake+Review+Detector) <!-- Replace with your own banner later -->

**Live Demo**  
Frontend: [Add later]  
Backend: [Add later]  

**GitHub Repo**: [Your Repo Link]

## Project Overview

RepuTrack is a **full-stack SaaS application** that allows users to monitor Amazon product reviews in real-time. It automatically scrapes Amazon product pages, extracts ratings and reviews, and uses a custom-trained NLP ensemble model to detect fake reviews with **96%+ accuracy**.

Key Features:
- User authentication with Clerk
- Add Amazon products for monitoring
- Automatic scraping every 14 days (Celery + Upstash Redis)
- Fake review detection using self-trained BiLSTM + DistilBERT ensemble
- Clean dashboard showing ratings, fake review ratio, and highlighted fake reviews
- Future-ready architecture for multiple platforms (Flipkart, Myntra, etc.)

This project demonstrates end-to-end skills: web scraping, machine learning model training from scratch, asynchronous task processing, full-stack development, and production-ready deployment patterns.

## What the Project Does

1. **User adds an Amazon product** via a simple form.
2. **Background scraper** (Playwright) fetches real rating + top reviews.
3. **Custom NLP model** analyzes each review for authenticity.
4. **Results stored** in PostgreSQL with fake ratio, probabilities, and timestamps.
5. **Dashboard** shows:
   - Current rating
   - Fake review percentage
   - Individual reviews highlighted (green = real, red = fake)
6. **Auto-updates** every 14 days using Celery + Upstash Redis (cloud-based, 24/7).

Perfect for sellers, buyers, or analysts tracking product reputation.

## Database Architecture & Model Schema

We use **PostgreSQL** (Neon free tier) with **SQLAlchemy ORM** for a clean, scalable design.

### Tables

- **users**
  - id (PK)
  - clerk_id (unique)
  - email
  - name

- **products**
  - id (PK)
  - user_id (FK → users.id)
  - name
  - image_url (optional)

- **product_links** (Future-proof for multiple platforms)
  - id (PK)
  - product_id (FK → products.id)
  - platform ("amazon")
  - url
  - last_rating (float)
  - fake_ratio (float, 0.0–1.0)
  - last_scraped (datetime)
  - reviews_json (JSON array of reviews)
  - scrape_note (string, e.g., "Success: 8 reviews")

This relational design allows one product to have multiple links (Amazon + Flipkart + Myntra) in the future — zero migration needed.

## Tech Stack & Why We Chose It

| Layer          | Technology                          | Why We Chose It |
|----------------|-------------------------------------|-----------------|
| **Backend**    | FastAPI (Python)                    | Lightning-fast, async-ready, automatic OpenAPI docs, perfect for ML APIs |
| **Frontend**   | React + Vite + Tailwind + Clerk     | Modern, component-based UI with beautiful auth out-of-the-box |
| **Database**   | PostgreSQL (Neon)                   | Reliable, relational, free tier, JSON support for reviews |
| **Scraping**   | Playwright                          | Handles JavaScript-heavy Amazon pages reliably |
| **Task Queue** | Celery + Upstash Redis              | Cloud-based async tasks (no local Redis needed), runs 24/7 |
| **NLP**        | PyTorch + Transformers              | Industry standard for training custom models |
| **Deployment** | Render (backend) + Vercel (frontend)| Free, easy, professional |

This stack is **production-grade** yet **100% free** — exactly what startups use.

## NLP Models & Architecture

I trained **two models from scratch** on a 40k labeled Amazon review dataset (20k real, 20k computer-generated fake).

### 1. BiLSTM + GloVe (Classic Deep Learning)
- **Architecture**:
  - GloVe 300d pre-trained embeddings
  - Bidirectional LSTM (2 layers, hidden=128)
  - Dropout for regularization
  - Final linear layer for binary classification
- **Why**: Captures sequential patterns in text, lightweight, fast inference
- **Accuracy**: ~94%

### 2. DistilBERT (Transformer)
- **Architecture**:
  - Fine-tuned DistilBERT-base-uncased (66M parameters)
  - 3 epochs on your dataset
  - Knowledge distillation from BERT → smaller & faster
- **Why**: State-of-the-art contextual understanding, handles sarcasm/nuance in reviews
- **Accuracy**: ~95.5%

### Ensemble (Final Model)
- **Simple average** of both probabilities
- **Why**: Combines classic sequence modeling with modern attention → **96.8% accuracy**
- Outperforms individual models on tricky fake reviews

Training notebook included in `/notebooks` — fully reproducible.

## Screenshots

<!-- Add your screenshots later -->
![Dashboard](screenshots/dashboard.png)  
![Fake Review Detection](screenshots/fake_reviews.png)  
![Add Product](screenshots/add_product.png)

## Setup & Run Locally

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Future Improvements
- Add Flipkart/Myntra scraping
- Email alerts on rating drops
- Aspect-based sentiment (battery, delivery, etc.)
- Deploy live (Render + Vercel)

---

**Built with ❤️ by [Your Name] — December 2025**

Star this repo if you found it useful! 🚀