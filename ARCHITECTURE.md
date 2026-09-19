# ARCHITECTURE: Student Academic Advisor

Copied from `docs/archive/MASTER_DESIGN.md` §2. Decision Log seeded from §0 (D1–D13).

## 2. FINAL ARCHITECTURE (Output 2)

### 2.1 Diagram

```text
 [Frontend: React+TS+Vite+Tailwind+Recharts]        <- built LAST (Phases 13-19)
                     | REST/JSON  (/api/v1, JWT bearer)
                     v
 +------------------- FastAPI -------------------------------+
 |  api/routers  (thin: validate, authorize, call service)   |
 |        |                                                  |
 |  services/  (orchestration: DB <-> engines <-> AI)        |
 |    |                 |                     |              |
 |  engines/ (PURE)   models/ + db/        ai_service        |
 |  risk, trend,      SQLAlchemy            |                |
 |  whatif, analytics      |            ai/ (client, context, |
 |  warnings               v             prompts, validators, |
 |                      SQLite           fallback)            |
 +------------------------------------------|----------------+
                                            v
                                     OpenAI API (optional at runtime)
```

### 2.2 Layering rules (enforced in code review and `project.mdc`)

1. `engines/*` are **pure**. They import no FastAPI, no SQLAlchemy, no `ai/` and no `datetime.now`. They take dataclasses plus `config` plus `as_of`.
2. Routers hold **no business logic**. They validate, authorize, call one service function and return a schema.
3. Only `services/ai_service.py` (via `ai/`) talks to the AI provider. Only the backend holds the API key.
4. Risk, trend and what-if never call the AI. The app must work with the AI turned off.
5. `ai/` never imports `models/`. It receives a plain `StudentAcademicContext` object.
6. Authorization lives in `api/deps.py`, not in scattered `if` statements.
7. The frontend contains **no** calculations of percentages, risk or trends. It displays backend values.

### 2.3 Folder structure

```text
student-academic-advisor/
├── SRS.md  PROJECT_SPEC.md  ARCHITECTURE.md  DEVELOPMENT_PLAN.md
├── DATABASE_SCHEMA.md  API_SPEC.md  AI_GUIDELINES.md  RISK_ENGINE_SPEC.md
├── UI_GUIDELINES.md  CLAUDE_CONTEXT.md  README.md
├── .env.example  .gitignore  (CLAUDE.md optional pointer for Claude Code)
├── .cursor/rules/project.mdc
├── docs/archive/            (original SRS/plan inputs)
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/      config.py security.py errors.py logging.py exception_handlers.py
│   │   ├── db/        base.py session.py
│   │   ├── models/    one file per entity + enums.py
│   │   ├── schemas/   Pydantic request/response models
│   │   ├── api/       deps.py  routers/{health,auth,students,subjects,attendance,
│   │   │              assessments,risk,trends,analytics,ai,study_plans,
│   │   │              interventions,teacher,imports}.py
│   │   ├── services/  academic_data_loader.py risk_service.py trend_service.py
│   │   │              analytics_service.py whatif_service.py ai_service.py
│   │   │              study_plan_service.py intervention_service.py teacher_service.py
│   │   │              overview_service.py import_service.py
│   │   ├── engines/   academic_types.py risk_config.py metrics.py risk_engine.py
│   │   │              trend_engine.py warnings.py analytics.py whatif.py time_budget.py
│   │   └── ai/        client.py context_builder.py prompts/ schemas.py
│   │                  validators.py fallback.py
│   ├── scripts/       reset_db.py seed_generator.py seed_demo.py create_teacher.py
│   │                  demo_advance.py demo_flow.py export_openapi.py
│   ├── tests/         unit/ api/ ai/ conftest.py
│   ├── requirements.txt  requirements-dev.txt  pytest.ini
└── frontend/          (created in Phase 13)
    └── src/ api/ auth/ components/ pages/{student,teacher}/ hooks/ types/ routes/ lib/
```

### 2.4 Responsibility matrix

| Responsibility | Frontend | Backend | Database | AI |
|---|---|---|---|---|
| Percentages, risk score, trends, thresholds | No | **Yes** | No | No |
| What-if recalculation | Inputs only | **Yes** (in memory) | Untouched | No |
| Charts | **Render** | Provide data | No | No |
| Explanation of risk factors (facts) | Display | **Templated notes** | No | No |
| Explanation and advice (prose) | Display | Request, validate, fallback | Store | **Generate** |
| Study plan: subject, day, minutes | Display | **Decide** | Store | No |
| Study plan: topic, activity text | Display | Validate, store | Store | **Generate** |
| Chat answers | Display | Build context, validate | Store | **Generate** |
| Authentication | Login UI, hold token | **Verify, issue JWT** | Store hashes | No |
| Authorization | Hide UI only | **Enforce** | No | No |
| Input validation | Convenience | **Authoritative** | Constraints | No |
| Intervention before/after | Display | **Compute** | Store snapshots | No |

### 2.5 Key data flows

**Student dashboard (Phase 12 composite endpoint)**
`GET /students/{id}/overview` (`{id}` may be `me`) → `authorize_student_access` → `load_academic_data` (bulk) → risk engine + trend engine + subject analysis + warnings → JSON (persist snapshot if changed) → frontend renders.

**AI analysis**
`POST /ai/analysis` → authorize → compute facts (engines) → `context_builder` → hash → cache hit? return. Otherwise check daily limit → AI client (timeout, ≤1 retry) → validate schema and grounding → store → return `{facts, advice, source}`. On any AI failure, use the deterministic fallback with `source: FALLBACK`.

**AI chat**
`POST /ai/chat` → student role only (caller’s own profile; `student_id` in the body is ignored) → daily USER-message limit → same academic context as analysis → last 6 `ai_chat_messages` + question in `chat_v1` → validate JSON and grounding → persist USER + ASSISTANT rows → `{answer, suggested_followups, source}`. Failure uses `fallback_chat`.

**What-if**
`POST /risk/{id}/what-if {overrides}` → load real inputs → `dataclasses.replace(inputs, **overrides)` → engine twice (current, simulated) → diff. **Zero DB writes.**

**Auth**
`POST /auth/login` (form) → verify hash → JWT `{sub, role, exp, iat}` (PyJWT, HS256) → client sends `Authorization: Bearer` → `get_current_user` (role from DB, not from the token) → `require_role` / `authorize_student_access`. Teacher visibility: the student is enrolled in a subject the teacher is assigned to, and the assignment `section` is `ALL` or equals the student's section (D4, D18). Public register creates STUDENT only; teachers via `scripts/create_teacher.py`. Teacher writes to subjects, enrollments, attendance and assessments use `authorize_teacher_subject_write` in `api/deps.py` (same assignment + section rule). List pagination is `api/pagination.py`. Engines must load facts only through `services/academic_data_loader.load(student_ids, as_of)` (bulk queries; `as_of` filters attendance and assessment dates).

---

## Decision Log

| ID | Date | Decision | Reason |
|---|---|---|---|
| D1 | 2026-09-19 | Frontend/UI last. All frontend and UI work is Phases 13–19. Phases 0–12 are backend-only, verified by pytest, Swagger UI (`/docs`) and a scripted API demo. | The SRS built UI before integration and design. Frontend last keeps the backend freezable and avoids UI work before the API exists. |
| D2 | 2026-09-19 | Public registration creates STUDENT only. Teachers are created with `scripts/create_teacher.py`. | Prevents role escalation at signup (FR-01 listed roles on public register). |
| D3 | 2026-09-19 | Teachers enter attendance, marks and previous-semester results. Students are read-only, except study habits, study plans, chat and intervention status. | The SRS never named the writer of academic data; write endpoints and authorization require a single rule. |
| D4 | 2026-09-19 | A teacher sees students enrolled in a subject the teacher teaches (`teaching_assignments`). | “Authorized data” was undefined; visibility is derived from enrollments plus teaching assignments. |
| D5 | 2026-09-19 | Attendance is stored as weekly counts (`classes_held`, `classes_attended`). Percentage is always computed, never stored. | Storing a percentage invites inconsistency with the records that define it. |
| D6 | 2026-09-19 | Risk formula keeps SRS weights, plus normalization rules, an `INSUFFICIENT_DATA` state and two escalation floors. | The SRS left gaps in ranges, missing-data behaviour and cutoffs. |
| D7 | 2026-09-19 | No Alembic. Use `create_all` + `scripts/reset_db.py` + seed. | College-demo scope; schema is rebuilt with the seed. Alembic is deferred. |
| D8 | 2026-09-19 | Study planner is hybrid. Python decides the subject, day and minutes (time budget). The AI writes the topic and activity text for each slot. | Prevents the AI from inventing durations or dropping required slots. |
| D9 | 2026-09-19 | Analysis and recommendations are one call (`analyze_performance`). Three AI capabilities in total: analysis, study plan, chat. | `analyze_performance` and `generate_recommendations` overlapped; one call saves cost and keeps advice coherent. |
| D10 | 2026-09-19 | Libraries: PyJWT, `pwdlib[argon2]` (or `bcrypt`), `pydantic-settings`, OAuth2 password-form login so Swagger “Authorize” works. Avoid `python-jose` and `passlib`. | Maintenance concerns on the avoided libraries; Swagger login is required for demo verification. |
| D11 | 2026-09-19 | New doc `RISK_ENGINE_SPEC.md`. TypeScript API types are generated from the exported OpenAPI (Phase 13). | Risk formulas need a dedicated spec; frontend types must match the frozen API. |
| D12 | 2026-09-19 | Deferred: notifications, email, PDF export, reporting module, Docker, Alembic. CI is optional. | Low demo value relative to cost; reporting and notifications had no endpoints. |
| D13 | 2026-09-19 | Risk snapshots persisted as a side effect of computing risk. No background jobs, no cache invalidation. | Keeps scoring request-driven and testable; avoids a job runner for a college project. |
| D14 | 2026-09-19 | Escalation reason is per floor that fired (attendance and/or internal). Both reasons are stored when both fire. | `RISK_ENGINE_SPEC` named two floors but only one example string. |
| D15 | 2026-09-19 | Errors live in `core/errors.py` + `core/exception_handlers.py`; request tracing lives in `core/logging.py` (`RequestIdMiddleware`). All HTTP failures use the `API_SPEC.md` `{error:{code,message,details}}` envelope. | Phase 1 needs one error shape and a request id without adding auth or a logging framework. |
| D16 | 2026-09-19 | Password hashing uses `pwdlib[argon2]` via `PasswordHash.recommended()` in `core/security.py`. JWT create/decode uses PyJWT HS256 in the same module (`create_access_token` / `decode_access_token`). | D10 named PyJWT and pwdlib; hashing shipped in Phase 2 and tokens in Phase 3. |
| D17 | 2026-09-19 | Demo seed logic lives in `scripts/seed_generator.py`; `scripts/seed_demo.py` is the CLI. Default `--as-of` is the fixed date `2026-09-19` (not `date.today()`). One password hash is reused for all seeded users. Phase 5.10 writes 4 risk snapshots per student (`as_of` minus 9/6/3/0 weeks). | Tests need an importable generator and date-stable records. Argon2-per-user would make seed slow. `datetime.now()` would break determinism. |
| D18 | 2026-09-19 | Teacher visibility requires an enrollment on an assigned subject **and** (`teaching_assignments.section` is `ALL` or equals `students.section`). Authorization stays in `api/deps.py`. | D4 named subject+enrollment only; the seed gives `teacher2` CS301 section B, which is meaningless without a section match. |
| D19 | 2026-09-19 | Creating a subject assigns the creator with section `ALL`. Teacher writes share `authorize_teacher_subject_write`. CSV import (task 4.9) is deferred to Phase 12.9. | POST `/subjects` must leave the creator able to enroll any section; one write rule avoids duplicating D18 in each router. CSV is optional and not needed for engines. |
| D20 | 2026-09-19 | `StudentAcademicData` and row dataclasses live in `engines/academic_types.py`; the loader re-exports them. | `metrics.py` must stay free of SQLAlchemy; importing the loader would violate the engine import boundary. |
| D21 | 2026-09-19 | Class analytics uses Pandas (`pandas==2.3.3`) over dataclasses in `engines/analytics.py`. Trend slope is hand-rolled least squares (no NumPy in the trend engine). | Phase 6.6 requires Pandas for class summaries; keeping slope local avoids pulling a numeric stack into every engine. |
| D22 | 2026-09-19 | Student-vs-class comparison group = same `department`, `semester` and `section`. Hidden unless the group has ≥ 5 students. | Spec required a privacy floor; the natural cohort is the section. |
| D23 | 2026-09-19 | Seed IMPROVING/DECLINING marks follow the assessment week (not item index); IMPROVING attendance lerps 55→92 so weekly attendance slope clears ±2.0. | Mixed-type overall series stayed STABLE under the official cutoffs; the demo story is visible on weekly attendance. |
| D24 | 2026-09-19 | What-if `study_hours_per_day` is 0–24. `changed_factors` include `hypothetical` when an override activates a previously `None` component. Optional `as_of` on `POST /risk/{id}/what-if`. | Spec required out-of-range 422 and a hypothetical flag but did not name an hours ceiling or the query date. |
| D25 | 2026-09-19 | AI provider SDK is `openai==1.109.1`. Extra settings defaults (not required in `.env.example`): `AI_MAX_TOKENS_ANALYSIS=800`, `AI_CACHE_TTL_HOURS=24`, `AI_RETRY_BACKOFF_SECONDS=1`. Chat usage stays 0 until Phase 10. | Phase 8 needs a thin Chat Completions wrapper; extra knobs stay optional so the env template from 0.1 is unchanged. |
| D26 | 2026-09-19 | Study window is `[as_of, exam_date)` (exam tomorrow = 1 day). Empty `subject_ids` auto-picks up to 3 HIGH_CONCERN / lowest-performance enrolled subjects. Slot text caps: topic 80, activity 200, tips 3×200. Extra setting `AI_MAX_TOKENS_PLAN=1200`. Daily plan limit counts `study_plans` rows. | AI-2 left auto-pick count, window edges and text caps unspecified; Python must still guarantee minutes and dates. |
| D27 | 2026-09-19 | Chat is student-only and always uses the caller’s facts (`student_id` ignored). Prompt window is the last 6 stored messages. Daily chat limit counts USER `ai_chat_messages` for the UTC day. Extra setting `AI_MAX_TOKENS_CHAT=600`. Follow-ups capped at 3×120. | AI-3 left limit counting, history persistence details and chat token cap unspecified. |
| D28 | 2026-09-19 | Intervention progress: `change = current_score − baseline_score`; `|change| < 2.0` is UNCHANGED (`engines/intervention_progress.py`). Students may only move PENDING → IN_PROGRESS → COMPLETED. Teachers may reopen. AI-4 suggestions are not persisted and do not use the analysis cache or daily analysis limit. Teacher lists compute live risk in memory (no snapshot writes). | Phase 11 needed a single observational threshold and a cheap suggestions path that does not expand `ai_advice.kind`. |
| D29 | 2026-09-19 | `GET /students/{id}/overview` is a composite of profile, compact risk, top factors, subject analysis, trend labels/slopes, warnings and open (PENDING/IN_PROGRESS) interventions. Risk persistence uses the existing snapshot rule. | Phase 12 dashboard contract; avoids a second risk formula. |
| D30 | 2026-09-19 | CSV import is `POST /imports/attendance` and `POST /imports/assessments` (multipart `file`, `dry_run` default true). Parsing uses the stdlib `csv` module, not Pandas. Teacher write rules are applied per row; commit is all-or-nothing. | Completes deferred 4.9 without adding a dependency. Class analytics still uses Pandas (D21). |
| D31 | 2026-09-19 | Teacher list/dashboard snapshot history is loaded in one query (`load_snapshots_bulk`). Seed story marks/attendance were steepened so Rahul’s live score is ≥ 80; `scripts/demo_advance.py` adds 4 recovery weeks so later risk lands about 50–70. | Phase 12.5/12.6: demo story and N+1 on `/teacher/students`. |
