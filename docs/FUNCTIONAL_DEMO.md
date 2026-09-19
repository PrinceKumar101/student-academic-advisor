# Functional demo checklist (Phase 16)

Manual happy path against a seeded backend and the unstyled UI. Playwright was not added (D35).

## Setup

```bash
# backend/
python -m scripts.reset_db
python -m scripts.seed_demo --as-of 2026-09-19
uvicorn app.main:app --reload

# frontend/ (backend already on :8000)
npm run dev
```

Leave `OPENAI_API_KEY` blank for the AI-off / fallback run. Password for all demo accounts: `Demo@1234`.

The UI uses `date.today()` unless you set **As of** in the header (writes `?as_of=YYYY-MM-DD` and forwards it to the API). After `demo_advance`, set **As of** to the printed new date.

## Student story (`rahul@demo.edu`)

Observed on 2026-09-19 against the live seed (as of 2026-09-19):

| Step | Page | Check | Result |
|---|---|---|---|
| 1 | `/login` | Login lands on `/student` | Pass — Rahul Venn (STUDENT) |
| 2 | Dashboard | HIGH risk, top factors, warnings | Pass — score **84.1 HIGH**; factors internal / attendance / quizzes; attendance warnings |
| 3 | `/student/risk` | Component table, weights, notes | Pass |
| 4 | `/student/performance` | Charts + decline visible | Pass — attendance **DECLINING** (slope −2.7) · SUDDEN_DROP; two SVG charts. Overall assessment **STABLE** (−0.5) |
| 5 | `/student/subjects` | Bands from backend | Pass — all CS301–CS305 HIGH_CONCERN, attendance alert yes |
| 6 | `/student/what-if` | Attendance 80, internal 60; not persisted | Pass — 84.1 HIGH → **53.9 MEDIUM**, difference **−30.2**, persisted no |
| 7 | `/student/advisor` | Analysis + chat “Why am I at high risk?” | Pass — facts vs advice; fallback banner `NOT_CONFIGURED`; chat ASSISTANT (FALLBACK) |
| 8 | `/student/planner` | Exam 2026-10-10, 3 h/day; tick item | Pass — 63 FALLBACK items; checkbox PATCH works |
| 9 | `/student/interventions` | Status + progress | Pass — seed “Meet after class” PENDING → IN_PROGRESS; progress UNCHANGED observational note |
| 10 | `/student/profile` | Habits form + semester table | Pass |
| 11 | `/teacher` as student | Role guard | Pass — `/forbidden`; after 16.2, “Go to your dashboard” + Log out |

## Teacher story (`teacher1@demo.edu`)

| Step | Page | Check | Result |
|---|---|---|---|
| 12 | `/teacher` | Counts / means | Pass — group 42; HIGH 8; mean attendance 77.1 |
| 13 | `/teacher/students` | HIGH + search Rahul | Pass — 1 student, Rahul Venn. Unfiltered first page does not list Rahul (D34 page-local sort) |
| 14 | `/teacher/students/1` | Detail + create intervention | Pass — created “Attendance recovery plan” |
| 15 | Same page | AI analysis / suggestions | Pass — fallback suggestions (internal, attendance, quizzes) |
| 16 | `/teacher/interventions` | List + progress | Pass — both interventions listed |
| 17 | `/teacher/subjects` | Load CS301 | Pass — group 42, means shown |
| 18 | Filters | Empty result | Covered by `TeacherStudentsPage` tests; empty title “No students match these filters” |

## After `demo_advance`

```bash
# backend/
python -m scripts.demo_advance --email rahul@demo.edu
# prints New as_of: YYYY-MM-DD
```

Set the header **As of** to that date (or open `?as_of=YYYY-MM-DD`). Verified: `2026-10-17` shows Rahul **68.5 HIGH** (was 84.1 on 2026-09-19).

## AI-off

With a blank `OPENAI_API_KEY`, advisor analysis, chat, planner, and intervention suggestions all returned `source=FALLBACK` / `NOT_CONFIGURED` and the pages still worked. Risk, trends, and what-if never call the AI.

## Known non-blocking notes

- SRS example numbers (attendance 64%, risk 82) differ from the live seed (attendance ~56.7%, risk 84.1). The story is still HIGH → what-if MEDIUM → teacher intervention.
- Overall assessment trend is STABLE; decline is on attendance and per-subject series.
- Long raw floats in tables are backend values (no frontend rounding).
- UI is unstyled by design until Phase 17.
- Git tag `frontend-functional` is not created unless requested.

## Defects found and fixed in 16.2

1. **Forbidden page dead-end** — no link home or logout after a student opened `/teacher`. Added dashboard link + logout.
2. **Post-advance data invisible** — frontend never sent `as_of`, so recovery weeks after today were filtered out. Header date + `?as_of=` now forwarded on API calls (D35).
