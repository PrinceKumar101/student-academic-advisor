# Final report: Student Academic Advisor

**Course project (v1)** · 2026-09-19  
**Stack:** FastAPI + SQLAlchemy + SQLite · React 18 + TypeScript + Vite + Tailwind CSS 3  
**Principle:** Python computes academic facts; an optional LLM explains them.

## 1. Problem

Attendance, internals, quizzes, assignments and prior results live in separate places. Students often notice decline only near exams. Teachers cannot scan every record by hand. The system combines those records into a **transparent risk score**, trends, what-if experiments, and optional AI wording — without claiming that a model was trained on student outcomes.

## 2. Objectives (met)

- Deterministic risk 0–100 with documented weights and floors (`RISK_ENGINE_SPEC.md`).
- Trends, subject bands, early warnings.
- What-if simulation with **no persistence**.
- AI analysis, chat and study-plan text with **fallback** when the key is missing or the model fails.
- Teacher dashboard, filters, interventions with baseline and observational progress.
- Role-based JWT auth; student-to-student isolation.
- Functional then designed UI (Phases 13–18). Frontend displays API values only.

## 3. Architecture

Thin routers → services → **pure engines** or `ai/`. Authorization only in `api/deps.py`. OpenAPI exported to `openapi.json`; frontend types generated from that file. See `ARCHITECTURE.md` (Decision Log D1–D37).

```text
UI (React) → /api/v1 + JWT → FastAPI
  services: load data, persist snapshots, call AI
  engines: risk, trend, what-if, time budget, analytics (no I/O)
  ai/: client, prompts, validators, fallback (optional OpenAI)
  SQLite: identities, academic rows, risk history, plans, chat, interventions
```

## 4. Implementation summary

| Area | What shipped |
|---|---|
| Data | 43 seeded students, 5 CS subjects, 2 teachers, edge cases |
| Risk | R1–R13 tests; live Rahul **84.1 HIGH** on 2026-09-19 seed |
| Trends | Slope labels; attendance decline on the story student |
| What-if | Live 84.1 → **53.9 MEDIUM** at attendance 80 / internal 60 |
| AI | analysis_v1, chat_v1, plan_v1; cache and daily limits |
| Teacher | Dashboard, filters, subject analytics, CSV import, interventions |
| UI | Paper/ink design, responsive shell, skeletons, risk colour + text |

## 5. Testing

- Backend: `pytest` (unit engines, API matrix, full-story, fake AI).
- Frontend: `vitest` + React Testing Library (auth, pages, a11y assertions).
- Manual: `docs/FUNCTIONAL_DEMO.md`, `scripts/demo_flow.py`.
- No test calls the real OpenAI API.

## 6. Results of the demo story

See `docs/DEMO_SCRIPT.md`. After `demo_advance` and `as_of` on the printed date, Rahul’s score moved from **84.1** to **68.5** (still HIGH). Improvement is shown as a number change plus observational intervention progress — not as proof of causality.

## 7. Limitations

Heuristic weights; synthetic data; SQLite; JWT in `localStorage`; page-local teacher sort; no Docker/Alembic/notifications. Git release tags are created only on request.

## 8. Future work

College ERP/LMS import, PostgreSQL, httpOnly cookies, outcome-validated models (if ethics and data allow), notifications, parent view. SRS §43.

## 9. Conclusion

The project is a complete academic decision-support demo: reproducible scoring, safe AI language, teacher workflow, and a documented setup path from a fresh clone (`README.md`).
