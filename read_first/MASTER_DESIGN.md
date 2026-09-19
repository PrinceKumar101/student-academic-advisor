# STUDENT ACADEMIC ADVISOR: MASTER DESIGN

**Covers planning Outputs 1–5** (review, architecture, database, API, AI) plus the risk-engine design, analytics design, security review, seed-data strategy and scope control.
**Companion files:** `DEVELOPMENT_PLAN.md` (phases, tasks, verification), `CODING_PROMPTS.md` (agent prompts), `CLAUDE_CONTEXT.md` (state).
**Status:** Proposed. Awaiting approval. Phase 0 splits this file into the repo docs (`ARCHITECTURE.md`, `DATABASE_SCHEMA.md`, `API_SPEC.md`, `AI_GUIDELINES.md`, `RISK_ENGINE_SPEC.md`).

The SRS remains the primary source of truth. Where this document deviates from the SRS, the deviation is listed in §1 and in the decisions table below.

---

## 0. HEADLINE DECISIONS (defaults adopted; override any before Phase 0)

| # | Decision | Default adopted |
|---|---|---|
| D1 | **Frontend/UI last** | All frontend and UI work is Phases 13–19. Phases 0–12 are backend-only, verified by pytest, Swagger UI (`/docs`) and a scripted API demo. |
| D2 | Teacher accounts | Public registration creates **STUDENT only**. Teachers are created with `scripts/create_teacher.py`. This prevents role escalation. |
| D3 | Who enters academic data | **Teachers** enter attendance, marks and previous-semester results. Students are read-only, except study habits, study plans, chat and intervention status. |
| D4 | Teacher data visibility | A teacher sees students enrolled in a subject the teacher teaches (`teaching_assignments`). |
| D5 | Attendance storage | Weekly counts (`classes_held`, `classes_attended`). **Percentage is always computed, never stored.** |
| D6 | Risk formula | SRS weights kept (§6), plus normalization rules, an `INSUFFICIENT_DATA` state and two escalation floors. |
| D7 | Migrations | No Alembic. Use `create_all` + `scripts/reset_db.py` + seed. |
| D8 | Study planner | **Hybrid.** Python decides the subject, day and minutes (time budget). The AI writes the topic and activity text for each slot. |
| D9 | AI calls | Analysis and recommendations are **one** call (`analyze_performance`). Three AI capabilities in total: analysis, study plan, chat. |
| D10 | Libraries | PyJWT, `pwdlib[argon2]` (or `bcrypt`), `pydantic-settings`, OAuth2 password-form login so Swagger "Authorize" works. Avoid `python-jose` and `passlib` (maintenance concerns). |
| D11 | Extra docs/tools | New doc `RISK_ENGINE_SPEC.md`. TypeScript API types are generated from the exported OpenAPI (Phase 13). |
| D12 | Deferred | Notifications, email, PDF export, reporting module, Docker, Alembic. CI is optional. |
| D13 | Risk snapshots | Persisted as a side effect of computing risk. No background jobs, no cache invalidation. |

---

## 1. ARCHITECTURAL REVIEW (Output 1)

Format: **Issue / Why it matters / Recommended / Impact / Decision** (a default is given so nothing blocks the start).

### A. Missing decisions

**A1. Who enters academic data?**
Issue: the SRS never says who creates attendance and marks. Why: without it there are no write endpoints, no authorization rules and no seed logic. Recommended: teachers write, students read (D3). Impact: Phase 4 permissions. Decision: default adopted.

**A2. Teacher↔student relationship.**
Issue: "Teacher → only authorized data" but nothing defines "authorized". Why: this is the core authorization test. Recommended: `teaching_assignments(teacher, subject, section)`; visibility is derived from enrollments (D4). Impact: extra table, one shared access dependency. Decision: default adopted.

**A3. Teacher registration and role escalation.**
Issue: FR-01 has public registration with roles. Why: anyone could register as TEACHER. Recommended: D2. Impact: register schema has no `role` field. Decision: default adopted.

**A4. Previous academic performance has no table.**
Issue: the risk engine needs "Previous Performance" and FR-06 stores history, but the entity list has no such table. Recommended: add `semester_results(student, semester, percentage, sgpa?)`. Impact: model in Phase 2. Decision: add.

**A5. "Missing assignments" cannot be represented.**
Issue: the problem statement cites missing assignments, but an assessment only has marks. Recommended: `assessments.status` = GRADED / MISSING / PENDING, with `obtained_marks` nullable. Impact: assignment component uses the submission rate. Decision: add.

**A6. Chat history has no table.**
Recommended: `ai_chat_messages`; only the last 6 messages are sent to the AI. Decision: add.

**A7. Syllabus is not in the system.**
Issue: the study planner would invent topics. Recommended: the student may supply topics per subject; otherwise the AI proposes generic activities and labels topics as suggestions. Decision: default adopted.

**A8. Migration strategy.**
Recommended: D7. `reset_db.py` drops, creates and seeds. Alembic is optional future work. Decision: default adopted.

### B. Contradictions

**B1. Frontend order.** The SRS builds student and teacher UIs in Phases 11–12, before Integration Testing (14) and UI Design (15). The requirement is frontend last. Recommended: D1. Risk: late integration surprises, mitigated in E5. Decision: reordered.

**B2. Attendance %: stored or calculated?** FR-04 lists "attendance percentage" as stored data and also says the backend calculates it. Recommended: compute only (D5). Storing it invites inconsistency. Decision: computed.

**B3. Assignment completion counted twice.** FR-07 (study habits) and FR-08 (assignments 15%) both use it. Recommended: remove it from study habits. Habits = study hours + self-confidence only. Decision: adopted.

**B4. Risk-level ranges leave gaps.** `0–30 / 31–60 / 61–100` has no home for 30.5. Recommended: round the score to 1 decimal, then use inclusive upper bounds (`<=30` LOW, `<=60` MEDIUM, else HIGH). Decision: adopted.

**B5. Testing is "throughout" but Phase 14 is "Integration & Testing".** Recommended: every phase has a gate (tests + docs + context). The late phases are full-flow tests only. Decision: adopted.

**B6. Two prompt formats.** SRS §29 and the instructions §12 differ. Recommended: one template (see `CODING_PROMPTS.md`). The shared agent rules live in `.cursor/rules/project.mdc`, not in every prompt. Decision: adopted.

**B7. Fifteen modules but twelve API groups.** Reporting and Notifications have no endpoints. Recommended: defer both (D12). Early warnings are computed live. Decision: adopted.

**B8. AI functions overlap.** `analyze_performance` and `generate_recommendations` produce nearly the same output. Recommended: merge them (D9). This saves cost and gives coherent advice. Decision: adopted.

### C. Over-engineering

**C1. Pandas in the risk engine.** The engine is simple arithmetic. Recommended: pure Python (dataclasses in, dataclasses out, no DB). Use Pandas only for analytics aggregation, seed generation and CSV import.
**C2. Notifications, email alerts, PDF export, reporting.** Low demo value, high cost. Defer.
**C3. Chat memory and summarization.** Use a fixed window of 6 messages. Nothing more.
**C4. Refresh tokens and token blacklist.** Use a single short-lived access token (60 min). Logout is client-side plus a 204 response. Document this limitation.
**C5. Repository pattern, Docker, Kubernetes.** Services query SQLAlchemy directly. Docker and CI are optional.

### D. Under-specified areas (now specified)

| Area | Where defined |
|---|---|
| Normalization, missing data, weights, boundaries | §6 |
| Trend thresholds, sudden-change rule | §7.1 |
| Early-warning windows and thresholds | §7.3 |
| What-if variables | §6.7 |
| Intervention status ownership and before/after semantics | §4.3 and §7.5 |
| Class analytics definitions | §7.4 |
| AI failure behaviour | §5.5 |

### E. Technical risks

**E1. SQLite foreign keys are OFF by default.** Mitigation: `PRAGMA foreign_keys=ON` on every connection, with a test that proves enforcement.
**E2. The LLM invents numbers or syllabus.** Mitigation: AI receives calculated facts only; strict Pydantic output schemas; the plan's slots are pre-decided by Python; a "percent-grounding" check rejects unknown percentages; the UI separates *Calculated facts* from *AI advice*.
**E3. AI cost, latency and rate limits.** Mitigation: caching by input hash, daily per-user limits counted from DB rows, hard timeouts, max 1 retry, token caps.
**E4. N+1 queries on teacher lists.** Mitigation: one bulk loader (`load_academic_data(student_ids, as_of)`). A test with about 200 seeded students checks speed.
**E5. Late frontend integration.** Mitigation: freeze and export `openapi.json` at Phase 12, run a full-story API test (mirrors the demo), and generate TS types from the OpenAPI file.
**E6. Heuristic risk may mislead.** The weights are expert-set, not learned. Mitigation: `INSUFFICIENT_DATA`, low-sample flags, a completeness score, versioned config stored on every snapshot, wording "risk indicator, not a prediction", and honest viva framing.
**E7. Time-dependent logic breaks tests.** Mitigation: every engine takes an explicit `as_of: date`. Nothing calls `date.today()` inside engines.
**E8. Library pitfalls (JWT, hashing).** Mitigation: D10.
**E9. AI SDK/API surface changes.** Mitigation: a thin wrapper `ai/client.py`, model name from env, and our own Pydantic validation even if the provider offers structured outputs.
**E10. IDOR (student A reads student B).** Mitigation: one dependency `authorize_student_access()` used by every student-scoped route, plus a parametrized authorization-matrix test.

### F. Scope risks

**F1. Twenty phases is a lot for one semester.** Every task is tagged **[M]ust / [S]hould / [C]ould**. The Minimum Demonstrable Path is in §10.
**F2. UI phase creep.** UI is last, but time-boxed. A "functional freeze" gate precedes design.
**F3. Chasing perfect AI output.** Accept fallbacks. A deterministic fallback is a feature, not a failure.

---

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
│   │   ├── core/      config.py security.py errors.py logging.py
│   │   ├── db/        base.py session.py
│   │   ├── models/    one file per entity + enums.py
│   │   ├── schemas/   Pydantic request/response models
│   │   ├── api/       deps.py  routers/{auth,students,subjects,attendance,
│   │   │              assessments,risk,trends,analytics,ai,study_plans,
│   │   │              interventions,teacher}.py
│   │   ├── services/  academic_data_loader.py risk_service.py trend_service.py
│   │   │              analytics_service.py whatif_service.py ai_service.py
│   │   │              study_plan_service.py intervention_service.py teacher_service.py
│   │   ├── engines/   risk_config.py metrics.py risk_engine.py trend_engine.py
│   │   │              warnings.py analytics.py whatif.py time_budget.py
│   │   └── ai/        client.py context_builder.py prompts/ schemas.py
│   │                  validators.py fallback.py
│   ├── scripts/       reset_db.py seed_demo.py create_teacher.py
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
`GET /students/me/overview` → `authorize_student_access` → `load_academic_data` (bulk) → risk engine + trend engine + subject analysis + warnings → JSON (persist snapshot if changed) → frontend renders.

**AI analysis**
`POST /ai/analysis` → authorize → compute facts (engines) → `context_builder` → hash → cache hit? return. Otherwise check daily limit → AI client (timeout, ≤1 retry) → validate schema and grounding → store → return `{facts, advice, source}`. On any AI failure, use the deterministic fallback with `source: FALLBACK`.

**What-if**
`POST /risk/{id}/what-if {overrides}` → load real inputs → `dataclasses.replace(inputs, **overrides)` → engine twice (current, simulated) → diff. **Zero DB writes.**

**Auth**
`POST /auth/login` (form) → verify hash → JWT `{sub, role, exp, iat}` → client sends `Authorization: Bearer` → `get_current_user` → `require_role` / `authorize_student_access`.

---

## 3. DATABASE PLAN (Output 3)

SQLite, SQLAlchemy 2.x models. Foreign keys enforced via pragma. IDs are integers. All dates are ISO.

### 3.1 Relationships

```text
users 1─1 students          users 1─1 teachers
students 1─* enrollments *─1 subjects
teachers 1─* teaching_assignments *─1 subjects
enrollments 1─* attendance_records
enrollments 1─* assessments
students 1─* semester_results      students 1─1 study_habits
students 1─* risk_assessments      students 1─* ai_advice
students 1─* study_plans 1─* study_plan_items *─1 subjects
students 1─* ai_chat_messages
students 1─* interventions *─1 teachers ; interventions *─0..1 subjects
```

16 tables. Changes vs SRS: **added** `teaching_assignments`, `semester_results`, `ai_chat_messages`. No SRS table was dropped.

### 3.2 Tables

```text
users(id PK, email UNIQUE lowercase, password_hash, role[STUDENT|TEACHER],
      is_active default true, created_at)
students(id PK, user_id FK UNIQUE, student_code UNIQUE, full_name, department,
         semester 1..8, section, created_at)
teachers(id PK, user_id FK UNIQUE, full_name, department)
subjects(id PK, code UNIQUE, name, semester 1..8)
enrollments(id PK, student_id FK, subject_id FK, UNIQUE(student_id, subject_id))
teaching_assignments(id PK, teacher_id FK, subject_id FK, section NOT NULL default 'ALL',
                     UNIQUE(teacher_id, subject_id, section))
   -- 'ALL' instead of NULL because SQLite treats NULLs as distinct in UNIQUE.
attendance_records(id PK, enrollment_id FK, record_date DATE,
                   classes_held INT>=0, classes_attended INT 0..classes_held,
                   UNIQUE(enrollment_id, record_date))
assessments(id PK, enrollment_id FK, type[INTERNAL|QUIZ|ASSIGNMENT|EXAM], name,
            max_marks >0, obtained_marks NULL 0..max_marks,
            status[GRADED|MISSING|PENDING], assessment_date DATE (due date for assignments),
            created_at,
            CHECK(status<>'GRADED' OR obtained_marks IS NOT NULL))
semester_results(id PK, student_id FK, semester 1..8, percentage 0..100, sgpa NULL,
                 UNIQUE(student_id, semester))
study_habits(id PK, student_id FK UNIQUE, study_hours_per_day 0..24,
             self_confidence 1..5, available_hours_per_day 0..24, updated_at)
risk_assessments(id PK, student_id FK, computed_at DATETIME, as_of DATE,
                 score REAL NULL, level[LOW|MEDIUM|HIGH|INSUFFICIENT_DATA],
                 escalated BOOL, escalation_reason NULL, data_completeness REAL,
                 config_version, components JSON, flags JSON)
ai_advice(id PK, student_id FK, kind[ANALYSIS], input_hash, payload JSON,
          source[AI|FALLBACK], model NULL, prompt_version, created_by_user_id FK, created_at)
study_plans(id PK, student_id FK, exam_date, available_hours_per_day, inputs JSON,
            source[AI|FALLBACK], model NULL, prompt_version, created_by_user_id FK, created_at)
study_plan_items(id PK, plan_id FK ON DELETE CASCADE, plan_date, subject_id FK,
                 topic, activity, duration_minutes 1..480, priority[LOW|MEDIUM|HIGH],
                 is_completed default false, completed_at NULL)
ai_chat_messages(id PK, student_id FK, role[USER|ASSISTANT], content,
                 source[AI|FALLBACK] NULL, created_at)
interventions(id PK, student_id FK, teacher_id FK, subject_id FK NULL, title, description,
              priority, status[PENDING|IN_PROGRESS|COMPLETED], due_date,
              baseline_score NULL, baseline_level, baseline_at,
              outcome_score NULL, outcome_level NULL, outcome_at NULL,
              completion_note NULL, created_at, updated_at)
```

### 3.3 Indexes

`enrollments(student_id)`, `enrollments(subject_id)`, `attendance_records(enrollment_id, record_date)`, `assessments(enrollment_id, type, assessment_date)`, `risk_assessments(student_id, computed_at)`, `ai_advice(student_id, kind, input_hash)`, `ai_chat_messages(student_id, created_at)`, `interventions(student_id, status)`, `interventions(teacher_id, status)`, `study_plan_items(plan_id, plan_date)`.

### 3.4 Delete and integrity rules

- No delete endpoints for students or teachers (deactivate with `users.is_active`).
- Subject delete: RESTRICT while enrollments exist.
- Enrollment delete cascades to its attendance and assessments. Study plan delete cascades to items.
- Validation lives in **both** Pydantic (friendly errors) and DB CHECK constraints (safety net).

---

## 4. API PLAN (Output 4)

Base path `/api/v1`. JSON. Interactive docs at `/docs`.

### 4.1 Conventions

- **Auth:** `Authorization: Bearer <JWT>`. Claims: `sub` (user id), `role`, `iat`, `exp`. Lifetime from config (default 60 min).
- **`{student_id}`** accepts an integer or the literal `me` (resolves to the caller's own student profile; students only).
- **Access rule** (`authorize_student_access`): STUDENT → own id only; TEACHER → students visible per D4; otherwise **403**. A missing resource for an authorized caller is **404**.
- **Pagination:** `?page=1&page_size=20` → `{items, total, page, page_size}`.
- **Error format (all errors, including validation):**

```json
{ "error": { "code": "FORBIDDEN", "message": "Human readable", "details": null } }
```
Codes: `VALIDATION_ERROR` 422, `UNAUTHENTICATED` 401, `FORBIDDEN` 403, `NOT_FOUND` 404, `CONFLICT` 409, `RATE_LIMITED` 429, `INTERNAL_ERROR` 500.
An AI outage is **not** an error: it returns 200 with `source: "FALLBACK"`.

- **Enums:** `RiskLevel` LOW/MEDIUM/HIGH/INSUFFICIENT_DATA · `AssessmentType` INTERNAL/QUIZ/ASSIGNMENT/EXAM · `AssessmentStatus` GRADED/MISSING/PENDING · `Priority` LOW/MEDIUM/HIGH · `InterventionStatus` PENDING/IN_PROGRESS/COMPLETED · `TrendLabel` IMPROVING/STABLE/DECLINING/INSUFFICIENT_DATA · `Source` AI/FALLBACK.
- Percentages are floats 0–100 rounded to 1 decimal in responses.

### 4.2 Endpoint list

Legend: **S** = student (own data), **T** = teacher (visible students / taught subjects), **A** = any authenticated, **P** = public. `[S]/[C]` marks Should/Could priority; unmarked = Must.

**System / Auth**

| Method | Path | Who | Purpose |
|---|---|---|---|
| GET | `/health` | P | Liveness |
| POST | `/auth/register` | P | Create STUDENT account + profile |
| POST | `/auth/login` | P | OAuth2 password form → token |
| POST | `/auth/logout` | A | 204; client discards token |
| GET | `/auth/me` | A | Current user + profile id |

**Students**

| Method | Path | Who | Purpose |
|---|---|---|---|
| GET | `/students/{id}` | S,T | Profile |
| GET | `/students/{id}/overview` | S,T | Composite dashboard payload (Phase 12) |
| GET | `/students/{id}/study-habits` | S,T | Read habits |
| PUT | `/students/{id}/study-habits` | S | Update own habits |
| GET | `/students/{id}/semester-results` | S,T | Previous results |
| PUT | `/students/{id}/semester-results/{semester}` | T | Upsert a previous result |

**Subjects**

| Method | Path | Who | Purpose |
|---|---|---|---|
| GET | `/subjects?mine=true` | A | List subjects |
| POST | `/subjects` | T | Create (creator gets a teaching assignment) |
| PATCH | `/subjects/{id}` | T | Edit taught subject |
| POST | `/subjects/{id}/enrollments` | T | Enroll `{student_id}` |
| DELETE | `/subjects/{id}/enrollments/{student_id}` | T | Unenroll |

**Attendance and Assessments** (writes are teacher-only, for taught subjects and sections)

| Method | Path | Who | Purpose |
|---|---|---|---|
| GET | `/attendance?student_id=&subject_id=` | S,T | Per-subject summary (computed %) + records |
| POST | `/attendance` | T | Add weekly record |
| PUT / DELETE | `/attendance/{record_id}` | T | Edit / remove |
| GET | `/assessments?student_id=&subject_id=&type=` | S,T | List |
| POST | `/assessments` | T | Create |
| PUT / DELETE | `/assessments/{id}` | T | Edit / remove |

**Risk, Trends, Analytics**

| Method | Path | Who | Purpose |
|---|---|---|---|
| GET | `/risk/{student_id}` | S,T | Current risk with components |
| GET | `/risk/{student_id}/history` | S,T | Snapshots over time |
| POST | `/risk/{student_id}/what-if` | S,T | Simulate; no DB writes |
| GET | `/trends/{student_id}` | S,T | Assessment, attendance and risk trends |
| GET | `/trends/{student_id}/warnings` | S,T | Early warnings |
| GET | `/analytics/students/{student_id}/subjects` | S,T | Subject analysis |
| GET | `/analytics/students/{student_id}/comparison` [S] | S,T | Student vs class average (only when group ≥ 5) |

**AI**

| Method | Path | Who | Purpose |
|---|---|---|---|
| POST | `/ai/analysis` | S,T | Facts + AI advice (cached, limited) |
| POST | `/ai/chat` | S | Ask the academic assistant |
| GET | `/ai/chat/history` | S | Last messages |
| DELETE | `/ai/chat/history` | S | Clear |
| GET | `/ai/usage` | A | Remaining daily allowances |
| POST | `/ai/intervention-suggestions` [C] | T | Suggested interventions for a student |

**Study plans**

| Method | Path | Who | Purpose |
|---|---|---|---|
| POST | `/study-plans` | S | Generate and store a plan |
| GET | `/study-plans` | S | List own plans |
| GET | `/study-plans/{plan_id}` | S | Plan with items |
| PATCH | `/study-plans/{plan_id}/items/{item_id}` | S | Mark item done/undone |
| DELETE | `/study-plans/{plan_id}` | S | Delete |

**Interventions and Teacher**

| Method | Path | Who | Purpose |
|---|---|---|---|
| POST | `/interventions` | T | Create; stores baseline risk |
| GET | `/interventions?student_id=&status=` | S (own), T | List |
| GET | `/interventions/{id}` | S,T | Detail |
| PATCH | `/interventions/{id}` | T: any field. S: `status` + `completion_note` only | Update |
| GET | `/interventions/{id}/progress` | S,T | Before/after |
| GET | `/teacher/dashboard` | T | Class summary |
| GET | `/teacher/students?risk_level=&department=&semester=&section=&subject_id=&search=` | T | Filtered, paginated list with risk |
| GET | `/teacher/subjects/{subject_id}/analytics` | T | Subject-level class analytics |

**Intervention rules.** Status moves PENDING → IN_PROGRESS → COMPLETED. A teacher may also reopen. When status becomes COMPLETED, the backend stores the outcome snapshot (`outcome_score`, `outcome_level`, `outcome_at`).

### 4.3 Key contracts (others are derived from schemas in `API_SPEC.md`)

**POST `/auth/register`**: `{email, password(min 8), full_name, student_code, department, semester, section}` → 201 `{user_id, student_id}`. No `role` field exists. Duplicate email or code → 409.

**POST `/auth/login`** (`application/x-www-form-urlencoded`: `username`=email, `password`) →
`{access_token, token_type:"bearer", expires_in, user:{id, role, student_id|teacher_id, full_name}}`. Any failure gives the same 401 message (no user enumeration).

**GET `/risk/{student_id}`**
```json
{
  "student_id": 12, "as_of": "2026-09-19", "score": 67.1, "level": "HIGH",
  "escalated": false, "escalation_reason": null,
  "data_completeness": 1.0, "config_version": "1.0",
  "components": [
    {"key":"attendance","label":"Attendance","available":true,
     "raw_value":64.0,"unit":"percent","risk":65.0,"weight":0.25,
     "effective_weight":0.25,"contribution":16.25,"level":"HIGH",
     "note":"Attendance is 64.0%, below the 75% cutoff."}
  ],
  "top_factors": ["internal","attendance","quizzes"],
  "flags": ["LOW_SAMPLE:quizzes"]
}
```

**POST `/risk/{student_id}/what-if`**
Request: `{"overrides": {"attendance_percent": 80, "study_hours_per_day": 3}}`. Allowed keys: `attendance_percent`, `internal_percent`, `quiz_percent`, `assignment_percent`, `assignment_submission_rate`, `study_hours_per_day`, `self_confidence`. Unknown keys → 422. Out-of-range → 422.
Response: `{"current":{score,level}, "simulated":{score,level}, "difference":-10.0, "changed_factors":[{"key":"attendance","from_value":64.0,"to_value":80.0,"risk_from":65.0,"risk_to":25.0,"contribution_delta":-10.0}], "persisted": false}`

**POST `/ai/analysis`** (body `{student_id?:"me", refresh?:false}`)
```json
{
  "source": "AI", "generated_at": "...", "cached": false,
  "facts": { "...calculated values, risk, top factors, weak subjects, trend labels..." },
  "advice": { "summary":"...", "main_concerns":[{"factor":"attendance","explanation":"..."}],
              "recommendations":[{"action":"...","reason":"...","priority":"HIGH"}],
              "priority":"HIGH" },
  "fallback_reason": null
}
```
`fallback_reason` when `source=FALLBACK`: `NOT_CONFIGURED | TIMEOUT | PROVIDER_ERROR | INVALID_OUTPUT | UNGROUNDED_OUTPUT`. Daily limit reached → 429 `RATE_LIMITED`.

**POST `/study-plans`**
Request: `{"exam_date":"2026-10-15","available_hours_per_day":3,"subject_ids":[1,2],"topics":{"1":["Trees","Graphs"]}}` (`subject_ids` empty = auto-pick weak subjects; `topics` optional).
Response: `{"id":5,"source":"AI","items":[{"id":1,"plan_date":"...","subject":{"id":1,"code":"CS301"},"topic":"...","activity":"...","duration_minutes":60,"priority":"HIGH","is_completed":false}], "tips":[...]}`.
Validation: exam date in the future and within 60 days; hours 0.5–12.

**GET `/interventions/{id}/progress`**
```json
{ "baseline":{"score":84.0,"level":"HIGH","at":"2026-09-01"},
  "current":{"score":63.0,"level":"HIGH","as_of":"2026-09-19"},
  "change":-21.0, "direction":"IMPROVED", "days_elapsed":18,
  "note":"This shows the observed change in risk since the intervention was created. It does not prove the intervention caused it." }
```
`direction`: IMPROVED / WORSENED / UNCHANGED (`|change| < 2.0` = UNCHANGED, configurable).

---

## 5. AI PLAN (Output 5)

### 5.1 Principle

Python computes every fact. The AI only turns supplied facts into language. No AI capability can change a risk score, a percentage or a database record.

### 5.2 Capabilities

**AI-1 `analyze_performance` (analysis + recommendations, one call)**
- Purpose: explain the student's situation and give prioritized advice.
- Input context (`StudentAcademicContext`): overall attendance %, per-subject %, risk score/level/completeness, top factors with raw values, weak subjects (name + %), trend labels with first/last values, active early warnings, study habits (hours, confidence).
- Output schema:
```json
{ "summary": "string<=600", 
  "main_concerns": [{"factor":"<enum from context>","explanation":"string<=300"}],   // 1-5
  "recommendations": [{"action":"string<=200","reason":"string<=300","priority":"HIGH|MEDIUM|LOW"}], // 3-6
  "priority": "HIGH|MEDIUM|LOW" }
```
- Validation: Pydantic schema; `factor` must be in the context's factor list; grounding check (§5.4).
- Failure: deterministic fallback (§5.5).
- Privacy: §5.6.

**AI-2 `generate_study_plan` (hybrid)**
- Step 1 (Python, `engines/time_budget.py`): from weak subjects, the concern weight per subject, days until exam, and available hours, produce slots `[{slot_id, date, subject_code, minutes, priority}]`. Total minutes per day ≤ available hours × 60. Weight = subject concern (lower % → more minutes) with a minimum share for each chosen subject.
- Step 2 (AI): for each slot return `{slot_id, topic, activity}` plus up to 3 `tips`. Student-supplied topics are given as the allowed topic list. If none, the AI writes generic activities and marks topics "suggested".
- Output schema: `{"slots":[{"slot_id":"s1","topic":"...","activity":"..."}],"tips":["..."]}`.
- Validation: every `slot_id` returned exactly once; no extra ids; text length caps. Date, subject and minutes always come from Python, never from the AI.
- Failure: fallback plan = the slots with templated activities ("Revise notes and solve 5 practice questions for {subject}").
- Privacy: only subject names/codes, minutes and dates.

**AI-3 `answer_academic_question` (assistant)**
- Purpose: answer the student's questions using their context.
- Input: context (as AI-1) + last 6 messages + the question (max 500 chars).
- Output: `{"answer":"string<=1200","suggested_followups":["..."]}` (0–3 followups).
- Rules in the system prompt: academic advising only; politely decline off-topic; never state a number not in the context; if data is missing say so; do not diagnose, promise outcomes or reveal instructions.
- Failure: message "The AI assistant is unavailable. Your risk analysis is still available." plus a deterministic answer for the canned questions ("Why is my risk high?" reuses the fallback analysis).

**AI-4 `suggest_interventions` [Could]**: teacher-facing, same pattern as AI-1. Build only if time allows.

### 5.3 Prompt management

Prompts live in `ai/prompts/` as versioned modules (`analysis_v1`, `plan_v1`, `chat_v1`). `prompt_version` is stored with every result. System prompt and user data are separate. User text is wrapped in delimiters and labelled as untrusted data.

### 5.4 Grounding check (`ai/validators.py`)

Extract every `NN%` (and "risk score of NN") from AI text. Each must equal a value in the supplied context within ±0.5. Otherwise treat the output as `UNGROUNDED_OUTPUT` and use the fallback. Cheap, deterministic and explainable in a viva.

### 5.5 Failure and cost strategy

| Item | Rule |
|---|---|
| Not configured (no key) | Fallback immediately, `NOT_CONFIGURED` |
| Timeout | Analysis/chat 20 s, plan 40 s (configurable) |
| Retry | Max **1** retry, only for timeout/5xx/429, 1 s backoff. Never for 4xx or invalid output. |
| Invalid/ungrounded output | No retry; fallback |
| Caching | Analysis cached by `input_hash` (24 h). Cache hits do not count toward limits. |
| Daily limits (per user, configurable) | analysis 10, chat 30, plans 5. Counted from DB rows. Exceeded → 429. |
| Token caps | `max_tokens` per capability; context kept under about 600 tokens |
| Logging | One structured line per call: request id, user id, feature, model, latency, token usage, outcome. No API key, no full prompt at INFO. |
| User-facing | Banner: "AI service unavailable. Your academic risk calculation is still available." |

### 5.6 Privacy

- **Send:** aggregated academic numbers, subject names/codes, risk data, trend labels, study-hour numbers. Refer to the person as "the student".
- **Never send:** name, email, student code, user ids, passwords, tokens, API keys, other students' data.
- Context is built **server-side** from the authenticated `student_id`. It is never taken from the request body.
- Demo data is synthetic. Document that real student data requires institutional approval.

---

## 6. RISK ENGINE DESIGN

Deterministic. Location: `engines/`. Config: `risk_config.py` (versioned, validated at import). Pure functions on dataclasses. No I/O, no clock.

### 6.1 Inputs (`RiskInputs`, all optional)

| Field | Definition |
|---|---|
| `attendance_percent` | Σ classes_attended ÷ Σ classes_held × 100 across all subjects. `None` if Σ held = 0. |
| `internal_percent` | Σ obtained ÷ Σ max over GRADED INTERNAL + EXAM. `None` if none. |
| `quiz_percent` | Same for GRADED QUIZ. |
| `assignment_percent` | Same for GRADED ASSIGNMENT. |
| `assignment_submission_rate` | GRADED ÷ (GRADED + MISSING) for assignments. PENDING excluded. `None` if denominator is 0. |
| `previous_percentage` | Most recent `semester_results.percentage`. |
| `study_hours_per_day`, `self_confidence` | From `study_habits`. |
| `n_internal`, `n_quiz`, `n_assignment` | Sample sizes (for flags). |

### 6.2 Component normalization (risk 0–100, higher = worse; clamp to [0,100])

```text
attendance_risk  = clamp((90 - A) / (90 - 50) * 100)        # 90%+ -> 0, 50%- -> 100
performance_risk = clamp((75 - P) / (75 - 35) * 100)        # 75%+ -> 0, 35%- -> 100
                   (used for internal, quizzes, previous)
assignment_risk  = 0.5 * (100 - submission_rate)  +  0.5 * performance_risk(assignment_percent)
                   (if one part is missing, use the other at full weight)
study_risk       = mean of available:
                     clamp((2.0 - hours) / 2.0 * 100)          # target 2 h/day
                     (5 - confidence) / 4 * 100                 # confidence 1..5
```

### 6.3 Weights and aggregation

Default weights (sum = 1.00, validated at import): attendance 0.25, internal 0.25, assignments 0.15, quizzes 0.15, previous 0.10, study_habits 0.10.

```text
available = components with data
if sum(weights of available) < 0.40  ->  level INSUFFICIENT_DATA, score None
else effective_weight_i = weight_i / sum(weights of available)
     score = round1( sum(effective_weight_i * risk_i) )
     data_completeness = sum(weights of available)
     contribution_i = effective_weight_i * risk_i
```

### 6.4 Classification and escalation

```text
base_level:  score <= 30 -> LOW ; <= 60 -> MEDIUM ; else HIGH      (on the rounded score)
floors (never lower a level, never raise above MEDIUM):
   attendance_percent < 75          -> at least MEDIUM
   internal_percent   < 40 (pass)   -> at least MEDIUM
final level = max(base_level, floor)
if floor raised the level: escalated = true, escalation_reason = "Attendance below 75% cutoff"
The numeric score is never altered by escalation.
```
Study habits (self-reported) can never trigger a floor.

### 6.5 Risk factors and explanations

Component level uses the same thresholds on the component risk (≤30 LOW, ≤60 MEDIUM, else HIGH). `top_factors` = components with level ≥ MEDIUM, sorted by `contribution` descending, max 3. Each component has a **templated** note that quotes the raw value, e.g. "Attendance is 64.0%, below the 75% cutoff." Notes are deterministic and never AI-generated.

### 6.6 Avoiding misleading conclusions

- `INSUFFICIENT_DATA` rather than a fake score.
- Flags: `LOW_SAMPLE:<component>` (fewer than 2 graded items), `PARTIAL_DATA` (completeness < 1), `STALE_DATA` (newest record older than 30 days before `as_of`).
- Zero classes held gives `None`, not 0% and not a crash.
- The UI must show completeness and the wording "risk indicator, not a prediction of failure".
- `config_version` is saved on every snapshot.
- Honest framing: weights are expert-chosen heuristics, configurable and testable, not learned from data.

### 6.7 What-if

`simulate(inputs, overrides, config)` builds `replace(inputs, **overrides)`, runs `compute_risk` twice and diffs. Allowed override keys are those in §4.3. An override may activate a component whose real value is `None`; the response marks it as `hypothetical`. No DB access.

### 6.8 Required risk-engine test cases (worked expected values)

| ID | Scenario | Expected |
|---|---|---|
| R1 Low | att 92, internal 82, assign sub 100%/85, quiz 80, prev 78, study 3 h/conf 4 | attendance 0; internal 0; assignments 0; quizzes 0; previous 0; study 12.5. **Score 1.3 (1.25 rounded), LOW** |
| R2 Medium | att 75, internal 60, assign 100%/65, quiz 55, prev 65, study 1.5 h/conf 3 | component risks 37.5 / 37.5 / 12.5 / 50 / 25 / 37.5. **Score 34.4, MEDIUM** |
| R3 High | att 64, internal 45, assign 60%/50, quiz 40, prev 55, study 1 h/conf 2 | risks 65 / 75 / 51.25 / 87.5 / 50 / 62.5. **Score 67.1, HIGH** |
| R4 Boundaries | classify 30.0, 30.1, 60.0, 60.1 | LOW, MEDIUM, MEDIUM, HIGH |
| R5 Missing data | only attendance 64 and internal 45 | completeness 0.50; score (0.25×65+0.25×75)/0.5 = **70.0, HIGH**; flag PARTIAL_DATA |
| R6 Insufficient | only study habits | completeness 0.10 < 0.40, **INSUFFICIENT_DATA**, score None |
| R7 Escalation | attendance 60, all else risk 0 | score 18.8 (base LOW), attendance < 75 → **MEDIUM, escalated=true**, score unchanged |
| R8 Zero classes | Σ held = 0 | attendance None (not 0%), no exception |
| R9 Clamp | attendance 100 / 30 | risk 0 / 100 |
| R10 Invalid | attended > held, percent < 0 or > 100 | validation error |
| R11 Weights | weights not summing to 1 | config validation error at import |
| R12 Determinism | same inputs twice; inputs not mutated | identical outputs |
| R13 Monotonic | random seeded inputs: improving any single input never increases score | property holds over ≥ 500 cases |
| W1 What-if | R3 with attendance 64 → 80 | attendance risk 65 → 25; contribution 16.25 → 6.25; **difference −10.0; score 57.1, MEDIUM**; DB unchanged |

---

## 7. TREND, WARNING, SUBJECT AND CLASS ANALYTICS DESIGN

All in `engines/` (pure). Thresholds live in config.

### 7.1 Trend engine

Series = ordered (by date) percentage values. Requires ≥ 3 points, else `INSUFFICIENT_DATA`.
- Slope by least squares over index 0..n−1 (points per assessment).
- `slope ≥ +2.0` IMPROVING · `slope ≤ −2.0` DECLINING · otherwise STABLE.
- **Sudden change:** last value differs from the mean of the previous values by ≥ 15 points → `SUDDEN_DROP` / `SUDDEN_RISE` flag.
- Worked check: 72, 69, 63, 55 → mean 64.75, slope **−5.7**, DECLINING; last vs mean of previous = 55 − 68 = −13, no sudden flag.
- Series produced: overall assessments, per type, per subject, weekly attendance, risk history.

### 7.2 Subject analysis

Subject % = Σ obtained ÷ Σ max over all GRADED assessments in the subject. Band: `< 50` HIGH_CONCERN · `< 65` MEDIUM · else GOOD. Also returns subject attendance % and an alert if below 75%. Subject attendance never changes the overall risk level (it is shown as an alert only).

### 7.3 Early warnings

Compare the recent window with the previous window:

| Rule | WARNING | CRITICAL |
|---|---|---|
| Attendance drop (last 4 weeks vs previous weeks) | ≥ 10 pp | ≥ 20 pp |
| Internal marks drop (latest vs mean of earlier) | ≥ 10 pts | ≥ 20 pts |
| Quiz drop | ≥ 10 pts | ≥ 20 pts |
| Overall attendance crosses below 75% | WARNING | n/a |
| 2 consecutive MISSING assignments | WARNING | 3+ → CRITICAL |
| Risk level higher than previous snapshot | WARNING | LOW→HIGH = CRITICAL |

Example from the SRS: attendance 82 → 67 (15 pp) = WARNING; quiz 76 → 48 (28 pts) = CRITICAL.

### 7.4 Class analytics (teacher)

Counts by risk level; mean attendance (mean of student-level values); mean marks; per-subject mean %; trend-label distribution. Implemented with Pandas over the bulk-loaded data. Student-vs-class comparison is returned only if the comparison group has ≥ 5 students (prevents identifying individuals).

### 7.5 Intervention before/after

Baseline (score, level, timestamp) is **copied** onto the intervention at creation. Outcome is captured when the intervention is completed. `progress` compares the baseline with the current live risk. Wording is observational only (see the contract in §4.3).

---

## 8. SECURITY REVIEW

| Risk | Mitigation (proportional to a college project) |
|---|---|
| Role escalation at signup | No `role` on register; teachers via script (D2) |
| Weak passwords | Min 8 chars; Argon2/bcrypt hash; never log passwords |
| JWT weakness | Secret from env; app refuses to start in non-dev with the default secret; short expiry; verify `exp` and signature; tests for expired and tampered tokens |
| IDOR | Single `authorize_student_access` dependency; parametrized authorization-matrix test (every endpoint × role) |
| Teacher overreach | Writes checked against `teaching_assignments` |
| API key exposure | Backend env only; `.env` gitignored; `.env.example` has blanks; a grep check in Phase 12 |
| SQL injection | SQLAlchemy parameterization only; no string-built SQL |
| Input validation | Pydantic bounds on every field; DB CHECK constraints |
| Prompt injection | AI has no tools and no DB access; user text delimited and labelled untrusted; context built server-side; output schema-validated and grounding-checked. Worst case: odd text shown to the same user. |
| Data leakage to AI | Privacy rules §5.6; a test asserts context contains no PII fields |
| Data leakage in responses | Explicit response schemas (never return ORM objects); `password_hash` never serialized |
| User enumeration | Identical 401 for unknown email and wrong password |
| Brute force | Simple in-memory failed-login throttle [Could] |
| CORS | Restricted to configured origins (`http://localhost:5173`) |
| Swagger in prod | Note: disable `/docs` for a real deployment. Left on for the demo. |

---

## 9. DATA (SEED) STRATEGY

Synthetic only. Deterministic: `random.Random(42)`. Command: `python -m scripts.reset_db && python -m scripts.seed_demo [--as-of YYYY-MM-DD]`.

**Scale:** 40 generated students + 3 edge-case students, 2 teachers, 5 subjects (CS301 Data Structures, CS302 DBMS, CS303 Operating Systems, CS304 Computer Networks, CS305 Software Engineering), Semester 5, sections A/B.

**Per student per subject:** 12 weekly attendance records; INTERNAL ×3, QUIZ ×4, ASSIGNMENT ×3; previous results for semesters 3 and 4; one study-habits row.

| Profile | Count | Marks | Attendance | Assignments submitted | Habits |
|---|---|---|---|---|---|
| High performer | 6 | 82–95 flat | 90–98% | ~98% | 3–5 h, conf 4–5 |
| Average | 12 | 60–72 | 78–88% | ~90% | 2–3 h, conf 3 |
| Low performer | 7 | 35–50 | 60–72% | ~60% | 0.5–1.5 h, conf 1–2 |
| Improving | 5 | 45–55 rising ~+4/assessment | 68% → 85% | rising | improving |
| Declining | 6 | 75–82 falling ~−5/assessment | 90% → 65% | falling | falling |
| Inconsistent | 4 | mean 60, noise sd 15 | random walk | mixed | mixed |

**Story and edge students** (fixed logins, password `Demo@1234`):
- `rahul@demo.edu`: the demo student. DECLINING profile tuned to end at HIGH risk (about 80+), with attendance 82 → 64 and a clear marks decline.
- `newstudent@demo.edu`: no data (tests INSUFFICIENT_DATA).
- `zeroclass@demo.edu`: enrolled, 0 classes held (tests division by zero).
- `missingassign@demo.edu`: many MISSING assignments.
- `teacher1@demo.edu` (CS301, CS302, CS303), `teacher2@demo.edu` (CS304, CS305, CS301 section B).

**Risk history:** because engines take `as_of`, the seed back-fills 4 historical risk snapshots per student by evaluating the engine on data filtered up to earlier dates.
**Names:** from a static list of clearly fictional names. No real people.
**Tests:** assert exact counts, determinism (two runs equal), and that profile students land in the expected risk bands.

---

## 10. SCOPE CONTROL

**Minimum Demonstrable Path (must exist for the demo story):** auth → seed data → risk engine + explanation → trends + subject analysis → what-if → AI analysis (+ fallback) → study plan → teacher dashboard + filtering → intervention + before/after → minimal functional frontend for all of these.

**Cut order if time runs short (first to cut):**
1. CSV import [S], AI intervention suggestions [C], comparison endpoint [S]
2. Chat history persistence (keep chat, drop history endpoints)
3. Extra early-warning rules (keep attendance + marks drop)
4. Advanced charts and micro-animations
5. Playwright E2E (keep the manual checklist)

**Never cut:** deterministic risk engine, authorization tests, AI fallback, before/after tracking.

---

## 11. QUALITY SELF-CHECK

| Question | Answer |
|---|---|
| Architecture simple enough for a college project? | Yes: one backend, SQLite, no services layer beyond FastAPI. |
| Responsibilities separated? | Yes: §2.2 rules and §2.4 matrix. |
| Frontend/backend independent? | Yes: frozen OpenAPI and generated types (Phase 12 to 13). |
| Risk deterministic and isolated? | Yes: pure engine, versioned config, worked test cases. |
| AI prevented from calculating? | Yes: facts in, prose out; plan slots pre-decided; grounding check. |
| AI failures handled? | Yes: §5.5 fallback for all capabilities. |
| Historical data supported? | Yes: weekly attendance, dated assessments, semester results, risk snapshots. |
| Every phase independently implementable and testable? | Yes: see `DEVELOPMENT_PLAN.md` gates. |
| Realistic for a student? | Yes, with the Must/Should/Could tags and the cut order in §10. |
| Token-efficient prompts? | Yes: shared rules in `project.mdc`; each prompt names only its task and docs. |
