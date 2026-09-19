# Student Academic Advisor

Student Academic Advisor is an AI-assisted academic decision-support system. Python computes attendance, risk scores, trends and what-if results; an optional AI API explains those facts and drafts study-plan or chat text, with a deterministic fallback when the AI is unavailable.

## Backend setup (Phase 1)

Requires **Python 3.11+**. This repo uses a local virtualenv under `backend/.venv` (not committed).

```bash
# from the repository root
cp .env.example backend/.env   # edit secrets later; APP_ENV=dev is fine for local work

cd backend
python3.12 -m venv .venv       # or python3.11
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# run the API (from the backend/ directory)
uvicorn app.main:app --reload
```

Then open:

- Health: http://127.0.0.1:8000/api/v1/health → `{"status":"ok"}`
- Interactive docs: http://127.0.0.1:8000/docs

```bash
# tests and lint (from backend/)
pytest
ruff check .

# rebuild schema and load the demo dataset (from backend/)
python -m scripts.reset_db
python -m scripts.seed_demo --as-of 2026-09-19
```

Demo password for all seeded accounts is `Demo@1234`. Logins include `rahul@demo.edu`, `teacher1@demo.edu`, `teacher2@demo.edu`, plus edge users `newstudent@demo.edu`, `zeroclass@demo.edu`, `missingassign@demo.edu`. If `--as-of` is omitted, the seed uses `2026-09-19`.

In `/docs`, use **Authorize** with OAuth2 password flow (`username` = email) against `POST /api/v1/auth/login`.

```bash
# create an extra teacher (not available via public register)
python -m scripts.create_teacher --email teacher3@demo.edu --password 'Demo@1234' --full-name 'Teacher Three' --department CS
```

```bash
# after seed: add Rahul’s post-intervention recovery weeks
python -m scripts.demo_advance --email rahul@demo.edu

# print the demo story against a running server
python -m scripts.demo_flow --base-url http://127.0.0.1:8000

# refresh the committed OpenAPI document (repo root)
python -m scripts.export_openapi
```

If `APP_ENV` is anything other than `dev`, `JWT_SECRET_KEY` must not be the placeholder `change-me` or the app will refuse to start.

Optional AI analysis (`POST /api/v1/ai/analysis`) works without a key and returns `source: FALLBACK`. To try the real provider locally (never in CI):

```bash
# from backend/, with OPENAI_API_KEY set in backend/.env
python -m scripts.ai_smoke_test
```

## Documents

| File | Purpose |
|---|---|
| `SRS.md` | Primary source of truth: problem, features and original requirements |
| `PROJECT_SPEC.md` | Concise project definition, stack, principle and constraints |
| `ARCHITECTURE.md` | Layers, folder structure, data flows and Decision Log (D1–D31) |
| `DATABASE_SCHEMA.md` | Tables, indexes and integrity rules |
| `API_SPEC.md` | Conventions, endpoints (with planned phase) and key contracts |
| `AI_GUIDELINES.md` | AI capabilities, validation, fallback, cost limits and privacy |
| `RISK_ENGINE_SPEC.md` | Risk, trend, warning and analytics formulas; cases R1–R13, W1 |
| `UI_GUIDELINES.md` | UI design notes (deferred to Phase 17) |
| `DEVELOPMENT_PLAN.md` | Phases, tasks, verification and Definition of Done |
| `CLAUDE_CONTEXT.md` | Short session snapshot (current phase and decisions) |
| `docs/archive/MASTER_DESIGN.md` | Archived master design this documentation set was split from |
| `docs/CONSISTENCY_REVIEW.md` | Phase 0.3 living-doc consistency report |
| `.cursor/indexes/PHASE_TRACK.md` | Completed-phase tracker for the coding agent |
