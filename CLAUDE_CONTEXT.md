# CLAUDE_CONTEXT: Student Academic Advisor

*Keep under ~60 lines. Overwrite sections; do not append history. Update at the end of every phase.*

**Current Phase:** 0: Planning & Documentation (plan produced, awaiting approval)
**Current Task:** Review and approve the plan; then run Prompt 0.1
**Last updated:** 2026-09-19

## Project in one paragraph
AI-assisted academic decision-support system. Python computes all facts (attendance %, deterministic risk score 0–100, trends, what-if). The AI API (OpenAI, backend only) only writes explanations, recommendations, study-plan text and chat answers, and always has a deterministic fallback. Stack: FastAPI + SQLAlchemy + SQLite (backend); React + TS + Vite + Tailwind + Recharts (frontend). No custom ML.

## Ordering rule
**Backend first (Phases 0–12, then FREEZE). Frontend and UI last (Phases 13–19).** No frontend code before the backend freeze.

## Completed
- Planning documents produced: MASTER_DESIGN.md, DEVELOPMENT_PLAN.md, CODING_PROMPTS.md

## In Progress
- Nothing

## Next
- 0.1 Repo skeleton, .gitignore, .env.example, project.mdc
- 0.2 Split MASTER_DESIGN into ARCHITECTURE / DATABASE_SCHEMA / API_SPEC / AI_GUIDELINES / RISK_ENGINE_SPEC / PROJECT_SPEC
- 0.3 Consistency review

## Important Decisions (defaults, pending approval)
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

## Known Issues
- None yet

## Recent Changes
- 2026-09-19: Plan created; roadmap reordered so all frontend work is in Phases 13–19

## Key Files (once created)
`backend/app/engines/` (pure logic) · `backend/app/services/ai_service.py` · `backend/app/api/deps.py` · `backend/tests/` · `openapi.json` (after freeze)
