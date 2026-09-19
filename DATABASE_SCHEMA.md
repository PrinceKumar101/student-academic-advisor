# DATABASE_SCHEMA: Student Academic Advisor

Copied from `docs/archive/MASTER_DESIGN.md` §3.

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
                 topic<=80, activity<=200, duration_minutes 1..480, priority[LOW|MEDIUM|HIGH],
                 is_completed default false, completed_at NULL)
ai_chat_messages(id PK, student_id FK, role[USER|ASSISTANT], content,
                 source[AI|FALLBACK] NULL, created_at)
interventions(id PK, student_id FK, teacher_id FK, subject_id FK NULL, title, description,
              priority[LOW|MEDIUM|HIGH], status[PENDING|IN_PROGRESS|COMPLETED], due_date,
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

### 3.5 Seed scale

Copied from archived `MASTER_DESIGN.md` §9 so Phase 2 does not depend on the archive.

Synthetic, deterministic (`random.Random(42)`). Command: `python -m scripts.reset_db && python -m scripts.seed_demo [--as-of YYYY-MM-DD]`.

Default `--as-of` is `2026-09-19` (D17). Weekly attendance dates are the 12 days `as_of - 11 weeks` … `as_of`. Implementation: `scripts/seed_generator.py`.

**Counts:** 40 generated students + 3 edge-case students (**43** total). Story login `rahul@demo.edu` is one of the 40 (DECLINING profile), not an extra row. 2 teachers, 5 subjects (CS301–CS305), Semester 5, sections A/B.

**Per student per subject (generated profiles):** 12 weekly attendance records; INTERNAL ×3, QUIZ ×4, ASSIGNMENT ×3; previous results for semesters 3 and 4; one study-habits row.

**Edge logins** (password `Demo@1234`): `newstudent@demo.edu` (no data), `zeroclass@demo.edu` (0 classes held), `missingassign@demo.edu` (many MISSING assignments). Teachers: `teacher1@demo.edu` (CS301/CS302/CS303, section ALL), `teacher2@demo.edu` (CS304/CS305 ALL, CS301 section B).

**Profile mix** (of the 40 generated students): High 6 / Average 12 / Low 7 / Improving 5 / Declining 6 / Inconsistent 4.

Risk-history back-fill: 4 snapshots per student at `as_of` minus 9, 6, 3 and 0 weeks (Phase 5.10). Story login `rahul@demo.edu` is tuned so the latest snapshot is HIGH.

---
