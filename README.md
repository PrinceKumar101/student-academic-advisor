# Student Academic Advisor

AI-assisted academic **decision-support** for students and teachers. Python computes every academic fact (attendance %, risk 0–100, trends, what-if). An optional OpenAI call (backend only) writes explanations, study-plan wording and chat answers. If the AI is off or fails, a deterministic fallback still returns useful text. The UI never calculates percentages, risk or trends.

**Principle:** Python computes. AI explains.

## Requirements

| Layer | Need |
|---|---|
| Backend | Python **3.11+** |
| Frontend | Node.js **20+** |
| Database | SQLite (file created by seed; no extra server) |
| Optional | `OPENAI_API_KEY` for live AI; leave blank for fallbacks |

## Quick start (fresh clone)

From the repository root:

```bash
# 1. Backend env
cp .env.example backend/.env
# APP_ENV=dev is fine locally. JWT_SECRET_KEY=change-me is allowed only in dev.

# 2. Python env and install
cd backend
python3.12 -m venv .venv          # or python3.11
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# 3. Schema + demo data
python -m scripts.reset_db
python -m scripts.seed_demo --as-of 2026-09-19

# 4. API
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
cd frontend
cp .env.example .env              # blank VITE_API_BASE_URL → Vite proxies /api → :8000
npm install
npm run dev                       # http://127.0.0.1:5173
```

Then open http://127.0.0.1:5173. `/` is the public landing page (static example data, no API calls); use **Log in** there, or go to `/login`, with a demo account below. `/home` sends a signed-in user to their role's dashboard.

- Health: http://127.0.0.1:8000/api/v1/health → `{"status":"ok"}`
- Swagger: http://127.0.0.1:8000/docs (Authorize with email as `username`)

If `APP_ENV` is not `dev`, the app refuses to start with the placeholder JWT secret.

## Demo logins

Password for **all** seeded accounts: `Demo@1234`

| Email | Role | Use |
|---|---|---|
| `rahul@demo.edu` | Student | Main story (HIGH risk, declining attendance) |
| `teacher1@demo.edu` | Teacher | CS301–CS303, section ALL |
| `teacher2@demo.edu` | Teacher | CS304–CS305 ALL, CS301 section B |
| `newstudent@demo.edu` | Student | No academic rows |
| `zeroclass@demo.edu` | Student | Zero classes held |
| `missingassign@demo.edu` | Student | Many MISSING assignments |

Public register creates a **student** only. Extra teachers:

```bash
# from backend/ with venv active
python -m scripts.create_teacher \
  --email teacher3@demo.edu --password 'Demo@1234' \
  --full-name 'Teacher Three' --department CS
```

Seed scale: 43 students, 5 subjects (CS301–CS305), 2 teachers. If `--as-of` is omitted, the seed uses `2026-09-19`.

### Header “As of” date

The UI sends `?as_of=YYYY-MM-DD` on API calls. After you run `demo_advance`, set **As of** to the printed date so recovery weeks after today appear.

## Tests and lint

```bash
# backend/ (venv active)
pytest
ruff check .

# frontend/
npm test
npm run typecheck
```

Tests never call the real OpenAI API (fake client). Optional live smoke (never in CI):

```bash
# backend/, OPENAI_API_KEY set in backend/.env
python -m scripts.ai_smoke_test
```

Regenerate TypeScript types after an API change:

```bash
# repo root: refresh committed OpenAPI, then frontend types
cd backend && python -m scripts.export_openapi
cd ../frontend && npm run generate:types
```

## Demo story (short)

Full click-by-click script: [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md). Observed values from the 2026-09-19 seed (SRS example 82 is illustrative; live Rahul is **84.1 HIGH**):

1. Log in as Rahul → dashboard HIGH, top factors, warnings.
2. Risk + performance pages (attendance **DECLINING**).
3. What-if: attendance 80, internal 60 → **53.9 MEDIUM**, not persisted.
4. AI advisor + study planner (fallback if no key).
5. Teacher: filter HIGH + search Rahul → create intervention.
6. Advance data, then set **As of** to the new date → score drops (e.g. **68.5 HIGH**).

```bash
# backend/ — add Rahul’s recovery weeks
python -m scripts.demo_advance --email rahul@demo.edu

# print the 11-step API story against a running server
python -m scripts.demo_flow --base-url http://127.0.0.1:8000
```

Phase 16 browser checklist: [`docs/FUNCTIONAL_DEMO.md`](docs/FUNCTIONAL_DEMO.md).

## Project layout

```text
backend/app/     FastAPI routers → services → engines (pure) / ai/
backend/scripts/ reset_db, seed_demo, create_teacher, demo_*, export_openapi
frontend/src/    React + TypeScript UI (display only)
openapi.json     Frozen API contract
```

Engines (`risk`, `trend`, `whatif`, `time_budget`, …) import no FastAPI, SQLAlchemy or `ai/`. Risk, trends and what-if never call the AI.

## Documents

| File | Purpose |
|---|---|
| `SRS.md` | Original requirements |
| `PROJECT_SPEC.md` | Scope, stack, constraints |
| `ARCHITECTURE.md` | Layers, flows, Decision Log |
| `DATABASE_SCHEMA.md` | Tables and seed scale |
| `API_SPEC.md` | Endpoints and contracts |
| `AI_GUIDELINES.md` | Prompts, validation, fallback, limits |
| `RISK_ENGINE_SPEC.md` | Formulas; cases R1–R13, W1 |
| `UI_GUIDELINES.md` | Design tokens and a11y rules |
| `DEVELOPMENT_PLAN.md` | Phases and Definition of Done |
| `CLAUDE_CONTEXT.md` | Short session snapshot |
| `docs/DEMO_SCRIPT.md` | 11-step viva/demo script |
| `docs/VIVA_NOTES.md` | Likely questions |
| `docs/FINAL_REPORT.md` | Written report |
| `docs/PRESENTATION_OUTLINE.md` | Slide outline |
| `docs/DEFINITION_OF_DONE.md` | Final DoD run |
| `docs/DOC_VERIFICATION.md` | Docs vs code check |
| `docs/FUNCTIONAL_DEMO.md` | Phase 16 browser checklist |
| `docs/UI_POLISH.md` | Phase 18 a11y / polish notes; landing redesign log |
| `docs/UI_REDESIGN_PLAN.md` | Landing-page redesign plan and final design |
| `docs/screenshots/` | Demo captures |
| `.cursor/indexes/PHASE_TRACK.md` | Phase/task tracker |

## What this is not

No custom ML, no Docker/Alembic in v1, no notifications or PDF export. Demo data is synthetic. Do not load real student records without institutional approval.

JWT is stored in `localStorage` (`saa_access_token`) for the college demo. A 401 clears it and returns to `/login`.
