# Industrial Document AI — Project-based RAG Chatbot

React + TypeScript → **FastAPI (single backend)** → Supabase (PostgreSQL + pgvector, Auth, Storage) + Gemini API.
Users create Projects, upload PDFs into a Project, and chat with that Project's knowledge base only. Answers cite file + page.

## Features (MVP)
- Supabase Auth login/signup, Project CRUD
- PDF upload (≤ 20 MB, text PDFs) → background parse/chunk/embed/index with status tracking
- Hybrid retrieval (pgvector + PostgreSQL full-text) fused with RRF, always filtered by `project_id`
- Gemini-grounded answers with citations (document name + page), multi-turn conversations with memory
- Tests: pytest (chunking, cleaning, parsing, RRF, metrics, auth gate), Vitest; retrieval evaluation script

## Setup
**1. Supabase** — create a project, then run `supabase/migrations/20260101000000_init.sql` in the SQL editor
(or `supabase db push`). It creates tables, pgvector/FTS indexes, RLS policies and the private `documents` bucket.
For quick local testing you may disable "Confirm email" in Auth settings.

**2. Env** — `cp .env.example .env` and fill it in; `cp frontend/.env.example frontend/.env`.

**3. Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt        # first run downloads torch + the e5 model (~hundreds of MB)
uvicorn app.main:app --reload --port 8000  # docs at http://localhost:8000/docs
pytest
```
**4. Frontend**
```bash
cd frontend && npm install && npm run dev   # http://localhost:5173
npm test
```
Or `docker compose up --build`.

## Evaluate
Copy `data/eval/sample_questions.jsonl` to `data/eval/questions.jsonl`, replace with real questions and the pages that answer them, then:
```bash
cd backend
python -m app.evaluation.run_eval --project <project-uuid> --dataset ../data/eval/questions.jsonl --k 5
python -m app.evaluation.run_eval --project <project-uuid> --dataset ../data/eval/questions.jsonl --with-answers
```
Reports Recall@K, MRR, citation accuracy and latency. Do not quote scores before measuring them on your own data.

## Known limitations / next steps (per plan: post-MVP)
- No OCR: scanned PDFs fail with a clear message (PaddleOCR is optional in the plan).
- Background processing uses FastAPI `BackgroundTasks` (runs in-process; jobs are lost if the server restarts mid-ingestion). Swap for ARQ/Celery later.
- Faithfulness / Answer Relevancy require an LLM-judge and are not implemented; reranker, Sentry, CI/CD not included.
- UI uses plain Tailwind components (shadcn/ui can be added incrementally).
- Integration tests against a real Supabase/Gemini are not included; only unit + auth-gate tests run offline.
- Schema is managed by Supabase migrations (Alembic intentionally skipped).
