# CODING PROMPTS: Student Academic Advisor

**Covers Output 8.** Prompts for the coding agent (Cursor or Claude Code).

**How this stays small:** the rules every prompt needs live once in `.cursor/rules/project.mdc` (§1). Each prompt then contains only its task, its files, its tests and its "done" list. Prompts never repeat the SRS.

**Scope of this file:** full prompts for **Phases 0–2** (Prompts 0.1 to 2.2). The rest of the prompts follow the same template and are generated phase by phase after you approve the plan and finish the previous phase. Prompt ID = task ID in `DEVELOPMENT_PLAN.md`. Every task there has a unique prompt ID.

---

## 1. Agent protocol → save as `.cursor/rules/project.mdc`

(For Claude Code, also create a `CLAUDE.md` containing: "Read `.cursor/rules/project.mdc` and `CLAUDE_CONTEXT.md` before every task.")

```text
---
description: Student Academic Advisor: permanent project rules
alwaysApply: true
---

SOURCES OF TRUTH (read the relevant ones before every task)
SRS.md, PROJECT_SPEC.md, ARCHITECTURE.md, DATABASE_SCHEMA.md, API_SPEC.md,
AI_GUIDELINES.md, RISK_ENGINE_SPEC.md. Current status: CLAUDE_CONTEXT.md and DEVELOPMENT_PLAN.md.

ARCHITECTURE RULES
- Frontend and UI are built LAST (Phases 13+). Do not create frontend code before the Backend Freeze.
- backend/app/engines/* are PURE: no FastAPI, no SQLAlchemy, no ai/, no datetime.now().
  Pass `as_of: date` explicitly. Inputs and outputs are dataclasses.
- Routers are thin: validate, authorize (api/deps.py), call one service, return a schema.
- Authorization lives only in api/deps.py. Never return ORM objects; use response schemas.
- Risk, trends and what-if NEVER call the AI. The app must work with the AI disabled.
- Only services/ai_service.py (via ai/) talks to the AI provider. The API key exists only in backend env.
- AI never computes numbers or writes academic facts. AI output is validated; failures use the fallback.
- The frontend never computes percentages, risk or trends.
- Do not add a dependency, framework, table or endpoint that is not in the docs without recording
  it in ARCHITECTURE.md > Decision Log with a reason.

WORKING RULES
1. Inspect the repository and read the named docs BEFORE changing anything.
2. Make the smallest change that meets the task. No unrelated refactoring or file edits.
3. Never rewrite working code without a stated reason. Never delete functionality silently.
4. Write tests for business logic and edge cases. Never call the real AI API in tests (use the fake client).
5. Run the tests and linter. Fix failures. NEVER claim a test passed unless you ran it and saw it pass.
   If something cannot be run, say so explicitly.
6. Never hardcode or print secrets. .env is gitignored; .env.example has blanks.
7. Update docs per this table:
   DB change -> DATABASE_SCHEMA.md | API change -> API_SPEC.md | structure/dependency/decision -> ARCHITECTURE.md
   AI behaviour -> AI_GUIDELINES.md | risk formula -> RISK_ENGINE_SPEC.md (+ bump config_version)
   task done -> tick DEVELOPMENT_PLAN.md | phase done -> update CLAUDE_CONTEXT.md
8. If the spec is ambiguous in a way that affects architecture, STOP and ask. Otherwise choose the
   simplest option and record it.

FINAL REPORT FORMAT (end every task with this)
- Changed files: (list)
- Tests run: (exact command + result summary)
- Docs updated: (list or "none needed")
- Deviations / open questions: (list or "none")
```

---

## 2. Prompt template

```text
PROMPT ID:
Phase:
Task:
Objective:

Read first:
- (only the docs this task needs)

Inspect:
- (existing files/folders to look at first)

Requirements:
- (exact, numbered)

Constraints:
- (what must not change)

Tests:
- (what to write and run)

Documentation:
- (docs to update)

Definition of Done:
- (checkable items)

Follow .cursor/rules/project.mdc and end with the Final Report.
```

---

## 3. Prompts: Phase 0

### PROMPT 0.1

```text
PROMPT ID: 0.1
Phase: 0: Planning & Documentation
Task: Repository skeleton and agent rules
Objective: Create the empty project structure, ignore rules, env template and agent rules so later work has a stable base.

Read first:
- MASTER_DESIGN.md §2.3 (folder structure), §5.6 and §8 (secrets)
- DEVELOPMENT_PLAN.md (Phase 0)

Inspect:
- Current directory contents (it may only hold the SRS and the three plan files).

Requirements:
1. Create the folder structure from MASTER_DESIGN.md §2.3: docs/archive/, backend/ (empty, with .gitkeep), frontend/ (empty, .gitkeep). Do NOT create backend or frontend code.
2. Move SRS input files into docs/archive/ (keep a copy of the SRS as SRS.md in the root).
3. Create .gitignore for Python (venv, __pycache__, .pytest_cache, .ruff_cache, *.db, *.sqlite3), Node (node_modules, dist), env files (.env, .env.*, but NOT .env.example), IDE files, OS files.
4. Create .env.example with blank or safe placeholder values for: APP_ENV=dev, DATABASE_URL=sqlite:///./advisor.db, JWT_SECRET_KEY=change-me, JWT_EXPIRE_MINUTES=60, CORS_ORIGINS=http://localhost:5173, OPENAI_API_KEY=, OPENAI_MODEL=, AI_TIMEOUT_SECONDS=20, AI_PLAN_TIMEOUT_SECONDS=40, AI_DAILY_ANALYSIS_LIMIT=10, AI_DAILY_CHAT_LIMIT=30, AI_DAILY_PLAN_LIMIT=5.
5. Create .cursor/rules/project.mdc from the "Agent protocol" block in CODING_PROMPTS.md §1, exactly as written.
6. Create a short README.md stub (project name, one-paragraph description, "setup instructions coming in Phase 1").
7. git init; make the first commit "phase-0: repo skeleton".

Constraints:
- No application code. No dependencies installed.

Tests:
- None. Verify manually: `git status` clean, `.env` is ignored (create an empty .env, confirm it is ignored, then delete it).

Documentation:
- None beyond the files above.

Definition of Done:
- [ ] Folders, .gitignore, .env.example, project.mdc, README stub exist
- [ ] .env is ignored, .env.example is tracked
- [ ] First commit exists

Follow .cursor/rules/project.mdc and end with the Final Report.
```

### PROMPT 0.2

```text
PROMPT ID: 0.2
Phase: 0: Planning & Documentation
Task: Split the master design into the repo documentation set
Objective: Produce the documentation files the whole project will be built against.

Read first:
- docs/archive/MASTER_DESIGN.md (all)
- SRS.md (§16 and §17 for document purposes)

Inspect:
- Repo root (confirm 0.1 is done).

Requirements:
1. Create these files by COPYING the relevant sections (do not paraphrase or invent):
   - PROJECT_SPEC.md: concise (max ~1.5 pages): what the project is, main features, constraints, tech stack, the "Python computes, AI explains" principle.
   - ARCHITECTURE.md: MASTER_DESIGN §2 plus a "Decision Log" section seeded with decisions D1–D13 (date, decision, reason).
   - DATABASE_SCHEMA.md: §3.
   - API_SPEC.md: §4 (conventions, endpoint tables, key contracts). Mark every endpoint with its planned phase.
   - AI_GUIDELINES.md: §5 plus the privacy and failure rules.
   - RISK_ENGINE_SPEC.md: §6 and §7 (all formulas, thresholds, test cases R1–R13, W1).
   - UI_GUIDELINES.md: stub stating "Deferred to Phase 17. Do not design UI earlier."
2. Place DEVELOPMENT_PLAN.md and CLAUDE_CONTEXT.md in the repo root as provided.
3. Move MASTER_DESIGN.md to docs/archive/ after splitting (if not already there).
4. Add a "Documents" table to README.md listing each file and its purpose.

Constraints:
- Do not change any decision, number or name while copying.
- No code.

Tests:
- None.

Documentation:
- README.md documents table only.

Definition of Done:
- [ ] All listed docs exist and match the master design
- [ ] Decision Log contains D1–D13
- [ ] README lists the documents
- [ ] Commit "phase-0: documentation set"

Follow .cursor/rules/project.mdc and end with the Final Report.
```

*Task 0.3 (consistency review) is a prompt to a planner/reviewer: "Read all root docs. List any endpoint, table, enum or number that is inconsistent between documents. Do not fix; report." Run it once, then fix findings with small edits.*

---

## 4. Prompts: Phase 1

### PROMPT 1.1

```text
PROMPT ID: 1.1
Phase: 1: Backend Setup
Task: FastAPI scaffold with health endpoint and settings
Objective: A runnable backend with configuration loaded from environment.

Read first:
- PROJECT_SPEC.md, ARCHITECTURE.md (folder structure, layering)
- API_SPEC.md (conventions only)

Inspect:
- backend/ (should be empty), .env.example

Requirements:
1. Python 3.11+ virtual environment in backend/.venv (not committed).
2. backend/requirements.txt (fastapi, uvicorn[standard], pydantic-settings, python-multipart) and requirements-dev.txt (pytest, pytest-cov, httpx, ruff). Install the current stable versions and pin them.
3. Create backend/app/ with: main.py (app factory `create_app()`), core/config.py (pydantic-settings `Settings` reading .env: every variable in .env.example), api/__init__.py, api/routers/health.py.
4. Mount routers under `/api/v1`. Implement `GET /api/v1/health` returning {"status":"ok"} (public).
5. Add a settings guard: if APP_ENV != "dev" and JWT_SECRET_KEY == "change-me", raise at startup.
6. Empty package folders (with __init__.py) for the structure in ARCHITECTURE.md: core, db, models, schemas, services, engines, ai. Do not add code to them yet.
7. Update README.md with venv, install, run (`uvicorn app.main:app --reload`) instructions.

Constraints:
- Do not add SQLAlchemy, JWT, pandas, numpy or openai yet.
- No frontend work.

Tests:
- None yet (added in 1.3). Manually run the server and open /docs.

Documentation:
- README.md (backend run steps). Tick 1.1 in DEVELOPMENT_PLAN.md.

Definition of Done:
- [ ] `uvicorn app.main:app` starts and /api/v1/health returns {"status":"ok"}
- [ ] /docs loads
- [ ] Settings load from .env; guard verified manually
- [ ] requirements files exist with pinned versions

Follow .cursor/rules/project.mdc and end with the Final Report.
```

### PROMPT 1.2

```text
PROMPT ID: 1.2
Phase: 1: Backend Setup
Task: Error format, logging, CORS
Objective: Every error uses one JSON shape; requests are traceable; the future frontend origin is allowed.

Read first:
- API_SPEC.md (Conventions > Error format and codes)
- ARCHITECTURE.md (layering)

Inspect:
- backend/app/main.py, core/config.py

Requirements:
1. core/errors.py: an `AppError(code, message, status_code, details=None)` base class and subclasses NotFound, Forbidden, Unauthenticated, Conflict, RateLimited.
2. Exception handlers so ALL errors return {"error":{"code","message","details"}}, including FastAPI's 422 validation errors (code VALIDATION_ERROR, details = list of field errors), unknown routes (NOT_FOUND) and unhandled exceptions (INTERNAL_ERROR, no stack trace in the response).
3. core/logging.py: structured logging setup and a middleware that assigns a request id (X-Request-ID response header) and logs method, path, status, duration. Never log request bodies or Authorization headers.
4. CORS middleware using CORS_ORIGINS (comma-separated) from settings; allow credentials false, methods and headers as needed.

Constraints:
- Do not change the health endpoint contract.
- Do not add authentication.

Tests:
- Added in 1.3; for now confirm manually that a bad request returns the standard 422 shape.

Documentation:
- ARCHITECTURE.md: note the error and logging modules. Tick 1.2.

Definition of Done:
- [ ] 404, 422 and a forced 500 all return the standard shape
- [ ] X-Request-ID header present
- [ ] CORS allows only configured origins

Follow .cursor/rules/project.mdc and end with the Final Report.
```

*Task 1.3 (pytest config, conftest, tests for health/error format/CORS, ruff config) and 1.4 (README) are generated next, once 1.1 and 1.2 are verified.*

---

## 5. Prompts: Phase 2 (first two)

### PROMPT 2.1

```text
PROMPT ID: 2.1
Phase: 2: Database & Seed Data
Task: SQLAlchemy foundation and identity models
Objective: Database plumbing, SQLite foreign-key enforcement and the User/Student/Teacher models.

Read first:
- DATABASE_SCHEMA.md (users, students, teachers, integrity rules)
- ARCHITECTURE.md (layering, Decision Log D7, D10)

Inspect:
- backend/app/core/config.py, backend/app/db/, backend/app/models/ (empty), tests/

Requirements:
1. Add sqlalchemy (2.x) and pwdlib[argon2] (or bcrypt; record the choice in the Decision Log) to requirements.txt.
2. db/base.py (DeclarativeBase), db/session.py (engine from DATABASE_URL, SessionLocal, `get_db` dependency). For SQLite, register a connect-event listener executing `PRAGMA foreign_keys=ON` on EVERY connection.
3. models/enums.py: UserRole (STUDENT, TEACHER) and other enums listed in API_SPEC.md conventions that are needed by later models (define now; use later).
4. models/user.py, student.py, teacher.py exactly per DATABASE_SCHEMA.md (types, uniqueness, CHECK on semester 1..8, lowercase email normalization at the model or validation layer).
5. core/security.py: `hash_password(plain)` and `verify_password(plain, hashed)` only (JWT comes in Phase 3).
6. A helper `create_all()` in db/base.py or db/init.py. No seed data yet.

Constraints:
- No Alembic.
- Do not create other models yet.
- Do not add routes.

Tests (tests/unit/test_db_identity.py, using an in-memory SQLite engine fixture in conftest.py with the FK pragma):
- FK enforcement proven: inserting a Student with a non-existent user_id raises IntegrityError.
- Unique email and unique student_code enforced.
- Semester CHECK rejects 0 and 9.
- One user cannot have two student profiles (unique user_id).
- hash_password never returns the plain text; verify_password true/false cases.

Documentation:
- DATABASE_SCHEMA.md if any column differs from the doc; ARCHITECTURE.md Decision Log (hashing library). Tick 2.1.

Definition of Done:
- [ ] Models create cleanly via create_all
- [ ] All new tests pass (paste command + result)
- [ ] `ruff check` clean

Follow .cursor/rules/project.mdc and end with the Final Report.
```

### PROMPT 2.2

```text
PROMPT ID: 2.2
Phase: 2: Database & Seed Data
Task: Academic models
Objective: Subjects, enrollments, teaching assignments, attendance, assessments, semester results and study habits with strict constraints.

Read first:
- DATABASE_SCHEMA.md (all tables listed below, indexes, integrity rules)
- RISK_ENGINE_SPEC.md §Inputs (to confirm fields the engine needs)

Inspect:
- backend/app/models/*, db/*, tests/conftest.py

Requirements:
1. Create models per DATABASE_SCHEMA.md: Subject, Enrollment, TeachingAssignment (section NOT NULL default 'ALL'), AttendanceRecord, Assessment, SemesterResult, StudyHabit. Include all UNIQUE constraints, CHECK constraints and the indexes listed for these tables.
2. Assessment CHECK: status <> 'GRADED' OR obtained_marks IS NOT NULL; also 0 <= obtained_marks <= max_marks and max_marks > 0.
3. AttendanceRecord CHECK: classes_held >= 0 and 0 <= classes_attended <= classes_held.
4. Relationships with back_populates; cascade delete Enrollment -> attendance_records and assessments; Subject delete restricted while enrollments exist.
5. Register all models so create_all builds them.

Constraints:
- Do not add a stored attendance-percentage column.
- Do not create RiskAssessment or AI tables yet.
- Do not modify identity models except to add relationships.

Tests (tests/unit/test_db_academic.py):
- Each CHECK constraint: one violating case (attended > held, GRADED with NULL marks, marks above max, max_marks 0).
- Duplicate (student_id, subject_id) enrollment rejected; duplicate (enrollment_id, record_date) rejected.
- Duplicate teaching assignment with the same section rejected.
- Deleting an enrollment removes its attendance and assessments; deleting a subject with enrollments fails.
- Zero-classes attendance row (held=0, attended=0) is allowed.

Documentation:
- DATABASE_SCHEMA.md (only if implementation differs). Tick 2.2.

Definition of Done:
- [ ] All constraints demonstrably enforced by tests
- [ ] Previous tests still pass
- [ ] ruff clean

Follow .cursor/rules/project.mdc and end with the Final Report.
```

---

## 6. Prompt backlog: how the rest is generated

For every remaining task, the planner produces a prompt from the template using:
- **Read first:** only the doc sections for that task (e.g. Task 5.3 reads `RISK_ENGINE_SPEC.md` §Normalization).
- **Inspect:** the files created by earlier tasks.
- **Tests:** the test list already written in that phase's block in `DEVELOPMENT_PLAN.md`.
- **Size rule:** one coherent task per prompt. If a prompt needs more than about 8 requirements, split it.

**Suggested cadence:** ask for the prompts of one phase at a time (e.g. "Generate the prompts for Phase 3 using CLAUDE_CONTEXT.md"), run them in order, verify, then request the next phase.

---

## 7. Planning-session opening message (paste at the start of a new Claude chat)

```text
You are the lead architect and prompt planner for the Student Academic Advisor project.
Frontend/UI is built last (Phases 13+). Below is CLAUDE_CONTEXT.md. Do not ask me to resend the SRS;
rely on this context and the documents named in it.

[paste CLAUDE_CONTEXT.md]

Task for this session: <e.g. "Generate the coding prompts for Phase 3" / "Review the risk engine diff" /
"I hit this failing test: ...">

Rules: keep prompts small (one task each); use the prompt template; reference docs instead of repeating them;
if you must change a decision, say which document must be updated.
```
