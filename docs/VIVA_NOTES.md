# Viva notes

Short answers. Point at the file in parentheses if they ask to “show the code”.

## Why is risk deterministic (not an ML model)?

Risk is a **weighted, documented heuristic** so a teacher can reproduce the score from the same inputs. A trained model would need labelled outcomes, would change between runs, and would hide the formula. Cases R1–R13 in `RISK_ENGINE_SPEC.md` lock expected values. Weights are honest approximations of academic concern, not causal discovery. Change a weight only in `risk_config.py` + the spec, and bump `config_version`.

## Why does the AI not calculate numbers?

The product claim is “decision support”, not “the model predicted 82”. LLMs invent figures. Python owns attendance %, risk, slopes and what-if. The AI receives a **fact context** (no name/email/id) and may only write language. Grounding validation rejects percentages that are not in that context (`UNGROUNDED_OUTPUT` → fallback). (`AI_GUIDELINES.md`, `ai/validators.py`)

## How is hallucination handled?

1. Structured JSON schemas (Pydantic).
2. Enum and length checks.
3. Grounding: no invented percentages or unknown subject codes.
4. Timeout, one retry on 429/5xx, no retry on 4xx.
5. Any failure → deterministic fallback, `source: FALLBACK`.
6. Daily limits + 24 h analysis cache.
7. Tests use a fake client; CI never calls OpenAI.

## Why SQLite?

One-file demo, no extra process, FK pragma on, `reset_db` + seed in seconds. Fine for a college project with tens of students. Not for multi-writer production; future work would be PostgreSQL + migrations (Alembic is deferred, D7/D12).

## Why JWT in localStorage?

Accepted for a **local demo**. Documented risk (XSS can steal the token). Production would use httpOnly cookies or a BFF. Role in the token is **not** trusted: `get_current_user` reloads role from the database.

## How is authorization enforced?

Only `api/deps.py`: `get_current_user`, `require_role`, `authorize_student_access`, `authorize_teacher_subject_write`. Student A cannot read student B (403). Teachers see students enrolled in subjects they are assigned to (section `ALL` or match). The UI hides links; the API is the real gate. Phase 12 authorization matrix covers every route × five actors.

## Why are engines “pure”?

`engines/*` take dataclasses + `as_of` + config. No FastAPI, SQLAlchemy, `ai/`, or `datetime.now()`. That makes R1–R13 unit-testable and keeps risk/trends/what-if independent of the AI. Services load data and persist snapshots.

## What-if: does it change the database?

No. Same engine twice (current vs overrides). Response includes `persisted: false`. Tests assert row counts and values unchanged.

## Why `as_of`?

Attendance and assessments are filtered by date. Seed snapshots and `demo_advance` write later weeks. Without `as_of`, the UI would hide recovery after “today”. Header date → `?as_of=` (D35).

## How does the study planner work?

Hybrid: `time_budget.allocate` assigns minutes (never over the daily cap; weaker subjects get more). AI fills activity text per `slot_id`. Validator requires every slot exactly once; otherwise fallback templates. (`engines/time_budget.py`)

## Interventions and “improvement”

Create stores **baseline** score/level. Progress compares live risk at `as_of` to that baseline. Wording is observational (IMPROVED / WORSENED / UNCHANGED at ±2). We do **not** claim the intervention caused the change.

## Attendance % is never stored

Computed from Σ attended / Σ held. Zero classes → `null`, not 0%. (`D5`)

## Frontend has no Recharts?

Phase 14 named Recharts; D33 used an SVG of backend points so the install stayed small. Scale-to-view only — no slope math in the browser.

## Limitations (say these yourself)

- Heuristic weights, not validated against outcomes.
- Synthetic seed; not a real college dataset.
- SQLite, no Alembic, no Docker, no notifications.
- Git tags `backend-v1` / `frontend-functional` / `v1.0` only if the maintainer creates them.
- Live Lighthouse/axe were not required in the agent environment (`docs/UI_POLISH.md`).
- Teacher list sort is **current page only** (API has no sort query, D34).
- Overall assessment trend for Rahul can be STABLE while attendance is DECLINING.

## Concepts the panel often maps to the syllabus

| Topic | Where |
|---|---|
| Functions / classes / exceptions | engines, services, error handlers |
| Pandas | class analytics (`engines/analytics.py`) |
| REST + JWT | FastAPI routers, `core/security.py` |
| Validation | Pydantic + DB CHECK |
| React + TS + state | `AuthContext`, `useAsync`, pages |
| Charts | `TrendLineChart` SVG |
| LLM prompts + fallback | `ai/prompts/*`, `fallback.py` |
| Relational schema + history | models, `risk_assessments` snapshots |

## What we did **not** build (on purpose)

Custom ML, mobile app, microservices, Kubernetes, email, PDF, parent portal. See SRS §42–43.
