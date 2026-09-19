# CLAUDE_CONTEXT: Student Academic Advisor

*Keep under ~60 lines. Overwrite sections; do not append history. Update at the end of every phase.*

**Current Phase:** 2: Database & Seed Data
**Current Task:** 2.2 Academic models
**Last updated:** 2026-09-19

## Project in one paragraph
AI-assisted academic decision-support system. Python computes all facts (attendance %, deterministic risk score 0–100, trends, what-if). The AI API (OpenAI, backend only) only writes explanations, recommendations, study-plan text and chat answers, and always has a deterministic fallback. Stack: FastAPI + SQLAlchemy + SQLite (backend); React + TS + Vite + Tailwind + Recharts (frontend). No custom ML.

## Ordering rule
**Backend first (Phases 0–12, then FREEZE). Frontend and UI last (Phases 13–19).** No frontend code before the backend freeze.

## Completed
- Phase 0 Planning & Documentation (0.1 skeleton, 0.2 doc split, 0.3 consistency review + living-doc fixes C1–C10)
- Phase 1 Backend Setup (1.1 FastAPI scaffold + health + settings, 1.2 errors/logging/CORS, 1.3 pytest/ruff, 1.4 README)

## In Progress
- Phase 2 Database & seed data (2.1 done; next: Prompt 2.2)

## Next
- 2.2 Academic models (`CODING_PROMPTS.md`)

## Important Decisions
- D2 Public register = STUDENT only; teachers via `scripts/create_teacher.py`
- D3 Teachers enter attendance/marks; students read-only (except habits, plans, chat, intervention status)
- D4 Teacher visibility via `teaching_assignments` + enrollments
- D5 Attendance = weekly counts; % always computed
- D6 Risk: SRS weights; normalization good/bad points (attendance 90/50, performance 75/35); INSUFFICIENT_DATA if available weight < 0.40; floors (attendance < 75 or internal < 40 → at least MEDIUM)
- D7 No Alembic (`reset_db.py` + seed)
- D8 Study plan hybrid: Python picks subject/day/minutes; AI writes topic/activity text
- D9 One AI call for analysis + recommendations; 3 AI capabilities (analysis, plan, chat)
- D10 PyJWT + pwdlib[argon2]/bcrypt; OAuth2 form login (Swagger Authorize works)
- D13 Risk snapshots persisted as a side effect; no background jobs
- D14 Escalation reason is per floor that fired (attendance and/or internal)
- D15 Standard error envelope + request-id logging in `core/errors.py`, `core/exception_handlers.py`, `core/logging.py`
- D16 Password hashing: `pwdlib[argon2]` (`PasswordHash.recommended()`)

## Known Issues
- None that block Phase 2. Starlette TestClient warns that `httpx` is deprecated in favor of `httpx2`; not added (not in the approved dependency list).

## Recent Changes
- 2026-09-19: Phase 1 closed. Runnable FastAPI app, `/api/v1/health`, env settings, error format, CORS, pytest.

## Key Files
`PROJECT_SPEC.md` · `ARCHITECTURE.md` · `DATABASE_SCHEMA.md` · `API_SPEC.md` · `AI_GUIDELINES.md` · `RISK_ENGINE_SPEC.md` · `backend/app/main.py` · `.cursor/indexes/PHASE_TRACK.md`
