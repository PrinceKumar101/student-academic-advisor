# CLAUDE_CONTEXT: Student Academic Advisor

*Keep under ~60 lines. Overwrite sections; do not append history. Update at the end of every phase.*

**Current Phase:** 13: Frontend foundation
**Current Task:** 13.1 Vite + React + TypeScript + Tailwind + React Router scaffold
**Last updated:** 2026-09-19

## Project in one paragraph
AI-assisted academic decision-support system. Python computes all facts (attendance %, deterministic risk score 0–100, trends, what-if). The AI API (OpenAI, backend only) only writes explanations, recommendations, study-plan text and chat answers, and always has a deterministic fallback. Stack: FastAPI + SQLAlchemy + SQLite (backend); React + TS + Vite + Tailwind + Recharts (frontend). No custom ML.

## Ordering rule
**Backend first (Phases 0–12, then FREEZE). Frontend and UI last (Phases 13–19).** Backend freeze is in place: API changes need a documented reason.

## Completed
- Phase 0 Planning & Documentation (0.1–0.3)
- Phase 1 Backend Setup (1.1–1.4)
- Phase 2 Database & seed data (2.1–2.7)
- Phase 3 Authentication & authorization (3.1–3.7)
- Phase 4 Academic data APIs (4.1–4.9; CSV via 12.9)
- Phase 5 Academic risk engine (5.1–5.10)
- Phase 6 Trends, subject analysis, early warnings (6.1–6.8)
- Phase 7 What-if simulator (7.1–7.4)
- Phase 8 AI service (analysis) (8.1–8.10)
- Phase 9 AI study planner (9.1–9.8)
- Phase 10 AI academic assistant (10.1–10.6)
- Phase 11 Interventions & teacher APIs (11.1–11.9)
- Phase 12 Backend integration, hardening, freeze (12.1–12.10)

## In Progress
- Phase 13 Frontend foundation (next: Prompt 13.1)

## Next
- 13.1 Vite + React + TypeScript + Tailwind + React Router scaffold

## Important Decisions
- D2 Public register = STUDENT only; teachers via `scripts/create_teacher.py`
- D3 Teachers enter attendance/marks; students read-only (except habits, plans, chat, intervention status)
- D4 / D18 Teacher visibility: teaching assignment + enrollment; section `ALL` or student section match
- D5 Attendance = weekly counts; % always computed
- D6 Risk: SRS weights; INSUFFICIENT_DATA if available weight < 0.40; floors
- D7 No Alembic (`reset_db.py` + seed)
- D8 / D26 Hybrid study plan: Python budget + AI text; auto-pick ≤3; window `[as_of, exam_date)`
- D10 / D16 PyJWT HS256 + pwdlib[argon2]; authz only in `api/deps.py`
- D13 Risk snapshots persisted as a side effect
- D17 Seed `scripts/seed_generator.py`; default as_of `2026-09-19`
- D25 `openai==1.109.1`; analysis cache 24 h
- D27 Chat student-only; `student_id` ignored; last 6 messages; USER rows count toward daily limit
- D28 Intervention progress ±2 UNCHANGED; student status forward-only; AI-4 not persisted/cached
- D29 Overview composite; D30 CSV import stdlib; D31 bulk snapshots + Rahul ≥80 then ~50–70 after advance

## Known Issues
- Git tag `backend-v1` not created (commit/tag only on request).
- Starlette TestClient warns that `httpx` is deprecated in favor of `httpx2`; not added.

## Recent Changes
- 2026-09-19: Phase 12 complete — overview, auth matrix, full-story test, demo scripts, CSV import, `openapi.json`, backend freeze.

## Key Files
`openapi.json` · `API_SPEC.md` · `backend/app/services/overview_service.py` · `backend/scripts/demo_flow.py` · `.cursor/indexes/PHASE_TRACK.md`
