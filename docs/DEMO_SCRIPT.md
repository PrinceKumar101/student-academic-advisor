# Demo script (11-step story)

Use this for a viva or recorded walkthrough. Password for all seeded accounts: `Demo@1234`.

**Setup** (see `README.md`): seed `--as-of 2026-09-19`, backend `:8000`, frontend `:5173`. Leave `OPENAI_API_KEY` blank unless you want a live model (the story works either way).

The SRS example (attendance 64%, risk **82**) is the design illustration. The **live seed** numbers below were recorded on 2026-09-19 (`docs/FUNCTIONAL_DEMO.md`). Say this once at the start so the panel is not surprised.

| Source | Attendance (approx.) | Risk |
|---|---|---|
| SRS example | 64% | 82 HIGH |
| Live seed `as_of=2026-09-19` | ~56.7% | **84.1 HIGH** |

API equivalent: `python -m scripts.demo_flow --base-url http://127.0.0.1:8000` from `backend/`.

---

## Step 1 — Login as Rahul (why he is at risk)

1. Open http://127.0.0.1:5173/login.
2. Email `rahul@demo.edu`, password `Demo@1234`.
3. Land on `/student`.

**Show:** score **84.1**, level **HIGH**, top factors (internal / attendance / quizzes), attendance warnings. Point at the disclaimer: risk is an **indicator**, not a prediction.

**Say:** Python computed this from stored records. The frontend only displays the API payload.

---

## Step 2 — Performance decline

1. `/student/risk` — component table, weights, contributions, notes, completeness, flags.
2. `/student/performance` — attendance series **DECLINING** (slope about **−2.7**, sudden drop). Overall assessment trend may be **STABLE** (about −0.5); decline is clearest on attendance and subjects.
3. `/student/subjects` — CS301–CS305 **HIGH_CONCERN**, attendance alert yes.

**Say:** Trend labels and slopes come from the trend engine (least-squares). Charts plot backend `{on, value}` points.

---

## Step 3 — Ask the advisor

1. `/student/advisor`.
2. Generate analysis. Facts panel is separate from advice. With no key: banner `FALLBACK` / `NOT_CONFIGURED`.
3. Chat: “Why am I at high risk?”

**Say:** The model (or fallback) is not allowed to invent percentages. Grounding validation rejects ungrounded numbers.

---

## Step 4 — Study plan

1. `/student/planner`.
2. Exam date e.g. `2026-10-10`, 3 hours/day, generate.
3. Tick one item (PATCH).

**Say:** Minutes per subject are allocated in Python (`time_budget`). AI only fills slot text; if it fails, templated activities still appear (`source=FALLBACK`).

---

## Step 5 — What-if (does not save)

1. `/student/what-if`.
2. Set attendance **80**, internal **60**. Submit.

**Expected (live seed):** 84.1 HIGH → **53.9 MEDIUM**, difference **−30.2**, `persisted` false. Refresh the dashboard: score is still 84.1.

SRS W1 (attendance 64 → 80 on fixture R3) is **−10.0** to MEDIUM. That is the unit-test case, not Rahul’s live inputs.

**Say:** Same risk engine, in memory. Zero database writes.

---

## Step 6 — Teacher finds Rahul and creates an intervention

1. Log out. Log in as `teacher1@demo.edu`.
2. `/teacher` — group size **42**, HIGH count, mean attendance (about **77.1**).
3. `/teacher/students` — filter **HIGH**, search **Rahul**. One row: Rahul Venn.  
   Unfiltered first page may not list him (page-local sort, D34).
4. Open `/teacher/students/1` (or his id). Create intervention, e.g. “Attendance recovery plan”. Baseline risk is stored at creation.

**Say:** Teachers only see students in subjects they teach. Authorization is enforced in `api/deps.py`, not only in the UI.

---

## Step 7 — Update academic data

From `backend/` with the venv active:

```bash
python -m scripts.demo_advance --email rahul@demo.edu
```

Note the printed **New as_of** date (example: `2026-10-17`).

Alternatively add better attendance/marks in Swagger as the teacher.

---

## Step 8 — Show improvement

1. In the header, set **As of** to the printed date (or open `?as_of=2026-10-17`).
2. Student dashboard or teacher detail: Rahul **68.5 HIGH** (was 84.1). Still HIGH, but lower.
3. `/teacher/interventions` or student interventions → progress: observational wording (IMPROVED / WORSENED / UNCHANGED). Direction uses a ±2 score threshold; this is **not** a causal claim.

**Say:** Snapshots and `as_of` let the demo move time without rewriting history.

---

## Steps 9–11 (optional extras)

| # | Action | Point |
|---|---|---|
| 9 | `/student/profile` | Study habits (student-writable); semester results read-only. |
| 10 | Open `/teacher` while still logged in as Rahul | `/forbidden` + link back to the student dashboard. |
| 11 | Blank `OPENAI_API_KEY`, reload advisor / planner | App still works; risk/trends/what-if never call the AI. |

---

## Talking order (about 8–10 minutes)

Login → “how am I doing?” → risk components → decline charts → what-if → advisor/fallback → plan → teacher filter → intervention → `demo_advance` + As of → progress note.

Screenshots: [`docs/screenshots/`](screenshots/).
