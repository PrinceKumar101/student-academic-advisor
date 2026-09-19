# DEVELOPMENT PLAN: Student Academic Advisor

**Covers Outputs 6, 7, 9, 10** (roadmap, task breakdown, verification, state management).
Design details live in `MASTER_DESIGN.md` (later split into `ARCHITECTURE.md`, `DATABASE_SCHEMA.md`, `API_SPEC.md`, `AI_GUIDELINES.md`, `RISK_ENGINE_SPEC.md`).

**Core ordering rule: all frontend and UI work is in Stage 2 (Phases 13–19).** Stage 1 (Phases 0–12) is backend-only. It is verified with pytest, Swagger UI (`/docs`) and scripted demos, then frozen before any frontend code exists.

**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked
**Priority tags:** **[M]** must · **[S]** should · **[C]** could
**Task ID = Prompt ID.** Each task is one coding-agent prompt (`CODING_PROMPTS.md`).

---

## 1. Roadmap at a glance

| Stage | Phase | Name | Depends on |
|---|---|---|---|
| **1: Backend** | 0 | Planning & documentation | none |
| | 1 | Backend setup | 0 |
| | 2 | Database & seed data | 1 |
| | 3 | Authentication & authorization | 2 |
| | 4 | Academic data APIs | 3 |
| | 5 | Risk engine | 4 |
| | 6 | Trends, subject analysis, early warnings | 5 |
| | 7 | What-if simulator | 5 |
| | 8 | AI service (analysis) | 5, 6 |
| | 9 | AI study planner | 8 |
| | 10 | AI assistant (chat) | 8 |
| | 11 | Interventions & teacher APIs | 4, 5, 6 |
| | 12 | Backend integration, hardening, **freeze** | 6–11 |
| **2: Frontend (last)** | 13 | Frontend foundation | 12 |
| | 14 | Student pages (functional) | 13 |
| | 15 | Teacher pages (functional) | 13 |
| | 16 | Frontend integration & E2E, **functional freeze** | 14, 15 |
| | 17 | UI design | 16 |
| | 18 | UI polish | 17 |
| | 19 | Final documentation & demo | 18 |

### Dependency graph

```text
P0 Planning
 └─ P1 Setup ─ P2 Database ─ P3 Auth ─ P4 Academic data ─ P5 Risk engine
                                                            ├─ P6 Analytics ──┐
                                                            ├─ P7 What-if ────┤   (P6 ∥ P7)
                                                            │                 ├─ P8 AI service ─┬─ P9 Planner ─┐
                                                            │                 │                 └─ P10 Chat ───┤  (P9 ∥ P10 ∥ P11)
                                                            └─────────────────┴─ P11 Interventions ───────────┤
                                                                                                              P12 Integration + BACKEND FREEZE
                                                                                                                │
                                                                                          P13 Frontend foundation
                                                                                           ├─ P14 Student pages ─┐  (P14 ∥ P15)
                                                                                           └─ P15 Teacher pages ─┤
                                                                                                                 P16 Integration + FUNCTIONAL FREEZE
                                                                                                                 └─ P17 UI design ─ P18 UI polish ─ P19 Final docs & demo
```

Parallel groups (only useful if more than one person or agent works at once; a single developer just picks the order): **P6 ∥ P7**, **P9 ∥ P10 ∥ P11**, **P14 ∥ P15**.

---

## 2. Global rules

### 2.1 Phase gate (every phase must pass before the next starts)

- [ ] All tests pass (`pytest`; frontend: `vitest` from Phase 13). Actual command output was seen, never assumed.
- [ ] New behaviour has tests, including edge cases.
- [ ] `ruff check` clean (backend) and no secrets in the diff.
- [ ] Docs synchronized (§2.2).
- [ ] `DEVELOPMENT_PLAN.md` checkboxes updated. `CLAUDE_CONTEXT.md` refreshed.
- [ ] Git commit `phase-N: <summary>` and tag `phase-N-done`.

### 2.2 Documentation synchronization

| If the agent changes… | Update |
|---|---|
| Tables, columns, constraints | `DATABASE_SCHEMA.md` |
| Endpoints, request/response, errors | `API_SPEC.md` |
| Folder structure, layering, new dependency, design decision | `ARCHITECTURE.md` (Decision Log) |
| AI prompts, schemas, limits, failure behaviour | `AI_GUIDELINES.md` |
| Risk weights, thresholds, formulas | `RISK_ENGINE_SPEC.md` (and bump `config_version`) |
| Any task status | `DEVELOPMENT_PLAN.md` |
| Phase completed | `CLAUDE_CONTEXT.md` |

### 2.3 Global edge cases (each phase checks the ones that apply)

Missing data · invalid values · empty datasets · zero classes held · no assessments · student with no enrollments · AI API failure/timeout/invalid JSON · database constraint violation · unauthorized and cross-student access.

### 2.4 Test tooling

`pytest`, FastAPI `TestClient`, an in-memory SQLite DB per test session with FK pragma on, factory helpers in `tests/conftest.py`, and a **fake AI client** fixture. **No test ever calls the real AI API.**

---

# STAGE 1: BACKEND (Phases 0–12)

---

## Phase 0: Planning & Documentation

**Objective:** Repo skeleton and the full documentation set exist; no architectural ambiguity remains.
**Depends on:** approval of this plan.
**Files:** repo root docs, `.cursor/rules/project.mdc`, `.gitignore`, `.env.example`.

- [x] 0.1 **[M]** Create the repo skeleton, `.gitignore`, `.env.example`, `project.mdc` (agent protocol), README stub, `git init`.
- [ ] 0.2 **[M]** Split `MASTER_DESIGN.md` into `PROJECT_SPEC.md`, `ARCHITECTURE.md` (with a Decision Log), `DATABASE_SCHEMA.md`, `API_SPEC.md`, `AI_GUIDELINES.md`, `RISK_ENGINE_SPEC.md`. Add `UI_GUIDELINES.md` stub ("deferred to Phase 17"). Place `DEVELOPMENT_PLAN.md` and `CLAUDE_CONTEXT.md`.
- [ ] 0.3 **[M]** Consistency review: check that endpoints, tables and enums agree across all docs. List open questions.

**Tests:** none (documentation). **Docs:** all created.
**Exit criteria:** every doc exists; the SRS and `MASTER_DESIGN.md` are in `docs/archive/`; open questions are empty or answered; first commit made.
**Risks:** docs drifting from the plan. Mitigation: copy, do not paraphrase.

---

## Phase 1: Backend Setup

**Objective:** A runnable FastAPI app with config, error format, logging, CORS and a passing test.
**Depends on:** 0.
**Files:** `backend/app/main.py`, `core/config.py`, `core/errors.py`, `core/logging.py`, `tests/`.

- [ ] 1.1 **[M]** Backend scaffold: venv, minimal `requirements.txt` (fastapi, uvicorn, pydantic-settings, python-multipart), `requirements-dev.txt` (pytest, pytest-cov, httpx, ruff), app factory, `/api/v1` router, `GET /health`, settings from `.env`.
- [ ] 1.2 **[M]** Standard error handlers (format in `MASTER_DESIGN.md` §4.1, including 422 conversion), structured logging with a request-id middleware, CORS from config.
- [ ] 1.3 **[M]** pytest config, `conftest.py` with a `client` fixture, tests for `/health`, error format and CORS. `ruff` config.
- [ ] 1.4 **[S]** README run instructions (venv, install, run, test).

**Tests:** `/health` 200; unknown route gives the standard 404; invalid body gives the standard 422 shape; CORS header present for the allowed origin only.
**Exit criteria:** `uvicorn` starts; `/docs` loads; `pytest` green; error format verified.
**Risks:** dependency creep. Add packages only when a phase needs them.

---

## Phase 2: Database & Seed Data

**Objective:** Schema, constraints and realistic synthetic data.
**Depends on:** 1.
**Files:** `db/`, `models/`, `core/security.py` (hash helpers only), `scripts/reset_db.py`, `scripts/seed_demo.py`.

- [ ] 2.1 **[M]** SQLAlchemy setup (engine, session, `Base`, `get_db`), **SQLite FK pragma**, `enums.py`. Models: `User`, `Student`, `Teacher`. `core/security.py` with `hash_password` / `verify_password`.
- [ ] 2.2 **[M]** Models: `Subject`, `Enrollment`, `TeachingAssignment`, `AttendanceRecord`, `Assessment` (with CHECK constraints), `SemesterResult`, `StudyHabit`.
- [ ] 2.3 **[M]** Model: `RiskAssessment` (JSON columns). Indexes review. `reset_db.py` (drop, create).
- [ ] 2.4 **[M]** Seed generator core: RNG, profile parameters (six profiles), name list, subject and teacher setup, enrollments, teaching assignments.
- [ ] 2.5 **[M]** Seed generator data: weekly attendance, assessments (INTERNAL/QUIZ/ASSIGNMENT with MISSING status), semester results, study habits per profile.
- [ ] 2.6 **[M]** Story and edge students (`rahul`, `newstudent`, `zeroclass`, `missingassign`) and `seed_demo.py` CLI with `--as-of`.
- [ ] 2.7 **[M]** Database tests: constraints, FK enforcement, uniqueness, cascade rules, seed counts and determinism.

**Tests:** CHECK violations (`attended > held`, `GRADED` without marks); duplicate `(student, subject)` enrollment rejected; FK enforcement proven (insert with a bad FK fails); seed twice gives identical data; counts match §9 of the design.
**Docs:** `DATABASE_SCHEMA.md` (final columns).
**Exit criteria:** `reset_db` + `seed_demo` runs in seconds; 43 students, 5 subjects, 2 teachers present; all DB tests green.
**Risks:** seed realism (tuned in 5.10 and 12.5); forgetting the FK pragma.

---

## Phase 3: Authentication & Authorization

**Objective:** Secure login and central access control.
**Depends on:** 2.
**Files:** `core/security.py`, `api/deps.py`, `api/routers/auth.py`, `schemas/auth.py`, `scripts/create_teacher.py`.

- [ ] 3.1 **[M]** JWT create/decode (PyJWT), config for secret and expiry, startup check for the default secret outside dev.
- [ ] 3.2 **[M]** `POST /auth/register` (student only, creates user + student profile), password rules, 409 on duplicates.
- [ ] 3.3 **[M]** `POST /auth/login` (OAuth2 form), identical 401 for all failures, inactive users rejected.
- [ ] 3.4 **[M]** `get_current_user`, `require_role(...)`, `GET /auth/me`, `POST /auth/logout` (204).
- [ ] 3.5 **[M]** `authorize_student_access(student_id | "me")` covering the student-own and teacher-visible rules (via `teaching_assignments` + enrollments).
- [ ] 3.6 **[M]** `scripts/create_teacher.py`.
- [ ] 3.7 **[M]** Auth tests (below).

**Tests:** valid login; wrong password and unknown email are indistinguishable; expired token 401; tampered token 401; missing token 401; register cannot set a role (extra field ignored or rejected); student cannot call a teacher-only route (403); **student A → student B = 403**; teacher sees own subject's students, not others; inactive user rejected; `password_hash` never in any response.
**Docs:** `API_SPEC.md` (auth), `ARCHITECTURE.md` (auth flow, library choice).
**Exit criteria:** Swagger "Authorize" works; the access dependency is unit-tested for all four user/target combinations.
**Risks:** authorization logic duplicated later. Mitigation: only `deps.py` decides.

---

## Phase 4: Academic Data APIs

**Objective:** CRUD for all academic data plus a bulk loader that feeds the engines.
**Depends on:** 3.
**Files:** `api/routers/{students,subjects,attendance,assessments}.py`, `services/academic_data_loader.py`, `schemas/`.

- [ ] 4.1 **[M]** Subjects CRUD + enrollment endpoints.
- [ ] 4.2 **[M]** `GET /students/{id}`, study-habits GET/PUT (student own only), semester-results GET/PUT (teacher).
- [ ] 4.3 **[M]** Attendance endpoints with the computed % summary per subject (guards zero classes).
- [ ] 4.4 **[M]** Assessment endpoints (types, status rules, marks bounds).
- [ ] 4.5 **[M]** Teacher write-permission rule (only taught subjects and sections) shared by 4.1, 4.3 and 4.4.
- [ ] 4.6 **[M]** Pagination and filter helpers.
- [ ] 4.7 **[M]** `academic_data_loader.load(student_ids, as_of)` returns plain dataclasses (`StudentAcademicData`) using bulk queries, filtering by `as_of`.
- [ ] 4.8 **[M]** API tests for all endpoints plus the loader.
- [ ] 4.9 **[S]** CSV import for attendance and assessments (validate, dry-run, then commit). *Defer to Phase 12 if time is short.*

**Tests:** every endpoint × (owner, other student, teacher-of-subject, teacher-of-other-subject); validation errors; percent computed from records; zero classes → `null`; loader returns the same numbers as raw SQL sums; loader respects `as_of`; loader query count does not grow with student count.
**Docs:** `API_SPEC.md`.
**Exit criteria:** all data can be created and read via Swagger; loader is the only place engines get data.
**Risks:** N+1 queries (test in 4.8); permission gaps (matrix test later in 12.2).

---

## Phase 5: Academic Risk Engine

**Objective:** Deterministic, tested risk scoring per `RISK_ENGINE_SPEC.md`.
**Depends on:** 4.
**Files:** `engines/{risk_config,metrics,risk_engine}.py`, `services/risk_service.py`, `api/routers/risk.py`, `tests/unit/test_risk_*.py`.

- [ ] 5.1 **[M]** `risk_config.py`: weights, thresholds, cutoffs, `config_version`, import-time validation, **round-half-up** helper.
- [ ] 5.2 **[M]** `metrics.py`: turn `StudentAcademicData` into `RiskInputs` (percent definitions from design §6.1).
- [ ] 5.3 **[M]** Component normalizers (attendance, performance, assignments, study).
- [ ] 5.4 **[M]** Aggregator: missing-data renormalization, completeness, `INSUFFICIENT_DATA`.
- [ ] 5.5 **[M]** Classification + escalation floors.
- [ ] 5.6 **[M]** Component levels, `top_factors`, templated notes, flags.
- [ ] 5.7 **[M]** `risk_service`: load → compute → persist snapshot (only if none today or score changed).
- [ ] 5.8 **[M]** `GET /risk/{id}`, `GET /risk/{id}/history`.
- [ ] 5.9 **[M]** Test suite: R1–R13 from the design, plus API tests.
- [ ] 5.10 **[M]** Extend seed: back-fill 4 historical snapshots per student using `as_of`; check profile students land in expected bands and `rahul` ends HIGH.

**Tests:** cases R1–R13 with the exact expected values; seeded property test for monotonicity; snapshot dedupe; API authorization; engine has no imports from FastAPI, SQLAlchemy or `ai/` (an import-boundary test).
**Docs:** `RISK_ENGINE_SPEC.md` final, `API_SPEC.md`.
**Exit criteria:** `pytest tests/unit/test_risk_*` green with ≥ 90% engine coverage; `GET /risk/me` works in Swagger for seeded users; results match the hand-calculated cases.
**Risks:** formula tuning trap. Change weights only in config plus spec, and bump `config_version`.

---

## Phase 6: Trends, Subject Analysis & Early Warnings

**Objective:** Performance over time and early-warning detection.
**Depends on:** 5.
**Files:** `engines/{trend_engine,warnings,analytics}.py`, `services/{trend_service,analytics_service}.py`, `api/routers/{trends,analytics}.py`.

- [ ] 6.1 **[M]** `trend_engine`: least-squares slope, labels, sudden-change flag, minimum 3 points.
- [ ] 6.2 **[M]** Series builders: overall, per type, per subject, weekly attendance, risk history.
- [ ] 6.3 **[M]** Subject analysis (bands, subject attendance alerts).
- [ ] 6.4 **[M]** Early-warning rules (design §7.3), configurable thresholds.
- [ ] 6.5 **[M]** `GET /trends/{id}`, `GET /trends/{id}/warnings`, `GET /analytics/students/{id}/subjects`.
- [ ] 6.6 **[M]** Class-analytics functions (Pandas): level counts, means, per-subject means, trend distribution. *(Endpoints in Phase 11.)*
- [ ] 6.7 **[S]** `GET /analytics/students/{id}/comparison` (only when group ≥ 5).
- [ ] 6.8 **[M]** Tests.

**Tests:** 72,69,63,55 → slope −5.7, DECLINING; flat → STABLE; 2 points → INSUFFICIENT_DATA; 50,52,51,90 → SUDDEN_RISE; SRS examples (82→67 attendance WARNING, 76→48 quiz CRITICAL); subject bands at 49.9/50/64.9/65; empty data; seeded `rahul` has DECLINING trend and warnings; seeded improving student has IMPROVING.
**Docs:** `RISK_ENGINE_SPEC.md` (trend section), `API_SPEC.md`.
**Exit criteria:** engines pure and tested; endpoints return sensible results for all seed profiles.
**Risks:** noisy small samples labelled with false confidence; return the values with the label.

---

## Phase 7: What-If Simulator

**Objective:** Hypothetical risk recalculation with zero persistence.
**Depends on:** 5.
**Files:** `engines/whatif.py`, `services/whatif_service.py`, `api/routers/risk.py`.

- [ ] 7.1 **[M]** Request schema with allowed keys and bounds.
- [ ] 7.2 **[M]** `simulate(inputs, overrides)` returning current, simulated, difference, changed factors.
- [ ] 7.3 **[M]** `POST /risk/{id}/what-if` with authorization.
- [ ] 7.4 **[M]** Tests.

**Tests:** attendance 64 → 80 on R3 gives −10.0 and MEDIUM (W1); unknown key 422; out-of-range 422; empty overrides give difference 0; **row counts and values in every table unchanged after the call**; activating a `None` component is flagged hypothetical.
**Docs:** `API_SPEC.md`.
**Exit criteria:** the "Attendance 64 → 80" demo step works in Swagger.
**Risks:** accidental commit inside the request; mitigated by using a read-only session path and the unchanged-DB test.

---

## Phase 8: AI Service (Analysis)

**Objective:** A safe, isolated AI layer with a guaranteed fallback.
**Depends on:** 5, 6.
**Files:** `ai/*`, `services/ai_service.py`, `models/ai_advice.py`, `api/routers/ai.py`.

- [ ] 8.1 **[M]** Config (key, model name, timeouts, daily limits) and `ai/` package skeleton. Add `openai` dependency.
- [ ] 8.2 **[M]** `ai/client.py`: timeout, single-retry policy, error taxonomy (`TIMEOUT`, `PROVIDER_ERROR`, `NOT_CONFIGURED`), usage logging. Injectable so tests use a fake.
- [ ] 8.3 **[M]** `context_builder`: `StudentAcademicContext` from engine outputs; no-PII test.
- [ ] 8.4 **[M]** Output schemas (Pydantic) and validators: structure, enums, lengths, grounding check (§5.4).
- [ ] 8.5 **[M]** Prompt `analysis_v1` (system + user templates, injection hardening).
- [ ] 8.6 **[M]** Deterministic fallback advice generator (from risk factors and warnings).
- [ ] 8.7 **[M]** `AIAdvice` model, input-hash cache (24 h), daily-limit counting, `GET /ai/usage`.
- [ ] 8.8 **[M]** `analyze_performance` service and `POST /ai/analysis`.
- [ ] 8.9 **[M]** Tests with the fake client (below).
- [ ] 8.10 **[S]** `scripts/ai_smoke_test.py` for a manual real-API check (never run in CI, skipped without a key).

**Tests:** happy path; timeout gives fallback; 429/5xx retries once then falls back; 4xx no retry; invalid JSON gives fallback; missing field gives fallback; wrong enum gives fallback; **hallucinated percentage gives `UNGROUNDED_OUTPUT` fallback**; no key gives `NOT_CONFIGURED`; cache hit does not call the client and does not count toward the limit; limit exceeded gives 429; context has no name/email/id; teacher and student authorization; risk endpoints work with the AI disabled.
**Docs:** `AI_GUIDELINES.md` (prompts, schemas, limits), `API_SPEC.md`.
**Exit criteria:** with a real key the smoke test returns valid advice; with no key the endpoint still returns useful fallback advice; all AI tests green.
**Risks:** provider API changes (thin wrapper), cost (limits and cache), model output drift (validation).

---

## Phase 9: AI Study Planner

**Objective:** Stored, validated study plans (hybrid Python budget + AI text).
**Depends on:** 8.
**Files:** `engines/time_budget.py`, `ai/prompts/plan_v1`, `models/study_plan*.py`, `services/study_plan_service.py`, `api/routers/study_plans.py`.

- [ ] 9.1 **[M]** Models `StudyPlan`, `StudyPlanItem`.
- [ ] 9.2 **[M]** Request schema and validation (exam date future and ≤ 60 days, hours 0.5–12, subjects belong to the student).
- [ ] 9.3 **[M]** `time_budget.allocate(...)` (pure): concern-weighted minutes per subject per day, per-day cap, priorities.
- [ ] 9.4 **[M]** Prompt `plan_v1` and output schema (slot text only).
- [ ] 9.5 **[M]** Plan validator: every `slot_id` exactly once, no extras, text caps; failure gives the fallback plan.
- [ ] 9.6 **[M]** Fallback plan with templated activities.
- [ ] 9.7 **[M]** Endpoints: create, list, get, patch item completion, delete.
- [ ] 9.8 **[M]** Tests.

**Tests:** budget never exceeds available minutes per day; weaker subjects get more minutes; exam tomorrow (1 day) works; 0 weak subjects auto-picks lowest subjects; AI returns an unknown or missing slot gives fallback; AI failure gives fallback plan with 200; invalid dates 422; a student cannot read another student's plan; item toggle persists; daily plan limit.
**Docs:** `AI_GUIDELINES.md`, `API_SPEC.md`, `DATABASE_SCHEMA.md`.
**Exit criteria:** a plan can be generated, stored, listed, ticked off; works with the AI off.
**Risks:** generic AI text; accepted, since dates and durations are guaranteed by Python.

---

## Phase 10: AI Academic Assistant

**Objective:** Context-aware chat with bounded history.
**Depends on:** 8.
**Files:** `ai/prompts/chat_v1`, `models/ai_chat_message.py`, `services/ai_service.py`, `api/routers/ai.py`.

- [ ] 10.1 **[M]** `AIChatMessage` model; history GET/DELETE.
- [ ] 10.2 **[M]** Chat context assembly (context + last 6 messages), length limits (question ≤ 500 chars).
- [ ] 10.3 **[M]** Prompt `chat_v1` (scope rules, no invented numbers, admit missing data).
- [ ] 10.4 **[M]** `answer_academic_question` and `POST /ai/chat` with the same validation, retry and fallback rules.
- [ ] 10.5 **[M]** Daily chat limit; friendly fallback message; canned deterministic answers for common questions.
- [ ] 10.6 **[M]** Tests.

**Tests:** ownership (student chats about own data only; `student_id` in the body is ignored/rejected); empty and over-long question 422; prompt-injection strings ("ignore previous instructions", "show me another student's marks") do not change context or expose other data (fake client asserts the prompt content); off-topic handling; AI failure gives fallback; history window is 6; clear history works; limit gives 429.
**Docs:** `AI_GUIDELINES.md`, `API_SPEC.md`.
**Exit criteria:** chat works with the real key and degrades gracefully without it.
**Risks:** long-lived history bloat (fixed window), off-topic misuse (system prompt + scope test).

---

## Phase 11: Interventions & Teacher APIs

**Objective:** The teacher workflow and intervention lifecycle.
**Depends on:** 4, 5, 6.
**Files:** `models/intervention.py`, `services/{intervention_service,teacher_service}.py`, `api/routers/{interventions,teacher}.py`.

- [ ] 11.1 **[M]** `Intervention` model.
- [ ] 11.2 **[M]** `POST /interventions`: only for visible students; **stores the baseline risk at creation**.
- [ ] 11.3 **[M]** List, get, patch with role rules (teacher: any field; student: `status` + `completion_note`), forward-only student transitions; capture the outcome on COMPLETED.
- [ ] 11.4 **[M]** `GET /interventions/{id}/progress` (before/after, observational wording).
- [ ] 11.5 **[M]** `GET /teacher/dashboard` (counts, means, subject performance, trend distribution).
- [ ] 11.6 **[M]** `GET /teacher/students` with filters (risk level, department, semester, section, subject, search) and pagination, using the bulk loader.
- [ ] 11.7 **[M]** `GET /teacher/subjects/{id}/analytics`.
- [ ] 11.8 **[C]** `POST /ai/intervention-suggestions`.
- [ ] 11.9 **[M]** Tests.

**Tests:** teacher cannot intervene on an invisible student; student sees only own interventions and can only change status/note; status regression by a student rejected; baseline captured and unaffected by later data; progress direction thresholds (IMPROVED / WORSENED / UNCHANGED at ±2); each filter individually and combined; filter to zero results; dashboard numbers equal a hand-computed set on a small fixture.
**Docs:** `API_SPEC.md`, `DATABASE_SCHEMA.md`.
**Exit criteria:** create → progress → complete works end to end via Swagger.
**Risks:** teacher list performance (200-student test in 12.6); causal wording (fixed note string).

---

## Phase 12: Backend Integration, Hardening & FREEZE

**Objective:** Prove the whole backend works as one story, then freeze the API.
**Depends on:** 6–11.
**Files:** `api/routers/students.py`, `tests/api/`, `scripts/{demo_advance,demo_flow,export_openapi}.py`, `openapi.json`.

- [ ] 12.1 **[M]** `GET /students/{id}/overview` composite (profile, risk, top factors, subject analysis, trend summary, warnings, open interventions).
- [ ] 12.2 **[M]** **Authorization matrix test**: parametrized over every route × {anonymous, student self, other student, teacher of subject, other teacher}.
- [ ] 12.3 **[M]** Full-story API test mirroring the demo: login → risk HIGH → trends → what-if → AI analysis (fake) → study plan → teacher login → filter → intervention → add improved records → progress shows improvement.
- [ ] 12.4 **[M]** `demo_advance.py` (adds post-intervention records) and `demo_flow.py` (prints each demo step against a running server).
- [ ] 12.5 **[M]** Seed tuning so the story is convincing (e.g. rahul about 80+ → about 60 after advance).
- [ ] 12.6 **[M]** Performance sanity: `/teacher/students` with ~200 seeded students under about 2 s; no N+1.
- [ ] 12.7 **[M]** Security checklist pass: secrets grep, CORS, response schemas exclude sensitive fields, default JWT secret guard.
- [ ] 12.8 **[M]** Export and commit `openapi.json`; finalize `API_SPEC.md`; coverage report (engines ≥ 90%).
- [ ] 12.9 **[S]** CSV import (if deferred from 4.9).
- [ ] 12.10 **[M]** Update docs, tag `backend-v1`.

**Tests:** as above plus AI-off run of the full story (all steps still succeed with fallbacks).
**Exit criteria (BACKEND FREEZE):** Definition of Done backend checklist ticked; `pytest` green; `demo_flow.py` completes; `openapi.json` committed; from now on API changes need a documented reason and a migration note for the frontend.
**Risks:** discovering gaps late; the full-story test exists precisely to find them now.

---

# STAGE 2: FRONTEND & UI (Phases 13–19)

*Started only after the Backend Freeze. The frontend contains no business logic; it displays backend values.*

---

## Phase 13: Frontend Foundation

**Objective:** Runnable, typed, authenticated frontend skeleton (functional, unstyled).
**Depends on:** 12.
**Files:** `frontend/` (`src/{api,auth,components,pages,routes,types,lib}`), `vite.config.ts`, `tailwind.config`.

- [ ] 13.1 **[M]** Vite + React + TypeScript + Tailwind + React Router scaffold; proxy or CORS to the backend.
- [ ] 13.2 **[M]** Generate TS types from `openapi.json` (`openapi-typescript`, dev dependency only) into `src/types/api.ts`.
- [ ] 13.3 **[M]** API client: base URL from env, token attach, 401 → logout/redirect, error normalization to the standard error shape.
- [ ] 13.4 **[M]** Auth context, login and register pages, token storage, `ProtectedRoute` and role routes.
- [ ] 13.5 **[M]** Layout skeleton with role-based nav (plain utility classes only).
- [ ] 13.6 **[M]** Basic shared components: `Loading`, `ErrorMessage`, `EmptyState`, `SimpleTable`, `RiskBadge` (text label always shown, never colour only).
- [ ] 13.7 **[M]** Vitest + React Testing Library; tests for the auth guard, the API client (401 handling) and `RiskBadge`.

**Tests:** login stores the token; logout clears it; student cannot open a teacher route; 401 redirects; errors show messages.
**Docs:** `README.md` (frontend run), `ARCHITECTURE.md` (frontend structure).
**Exit criteria:** login as `rahul@demo.edu` and `teacher1@demo.edu` works and lands on role-specific placeholder pages; types compile with `tsc --noEmit`.
**Risks:** token storage (accepted for a college demo; documented), type drift (regenerate from `openapi.json`).

---

## Phase 14: Student Pages (Functional)

**Objective:** Every student capability works end to end (plain layout, correct data).
**Depends on:** 13.
**Files:** `src/pages/student/*`, `src/api/*`, `src/components/charts/*`.

- [ ] 14.1 **[M]** Dashboard from `/students/me/overview`: risk score + level, top factors, warnings, open interventions.
- [ ] 14.2 **[M]** Risk page: component table with weights, contributions and notes; completeness and flags shown.
- [ ] 14.3 **[M]** Performance page: Recharts line charts for assessment and attendance trends, trend labels.
- [ ] 14.4 **[M]** Subjects page: subject analysis table with bands.
- [ ] 14.5 **[M]** What-If page: inputs, submit, current vs simulated, difference, changed factors.
- [ ] 14.6 **[M]** AI Advisor page: analysis (facts panel separate from AI advice panel, fallback banner) and chat.
- [ ] 14.7 **[M]** Study Planner page: form, generated plan, tick items.
- [ ] 14.8 **[M]** Interventions page: list, status update, progress.
- [ ] 14.9 **[M]** Profile page + study-habits form.
- [ ] 14.10 **[M]** Tests for What-If, AI Advisor (including the fallback banner) and Study Planner (mocked API).

**Tests:** each page renders loading, empty, error and success; What-If sends only changed values; fallback banner shown when `source=FALLBACK`; plan tick calls PATCH.
**Exit criteria:** the student half of the demo story works in the browser against the real backend.
**Risks:** creeping business logic into components. Rule: no percentage, risk or trend math in the frontend.

---

## Phase 15: Teacher Pages (Functional)

**Objective:** The teacher workflow works end to end.
**Depends on:** 13.
**Files:** `src/pages/teacher/*`.

- [ ] 15.1 **[M]** Teacher dashboard (counts, means, subject performance, trend distribution).
- [ ] 15.2 **[M]** Student list with all filters, pagination, sortable by risk.
- [ ] 15.3 **[M]** Student detail: overview, risk, trends, warnings, AI analysis (optional), interventions.
- [ ] 15.4 **[M]** Create intervention form (from the student detail page).
- [ ] 15.5 **[M]** Intervention tracking page with status filter and before/after progress.
- [ ] 15.6 **[S]** Subject analytics page.
- [ ] 15.7 **[M]** Tests for filters and the intervention form.

**Tests:** filter combinations produce the right query params; empty results state; create intervention shows validation errors from the API.
**Exit criteria:** teacher half of the demo works in the browser.

---

## Phase 16: Frontend Integration & E2E (FUNCTIONAL FREEZE)

**Objective:** The full demo story runs in the browser with an unpolished UI.
**Depends on:** 14, 15.

- [ ] 16.1 **[M]** Manual run of the complete demo script (Demo section of the SRS) against the real backend; log defects.
- [ ] 16.2 **[M]** Fix defects; regenerate types if the backend changed (documented).
- [ ] 16.3 **[M]** AI-off run: disable the key and confirm all pages still work with fallbacks.
- [ ] 16.4 **[S]** One Playwright happy-path test for the demo story (optional tool; else keep a manual checklist in `docs/`).
- [ ] 16.5 **[M]** Functional freeze: tag `frontend-functional`.

**Exit criteria:** every Definition-of-Done functional item is ticked; UI is ugly but complete.
**Risks:** starting design early. Do not.

---

## Phase 17: UI Design

**Objective:** Professional, academic, data-focused design system applied everywhere.
**Depends on:** 16.

- [ ] 17.1 **[M]** Design direction + `UI_GUIDELINES.md` (principles, tokens, accessibility rules).
- [ ] 17.2 **[M]** Tailwind theme: colours (risk semantic colours plus a non-colour cue), typography, spacing, radii.
- [ ] 17.3 **[M]** Component library: Button, Card, Badge, Table, Input, Select, Tabs, Modal, Alert, Skeleton.
- [ ] 17.4 **[M]** App shell and navigation (role-aware, responsive).
- [ ] 17.5 **[M]** Restyle student pages (dashboard hierarchy: "How am I doing?" visible within seconds).
- [ ] 17.6 **[M]** Restyle teacher pages.
- [ ] 17.7 **[M]** Chart styling consistency.

**Exit criteria:** all pages use the shared components; no ad-hoc styling left; visual review passes.

---

## Phase 18: UI Polish

**Objective:** Presentation-ready quality.
**Depends on:** 17.

- [ ] 18.1 **[M]** Responsive behaviour (mobile, tablet, desktop).
- [ ] 18.2 **[M]** Loading skeletons, empty states, error states on every data view.
- [ ] 18.3 **[M]** Accessibility: keyboard navigation, focus styles, labels, contrast, ARIA for charts and tables (run axe or Lighthouse).
- [ ] 18.4 **[S]** Useful micro-interactions only (risk gauge transition, list transitions).
- [ ] 18.5 **[M]** Consistency audit (spacing, wording, disclaimers such as "risk indicator, not a prediction").

**Exit criteria:** no horizontal scroll at 375 px; accessibility checks show no critical issues; the demo path is smooth.

---

## Phase 19: Final Documentation & Demo

**Objective:** Submission-ready project.
**Depends on:** 18.

- [ ] 19.1 **[M]** Final `README.md` (setup, seed, run, test, demo logins).
- [ ] 19.2 **[M]** `docs/DEMO_SCRIPT.md` (the 11-step story with expected values).
- [ ] 19.3 **[M]** Screenshots; architecture, database and API docs verified against the code.
- [ ] 19.4 **[M]** `docs/VIVA_NOTES.md`: likely questions (why deterministic risk? why is AI not calculating? how is hallucination handled? why SQLite? limitations and honesty about heuristic weights).
- [ ] 19.5 **[M]** Final report and presentation outline.
- [ ] 19.6 **[M]** Definition of Done checklist run; tag `v1.0`.

**Exit criteria:** a fresh clone can be set up from the README and run the demo.

---

# 3. VERIFICATION SUMMARY (Output 9)

| Phase | Key acceptance test | Exit evidence |
|---|---|---|
| 0 | Docs consistent | All docs present, open questions closed |
| 1 | `/health`, error format | pytest green, `/docs` loads |
| 2 | Constraints and FK enforced; seed deterministic | DB tests green, 43 students seeded |
| 3 | Login, expiry, tamper, cross-student 403 | Auth tests green |
| 4 | CRUD and permissions; loader correct | API tests green, no N+1 |
| 5 | R1–R13 exact values | ≥ 90% engine coverage |
| 6 | −5.7 slope example; warnings | Trend tests green |
| 7 | 64 → 80 gives −10.0; DB unchanged | What-if tests green |
| 8 | AI failure modes all fall back | AI tests green; smoke test OK |
| 9 | Plan constraints hold; fallback works | Planner tests green |
| 10 | Injection and ownership tests | Chat tests green |
| 11 | Intervention lifecycle and filters | Teacher tests green |
| 12 | Full-story test; authorization matrix | Backend freeze tag |
| 13–16 | Pages and E2E per demo | Functional freeze tag |
| 17–18 | Design and accessibility checks | Visual and a11y review |
| 19 | Fresh-clone setup works | `v1.0` tag |

---

# 4. PROJECT STATE MANAGEMENT (Output 10)

### 4.1 `DEVELOPMENT_PLAN.md` (this file): the tracker

- Updated by the **coding agent at the end of every task**: tick the checkbox, and add a one-line note under the task if it deviated (e.g. `> 4.4 deviation: added status default GRADED; see DATABASE_SCHEMA.md`).
- Never delete tasks. Mark `[!]` with a reason if blocked. Add new tasks with an ID like `5.11` and a note "added because…".
- The **phase gate** checklist (§2.1) is confirmed at the end of each phase.

### 4.2 `CLAUDE_CONTEXT.md`: the snapshot

- Updated **at the end of each phase**, and after any major decision.
- Hard limit: about 60 lines. Overwrite sections instead of appending history.
- Sections: Current Phase · Current Task · Completed · In Progress · Next · Important Decisions · Known Issues · Recent Changes · Key Files.
- Use it: paste it at the start of every new Claude planning chat (opening message template in `CODING_PROMPTS.md`) instead of the SRS.

### 4.3 Loop per task

```text
1. Planner (Claude) picks the next unchecked task and writes/opens its prompt
2. Coding agent runs it: inspect -> smallest change -> tests -> docs -> report
3. You verify: run the tests yourself; skim the diff
4. Agent ticks DEVELOPMENT_PLAN.md; phase end: CLAUDE_CONTEXT.md + tag
5. Back to 1
```

### 4.4 Decision log

Any deviation from `MASTER_DESIGN.md` (new dependency, changed table, changed weight) is recorded in the Decision Log section of `ARCHITECTURE.md` with the date, the reason and the affected docs.

---

# 5. DEFINITION OF DONE (from the SRS, mapped to phases)

**Backend (Phases 1–12):** FastAPI (1) · Database (2) · Authentication and authorization (3) · Academic CRUD (4) · Risk engine (5) · Trend engine (6) · What-if (7) · AI service (8) · Study planner (9) · Assistant (10) · Interventions (11) · Tests pass (12).
**Frontend (Phases 13–18):** login · student dashboard, performance, risk, what-if, AI advisor, study planner · teacher dashboard · interventions · charts · loading/error states · responsive.
**Documentation (Phases 0, 19):** README · architecture · database · API · AI behaviour · setup · demo instructions.
