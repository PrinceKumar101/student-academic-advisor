# CLAUDE_CONTEXT: Student Academic Advisor

*Keep under ~60 lines. Overwrite sections; do not append history. Update at the end of every phase.*

**Current Phase:** UI redesign complete (UI-01 to UI-08); all planned phases 0–19 done
**Current Task:** none
**Last updated:** 2026-09-22

## Project in one paragraph
AI-assisted academic decision-support system. Python computes all facts (attendance %, deterministic risk score 0–100, trends, what-if). The AI API (OpenAI, backend only) only writes explanations, recommendations, study-plan text and chat answers, and always has a deterministic fallback. Stack: FastAPI + SQLAlchemy + SQLite (backend); React + TS + Vite + Tailwind (frontend; SVG charts, no Recharts). No custom ML.

## Ordering rule
**Backend first (Phases 0–12, then FREEZE). Frontend and UI last (Phases 13–19).** All stages including final docs are complete.

## Completed
- Phases 0–12 backend (freeze)
- Phases 13–16 frontend functional (freeze)
- Phase 17 UI design
- Phase 18 UI polish
- Phase 19 final README, demo script, viva notes, report, slides, screenshots, DoD
- UI redesign UI-01–UI-08: public landing page at `/` (plan + final design in `docs/UI_REDESIGN_PLAN.md`)

## In Progress
- None

## Next
- Optional: commit the UI-07/UI-08 working tree; git tags `v1.0` / `backend-v1` / `frontend-functional` on request

## Important Decisions
- D2 Public register = STUDENT only; teachers via `scripts/create_teacher.py`
- D3 Teachers enter attendance/marks; students read-only (except habits, plans, chat, intervention status)
- D32 Vite + React 18 + Tailwind 3 + RR6; `/api` proxy; JWT in `localStorage`; types from `openapi.json`
- D33 Trend charts plot backend `{on,value}` points (SVG, not Recharts)
- D34 Teacher list sorts the current page by backend `risk_score` (API has no sort query)
- D35 Frontend forwards `as_of` from `?as_of=` / header date field; Phase 16 checklist is `docs/FUNCTIONAL_DEMO.md` (no Playwright)
- D36 Academic paper/ink design system; risk colour + marker + printed level
- D37 Phase 18 polish without axe-core; `RiskGauge` displays backend score width only
- D38 `/` = public `LandingPage`; `HomeRedirect` at `/home`
- D39 Landing tokens are an additive `--landing-*` / `landing-*` layer; dashboards unchanged
- D40 Landing CTAs read `useAuth()` via `useLandingCta`; hero shows the engine's R3 case as static example data

## Known Issues
- Git tags `backend-v1`, `frontend-functional`, `v1.0` not created (commit/tag only on request).
- Starlette TestClient warns that `httpx` is deprecated in favor of `httpx2`; not added.
- Live seed Rahul is 84.1 HIGH (SRS example 82); overall assessment trend STABLE, attendance DECLINING.
- Screenshot PNGs may show webfont glyph artifacts; live UI text is correct (`docs/screenshots/README.md`).
- `TrendLineChart` logs a React duplicate-key dev warning when a series has two equal points on one date (pre-existing, Phase 17).

## Recent Changes
- 2026-09-22: UI-08 — final QA of the landing redesign; docs updated; live role/route check against the real backend.

## Key Files
`README.md` · `docs/DEMO_SCRIPT.md` · `docs/VIVA_NOTES.md` · `docs/FINAL_REPORT.md` · `docs/DEFINITION_OF_DONE.md` · `docs/UI_REDESIGN_PLAN.md`
