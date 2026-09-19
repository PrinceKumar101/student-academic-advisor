# Documentation vs code (Phase 19.3)

Checked 2026-09-19 against the repository. No API or schema change in this phase.

## Architecture (`ARCHITECTURE.md`)

| Claim | Code |
|---|---|
| Thin routers → one service | `backend/app/api/routers/*.py` (14 routers: health, auth, students, subjects, attendance, assessments, risk, trends, analytics, ai, study_plans, interventions, teacher, imports) |
| Engines pure | `backend/app/engines/` — no FastAPI/SQLAlchemy/`ai/` imports (enforced by unit import-boundary tests) |
| Auth only in `deps.py` | `backend/app/api/deps.py` |
| AI only via `ai_service` | `backend/app/services/ai_service.py` + `backend/app/ai/` |
| Frontend display-only | Pages consume API types; no risk/percent/slope formulas |
| Decision Log D32–D37 | Vite proxy, SVG charts (no Recharts), page-local sort, `as_of`, paper/ink UI, polish without axe-core |

Folder tree in §2.3 was refreshed to include `RiskGauge` and Phase 19 doc files.

## Database (`DATABASE_SCHEMA.md`)

| Claim | Code |
|---|---|
| Identity: User, Student, Teacher | `models/user.py`, `student.py`, `teacher.py` |
| Academic: Subject, Enrollment, TeachingAssignment, Attendance, Assessment, SemesterResult, StudyHabit | matching `models/*.py` |
| RiskAssessment JSON snapshots | `models/risk_assessment.py` |
| StudyPlan / items, AIAdvice, AIChatMessage, Intervention | matching models |
| Seed: 43 students, 5 subjects, 2 teachers | `scripts/seed_generator.py`; `seed_demo` prints “Seeded 43 students” |
| Default as_of `2026-09-19` | `DEFAULT_AS_OF` in seed scripts |

## API (`API_SPEC.md` vs `openapi.json`)

Endpoint table §4.2 matches the mounted `/api/v1` routes (health through CSV imports). Key contracts (login form, overview, risk, what-if `persisted`, AI `source`, intervention baseline, teacher filters) match the live routers. Frontend types are generated from committed `openapi.json` (`npm run generate:types`).

## Known documented deltas (not bugs)

- SRS demo numbers (risk 82, attendance 64%) vs live seed (84.1, ~56.7%) — recorded in `DEMO_SCRIPT.md` and `FUNCTIONAL_DEMO.md`.
- Recharts named in older plan text; implementation is SVG (D33).
- Git tags deferred until requested.

## Screenshots

Captured from the running local UI (`docs/screenshots/`). Index: `docs/screenshots/README.md`.
