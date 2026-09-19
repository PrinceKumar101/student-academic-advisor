# PROJECT_SPEC: Student Academic Advisor

Copied from `SRS.md` (overview, principle, stack) and `docs/archive/MASTER_DESIGN.md` (constraints and headline decisions). Do not treat this file as a paraphrase of the risk formulas or API tables.

## What this project is

Student Academic Advisor is a full-stack **academic decision-support and advisory system**, not a replacement for teachers.

It analyzes a student's academic information, identifies potential academic risks, explains the reasons behind those risks, and uses an AI API to provide personalized recommendations and study plans.

Students often receive academic information in separate places: attendance records, internal marks, assignments, quizzes, previous examination results, and other academic activities. Because this information is scattered, students may not realize that their academic performance is declining until examinations are approaching. Teachers also have difficulty manually monitoring every student's academic progress, especially when dealing with large classes.

## Principle: Python computes, AI explains

The system should NOT falsely claim that an AI model has been trained to predict student performance.

The project will use a **Python-based academic risk scoring algorithm** for quantitative risk assessment.

**Python = calculation, analysis and business logic**

**AI API = intelligent interpretation and personalized assistance**

Python computes every fact (attendance %, deterministic risk score 0–100, trends, what-if). The AI only turns supplied facts into language. No AI capability can change a risk score, a percentage or a database record. The app must work with the AI turned off (deterministic fallback).

## Main features

- Academic performance analysis
- Risk assessment (deterministic score 0–100; levels LOW / MEDIUM / HIGH / INSUFFICIENT_DATA)
- Performance trend detection
- Identification of weak areas
- Explanation of risk factors (templated notes from Python; prose from AI)
- Personalized recommendations
- AI-generated study plans (hybrid: Python time budget + AI slot text)
- What-if simulations (in memory; zero DB writes)
- Teacher/class-level analytics
- Intervention tracking (baseline at creation; observational before/after)

## Tech stack

| Layer | Choice |
|---|---|
| Primary language | Python |
| Backend | FastAPI |
| Database | SQLite + SQLAlchemy |
| Auth | JWT (PyJWT), password hashing (`pwdlib[argon2]` or bcrypt), OAuth2 password-form login |
| AI | OpenAI API (backend only; optional at runtime) |
| Frontend (Phases 13–19) | React + TypeScript + Vite + Tailwind CSS + Recharts |

No custom ML. Risk, trends and what-if never call the AI.

## Constraints

- **Frontend/UI last.** All frontend and UI work is Phases 13–19. Phases 0–12 are backend-only, verified by pytest, Swagger UI (`/docs`) and a scripted API demo (D1).
- Public registration creates **STUDENT only**. Teachers via `scripts/create_teacher.py` (D2).
- Teachers enter attendance, marks and previous-semester results. Students are read-only except study habits, study plans, chat and intervention status (D3).
- Attendance percentage is **always computed, never stored** (D5).
- No Alembic. Use `create_all` + `scripts/reset_db.py` + seed (D7).
- Deferred: notifications, email, PDF export, reporting module, Docker, Alembic. CI is optional (D12).
- No background jobs. Risk snapshots persist as a side effect of computing risk (D13).
- Demo data is synthetic. Real student data requires institutional approval.
- Secrets live in backend `.env` only; `.env.example` has blanks.

## Minimum Demonstrable Path

Auth → seed data → risk engine + explanation → trends + subject analysis → what-if → AI analysis (+ fallback) → study plan → teacher dashboard + filtering → intervention + before/after → minimal functional frontend for all of these.

**Never cut:** deterministic risk engine, authorization tests, AI fallback, before/after tracking.
