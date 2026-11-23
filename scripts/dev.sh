#!/usr/bin/env bash
# Run backend and frontend locally (two terminals are nicer, this is the quick version).
set -euo pipefail
cd "$(dirname "$0")/.."
(cd backend && uvicorn app.main:app --reload --port 8000) &
(cd frontend && npm run dev) &
wait
