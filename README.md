# Research Radar

Personalized research paper discovery and tracking. Daily email digests (max 5 papers), a web feed with Save/Skip/Not relevant/Refresh, University Radar, 4-step algorithmic onboarding, evidence/rigour panels, and chat-with-paper RAG.

## Architecture

```
frontend/    Next.js 16 App Router + Tailwind CSS
backend/     FastAPI (Python) + SQLAlchemy + pgvector
infra/       docker-compose (Postgres + Redis), demo script
```

**Stack:** Next.js · FastAPI · Postgres + pgvector · Redis + RQ · Supabase Auth · Resend · PyMuPDF · OpenAI Embeddings

## Quick Start

### 1. Start Infrastructure

```bash
docker compose -f infra/docker-compose.yml up -d
```

This starts Postgres (with pgvector extension auto-enabled) on port 5432 and Redis on port 6379.

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your keys (at minimum: OPENAI_API_KEY, SUPABASE_JWT_SECRET)

# Create database tables
python init_db.py

# Seed demo papers (12 papers with evidence + 6 institutions)
python seed_demo.py

# Start API server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Copy and configure environment
cp .env.local.example .env.local
# Edit with your Supabase project URL and anon key

npm run dev
```

Open http://localhost:3000

### 4. Run Workers (for background jobs)

```bash
cd backend
source venv/bin/activate
python -m app.worker
```

## 5-Minute Demo Walkthrough

After completing the Quick Start above:

```bash
cd backend
source venv/bin/activate
bash ../infra/demo.sh
```

This script walks through the **entire product flow** via API:

| Step | What happens |
|------|-------------|
| 1 | Health check |
| 2 | Create demo user (JWT with dev secret) |
| 3 | **Onboarding**: submit role (student) + topics (ML, NLP) |
| 4 | **View feed**: personalized paper recommendations with `why_matched` |
| 5 | **Feedback**: save the top paper → user vector updated |
| 6 | **Saved papers**: verify the paper appears in saved list |
| 7 | **Paper detail**: view rigour panel (datasets ✅, metrics ✅, code ✅, etc.) |
| 8 | **Chat with paper**: RAG-based Q&A with citations |
| 9 | **University Radar**: search for "Berkeley", see institution results |
| 10 | **Settings**: view user preferences |
| 11 | **Refresh feed**: get a diverse alternative set |

Or use the **frontend** at http://localhost:3000:

1. Sign up / log in (Supabase Auth)
2. Complete 4-step onboarding: Role → Topics → Rate 12 papers → 10 pairwise comparisons
3. View your feed — click Save / Skip / Not relevant
4. Click "Refresh" for diverse alternatives
5. Go to University Radar — search your institution
6. Click a paper → see the Evidence/Rigour panel
7. Save a paper → Chat with it using RAG

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Async Postgres connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `SUPABASE_JWT_SECRET` | Yes | JWT secret for auth validation |
| `OPENAI_API_KEY` | Yes* | For embeddings (*required if using OpenAI provider) |
| `RESEND_API_KEY` | No | Resend API key for email digests |
| `EMBEDDING_PROVIDER` | No | `openai` (default) |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` (default) |
| `APP_URL` | No | Frontend URL for email links (default: http://localhost:3000) |
| `BACKEND_URL` | No | Backend URL for email feedback links (default: http://localhost:8000) |
| `OPENALEX_EMAIL` | No | Polite pool email for OpenAlex API |
| `FEEDBACK_SECRET` | No | HMAC secret for email feedback URLs |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase anon/public key |
| `NEXT_PUBLIC_API_URL` | No | Backend API URL (default: http://localhost:8000) |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/onboarding/answers` | Submit onboarding answers |
| `GET` | `/onboarding/anchor-papers` | Get 12 anchor papers for onboarding step 3 |
| `GET` | `/onboarding/pairwise-papers` | Get 10 paper pairs for onboarding step 4 |
| `GET` | `/feed` | Get personalized paper feed |
| `GET` | `/feed?refresh=true` | Refresh with diverse alternatives |
| `POST` | `/feedback` | Record feedback (save/skip/not_relevant) |
| `GET` | `/api/feedback` | Email click-through feedback (signed URLs) |
| `GET` | `/university/search?q=` | Search institutions (OpenAlex) |
| `GET` | `/university/{id}/new` | New papers from institution |
| `GET` | `/university/{id}/related` | Related papers from elsewhere |
| `GET` | `/papers/{id}` | Paper detail + rigour panel |
| `POST` | `/papers/{id}/save` | Save paper |
| `POST` | `/papers/{id}/chat` | Chat with saved paper (RAG) |
| `GET` | `/saved` | List saved papers |
| `GET` | `/settings` | Get user settings |
| `POST` | `/settings` | Update user settings |

## Job Scheduling

Daily jobs can be triggered manually or scheduled with cron:

```bash
# Manual trigger
cd backend && source venv/bin/activate
python -c "from app.jobs.daily_ingest import daily_ingest_job; daily_ingest_job()"
python -c "from app.jobs.daily_digest import daily_digest_job; daily_digest_job()"

# Cron (example: run at 6am daily)
# 0 6 * * * cd /path/to/backend && source venv/bin/activate && python -c "from app.jobs.daily_ingest import daily_ingest_job; daily_ingest_job()" && python -c "from app.jobs.daily_digest import daily_digest_job; daily_digest_job()"
```

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest -v
```

Tests cover: OpenAlex/arXiv normalization, deduplication, ranking + MMR, feedback vector updates, evidence extraction, email rendering, chat service, rate limiting, and end-to-end integration.

## Data Sources

- **OpenAlex:** Works ingestion, institution search, university papers (no Google Scholar)
- **arXiv:** Recent papers from cs.AI, cs.RO, stat.ML categories
- Papers are deduplicated by DOI > arXiv ID > normalized title hash
