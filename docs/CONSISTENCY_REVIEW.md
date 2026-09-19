# Consistency review (task 0.3)

Reviewed: `PROJECT_SPEC.md`, `ARCHITECTURE.md`, `DATABASE_SCHEMA.md`, `API_SPEC.md`, `AI_GUIDELINES.md`, `RISK_ENGINE_SPEC.md`, `UI_GUIDELINES.md`, `DEVELOPMENT_PLAN.md`, `CLAUDE_CONTEXT.md`, `README.md`, `.env.example`, plus archived `MASTER_DESIGN.md` / `SRS.md` where living docs disagree.

**Rule used:** disagreements *between living docs* are defects. SRS vs living docs are expected (MASTER_DESIGN §1 / D1–D13) and are not defects. After this report, small living-doc fixes were applied so Phase 0 open questions are answered.

## Findings that were real (living docs)

| ID | Topic | Disagreement | Resolution (0.3 edit) |
|---|---|---|---|
| C1 | Study-habits who | `API_SPEC`: GET S,T; PUT S. `DEVELOPMENT_PLAN` 4.2: GET/PUT “student own only”. | Plan 4.2 aligned with API: GET S,T; PUT S. |
| C2 | Cross-refs to §4.3 | `RISK_ENGINE_SPEC` §6.7 / §7.5 point at “§4.3” (old master numbering). | Point at `API_SPEC.md` §4.3. |
| C3 | `MASTER_DESIGN.md` as live design | `DEVELOPMENT_PLAN` header, 1.2, §2 tests (“§9 of the design”), §4.4 still treat the master as the live spec. | Point at living docs; seed counts restated in `DATABASE_SCHEMA.md` §3.5. |
| C4 | Health path | Base `/api/v1` + table path `/health` vs Prompt 1.1 `/api/v1/health`; plan 1.1 says `GET /health`. | Living docs now say `GET /api/v1/health`. |
| C5 | Health router | `ARCHITECTURE` folder list omits `health.py`. | `health` added to the router set. |
| C6 | Overview path notation | Architecture flow: `/students/me/overview`. API: `/students/{id}/overview` (`me` allowed). | Architecture uses the API form. |
| C7 | `interventions.priority` | Schema: untyped `priority`. API enum: `Priority` LOW/MEDIUM/HIGH. | Schema: `priority[LOW\|MEDIUM\|HIGH]`. |
| C8 | AI `student_id` in body | API analysis body may include `student_id`. AI privacy: “never taken from the request body”. | Privacy clarified: facts never from the body; `student_id` is an authorized target only. |
| C9 | Escalation reason | Two floors (attendance &lt; 75, internal &lt; 40) but only one reason string (“Attendance below 75% cutoff”). | Reason is per floor; both listed if both fire. |
| C10 | Incomplete API enums | Conventions omit `UserRole`, chat role, subject band, warning severity, progress `direction`, AI `fallback_reason`. | Enums list extended in `API_SPEC.md`. |

## Intentional SRS vs design (do not “fix” the SRS)

These match MASTER_DESIGN §1. Living docs win.

- Endpoints: SRS `/students/{id}/risk`, `/ai/analyze-performance`, `/students/{id}/what-if`, student-written attendance, `PUT /students/{id}` vs API `/risk/{student_id}`, `/ai/analysis`, `/risk/{student_id}/what-if`, teacher writes, no student profile PUT.
- Risk bands: SRS `0–30 / 31–60 / 61–100` vs `<=30` / `<=60` / else (no gap at 30.5).
- Attendance % stored (SRS FR) vs computed only (D5).
- Public register with roles vs STUDENT-only (D2).
- Two AI calls (analyze + recommend) vs one `analyze_performance` (D9).
- Frontend mid-project in SRS vs Phases 13–19 (D1).

## Checked and consistent

- Tables (16) and relationship diagram.
- Risk weights 0.25 / 0.25 / 0.15 / 0.15 / 0.10 / 0.10 (match SRS suggestions).
- Normalization 90/50 attendance, 75/35 performance; incomplete if available weight &lt; 0.40.
- Cases R1–R13 and W1 numbers; trend slope −5.7; warning examples 82→67 / 76→48.
- Seed scale: 40 generated + 3 edge + story `rahul` inside the 40 = **43** students, 5 subjects, 2 teachers.
- AI limits 10 / 30 / 5 and timeouts 20 s / 40 s match `.env.example`.
- JWT 60 min, CORS `http://localhost:5173`.
- UI stub deferred to Phase 17.

## Open questions

None remaining that block Phase 1. Ambiguities above are answered in the living docs.
