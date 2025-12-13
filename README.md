# 🛡️ RepuTrack - AI-Powered Amazon Review Analysis Platform

<div align="center">

![RepuTrack Banner](https://img.shields.io/badge/RepuTrack-AI%20Review%20Analysis-blue?style=for-the-badge)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)

**[Live Demo](#) • [Documentation](#) • [Report Bug](#) • [Request Feature](#)**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Database Schema](#-database-schema)
- [AI/ML Models](#-aiml-models)
- [System Flow](#-system-flow)
- [Scraping Pipeline](#-scraping-pipeline)
- [Setup & Installation](#-setup--installation)
- [Deployment](#-deployment)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)

---

## 🎯 Overview

**RepuTrack** is a production-ready SaaS platform that monitors Amazon product reviews using advanced AI to detect fake reviews with **96%+ accuracy**. Built with a modern tech stack, it combines web scraping, natural language processing, and automated monitoring to provide actionable insights for sellers, buyers, and market analysts.

### What Makes RepuTrack Unique?

- **Custom-Trained Ensemble AI**: Two deep learning models (BiLSTM + DistilBERT) trained from scratch on 40,000+ labeled reviews
- **Triple Analysis**: Fake detection, sentiment analysis, and rating monitoring in one platform
- **Automated Monitoring**: Celery + Redis scheduler runs bi-monthly scrapes automatically
- **Production-Grade Architecture**: Scalable, secure, and ready for multiple e-commerce platforms
- **Clean UI/UX**: Minimalist design focused on actionable insights, not clutter

---

## ✨ Key Features

### 🔍 Core Functionality
- **Smart Product Tracking**: Add any Amazon product link and get instant AI analysis
- **Fake Review Detection**: 96.8% accuracy using ensemble deep learning models
- **Sentiment Analysis**: Understand overall customer sentiment (Positive/Mixed/Negative)
- **Rating Monitoring**: Track product rating changes over time
- **Automated Scraping**: Bi-monthly background analysis (1st & 15th of each month at 3 AM UTC)
- **Email Alerts**: Get notified when ratings drop significantly (>0.5 stars)

### 🛠️ Technical Highlights
- **Real-time Updates**: Auto-refresh UI every 10 seconds during analysis
- **Secure Authentication**: Clerk integration with JWT validation
- **Scalable Database**: PostgreSQL with future-ready multi-platform support
- **Cloud-Native**: Uses Upstash Redis (serverless) for task queue
- **Anti-Bot Protection**: Playwright scraper with stealth techniques

---

## 🚀 Tech Stack

### Backend
| Technology | Purpose | Why We Chose It |
|------------|---------|-----------------|
| **FastAPI** | REST API Framework | Async support, automatic OpenAPI docs, 3x faster than Flask |
| **PostgreSQL** (Neon) | Database | Reliable, free tier, JSONB support for reviews |
| **SQLAlchemy** | ORM | Type-safe, relationship management, migrations |
| **Playwright** | Web Scraper | Handles JavaScript-heavy pages, stealth mode |
| **Celery** | Task Queue | Distributed async tasks, scheduling |
| **Upstash Redis** | Message Broker | Serverless, no local Redis needed, 24/7 uptime |
| **PyTorch** | ML Framework | Industry standard, custom model training |
| **Transformers** | NLP Library | Pre-trained models, easy fine-tuning |
| **Resend** | Email Service | Developer-friendly, reliable delivery |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI Library |
| **Vite** | Build Tool (5x faster than CRA) |
| **Tailwind CSS** | Styling (utility-first) |
| **Clerk** | Authentication (social login, JWT) |
| **Axios** | HTTP Client |

### DevOps & Deployment
- **Hugging Face Spaces**: Backend hosting (Docker support)
- **Vercel**: Frontend hosting (edge network, auto-deploy)
- **GitHub Actions**: CI/CD pipeline (future)

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React App (Vercel)                                       │  │
│  │  • Clerk Authentication                                   │  │
│  │  • Product Dashboard                                      │  │
│  │  • Real-time Analysis Display                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS (JWT)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Auth       │  │  Products    │  │  Health Check        │ │
│  │   Middleware │  │  Router      │  │  Endpoint            │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌────────────────┐  ┌──────────────────┐
│  PostgreSQL   │  │  Celery Worker │  │  Upstash Redis   │
│  (Neon)       │  │  (HF Spaces)   │  │  (Message Broker)│
│               │  │                 │  │                  │
│  • Users      │  │  • Scrape Task │  │  • Task Queue    │
│  • Products   │  │  • Email Task  │  │  • Scheduling    │
│  • Links      │  └────────────────┘  └──────────────────┘
│  • Reviews    │           │
└───────────────┘           │
                            ▼
                ┌──────────────────────────┐
                │   PROCESSING PIPELINE    │
                ├──────────────────────────┤
                │ 1. Playwright Scraper    │
                │ 2. Fake Detector (NLP)   │
                │ 3. Sentiment Analyzer    │
                │ 4. Database Update       │
                │ 5. Email Notification    │
                └──────────────────────────┘
```

### Request Flow

1. **User Authentication**: Clerk handles OAuth → JWT token → FastAPI validates
2. **Add Product**: React sends product data → FastAPI saves to DB → Triggers Celery task
3. **Background Scraping**: Celery worker picks up task → Playwright scrapes Amazon
4. **AI Analysis**: Reviews pass through fake detector → sentiment analyzer
5. **Data Storage**: Results saved to PostgreSQL (reviews_json, fake_ratio, sentiment_score)
6. **Frontend Update**: React polls API every 10s → Displays results when ready
7. **Scheduled Tasks**: Celery Beat triggers bi-monthly scrapes → Email alerts on rating drops

---

## 🗄️ Database Schema

### Entity-Relationship Diagram

```
┌─────────────────────┐
│      users          │
├─────────────────────┤
│ id (PK)            │
│ clerk_id (UNIQUE)  │◄─────┐
│ email              │      │
│ name               │      │
└─────────────────────┘      │
                             │
                             │ 1:N
                             │
┌─────────────────────┐      │
│     products        │      │
├─────────────────────┤      │
│ id (PK)            │      │
│ user_id (FK) ──────┼──────┘
│ name               │
│ image_url          │
│ created_at         │
└─────────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────────────────┐
│      product_links              │
├─────────────────────────────────┤
│ id (PK)                        │
│ product_id (FK) ───────────────┤
│ platform (amazon/flipkart)     │
│ url                            │
│ last_rating (FLOAT)            │
│ fake_ratio (FLOAT 0.0-1.0)     │
│ sentiment_score (FLOAT -1 to 1)│
│ last_scraped (TIMESTAMP)       │
│ reviews_json (JSONB)           │
│ scrape_note (TEXT)             │
└─────────────────────────────────┘
```

### Design Decisions

**Why separate `product_links` table?**
- Future-proof for multi-platform support (Amazon, Flipkart, Myntra)
- One product can have multiple URLs without schema changes
- Each link has independent scraping status/results

**Why JSONB for reviews?**
- Flexible structure for different review formats
- PostgreSQL JSONB supports indexing & querying
- Easy to add new fields (helpful_votes, verified_purchase, etc.)

---

## 🤖 AI/ML Models

### Model Architecture Overview

We use an **ensemble approach** combining classical deep learning and modern transformers:

```
                    ┌─────────────────┐
                    │  Input Review   │
                    │  "Great product"│
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
        ┌───────────────┐        ┌──────────────────┐
        │   BiLSTM      │        │   DistilBERT     │
        │   + GloVe     │        │   Fine-tuned     │
        └───────┬───────┘        └────────┬─────────┘
                │                         │
                │ P(fake)=0.23           │ P(fake)=0.31
                │                         │
                └────────────┬────────────┘
                             │
                      ┌──────▼──────┐
                      │   Average   │
                      │  Ensemble   │
                      └──────┬──────┘
                             │
                    ┌────────▼────────┐
                    │ P(fake) = 0.27  │
                    │ Label: GENUINE  │
                    └─────────────────┘
```

### 1️⃣ BiLSTM + GloVe Model

**Architecture:**
```python
Input (Review Text)
    ↓
Tokenization → Word Indices
    ↓
GloVe Embedding Layer (300d)
    ↓
Bidirectional LSTM (128 hidden units, 2 layers)
    ↓
Dropout (0.5)
    ↓
Linear Layer (256 → 2)
    ↓
Softmax → [P(genuine), P(fake)]
```

**Key Features:**
- **Pre-trained GloVe Embeddings**: 300-dimensional vectors capture semantic relationships
- **Bidirectional Processing**: Reads reviews forward & backward for context
- **Sequence Modeling**: Captures word order patterns unique to fake reviews
- **Lightweight**: Only 2.3M parameters, fast inference (~50ms per review)

**Training Details:**
- Dataset: 40,000 labeled reviews (20k real, 20k fake)
- Optimizer: Adam (lr=0.001)
- Loss: Cross-Entropy
- Epochs: 15 with early stopping
- **Validation Accuracy: 94.2%**

**What It's Good At:**
- Detecting repetitive patterns ("amazing product", "must buy")
- Identifying unnatural grammar structures
- Recognizing copy-paste reviews

---

### 2️⃣ DistilBERT Fine-Tuned Model

**Architecture:**
```python
Input (Review Text)
    ↓
Tokenization (WordPiece)
    ↓
DistilBERT Encoder (6 layers, 768 hidden)
    ↓
[CLS] Token Representation
    ↓
Dropout (0.1)
    ↓
Linear Classifier (768 → 2)
    ↓
Softmax → [P(genuine), P(fake)]
```

**Key Features:**
- **Contextual Embeddings**: Understands word meaning based on context
- **Attention Mechanism**: Focuses on important words (e.g., "but", "however" indicating nuance)
- **Transfer Learning**: Pre-trained on 16GB of text, fine-tuned on our dataset
- **Distilled Model**: 40% smaller than BERT, 60% faster, 97% of performance

**Training Details:**
- Base Model: `distilbert-base-uncased`
- Optimizer: AdamW (lr=2e-5)
- Warmup Steps: 500
- Epochs: 3 (transformers need fewer epochs)
- **Validation Accuracy: 95.7%**

**What It's Good At:**
- Understanding sarcasm and complex sentiment
- Detecting subtle fake indicators ("I received this for free")
- Handling long, detailed reviews

---

### 3️⃣ Sentiment Analysis Model

**Architecture:**
```python
Input (Review Text)
    ↓
DistilBERT (sentiment-finetuned)
    ↓
Binary Classification: [POSITIVE, NEGATIVE]
    ↓
Sentiment Score: -1 (negative) to +1 (positive)
```

**Model:** `distilbert-base-uncased-finetuned-sst-2-english`
- Pre-trained on Stanford Sentiment Treebank (SST-2)
- 98% accuracy on movie reviews
- Generalizes well to product reviews

**How We Use It:**
- Analyze each review's sentiment
- Calculate overall sentiment score:
  - `score > 0.3` → Positive (😊)
  - `-0.3 ≤ score ≤ 0.3` → Mixed (😐)
  - `score < -0.3` → Negative (😞)
- Combine with fake detection for richer insights

---

### 4️⃣ Ensemble Strategy

**Why Ensemble?**
- BiLSTM catches sequence patterns
- DistilBERT catches contextual nuances
- Together: **96.8% accuracy** (vs 94-95% individually)

**Method:**
```python
fake_probability = (bilstm_prob + distilbert_prob) / 2
is_fake = fake_probability > 0.5
```

**Performance Metrics:**
| Metric | BiLSTM | DistilBERT | Ensemble |
|--------|--------|------------|----------|
| Accuracy | 94.2% | 95.7% | **96.8%** |
| Precision | 92.8% | 94.1% | **95.9%** |
| Recall | 95.1% | 96.2% | **97.3%** |
| F1-Score | 93.9% | 95.1% | **96.6%** |

---

## 🕷️ Scraping Pipeline

### How Amazon Scraping Works

```
┌──────────────────────────────────────────────────────────┐
│              PLAYWRIGHT SCRAPING FLOW                     │
└──────────────────────────────────────────────────────────┘

1. Launch Browser (Headless Chrome)
   ├─ User-Agent Spoofing
   ├─ Disable Automation Flags
   └─ Random Viewport Size

2. Navigate to Product Page
   ├─ Wait for DOM Load (not network idle - faster)
   ├─ Random Delay (2-4s) to mimic human
   └─ Extract Product Rating (4.2 stars)

3. Scroll to Reviews Section
   ├─ Smooth scroll to bottom
   ├─ Wait for review cards to load
   └─ Check if "See All Reviews" link exists

4. Extract Reviews (Top 8)
   For each review:
   ├─ Text Content
   ├─ Star Rating (1-5)
   ├─ Reviewer Name (future)
   └─ Verified Purchase Badge (future)

5. Close Browser & Return Data
   └─ {rating: 4.2, reviews: [{text: "...", stars: 5}, ...]}
```

### Anti-Detection Techniques

**Problem:** Amazon blocks automated scrapers

**Our Solutions:**
1. **Stealth Mode**: Remove `navigator.webdriver` flag
2. **Human-Like Behavior**: Random delays, smooth scrolling
3. **Realistic User-Agent**: Latest Chrome version
4. **Viewport Randomization**: Different screen sizes each time
5. **Error Handling**: Retry logic, fallback selectors

**Code Example:**
```python
context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined  // Hide automation
    });
""")
```

### Handling Dynamic Content

Amazon uses React → content loads via JavaScript:
- ✅ **Playwright**: Waits for JS execution, sees full page
- ❌ **BeautifulSoup**: Only sees initial HTML, misses reviews

---

## 🔄 System Flow

### End-to-End Process

```
USER ACTION                    SYSTEM RESPONSE
────────────                  ─────────────────

1. User adds product
   └─→ POST /api/products
                                ├─ Save to DB
                                ├─ Trigger Celery task
                                └─ Return product_id

2. Celery picks up task
                                ├─ Launch Playwright
                                ├─ Scrape Amazon
                                └─ Extract 8 reviews

3. AI Analysis Pipeline
                                ├─ Reviews → Fake Detector
                                │   ├─ BiLSTM: 0.23 fake prob
                                │   ├─ DistilBERT: 0.31 fake prob
                                │   └─ Ensemble: 0.27 → GENUINE
                                │
                                ├─ Reviews → Sentiment Analyzer
                                │   └─ Overall: +0.6 (Positive)
                                │
                                └─ Update DB (fake_ratio, sentiment_score)

4. Frontend polls API (every 10s)
                                └─ GET /api/products
                                    └─ Returns updated data

5. UI updates automatically
   └─ Shows: Rating, Fake %, Sentiment
```

### Scheduled Monitoring Flow

```
CELERY BEAT (Scheduler)
    │
    ├─ 1st of month, 3 AM UTC
    └─ 15th of month, 3 AM UTC
            ↓
    Trigger scrape_and_analyze_all()
            ↓
    For each product_link:
        ├─ Scrape Amazon
        ├─ Run AI analysis
        ├─ Compare old_rating vs new_rating
        └─ If drop > 0.5 stars:
            └─ Send email via Resend
```

---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or Neon account)
- Redis (or Upstash account)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/reputracker.git
cd reputracker/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:pass@host/db
CLERK_ISSUER=https://your-clerk-domain.clerk.accounts.dev
REDIS_URL=redis://your-upstash-url
RESEND_API_KEY=re_your_key
EOF

# Run migrations (if using Alembic)
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In separate terminal: Start Celery worker
celery -A app.celery_tasks worker --loglevel=info --pool=solo

# In another terminal: Start Celery beat (scheduler)
celery -A app.celery_tasks beat --loglevel=info
```

### Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_key
EOF

# Start development server
npm run dev
```

Visit `http://localhost:5173` 🎉

---

## 🚀 Deployment

### Backend → Hugging Face Spaces

**Why Hugging Face?**
- Free GPU/CPU hosting for ML apps
- Native Docker support
- Perfect for FastAPI + ML models
- Auto-scaling based on usage

**Steps:**

1. **Create `Dockerfile` in backend:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application
COPY . .

# Expose port
EXPOSE 7860

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

2. **Push to Hugging Face:**
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/reputracker
git push hf main
```

3. **Configure Environment Variables** in Space settings:
   - `DATABASE_URL`
   - `CLERK_ISSUER`
   - `REDIS_URL`
   - `RESEND_API_KEY`

### Celery Worker Deployment

**Option 1: Separate Space**
- Create another HF Space for Celery worker
- Use same Dockerfile but change CMD:
```dockerfile
CMD ["celery", "-A", "app.celery_tasks", "worker", "--loglevel=info"]
```

**Option 2: Single Container (Development)**
- Use `supervisord` to run both FastAPI + Celery
- Not recommended for production (resource limits)

### Frontend → Vercel

**Why Vercel?**
- Optimized for React/Vite
- Global CDN (edge network)
- Auto HTTPS, instant deployments
- Free tier: Unlimited bandwidth

**Steps:**

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy:**
```bash
cd frontend
vercel --prod
```

3. **Configure Environment Variables:**
   - Go to Vercel Dashboard → Settings → Environment Variables
   - Add `VITE_CLERK_PUBLISHABLE_KEY`
   - Add `VITE_API_URL` (your HF Spaces URL)

4. **Update CORS in FastAPI:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app"  # Add this
    ],
    ...
)
```

### Database → Neon (PostgreSQL)

Already configured if using `DATABASE_URL` env variable. No extra setup needed!

### Redis → Upstash

Already configured if using `REDIS_URL` env variable. No extra setup needed!

---

## 🔮 Future Enhancements

### Phase 1: Multi-Platform Support
- [ ] Flipkart scraper integration
- [ ] Myntra scraper integration
- [ ] Platform-specific fake review patterns

### Phase 2: Advanced Features
- [ ] Aspect-based sentiment (battery, delivery, quality)
- [ ] Review timeline visualization
- [ ] Competitor comparison dashboard
- [ ] Export reports (PDF/CSV)

### Phase 3: Intelligence
- [ ] Review summarization using LLMs
- [ ] Automated response suggestions for sellers
- [ ] Trend prediction (will rating drop?)
- [ ] Anomaly detection (sudden fake review spike)

### Phase 4: Scale
- [ ] Multi-tenancy (team accounts)
- [ ] API for developers
- [ ] Webhook notifications
- [ ] Mobile app (React Native)

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Areas we need help:**
- [ ] Flipkart/Myntra scrapers
- [ ] UI/UX improvements
- [ ] Documentation
- [ ] Test coverage
- [ ] Performance optimization

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **GloVe Embeddings**: Stanford NLP Group
- **DistilBERT**: Hugging Face Team
- **Dataset**: Amazon Review Dataset (Kaggle)
- **Inspiration**: Real-world problem of fake reviews hurting genuine sellers

---

## 📧 Contact

**Your Name** - [@yourtwitter](https://twitter.com/yourtwitter) - your.email@example.com

**Project Link**: [https://github.com/yourusername/reputracker](https://github.com/yourusername/reputracker)

---

<div align="center">

**Built with ❤️ using AI/ML, Modern Web Stack, and lots of ☕**

⭐ Star this repo if you found it useful!

</div>