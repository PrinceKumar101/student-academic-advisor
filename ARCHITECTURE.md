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
