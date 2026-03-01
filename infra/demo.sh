#!/usr/bin/env bash
# Research Radar - Local Demo Script
# Creates a test user, ingests mock papers, generates a feed, and runs one digest.
#
# Prerequisites:
#   - Postgres + Redis running (docker compose -f infra/docker-compose.yml up -d)
#   - Backend venv activated with deps installed
#   - .env configured (at minimum: DATABASE_URL, SUPABASE_JWT_SECRET)
#
# Usage:
#   cd backend && bash ../infra/demo.sh

set -euo pipefail

API="http://localhost:8000"

echo "=== Research Radar Local Demo ==="
echo ""

# 1. Check health
echo "1. Checking API health..."
curl -sf "$API/health" | python3 -m json.tool
echo ""

# 2. Create a demo JWT (for dev only - uses the default dev secret)
echo "2. Creating demo user token..."
USER_ID="00000000-0000-0000-0000-000000000001"
# Simple JWT for dev (HS256 with default secret)
TOKEN=$(python3 -c "
from jose import jwt
token = jwt.encode(
    {'sub': '$USER_ID', 'email': 'demo@researchradar.dev', 'role': 'authenticated'},
    'super-secret-jwt-token-for-dev',
    algorithm='HS256'
)
print(token)
")
echo "  Token: ${TOKEN:0:30}..."
echo ""

# 3. Submit onboarding
echo "3. Submitting onboarding..."
curl -sf "$API/onboarding/answers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "student",
    "topics": ["Machine Learning", "Natural Language Processing"],
    "anchor_labels": {},
    "pairwise_choices": []
  }' | python3 -m json.tool
echo ""

# 4. Get feed
echo "4. Getting feed..."
curl -sf "$API/feed" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 5. Get settings
echo "5. Getting settings..."
curl -sf "$API/settings" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 6. Search institutions
echo "6. Searching institutions (MIT)..."
curl -sf "$API/university/search?q=MIT" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Demo Complete ==="
echo ""
echo "The backend is running. Open http://localhost:3000 for the frontend."
echo "To trigger daily ingestion: python -c 'from app.jobs.daily_ingest import daily_ingest_job; daily_ingest_job()'"
echo "To trigger daily digest:    python -c 'from app.jobs.daily_digest import daily_digest_job; daily_digest_job()'"
