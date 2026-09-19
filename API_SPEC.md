# API_SPEC: Student Academic Advisor

Copied from `docs/archive/MASTER_DESIGN.md` §4. Each endpoint is marked with its planned phase from `DEVELOPMENT_PLAN.md`.

## 4. API PLAN (Output 4)

Base path `/api/v1`. JSON. Interactive docs at `/docs`. Paths in the tables below are relative to that base unless written as a full path.

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

- **Enums:** `UserRole` STUDENT/TEACHER · `RiskLevel` LOW/MEDIUM/HIGH/INSUFFICIENT_DATA · `AssessmentType` INTERNAL/QUIZ/ASSIGNMENT/EXAM · `AssessmentStatus` GRADED/MISSING/PENDING · `Priority` LOW/MEDIUM/HIGH · `InterventionStatus` PENDING/IN_PROGRESS/COMPLETED · `TrendLabel` IMPROVING/STABLE/DECLINING/INSUFFICIENT_DATA · `SuddenChange` SUDDEN_RISE/SUDDEN_DROP · `Source` AI/FALLBACK · `ChatMessageRole` USER/ASSISTANT · `SubjectBand` HIGH_CONCERN/MEDIUM/GOOD · `WarningSeverity` WARNING/CRITICAL · `ProgressDirection` IMPROVED/WORSENED/UNCHANGED · `FallbackReason` NOT_CONFIGURED/TIMEOUT/PROVIDER_ERROR/INVALID_OUTPUT/UNGROUNDED_OUTPUT.
- Percentages are floats 0–100 rounded to 1 decimal in responses.

### 4.2 Endpoint list

Legend: **S** = student (own data), **T** = teacher (visible students / taught subjects), **A** = any authenticated, **P** = public. `[S]/[C]` marks Should/Could priority; unmarked = Must.

**System / Auth**

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| GET | `/api/v1/health` | P | Liveness | 1 |
| POST | `/auth/register` | P | Create STUDENT account + profile | 3 |
| POST | `/auth/login` | P | OAuth2 password form → token | 3 |
| POST | `/auth/logout` | A | 204; client discards token | 3 |
| GET | `/auth/me` | A | Current user + profile id | 3 |

**Students**

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| GET | `/students/{id}` | S,T | Profile | 4 |
| GET | `/students/{id}/overview` | S,T | Composite dashboard payload | 12 |
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
| POST | `/imports/attendance?dry_run=` [S] | T | CSV attendance import | 12 |
| POST | `/imports/assessments?dry_run=` [S] | T | CSV assessment import | 12 |

**Intervention rules.** Status moves PENDING → IN_PROGRESS → COMPLETED. A teacher may also reopen. When status becomes COMPLETED, the backend stores the outcome snapshot (`outcome_score`, `outcome_level`, `outcome_at`).

### 4.3 Key contracts (others are derived from schemas in `API_SPEC.md`)

**POST `/auth/register`**: `{email, password(min 8), full_name, student_code, department, semester, section}` → 201 `{user_id, student_id}`. No `role` field exists (extra fields, including `role`, are ignored). Duplicate email or code → 409.

**POST `/auth/login`** (`application/x-www-form-urlencoded`: `username`=email, `password`) →
`{access_token, token_type:"bearer", expires_in, user:{id, role, student_id|teacher_id, full_name}}`. `expires_in` is seconds. Any failure (unknown email, wrong password, inactive user) gives the same 401 message (no user enumeration).

**GET `/auth/me`**: `{id, email, role, student_id, teacher_id, full_name}`. `password_hash` is never returned. Missing/invalid/expired token → 401.

**POST `/auth/logout`**: 204 empty body. Requires a valid bearer token; the server does not persist a denylist (the client discards the token).

**GET `/subjects`**: query `mine` (bool, default false), `page`, `page_size`. Response `{items:[{id,code,name,semester}], total, page, page_size}`. `mine=true` is enrolled subjects (student) or taught subjects (teacher).

**POST `/subjects`**: `{code, name, semester}` → 201 subject. Creator receives a `teaching_assignments` row with section `ALL`. Duplicate `code` → 409.

**PATCH `/subjects/{id}`**: teacher must be assigned to the subject. Duplicate `code` → 409.

**POST `/subjects/{id}/enrollments`**: `{student_id}` → 201 `{id, student_id, subject_id}`. Teacher must teach that subject and the student's section (`ALL` or exact match). Already enrolled → 409.

**DELETE `/subjects/{id}/enrollments/{student_id}`**: 204. Same write rule. Missing enrollment → 404.

**GET `/students/{id}`**: `{id, student_code, full_name, department, semester, section}`.

**GET `/students/{id}/overview`**: composite dashboard (`{id}` may be `me`). Optional query `as_of` (ISO date; default today). Computes live risk and persists a snapshot when needed (same rule as `GET /risk/{id}`). Response:
```json
{
  "student_id": 12, "as_of": "2026-09-19",
  "profile": {"id":12,"student_code":"CS2025001","full_name":"Rahul Venn",
              "department":"CSE","semester":5,"section":"B"},
  "risk": {"score":82.0,"level":"HIGH","escalated":false,"escalation_reason":null,
           "data_completeness":1.0,"config_version":"1.0","flags":[]},
  "top_factors": ["internal","attendance","quizzes"],
  "subjects": [{"subject_id":1,"code":"CS301","name":"Data Structures",
               "performance_percent":48.0,"band":"HIGH_CONCERN",
               "attendance_percent":64.0,"attendance_alert":true}],
  "trend_summary": {"overall_label":"DECLINING","overall_slope":-5.7,
                   "attendance_label":"DECLINING","attendance_slope":-2.2},
  "warnings": [{"code":"ATTENDANCE_DROP","severity":"WARNING","message":"...",
                "metric":"attendance","previous_value":82.0,"current_value":67.0}],
  "open_interventions": [{"id":1,"status":"PENDING","title":"..."}]
}
```
`open_interventions` is PENDING and IN_PROGRESS only.

**GET `/students/{id}/study-habits`**: `{student_id, study_hours_per_day, self_confidence, available_hours_per_day}`. Missing row → 404.

**PUT `/students/{id}/study-habits`**: student (own) only; upserts the same fields. Teacher → 403.

**GET `/students/{id}/semester-results`**: list of `{id, student_id, semester, percentage, sgpa}`.

**PUT `/students/{id}/semester-results/{semester}`**: teacher of a visible student; `{percentage, sgpa?}`. Upsert.

**GET `/attendance?student_id=&subject_id=`**: `{student_id, summaries:[{subject_id, subject_code, subject_name, classes_held, classes_attended, attendance_percent}], records:[...]}`. `attendance_percent` is computed (1 decimal) or `null` when `classes_held` is 0.

**POST `/attendance`**: teacher write on taught subject+section. `{student_id, subject_id, record_date, classes_held, classes_attended}`. Duplicate date → 409. `attended > held` → 422.

**PUT / DELETE `/attendance/{record_id}`**: same write rule. PUT may change date and counts.

**GET `/assessments?student_id=&subject_id=&type=`**: list of `{id, student_id, subject_id, type, name, max_marks, obtained_marks, status, assessment_date}`.

**POST `/assessments`**: teacher write. `GRADED` requires `obtained_marks`; `0 ≤ obtained_marks ≤ max_marks`; `max_marks > 0`.

**PUT / DELETE `/assessments/{id}`**: same write rule and marks bounds.

**GET `/risk/{student_id}`** (`student_id` may be `me`). Optional query `as_of` (ISO date); default is today. Computes live risk and persists a snapshot when none exists for that `as_of` or the score/level changed.
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

**GET `/risk/{student_id}/history`**
```json
{
  "student_id": 12,
  "items": [
    {"as_of":"2026-07-18","computed_at":"2026-07-18T00:00:00Z","score":42.0,
     "level":"MEDIUM","escalated":false,"escalation_reason":null,
     "data_completeness":1.0,"config_version":"1.0","flags":[]}
  ]
}
```

**GET `/trends/{student_id}`** (`student_id` may be `me`). Optional query `as_of` (ISO date); default is today. Live computation; no writes. Each series is `{label, slope, point_count, first, last, mean, sudden_change, points:[{on,value}]}`. `label` is `INSUFFICIENT_DATA` when the series has fewer than 3 points. `sudden_change` is `SUDDEN_RISE`, `SUDDEN_DROP`, or `null`.
```json
{
  "student_id": 12, "as_of": "2026-09-19",
  "overall": {"label":"DECLINING","slope":-5.7,"point_count":4,"first":72.0,"last":55.0,
              "mean":64.8,"sudden_change":null,"points":[{"on":"2026-06-01","value":72.0}]},
  "by_type": [{"type":"INTERNAL","label":"DECLINING","slope":-5.7,"point_count":4,
               "first":72.0,"last":55.0,"mean":64.8,"sudden_change":null,"points":[]}],
  "by_subject": [{"subject_id":1,"subject_code":"CS301","subject_name":"Data Structures",
                  "label":"INSUFFICIENT_DATA","slope":null,"point_count":2,"first":70.0,
                  "last":60.0,"mean":65.0,"sudden_change":null,"points":[]}],
  "attendance": {"label":"DECLINING","slope":-2.2,"point_count":12,"first":80.0,"last":52.0,
                 "mean":66.0,"sudden_change":null,"points":[]},
  "risk": {"label":"INSUFFICIENT_DATA","slope":null,"point_count":0,"first":null,"last":null,
           "mean":null,"sudden_change":null,"points":[]}
}
```

**GET `/trends/{student_id}/warnings`** (`student_id` may be `me`). Optional `as_of`. Live rules from `RISK_ENGINE_SPEC.md` §7.3; no writes.
```json
{
  "student_id": 12, "as_of": "2026-09-19",
  "warnings": [
    {"code":"ATTENDANCE_DROP","severity":"WARNING","message":"...","metric":"attendance_percent",
     "previous_value":82.0,"current_value":67.0}
  ]
}
```

**GET `/analytics/students/{student_id}/subjects`**. Optional `as_of`. Subject % = Σ obtained ÷ Σ max over GRADED assessments. Band: `<50` HIGH_CONCERN · `<65` MEDIUM · else GOOD. `attendance_alert` is true when subject attendance is below 75%.
```json
{
  "student_id": 12, "as_of": "2026-09-19",
  "subjects": [
    {"subject_id":1,"code":"CS301","name":"Data Structures","performance_percent":48.0,
     "band":"HIGH_CONCERN","attendance_percent":70.0,"attendance_alert":true}
  ]
}
```

**GET `/analytics/students/{student_id}/comparison`**. Optional `as_of`. Comparison group is the same department, semester and section. When the group has fewer than 5 students, `available` is false and peer metrics are omitted.
```json
{
  "student_id": 12, "as_of": "2026-09-19",
  "available": true, "group_size": 12,
  "group": {"department":"CSE","semester":5,"section":"B"},
  "student": {"attendance_percent":64.0,"marks_percent":52.0},
  "class_average": {"attendance_percent":78.0,"marks_percent":71.0},
  "reason": null
}
```

**POST `/risk/{student_id}/what-if`**. Optional query `as_of` (ISO date); default is today. Request: `{"overrides": {"attendance_percent": 80, "study_hours_per_day": 3}}`. Allowed keys: `attendance_percent`, `internal_percent`, `quiz_percent`, `assignment_percent`, `assignment_submission_rate`, `study_hours_per_day`, `self_confidence`. Percent fields 0–100; `study_hours_per_day` 0–24; `self_confidence` 1–5. Unknown keys → 422. Out-of-range → 422. No database writes (`persisted` is always false). An override that activates a previously missing component is `hypothetical: true`.
Response: `{"current":{score,level}, "simulated":{score,level}, "difference":-10.0, "changed_factors":[{"key":"attendance","from_value":64.0,"to_value":80.0,"risk_from":65.0,"risk_to":25.0,"contribution_delta":-10.0,"hypothetical":false}], "persisted": false}`

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
`fallback_reason` when `source=FALLBACK`: `NOT_CONFIGURED | TIMEOUT | PROVIDER_ERROR | INVALID_OUTPUT | UNGROUNDED_OUTPUT`. Daily limit reached → 429 `RATE_LIMITED`. Cache hit (`cached: true`) does not increment the daily analysis count. `refresh: true` bypasses the 24 h `input_hash` cache.

**POST `/ai/chat`** (students only; body `{question}` ≤ 500 characters after strip). A client-supplied `student_id` is ignored; the assistant always uses the caller's own academic facts. Empty or over-long question → 422. Response:
```json
{
  "source": "AI", "generated_at": "...",
  "answer": "...", "suggested_followups": ["..."],
  "fallback_reason": null
}
```
AI failure or invalid/ungrounded output still returns 200 with `source=FALLBACK` and the chat banner. Daily chat limit (USER messages that UTC day) → 429 `RATE_LIMITED`. The model sees the last 6 stored messages plus the new question.

**GET `/ai/chat/history`** (students only): `{ "messages": [{"id", "role":"USER|ASSISTANT", "content", "source":"AI|FALLBACK"|null, "created_at"}] }` in chronological order. USER rows have `source` null.

**DELETE `/ai/chat/history`**: 204; deletes the caller's messages.

**GET `/ai/usage`**
```json
{
  "analysis": {"used": 1, "limit": 10, "remaining": 9},
  "chat": {"used": 0, "limit": 30, "remaining": 30},
  "plans": {"used": 0, "limit": 5, "remaining": 5}
}
```
Counts are per authenticated user for the current UTC day. Plan `used` counts `study_plans` created that UTC day. Chat `used` counts the student's USER chat messages that UTC day.

**POST `/study-plans`**
Request: `{"exam_date":"2026-10-15","available_hours_per_day":3,"subject_ids":[1,2],"topics":{"1":["Trees","Graphs"]}}` (`subject_ids` empty = auto-pick up to 3 weak / lowest subjects; `topics` optional).
Response: `{"id":5,"source":"AI","exam_date":"2026-10-15","available_hours_per_day":3,"prompt_version":"plan_v1","created_at":"...","items":[{"id":1,"plan_date":"...","subject":{"id":1,"code":"CS301"},"topic":"...","activity":"...","duration_minutes":60,"priority":"HIGH","is_completed":false,"completed_at":null}], "tips":[...], "fallback_reason":null}`.
Validation: exam date in the future and within 60 days of today; hours 0.5–12; `subject_ids` must be enrolled. AI failure or invalid slots still returns 200 with `source=FALLBACK`. Daily plan limit → 429 `RATE_LIMITED`.
GET `/study-plans` lists the caller's summaries (`id`, dates, `source`, `item_count`). GET `/study-plans/{id}` is the full plan. PATCH item body: `{"is_completed":true}` (sets or clears `completed_at`). DELETE returns 204. Students only; another student's plan is 403.

**POST `/interventions`** (teacher only; target student must be visible). Body: `{student_id, subject_id?, title<=120, description?, priority, due_date?}`. Response includes copied `baseline_score`, `baseline_level`, `baseline_at` from live risk at `as_of` (query, default today). Invisible student → 403. Optional `subject_id` must be an enrolled subject the teacher is assigned to.

**GET `/interventions`**: students see only their own rows. Teachers see interventions for visible students. Filters: `student_id`, `status`.

**PATCH `/interventions/{id}`**: teacher may change title, description, priority, due_date, subject_id, status, completion_note, and may reopen. Students may send only `status` and `completion_note`; other fields → 403. Student status moves PENDING → IN_PROGRESS → COMPLETED only (skip or regress → 422). Transition into COMPLETED stores `outcome_score`, `outcome_level`, `outcome_at`.

**GET `/interventions/{id}/progress`**
```json
{ "baseline":{"score":84.0,"level":"HIGH","at":"2026-09-01"},
  "current":{"score":63.0,"level":"HIGH","as_of":"2026-09-19"},
  "change":-21.0, "direction":"IMPROVED", "days_elapsed":18,
  "note":"This shows the observed change in risk since the intervention was created. It does not prove the intervention caused it." }
```
`direction`: IMPROVED / WORSENED / UNCHANGED (`|change| < 2.0` = UNCHANGED; `engines/intervention_progress.py`). `change` is current score minus baseline (negative = lower risk = IMPROVED). Missing scores → `change` null and UNCHANGED.

**GET `/teacher/dashboard`** (teacher): `{as_of, group_size, risk_counts, mean_attendance, mean_marks, subject_performance:[{subject_id,code,name,mean_percent}], trend_distribution}` over visible students. Optional `as_of`.

**GET `/teacher/students`**: paginated `{items,total,page,page_size}`. Item: profile plus `risk_score`, `risk_level`, `attendance_percent`, `marks_percent`, `trend_label`. Filters: `risk_level`, `department`, `semester`, `section`, `subject_id`, `search` (name or student code). `subject_id` the teacher does not teach → 403.

**GET `/teacher/subjects/{subject_id}/analytics`**: same summary shape as the dashboard, scoped to visible students enrolled in that subject, plus `subject_id`, `code`, `name`. Unassigned subject → 403.

**POST `/ai/intervention-suggestions`** (teacher; body `{student_id}`): `{source, generated_at, student_id, prompt_version, suggestions:[{title,description,priority,reason}], fallback_reason}`. Same AI failure/grounding rules as analysis. Not cached; does not increment the analysis daily limit. Invisible student → 403.

**CSV import** (teacher only; Phase 12.9 / deferred 4.9)

| Method | Path | Who | Purpose | Phase |
|---|---|---|---|---|
| POST | `/imports/attendance?dry_run=` | T | Validate or commit weekly attendance rows | 12 |
| POST | `/imports/assessments?dry_run=` | T | Validate or commit assessment rows | 12 |

Multipart field `file` (UTF-8 CSV). `dry_run` defaults to **true**. Response `{kind, dry_run, valid, committed, created_count, errors:[{row,code,message}]}`. Row numbers are 1-based including the header (first data row is 2). Invalid or forbidden rows are collected; the file is committed only when `dry_run=false` and `valid` is true (all-or-nothing). Students → 403. A teacher who cannot write a row gets `FORBIDDEN` in `errors` (HTTP 200). Duplicate attendance dates (file or database) → `CONFLICT`. Missing columns or non-UTF-8 → 422.

Attendance columns: `student_code,subject_code,record_date,classes_held,classes_attended`.

Assessment columns: `student_code,subject_code,type,name,max_marks,obtained_marks,status,assessment_date`. `obtained_marks` may be empty unless `status=GRADED`. Same marks bounds as `POST /assessments`.

---
