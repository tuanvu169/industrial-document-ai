# Architecture notes

- **Modular monolith**: one FastAPI app. `api/` (HTTP) -> `services/` (business rules, ownership checks) -> `repositories/` (SQL) ; AI code lives in `processing/`, `embeddings/`, `rag/`, `inference/`, `prompts/`.
- **Isolation**: every retrieval query filters `project_id`; ownership is verified once in `services/project_service.get_owned_project` (404 for foreign projects). RLS in `supabase/migrations` is a second layer.
- **Ingestion**: upload -> Storage -> `BackgroundTasks` worker -> PyMuPDF -> clean -> chunk per page (500 tok / 80 overlap, using the e5 tokenizer) -> embed -> `document_chunks`. Status: processing / completed / failed.
- **Chat**: (follow-up -> condensed standalone query via Gemini) -> pgvector top-N + FTS top-N -> RRF (k=60) -> top-K -> prompt -> Gemini -> citations parsed from `[n]` markers -> stored in `messages.sources`.
- **Auth**: frontend signs in with Supabase Auth; FastAPI validates the bearer token by calling Supabase `/auth/v1/user`.
