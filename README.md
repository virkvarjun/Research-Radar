# Research Radar

Personalized research paper discovery and tracking. Daily email digests (max 5 papers), a web feed with Save/Skip/Not relevant/Refresh, University Radar, algorithmic onboarding, evidence/rigour panels, and chat-with-paper RAG.

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

This starts Postgres (with pgvector) on port 5432 and Redis on port 6379.

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
python -c "
from sqlalchemy import create_engine
from app.db import Base
from app.models import *
engine = create_engine('postgresql://research_radar:research_radar_dev@localhost:5432/research_radar')
engine.execute('CREATE EXTENSION IF NOT EXISTS vector')
Base.metadata.create_all(engine)
print('Tables created')
"

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
| `GET` | `/feed` | Get personalized paper feed |
| `POST` | `/feedback` | Record feedback (save/skip/not_relevant) |
| `GET` | `/university/search?q=` | Search institutions |
| `GET` | `/university/{id}/new` | Papers from institution |
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

## Local Demo

```bash
cd backend
source venv/bin/activate
bash ../infra/demo.sh
```

This creates a demo user, submits onboarding, queries the feed, and searches institutions.

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest -v
```

76 tests covering: OpenAlex/arXiv normalization, deduplication, ranking + MMR, feedback vector updates, evidence extraction, email rendering, and end-to-end integration.

## Data Sources

- **OpenAlex:** Works ingestion, institution search, university papers
- **arXiv:** Recent papers from cs.AI, cs.RO, stat.ML categories
- Papers are deduplicated by DOI > arXiv ID > normalized title hash
