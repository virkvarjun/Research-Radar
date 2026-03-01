#!/usr/bin/env bash
# Research Radar - Local Demo Script
# Walks through the full demo flow: create user, seed data, view feed, feedback, university, save, chat.
#
# Prerequisites:
#   - Postgres + Redis running (docker compose -f infra/docker-compose.yml up -d)
#   - Backend venv activated with deps installed
#   - Tables created and demo data seeded (python init_db.py && python seed_demo.py)
#
# Usage:
#   cd backend && bash ../infra/demo.sh

set -euo pipefail

API="http://localhost:8000"

echo "════════════════════════════════════════"
echo "  Research Radar — 5-Minute Demo"
echo "════════════════════════════════════════"
echo ""

# 1. Health check
echo "1️⃣  Checking API health..."
curl -sf "$API/health" | python3 -m json.tool
echo ""

# 2. Create a demo JWT
echo "2️⃣  Creating demo user token..."
USER_ID="00000000-0000-0000-0000-000000000001"
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
echo "3️⃣  Submitting onboarding (student, ML + NLP topics)..."
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
echo "4️⃣  Getting personalized feed..."
FEED=$(curl -sf "$API/feed" -H "Authorization: Bearer $TOKEN")
echo "$FEED" | python3 -m json.tool
echo ""

# 5. Provide feedback on first paper
echo "5️⃣  Sending feedback (save first paper)..."
FIRST_PAPER_ID=$(echo "$FEED" | python3 -c "
import json, sys
data = json.load(sys.stdin)
papers = data.get('papers', [])
if papers:
    print(papers[0]['id'])
else:
    print('')
")
if [ -n "$FIRST_PAPER_ID" ]; then
  curl -sf "$API/feedback" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"paper_id\": \"$FIRST_PAPER_ID\", \"action\": \"save\", \"source\": \"web\"}" | python3 -m json.tool
else
  echo "  (No papers in feed — skipping feedback)"
fi
echo ""

# 6. Get saved papers
echo "6️⃣  Listing saved papers..."
curl -sf "$API/saved" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 7. View paper detail
if [ -n "$FIRST_PAPER_ID" ]; then
  echo "7️⃣  Viewing paper detail + rigour panel..."
  curl -sf "$API/papers/$FIRST_PAPER_ID" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo ""

  # 8. Chat with paper
  echo "8️⃣  Chatting with saved paper..."
  curl -sf "$API/papers/$FIRST_PAPER_ID/chat" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"question": "What is the main contribution of this paper?"}' | python3 -m json.tool
  echo ""
fi

# 9. University Radar: search institutions
echo "9️⃣  Searching institutions (Berkeley)..."
curl -sf "$API/university/search?q=Berkeley" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 10. Settings
echo "🔟  Getting user settings..."
curl -sf "$API/settings" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 11. Refresh feed
echo "1️⃣1️⃣  Refreshing feed (diversity mode)..."
curl -sf "$API/feed?refresh=true" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "════════════════════════════════════════"
echo "  Demo Complete! ✅"
echo "════════════════════════════════════════"
echo ""
echo "Open http://localhost:3000 for the frontend."
echo ""
echo "To trigger daily ingestion (real papers):"
echo "  python -c \"from app.jobs.daily_ingest import daily_ingest_job; daily_ingest_job()\""
echo "To trigger daily digest emails:"
echo "  python -c \"from app.jobs.daily_digest import daily_digest_job; daily_digest_job()\""
