# API_SPEC: Student Academic Advisor

Copied from `docs/archive/MASTER_DESIGN.md` §4. Each endpoint is marked with its planned phase from `DEVELOPMENT_PLAN.md`.

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

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| GET | `/health` | P | Liveness | 1 |
| POST | `/auth/register` | P | Create STUDENT account + profile | 3 |
| POST | `/auth/login` | P | OAuth2 password form → token | 3 |
| POST | `/auth/logout` | A | 204; client discards token | 3 |
| GET | `/auth/me` | A | Current user + profile id | 3 |

**Students**

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| GET | `/students/{id}` | S,T | Profile | 4 |
| GET | `/students/{id}/overview` | S,T | Composite dashboard payload (Phase 12) | 12 |
| GET | `/students/{id}/study-habits` | S,T | Read habits | 4 |
| PUT | `/students/{id}/study-habits` | S | Update own habits | 4 |
| GET | `/students/{id}/semester-results` | S,T | Previous results | 4 |
| PUT | `/students/{id}/semester-results/{semester}` | T | Upsert a previous result | 4 |

**Subjects**

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| GET | `/subjects?mine=true` | A | List subjects | 4 |
| POST | `/subjects` | T | Create (creator gets a teaching assignment) | 4 |
| PATCH | `/subjects/{id}` | T | Edit taught subject | 4 |
| POST | `/subjects/{id}/enrollments` | T | Enroll `{student_id}` | 4 |
| DELETE | `/subjects/{id}/enrollments/{student_id}` | T | Unenroll | 4 |

**Attendance and Assessments** (writes are teacher-only, for taught subjects and sections)

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| GET | `/attendance?student_id=&subject_id=` | S,T | Per-subject summary (computed %) + records | 4 |
| POST | `/attendance` | T | Add weekly record | 4 |
| PUT / DELETE | `/attendance/{record_id}` | T | Edit / remove | 4 |
| GET | `/assessments?student_id=&subject_id=&type=` | S,T | List | 4 |
| POST | `/assessments` | T | Create | 4 |
| PUT / DELETE | `/assessments/{id}` | T | Edit / remove | 4 |

**Risk, Trends, Analytics**

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| GET | `/risk/{student_id}` | S,T | Current risk with components | 5 |
| GET | `/risk/{student_id}/history` | S,T | Snapshots over time | 5 |
| POST | `/risk/{student_id}/what-if` | S,T | Simulate; no DB writes | 7 |
| GET | `/trends/{student_id}` | S,T | Assessment, attendance and risk trends | 6 |
| GET | `/trends/{student_id}/warnings` | S,T | Early warnings | 6 |
| GET | `/analytics/students/{student_id}/subjects` | S,T | Subject analysis | 6 |
| GET | `/analytics/students/{student_id}/comparison` [S] | S,T | Student vs class average (only when group ≥ 5) | 6 |

**AI**

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| POST | `/ai/analysis` | S,T | Facts + AI advice (cached, limited) | 8 |
| POST | `/ai/chat` | S | Ask the academic assistant | 10 |
| GET | `/ai/chat/history` | S | Last messages | 10 |
| DELETE | `/ai/chat/history` | S | Clear | 10 |
| GET | `/ai/usage` | A | Remaining daily allowances | 8 |
| POST | `/ai/intervention-suggestions` [C] | T | Suggested interventions for a student | 11 |

**Study plans**

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| POST | `/study-plans` | S | Generate and store a plan | 9 |
| GET | `/study-plans` | S | List own plans | 9 |
| GET | `/study-plans/{plan_id}` | S | Plan with items | 9 |
| PATCH | `/study-plans/{plan_id}/items/{item_id}` | S | Mark item done/undone | 9 |
| DELETE | `/study-plans/{plan_id}` | S | Delete | 9 |

**Interventions and Teacher**

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| POST | `/interventions` | T | Create; stores baseline risk | 11 |
| GET | `/interventions?student_id=&status=` | S (own), T | List | 11 |
| GET | `/interventions/{id}` | S,T | Detail | 11 |
| PATCH | `/interventions/{id}` | T: any field. S: `status` + `completion_note` only | Update | 11 |
| GET | `/interventions/{id}/progress` | S,T | Before/after | 11 |
| GET | `/teacher/dashboard` | T | Class summary | 11 |
| GET | `/teacher/students?risk_level=&department=&semester=&section=&subject_id=&search=` | T | Filtered, paginated list with risk | 11 |
| GET | `/teacher/subjects/{subject_id}/analytics` | T | Subject-level class analytics | 11 |

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
