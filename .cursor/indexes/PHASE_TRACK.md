# Phase index

Single tracker for completed phases and the current task. Update this file at the end of every task and every phase (see `.cursor/rules/project.mdc`).

**Last updated:** 2026-09-19  
**Current phase:** UI-redesign — next is UI-07 Motion, Accessibility & Performance  
**Current task:** none (UI-06 complete; start UI-07 in a new chat)  
**Latest completed phase:** UI-06 Responsive Design  
**Latest completed task:** UI-06 validation (typecheck + 55 Vitest tests + build + browser audit at 320/375/768/1024/1440, mobile menu, touch targets, hover-only scan, console and zero-request check)  

## Status legend

`[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked

## Phases

| Phase | Name | Status | Completed on | Notes |
|---|---|---|---|---|
| 0 | Planning & Documentation | [x] | 2026-09-19 | 0.1–0.3 done; living-doc fixes C1–C10 |
| 1 | Backend setup | [x] | 2026-09-19 | FastAPI, health, errors, CORS, pytest |
| 2 | Database & seed data | [x] | 2026-09-19 | Models, reset_db, deterministic seed_demo |
| 3 | Authentication & authorization | [x] | 2026-09-19 | JWT, register/login, deps, create_teacher |
| 4 | Academic data APIs | [x] | 2026-09-19 | CRUD, write rule, loader; 4.9 via 12.9 |
| 5 | Risk engine | [x] | 2026-09-19 | R1–R13, GET /risk, 4 seed snapshots |
| 6 | Trends, subject analysis, early warnings | [x] | 2026-09-19 | Slope −5.7; warnings; comparison ≥5 |
| 7 | What-if simulator | [x] | 2026-09-19 | W1 64→80 = −10.0 MEDIUM; no DB writes |
| 8 | AI service (analysis) | [x] | 2026-09-19 | fallback + cache + GET /ai/usage |
| 9 | AI study planner | [x] | 2026-09-19 | hybrid budget + plan_v1 fallback |
| 10 | AI assistant (chat) | [x] | 2026-09-19 | chat_v1 + history + fallback |
| 11 | Interventions & teacher APIs | [x] | 2026-09-19 | 11.1–11.9; AI-4 included |
| 12 | Backend integration, hardening, freeze | [x] | 2026-09-19 | overview, matrix, story, CSV, openapi.json |
| 13 | Frontend foundation | [x] | 2026-09-19 | Vite + React + TS + Tailwind; types from openapi.json |
| 14 | Student pages (functional) | [x] | 2026-09-19 | Dashboard through profile; Recharts; mocked page tests |
| 15 | Teacher pages (functional) | [x] | 2026-09-19 | Dashboard, list/filters, detail, interventions, analytics |
| 16 | Frontend integration & E2E, functional freeze | [x] | 2026-09-19 | Demo checklist; as_of + forbidden fixes; no Playwright |
| 17 | UI design | [x] | 2026-09-19 | UI_GUIDELINES + tokens + shared ui/*; D36 |
| 18 | UI polish | [x] | 2026-09-19 | 18.1–18.5; D37; docs/UI_POLISH.md |
| 19 | Final documentation & demo | [x] | 2026-09-19 | README, demo script, viva, report, screenshots |

## Phase 0 tasks

| Task | Status | Completed on |
|---|---|---|
| 0.1 Repository skeleton and agent rules | [x] | 2026-09-19 |
| 0.2 Split MASTER_DESIGN into the repo documentation set | [x] | 2026-09-19 |
| 0.3 Consistency review | [x] | 2026-09-19 |

## Phase 1 tasks

| Task | Status | Completed on |
|---|---|---|
| 1.1 FastAPI scaffold with health endpoint and settings | [x] | 2026-09-19 |
| 1.2 Error format, logging, CORS | [x] | 2026-09-19 |
| 1.3 pytest config, conftest, health/error/CORS tests, ruff | [x] | 2026-09-19 |
| 1.4 README run instructions | [x] | 2026-09-19 |

## Phase 2 tasks

| Task | Status | Completed on |
|---|---|---|
| 2.1 SQLAlchemy foundation and identity models | [x] | 2026-09-19 |
| 2.2 Academic models | [x] | 2026-09-19 |
| 2.3 RiskAssessment, indexes, reset_db | [x] | 2026-09-19 |
| 2.4 Seed generator core | [x] | 2026-09-19 |
| 2.5 Seed generator data | [x] | 2026-09-19 |
| 2.6 Story/edge students and seed_demo CLI | [x] | 2026-09-19 |
| 2.7 Database tests | [x] | 2026-09-19 |

## Phase 3 tasks

| Task | Status | Completed on |
|---|---|---|
| 3.1 JWT create/decode | [x] | 2026-09-19 |
| 3.2 POST /auth/register | [x] | 2026-09-19 |
| 3.3 POST /auth/login | [x] | 2026-09-19 |
| 3.4 get_current_user, require_role, /me, logout | [x] | 2026-09-19 |
| 3.5 authorize_student_access | [x] | 2026-09-19 |
| 3.6 scripts/create_teacher.py | [x] | 2026-09-19 |
| 3.7 Auth tests | [x] | 2026-09-19 |

## Phase 4 tasks

| Task | Status | Completed on |
|---|---|---|
| 4.1 Subjects CRUD + enrollment endpoints | [x] | 2026-09-19 |
| 4.2 Student profile, study-habits, semester-results | [x] | 2026-09-19 |
| 4.3 Attendance endpoints + computed % | [x] | 2026-09-19 |
| 4.4 Assessment endpoints | [x] | 2026-09-19 |
| 4.5 Teacher write-permission rule | [x] | 2026-09-19 |
| 4.6 Pagination helpers | [x] | 2026-09-19 |
| 4.7 academic_data_loader | [x] | 2026-09-19 |
| 4.8 API and loader tests | [x] | 2026-09-19 |
| 4.9 CSV import | [x] | 2026-09-19 |

## Phase 5 tasks

| Task | Status | Completed on |
|---|---|---|
| 5.1 risk_config.py | [x] | 2026-09-19 |
| 5.2 metrics.py | [x] | 2026-09-19 |
| 5.3 Component normalizers | [x] | 2026-09-19 |
| 5.4 Aggregator / INSUFFICIENT_DATA | [x] | 2026-09-19 |
| 5.5 Classification + floors | [x] | 2026-09-19 |
| 5.6 top_factors, notes, flags | [x] | 2026-09-19 |
| 5.7 risk_service persist | [x] | 2026-09-19 |
| 5.8 GET /risk/{id} and /history | [x] | 2026-09-19 |
| 5.9 R1–R13 + API tests | [x] | 2026-09-19 |
| 5.10 Seed snapshots + profile bands | [x] | 2026-09-19 |

## Phase 6 tasks

| Task | Status | Completed on |
|---|---|---|
| 6.1 trend_engine slope, labels, sudden-change | [x] | 2026-09-19 |
| 6.2 Series builders | [x] | 2026-09-19 |
| 6.3 Subject analysis | [x] | 2026-09-19 |
| 6.4 Early-warning rules | [x] | 2026-09-19 |
| 6.5 Trends/warnings/subjects endpoints | [x] | 2026-09-19 |
| 6.6 Class analytics (Pandas) | [x] | 2026-09-19 |
| 6.7 Comparison endpoint | [x] | 2026-09-19 |
| 6.8 Tests | [x] | 2026-09-19 |

## Phase 7 tasks

| Task | Status | Completed on |
|---|---|---|
| 7.1 Request schema + override bounds | [x] | 2026-09-19 |
| 7.2 simulate() current vs simulated | [x] | 2026-09-19 |
| 7.3 POST /risk/{id}/what-if | [x] | 2026-09-19 |
| 7.4 Tests | [x] | 2026-09-19 |

## Phase 8 tasks

| Task | Status | Completed on |
|---|---|---|
| 8.1 AI config + package skeleton | [x] | 2026-09-19 |
| 8.2 AI client (timeout, retry, taxonomy) | [x] | 2026-09-19 |
| 8.3 context_builder + no-PII | [x] | 2026-09-19 |
| 8.4 Output schemas and grounding validators | [x] | 2026-09-19 |
| 8.5 Prompt analysis_v1 | [x] | 2026-09-19 |
| 8.6 Deterministic fallback | [x] | 2026-09-19 |
| 8.7 AIAdvice model, cache, usage | [x] | 2026-09-19 |
| 8.8 analyze_performance + POST /ai/analysis | [x] | 2026-09-19 |
| 8.9 Tests with fake client | [x] | 2026-09-19 |
| 8.10 scripts/ai_smoke_test.py | [x] | 2026-09-19 |

## Phase 9 tasks

| Task | Status | Completed on |
|---|---|---|
| 9.1 Models StudyPlan + StudyPlanItem | [x] | 2026-09-19 |
| 9.2 Request schema and validation | [x] | 2026-09-19 |
| 9.3 time_budget.allocate | [x] | 2026-09-19 |
| 9.4 Prompt plan_v1 and output schema | [x] | 2026-09-19 |
| 9.5 Plan validator | [x] | 2026-09-19 |
| 9.6 Fallback plan | [x] | 2026-09-19 |
| 9.7 Study plan endpoints | [x] | 2026-09-19 |
| 9.8 Tests | [x] | 2026-09-19 |

## Phase 10 tasks

| Task | Status | Completed on |
|---|---|---|
| 10.1 AIChatMessage model; history GET/DELETE | [x] | 2026-09-19 |
| 10.2 Chat context assembly + length limits | [x] | 2026-09-19 |
| 10.3 Prompt chat_v1 | [x] | 2026-09-19 |
| 10.4 answer_academic_question + POST /ai/chat | [x] | 2026-09-19 |
| 10.5 Daily limit, fallback, canned answers | [x] | 2026-09-19 |
| 10.6 Tests | [x] | 2026-09-19 |

## Phase 11 tasks

| Task | Status | Completed on |
|---|---|---|
| 11.1 Intervention model | [x] | 2026-09-19 |
| 11.2 POST /interventions + baseline | [x] | 2026-09-19 |
| 11.3 List, get, patch + outcome | [x] | 2026-09-19 |
| 11.4 GET progress | [x] | 2026-09-19 |
| 11.5 GET /teacher/dashboard | [x] | 2026-09-19 |
| 11.6 GET /teacher/students filters | [x] | 2026-09-19 |
| 11.7 GET /teacher/subjects/{id}/analytics | [x] | 2026-09-19 |
| 11.8 POST /ai/intervention-suggestions | [x] | 2026-09-19 |
| 11.9 Tests | [x] | 2026-09-19 |

## Phase 12 tasks

| Task | Status | Completed on |
|---|---|---|
| 12.1 GET /students/{id}/overview | [x] | 2026-09-19 |
| 12.2 Authorization matrix test | [x] | 2026-09-19 |
| 12.3 Full-story API test | [x] | 2026-09-19 |
| 12.4 demo_advance.py and demo_flow.py | [x] | 2026-09-19 |
| 12.5 Seed tuning | [x] | 2026-09-19 |
| 12.6 Performance sanity | [x] | 2026-09-19 |
| 12.7 Security checklist | [x] | 2026-09-19 |
| 12.8 Export openapi.json | [x] | 2026-09-19 |
| 12.9 CSV import | [x] | 2026-09-19 |
| 12.10 Docs (tag deferred) | [x] | 2026-09-19 |

## Phase 13 tasks

| Task | Status | Completed on |
|---|---|---|
| 13.1 Vite + React + TypeScript + Tailwind + React Router scaffold | [x] | 2026-09-19 |
| 13.2 Generate TS types from openapi.json | [x] | 2026-09-19 |
| 13.3 API client (token, 401, error shape) | [x] | 2026-09-19 |
| 13.4 Auth context, login/register, guards | [x] | 2026-09-19 |
| 13.5 Layout + role-based nav | [x] | 2026-09-19 |
| 13.6 Shared components | [x] | 2026-09-19 |
| 13.7 Vitest + RTL | [x] | 2026-09-19 |

## Phase 14 tasks

| Task | Status | Completed on |
|---|---|---|
| 14.1 Dashboard from `/students/me/overview` | [x] | 2026-09-19 |
| 14.2 Risk page | [x] | 2026-09-19 |
| 14.3 Performance page (Recharts) | [x] | 2026-09-19 |
| 14.4 Subjects page | [x] | 2026-09-19 |
| 14.5 What-If page | [x] | 2026-09-19 |
| 14.6 AI Advisor page | [x] | 2026-09-19 |
| 14.7 Study Planner page | [x] | 2026-09-19 |
| 14.8 Interventions page | [x] | 2026-09-19 |
| 14.9 Profile + study-habits | [x] | 2026-09-19 |
| 14.10 Tests (What-If, Advisor, Planner) | [x] | 2026-09-19 |

## Phase 15 tasks

| Task | Status | Completed on |
|---|---|---|
| 15.1 Teacher dashboard | [x] | 2026-09-19 |
| 15.2 Student list (filters, pagination, sort) | [x] | 2026-09-19 |
| 15.3 Student detail | [x] | 2026-09-19 |
| 15.4 Create intervention form | [x] | 2026-09-19 |
| 15.5 Intervention tracking | [x] | 2026-09-19 |
| 15.6 Subject analytics | [x] | 2026-09-19 |
| 15.7 Tests (filters + intervention form) | [x] | 2026-09-19 |

## Phase 16 tasks

| Task | Status | Completed on |
|---|---|---|
| 16.1 Manual demo script against the real backend | [x] | 2026-09-19 |
| 16.2 Fix defects; types if API changed | [x] | 2026-09-19 |
| 16.3 AI-off fallbacks | [x] | 2026-09-19 |
| 16.4 Playwright or manual checklist | [x] | 2026-09-19 |
| 16.5 Functional freeze | [x] | 2026-09-19 |

## Phase 17 tasks

| Task | Status | Completed on |
|---|---|---|
| 17.1 Design direction + UI_GUIDELINES.md | [x] | 2026-09-19 |
| 17.2 Tailwind theme | [x] | 2026-09-19 |
| 17.3 Component library | [x] | 2026-09-19 |
| 17.4 App shell and navigation | [x] | 2026-09-19 |
| 17.5 Restyle student pages | [x] | 2026-09-19 |
| 17.6 Restyle teacher pages | [x] | 2026-09-19 |
| 17.7 Chart styling consistency | [x] | 2026-09-19 |

## Phase 18 tasks

| Task | Status | Completed on |
|---|---|---|
| 18.1 Responsive behaviour | [x] | 2026-09-19 |
| 18.2 Loading / empty / error states | [x] | 2026-09-19 |
| 18.3 Accessibility | [x] | 2026-09-19 |
| 18.4 Micro-interactions | [x] | 2026-09-19 |
| 18.5 Consistency audit | [x] | 2026-09-19 |

## Phase 19 tasks

| Task | Status | Completed on |
|---|---|---|
| 19.1 Final README.md | [x] | 2026-09-19 |
| 19.2 docs/DEMO_SCRIPT.md | [x] | 2026-09-19 |
| 19.3 Screenshots + doc verification | [x] | 2026-09-19 |
| 19.4 docs/VIVA_NOTES.md | [x] | 2026-09-19 |
| 19.5 Final report and presentation outline | [x] | 2026-09-19 |
| 19.6 Definition of Done checklist | [x] | 2026-09-19 |

## How to update

1. After each **task**: set that task `[x]`, set **Current task** to the next unchecked task, set **Latest completed task**.
2. After every **phase**: set the phase `[x]`, fill **Completed on**, set **Latest completed phase**, refresh **Current phase**, and also update `CLAUDE_CONTEXT.md` and tick `DEVELOPMENT_PLAN.md`.

---

# UI-redesign-phase

## Overview

Landing-page redesign and UI polish for Student Academic Advisor. Plan: `docs/UI_REDESIGN_PLAN.md`. Rules: `.cursor/rules/ui-redesign.mdc`.

Scope:

- Public landing page
- Visual identity
- Hero
- Product visualization
- Marketing sections
- Responsive behavior
- Motion
- Accessibility
- Performance
- UI documentation

Explicitly excluded:

- Backend changes
- API changes
- Database changes
- Business-logic changes
- Risk-engine changes
- Authentication-mechanics changes

---

## UI-01 — Foundation & Landing Architecture

Status: [x]

Completed on: 2026-09-19

- [x] Landing page architecture created
- [x] Landing components structure created
- [x] Section primitive created
- [x] Reveal primitive created
- [x] useInView created
- [x] usePrefersReducedMotion created
- [x] `/` renders LandingPage
- [x] Existing routes verified
- [x] Existing tests pass
- [x] Phase documented

### Implemented

- `frontend/src/pages/LandingPage.tsx` — skip link, `LandingNav`, `main`, section stack, `LandingFooter`. No auth usage, no API calls.
- `frontend/src/components/landing/` — `Section.tsx`, `Reveal.tsx`, `LandingNav.tsx`, `HeroSection.tsx`, `TrustStrip.tsx`, `ProductPreview.tsx`, `FeatureGrid.tsx`, `HowItWorks.tsx`, `ExplainabilitySection.tsx`, `CtaBand.tsx`, `LandingFooter.tsx`. Sections below the hero are structural placeholders (heading plus one accurate sentence); UI-04/UI-05 fill them in.
- `HeroBackdrop.tsx`, `HeroAdvisorPanel.tsx` and `heroDemoData.ts` were **not** created — nothing needs them until UI-03.
- `frontend/src/lib/useInView.ts`, `frontend/src/lib/usePrefersReducedMotion.ts` — placed beside the existing `lib/useAsync.ts` hook. Both degrade to "visible / no reduced motion" when `IntersectionObserver` or `matchMedia` is missing (jsdom).
- `frontend/src/index.css` — additive `.saa-reveal` / `.saa-reveal-pending` classes plus a reduced-motion override. No existing selector or token was changed.
- `frontend/src/routes/index.tsx` — `/` now renders `LandingPage`; `HomeRedirect` was **not** deleted, it is mounted at the new `/home` route (D38). `*` still redirects to `/`, so unknown URLs now land on the landing page instead of the role redirect.
- Tests added: `frontend/src/pages/LandingPage.test.tsx` (single h1, zero fetch calls, CTA targets, section anchors) and three cases in `frontend/src/routes/AppRoutes.test.tsx` (`/` renders landing with no fetch, `/home` role redirect signed in and signed out).

### Validation

Node 26.9.0 was installed via Homebrew for this phase (D33 previously recorded that no Node was on PATH).

- `npm run typecheck` (`tsc --noEmit`) — passed, no errors.
- `npm test` (`vitest run`) — 20 files, 39 tests passed, including the 4 new `LandingPage` tests and 8 `AppRoutes` tests.
- Browser check against `npm run dev` (Vite 6.4.3, `http://localhost:5173`):
  - `/` renders the landing page; exactly one `h1`; `document.scrollWidth === clientWidth` (no horizontal overflow).
  - No backend request is issued from `/` — `performance.getEntriesByType("resource")` contains only Vite dev module URLs.
  - `/login` renders; `/register` reachable from it.
  - `/home` redirects a signed-out visitor to `/login`.
  - `/student` (protected) still redirects a signed-out visitor to `/login`.
  - Reveal behaviour: the hero fades in on load; sections below the fold reveal on scroll and re-reveal correctly when scrolled back into view.

### Known issues / blockers

- The hero is briefly at `opacity: 0` while its entrance transition runs, so a screenshot taken within ~500 ms of load catches a blank hero. UI-03/UI-07 own the final entrance sequence.
- Sections skipped by an instant jump (anchor link, Cmd+End) stay hidden while they are off-screen above the viewport; they fade in normally when scrolled back into view. Acceptable for now, revisit in UI-07 if it looks wrong.
- Backend, `frontend/src/api/`, `frontend/src/auth/`, `frontend/src/types/api.ts`, student pages and teacher pages were not modified.

---

## UI-02 — Landing Design Foundation

Status: [x]

Completed on: 2026-09-19

- [x] Landing typography established
- [x] Landing visual tokens established
- [x] Paper/canvas/surface hierarchy established
- [x] Accent system established
- [x] Landing shadows/radii established
- [x] Initial motion primitives established
- [x] Contrast checked
- [x] Existing UI regression checked
- [x] Phase documented

### Implemented

**Token layer (D39).** Landing tokens are a second, additive layer. Values live as
`--landing-*` custom properties on `:root` in `frontend/src/index.css`; colours are
rgb channel triples so Tailwind alpha modifiers work. `frontend/tailwind.config.js`
exposes them as a `landing-*` namespace (`bg-landing-canvas`, `text-landing-ink-muted`,
`shadow-landing-panel`, `rounded-landing-md`, `duration-landing-fast`, `ease-landing`).
**No Phase 17 token was redefined**, so nothing in the app shell moved.

- Surfaces: `paper` `#F4F0E6` → `canvas` `#FAF6EC` → `surface` `#FFFCF7` → `raised` `#FFFFFF`.
- Rules: `rule-faint` `#E6DFCF` (engraved grid) → `rule` `#D7D0C3` (hairline) → `rule-strong` `#BDB3A0` (measurement ticks).
- Ink: `ink` `#122033` (headings) → `ink-body` `#2A3A4D` (copy) → `ink-muted` `#5C6B7A` (labels, eyebrows).
- Accent: `accent` `#1F4E79`, `accent-hover` `#163A5A`, `accent-soft` `#E8F0F7`, `accent-ink` `#FFFCF7` (text on accent).
- Shadows `--landing-shadow-card / -panel / -nav`; radii `sm .375rem`, `md .625rem`, `lg .875rem`, `xl 1.25rem`.

**Typography.** `frontend/index.html` now requests Source Sans 3 400/500/600 and
Source Serif 4 600/700. Landing heading weights (h1/h2 at 700) are scoped under a
`.saa-landing` class on the landing root so dashboards keep serif 600. Type-scale
classes: `.saa-display`, `.saa-headline`, `.saa-subhead`, `.saa-lede`, `.saa-eyebrow`,
`.saa-label`, `.saa-metric`. The last three use `--landing-font-mono` (system mono)
for metrics, labels, dates and numeric readouts.

**Motion.** `.saa-landing-enter` (load-driven, staggerable via `--saa-enter-delay`)
and `.saa-landing-draw` (SVG path draw-on, via `--saa-draw-length`), plus keyframes
`saa-landing-rise` and `saa-landing-draw-kf`. `.saa-reveal` now reads the shared
`--landing-duration-base` / `--landing-ease` instead of hardcoded `500ms ease-out`.
The reduced-motion overrides for the two new classes sit inside `@layer components`
so they are emitted or purged together with the rules they override — otherwise
Tailwind shipped the `animation: none` override while purging the animation itself.

`HeroSection` now enters with `.saa-landing-enter` instead of the scroll-driven
`Reveal`, because it is above the fold. This resolves the UI-01 known issue where a
screenshot within ~500 ms of load caught a blank hero. The full six-step stagger
stays with UI-03.

**Applied to existing placeholders** as a class swap only — no layout, structure or
copy changed: `LandingPage`, `Section`, `LandingNav`, `HeroSection`, `TrustStrip`,
`ProductPreview`, `FeatureGrid`, `HowItWorks`, `ExplainabilitySection`, `CtaBand`,
`LandingFooter`.

### Validation

- `npm run typecheck` — passed.
- `npm test` — 20 files, 40 tests passed (one new test asserts the `.saa-landing` scope class is present).
- `npm run build` — passed; inspected `dist/assets/*.css` to confirm the `landing-*` utilities, the type-scale classes and both motion rules are emitted.
- Contrast computed against every landing surface. On the worst background (`paper`): `ink` 14.4, `ink-body` 10.2, `ink-muted` 4.8, `accent` 7.6 — all WCAG AA for normal text. `accent-ink` on `accent` is 8.5.
- Browser, `http://localhost:5175`: CTA resolves to `rgb(31,78,121)` on `rgb(255,252,247)` at 10 px radius; hero h1 is Source Serif 4 700 at 44 px; eyebrow is `ui-monospace` at 0.2 em tracking; section bands alternate paper/canvas correctly; `scrollWidth === clientWidth`.
- Zero API requests from `/` — the only non-Vite resource is the Google Fonts stylesheet.
- Reduced motion (`Emulation.setEmulatedMedia`): hero `animation-name: none`, opacity 1, no transform; all 5 `.saa-reveal` nodes visible with `0s` transitions. With motion on, `saa-landing-rise` runs for 420 ms with the landing easing and finishes at opacity 1.
- Regression check on `/login`: `.saa-landing` is absent, h1 is still serif 600 at `-0.02em`. Buttons and field labels now compute to weight 500.

### Known issues / blockers

- **Intended global change:** Source Sans 3 500 is now loaded, so every `font-medium` element across the app (`Button`, `Badge`, `Field` labels, `Tabs`, `EmptyState`) renders at true 500 instead of falling back to 400. Approved before implementing. Text metrics shift very slightly; no layout breakage seen on `/login`.
- `.saa-metric` and `.saa-landing-draw` are defined but not yet used, so Tailwind purges them from the bundle. They will be emitted as soon as UI-03 references them. Not a defect.
- Tailwind config changes need a dev-server restart; a server started before the config edit serves stale CSS and the `landing-*` utilities silently do nothing.
- Backend, `frontend/src/api/`, `frontend/src/auth/`, `frontend/src/types/api.ts`, student pages and teacher pages were not modified.

---

## UI-03 — Navigation & Hero

Status: [x]

Completed on: 2026-09-19

- [x] Landing navigation implemented
- [x] Mobile navigation implemented
- [x] Hero composition implemented
- [x] Hero typography implemented
- [x] Hero CTAs implemented
- [x] HeroBackdrop implemented
- [x] HeroAdvisorPanel implemented
- [x] RiskGauge reused
- [x] RiskBadge reused
- [x] Sparkline implemented
- [x] Factor rows implemented
- [x] AI insight card implemented
- [x] Example data clearly labelled
- [x] Hero makes zero API requests
- [x] Initial hero animation implemented
- [x] Phase documented

### Implemented

**Navigation** (`LandingNav.tsx`). Fixed bar, transparent over the hero, condensing
onto `landing-paper/90` with `backdrop-blur-sm` + `shadow-landing-nav` + a hairline
rule past 8 px of scroll (`CONDENSE_AT_PX`), inner padding dropping `py-4` → `py-2.5`.
Wordmark with
an inline SVG trend mark, three section anchors (`#product`, `#how-it-works`,
`#explainability`), and the auth pair. The mobile panel is **always mounted** and
toggled with the `hidden` attribute, so `aria-controls="landing-menu"` always
resolves and the links stay out of the tab order while closed. Escape closes it and
returns focus to the toggle. All controls are at least 44 px tall.

**Hero** (`HeroSection.tsx`). Asymmetric 7/5 grid at `lg`, stacked below it, with the
copy column centred against the taller panel from `lg`. Eyebrow "Python computes. AI
explains.", the two-tone `h1` (second clause in `landing-ink-muted`), the supporting
paragraph, the CTAs, then the shared `RISK_DISCLAIMER` line. `HeroBackdrop.tsx` is
the decorative layer: a 32 px engraved grid in `rule-faint` under one soft light
pool, radially masked so no edge reads as a hard line, mounted through the new
`backdrop` prop on `Section`. The hero uses `pt-28 sm:pt-32 lg:pt-36` to clear the
fixed bar.

**CTAs** (`useLandingCta.ts`). Reads the existing `useAuth()` only — no new auth
logic, no request. Signed out shows "Get started" (`/register`) and "Log in"
(`/login`); signed in collapses both to "Go to your dashboard", routed to `/teacher`
for teachers and `/student` otherwise. `LandingNav` uses the same hook, so the header
does not offer sign-up to someone already signed in — slightly beyond the written
UI-03 scope, which named only the hero; recorded in D40.

**Advisor panel** (`HeroAdvisorPanel.tsx` + `heroDemoData.ts`). A `<figure>` whose
`<figcaption>` reads "Example data · not a real student". It reuses the existing
`RiskGauge` (which renders `RiskBadge` internally) and adds a hand-rolled SVG
attendance sparkline, three contributing-factor rows with proportional bars, and the
AI explanation card. Every number is the risk engine's own worked R3 case from
`RISK_ENGINE_SPEC.md` 6.8 — score 67.1 HIGH, completeness 1.00, attendance 64.0%
declining at −4.4 pts/week, contributions 18.8 / 16.3 / 13.1 (`weight × risk` under
`round1` half-up) — and the factor notes copy the engine's note templates verbatim
("Attendance is 64.0%, below the 75% cutoff.", "Internal marks are 45.0%.", "Quiz
average is 40.0%."), so nothing on the page is a number the product could not really
produce. The six weekly readings `74, 71, 67, 62, 58, 52` have mean 64 (the overall
figure) and deliberately stay clear of a `SUDDEN_DROP`: the last value is 14.4 below
the mean of the previous five, under the 15-point rule.

**Entrance sequence.** Five `.saa-landing-enter` steps staggered with
`--saa-enter-delay` — eyebrow 0 ms, headline 80, supporting copy 160, CTAs 240,
panel 320 — then the sparkline draws at 560 ms with `.saa-landing-draw`. The polyline
sets `pathLength={1}` so the `--saa-draw-length` default of 1 draws it fully. No
ambient motion yet; that stays with UI-07.

No new dependency was added, and `index.css` needed no change — UI-02 had already
shipped both motion primitives. `Section.tsx` gained a `backdrop` prop and
`scroll-mt-24` so anchor targets clear the fixed nav; no other shared component
changed.

### Validation

- `npm run typecheck` — passed.
- `npm test` — 20 files, 45 tests passed, including 10 `LandingPage` tests (single
  h1, zero fetch, CTA targets, anchors, example-data label, demo risk/trend/factor
  values, mobile menu open/Escape/focus restore, signed-in student and teacher CTAs).
- `npm run build` — passed.
- Browser (Chrome via CDP) against `npm run dev` on `http://localhost:5180`:
  - 1920×1080 @2x: hero is a real 12-column split (panel at x≈1075), exactly one `h1` at 64 px Source Serif 4, hero CTA 44 px tall.
  - Scroll condensing measured: at the top the header is `rgba(0, 0, 0, 0)` with 16 px padding; scrolled it is `rgba(244, 240, 230, 0.9)` with `blur(4px)`, the rule border and 10 px padding.
  - 375×812 emulated: single column, hamburger menu, stacked full-width CTAs, `scrollWidth - clientWidth === 0`, toggle 58×44 px and hero CTA 105×44 px.
  - Mobile menu opens, Escape closes it, `aria-expanded` returns to `"false"`, and `document.activeElement` is the toggle — focus restoration confirmed in-browser.
  - Zero API requests: of 85 resources the only non-Vite entry is the Google Fonts stylesheet. Nothing reaches `localhost:8000`, and no `/auth/me` fires (a signed-out visitor has no token, so `AuthProvider` never calls it). No Vite error overlay.
  - Console: with `console.error` / `console.warn` / `error` / `unhandledrejection` collectors installed and the landing tree remounted client-side (`/` → `/login` → `/`), nothing was reported. This covers remount, not the very first page load.
  - Reduced motion (`Emulation.setEmulatedMedia`): all five `.saa-landing-enter` nodes report `animation-name: none`, opacity 1, no transform, and the sparkline reports `animation-name: none`, `stroke-dasharray: none`, `stroke-dashoffset: 0px`, so the final state is visible and nothing animates.
  - Motion on, measured: the stagger is 0 / 0.08 / 0.16 / 0.24 / 0.32 s at 0.42 s each, and the draw is delayed 0.56 s over 0.72 s, all on the landing easing curve.
  - `/login` still renders with its own `h1` and form.
- `git status` on `backend/`, `frontend/src/api/`, `frontend/src/auth/`, `frontend/src/types/`, `frontend/src/pages/student/`, `frontend/src/pages/teacher/` and `openapi.json` — all clean.

### Known issues / blockers

- Signed-in CTA routing was verified by test only. The live check was attempted with the backend running, but the sandboxed Vite dev server could not reach it through the `/api` proxy (the proxy returned 500 and the backend log recorded no request), so the browser stayed signed out. Both roles are covered by automated tests.
- The 75% attendance cutoff is **not** drawn as a reference line in the sparkline. The series peaks at 74%, one point under the cutoff, so at this size the dashed line landed within ~1 px of the trend line's start and read as noise rather than as a reference. The cutoff is stated in the attendance factor note and in the sparkline's `aria-label` instead.
- At 375 px the panel's "As of 13 Mar 2026" label wraps onto two lines because of the mono letter-spacing. Cosmetic; UI-06 owns the responsive pass.
- The stale-CSS trap recorded in UI-02 bit again and is worth repeating: a dev server started before the UI-02 `tailwind.config.js` edit serves CSS with **no** `landing-*` utilities, which renders the hero unstyled while still looking plausible, because base `index.css` supplies the paper background and ink colours. Confirm the CTA's accent fill resolves before judging a landing screenshot.
- A screenshot taken within ~1 s of load still catches the stagger mid-flight, so the hero looks blank. Expected; wait for the sequence to finish before capturing.
- `CtaBand` and `LandingFooter` touch targets were not audited — those sections are UI-05 placeholders and out of UI-03's scope.
- **Scope note:** UI-03's own validation numbers above (45 tests) were taken before UI-04 material appeared in the working tree. `TrustStrip`, `ProductPreview`, `FeatureGrid`, `HowItWorks`, `productPreviewData.ts` and five "product sections" tests were written concurrently by another process, not by the UI-03 work, and take the suite to 50 tests. UI-04 remains `[ ]` and that work has **not** been reviewed or validated as part of this phase; it is awaiting a decision (keep and validate in a UI-04 chat, or revert to the UI-01 placeholders).
- Backend, `frontend/src/api/`, `frontend/src/auth/`, `frontend/src/types/api.ts`, student pages and teacher pages were not modified.

---

## UI-04 — Core Product Sections

Status: [x]

Completed on: 2026-09-19

- [x] TrustStrip implemented
- [x] ProductPreview implemented
- [x] FeatureGrid implemented
- [x] HowItWorks implemented
- [x] Responsive section structure implemented
- [x] Product claims verified against project documentation
- [x] No unnecessary API usage
- [x] Phase documented

### Implemented

**TrustStrip.** Four measured product facts instead of fake logos, each a mono
figure over a hairline rule with a label and one sentence: the deterministic
0&ndash;100 score, the six weighted factors, **zero** AI calls to produce a score,
and the two roles. Four columns at `lg`, two at `sm`, one on mobile.

**ProductPreview.** A `<figure>` holding a static reconstruction of the student
dashboard: app header with the as-of date, the navigation rail from
`components/Layout.tsx` (decorative, `aria-hidden`, `lg` and up), then the real
page composition &mdash; risk gauge, overall and attendance trend cards,
completeness line, top factors and warnings. It **reuses the existing
`RiskGauge`**, so the gauge on the landing page is the component the app ships.
Three numbered accent markers sit on the risk, trend and top-factor cards and
resolve to a three-item callout list under the frame. Caption: "Student dashboard
layout &middot; example data, not a live account".

**FeatureGrid.** The six capability areas from the plan, each with a mono index,
an `h3`, a concrete description and a mono detail line quoting a real threshold.
Three columns at `lg`, two at `sm`, one on mobile.

**HowItWorks.** Three stages as an `<ol>`: data is recorded, Python computes, AI
explains. A hairline rule with an accent tick switches from the left edge
(vertical timeline, mobile) to the top edge (horizontal progression) at `md`.

**Claim verification.** Every figure on these sections was checked against the
documentation before it was written: weights and the 0&ndash;100 normalisation
from `RISK_ENGINE_SPEC.md` 6.2&ndash;6.3, the what-if line from the worked W1 case
(6.8, attendance 64 &rarr; 80 = &minus;10.0, HIGH &rarr; MEDIUM), slope and
sudden-change thresholds from 7.1, subject bands from 7.2, the 5-student
comparison floor from 7.4, the AI/fallback and grounding claims from
`AI_GUIDELINES.md` 5.2&ndash;5.5, and the recording/role split from
`PROJECT_SPEC.md` (D3, D5).

**New data file** `productPreviewData.ts` reuses `heroDemoData` (the engine's R3
case) so the hero and the preview describe one example student. The overall trend
is the trend engine's own worked series (72, 69, 63, 55 &rarr; slope &minus;5.7);
the attendance slope &minus;4.4 is the least-squares slope of the hero's six
weekly readings; both warning strings are the templates from
`engines/warnings.py` with values derived from those readings (previous weeks
72.5%, recent four weeks 59.8%, a 12.7 pp drop, so WARNING and not CRITICAL).

No new dependency, no asset file and no change to any shared component. The only
edit outside `components/landing/` and the landing test is `aria-labelledby` plus
a `figcaption` id on the hero panel, because two figures now exist on the page
and each needs its own accessible name.

### Validation

- `npm run typecheck` &mdash; passed.
- `npm test` &mdash; 20 files, **50 tests** passed (45 before), including 5 new
  `LandingPage` cases: trust-strip facts, the preview caption plus the reused
  gauge and the warning string, the three callouts, the six capability headings
  with the real weight line, and the three stages in order.
- `npm run build` &mdash; passed; the marker and preview utilities are present in
  `dist/assets/*.css`.
- Browser, Chrome against `npm run dev` on a **freshly started** server:
  - 1440 px: trust strip 4 columns, preview stat cards 3, callouts 3, features 3,
    stages 3, navigation rail visible, `scrollWidth === clientWidth`, one `h1`.
  - 768 px: trust 2 columns, features 2, stages still horizontal, rail hidden, no
    overflow.
  - 375 px: everything single column, the stage rule switches to the left edge
    (`border-left: 1px`, `border-top: 0`), no horizontal overflow.
  - Zero API requests: the only non-Vite resources are the Google Fonts
    stylesheet and two font files. No failed requests.
  - Console clean: a recorder installed before load captured no errors, no
    warnings, no uncaught exceptions and no unhandled rejections, and there is no
    Vite error overlay.
  - Reduced motion (`Emulation.setEmulatedMedia`): all nine `.saa-reveal` nodes
    report opacity 1, so every new section is fully visible.
  - `/login` still renders its own `h1` and form.
- `git status` on `backend/`, `frontend/src/api/`, `frontend/src/auth/`,
  `frontend/src/types/`, `frontend/src/pages/student/`,
  `frontend/src/pages/teacher/` and `openapi.json` &mdash; all clean.

### Known issues / blockers

- **Deviation:** the plan suggested building the preview from the screenshots in
  `docs/screenshots/`. Those are 1024-px-wide viewport captures cropped
  mid-content (the right-hand card is cut off and the as-of field is empty), so
  they would have shipped a broken-looking image and a stale asset. The preview
  is composed in the DOM from the same components and figures instead, which also
  keeps it responsive and adds no asset to the bundle.
- The scroll-triggered reveal could **not** be re-verified in this run: the
  automation tab produces no animation frames (`requestAnimationFrame` never
  fires), so `IntersectionObserver` never reports intersection and every
  `.saa-reveal` stays at opacity 0 regardless of scrolling. The layout was
  verified under emulated reduced motion, where `Reveal` skips the pending state.
  Worth one manual scroll in UI-06/UI-07.
- A dev server that was already running before these files were created serves
  stale Tailwind CSS: the new utilities silently do nothing (markers rendered
  without their accent square). The production build contains them. Restart the
  dev server after adding a file to `components/landing/`.
- `HowItWorks` keeps three columns at 768 px, which is 213 px per stage. Readable
  but tight; UI-06 owns the decision to drop to two rows there.
- The new sections contain no interactive elements, so there was nothing to check
  for touch-target size or hover-only behaviour.

---

## UI-05 — Explainability, CTA & Footer

Status: [x]

Completed on: 2026-09-19

- [x] ExplainabilitySection implemented
- [x] Real risk weights represented accurately
- [x] Risk disclaimer included
- [x] CTA section implemented
- [x] Footer implemented
- [x] Synthetic-data disclaimer included
- [x] CTA routing verified
- [x] Phase documented

### Implemented

**ExplainabilitySection.** The `h2` is the shared `RISK_DISCLAIMER` constant
("Risk indicator, not a prediction."), so the page and the dashboards state the
limitation in identical words. Below it, a two-column block at `lg`: on the left
a decorative weight ruler — one bar split into six segments sized by
`flexGrow: weight * 100`, in descending accent tints — over the six components
as a hairline-divided list carrying the real numbers (attendance 0.25, internal
0.25, assignments 0.15, quizzes 0.15, previous 0.10, study habits 0.10, summing
to 1.00), each with the normalisation range from `RISK_ENGINE_SPEC.md` 6.2
(attendance 90/50, marks 75/35, assignments half submission rate and half marks,
study habits 2 h/day and confidence 1–5). The ruler is `aria-hidden` because the
list carries the same figures.

On the right, the four things the section must not overstate, from 6.6: the
weights are expert-chosen heuristics validated to sum to 1.00 at import and were
not learned from data; only components with records are counted and renormalised,
under 0.40 of total weight there is no score at all (INSUFFICIENT_DATA) and every
result carries its completeness; risk, trends and what-if make no AI call and AI
text is checked against the computed figures; the attendance-75% and
internal-40% floors move the level and never the score, and self-reported study
habits can never trigger one.

**CtaBand.** Now a raised panel (`bg-landing-surface`, hairline, card shadow) on
the paper band: eyebrow, the `h2` that names the section, one sentence about
partial data, then the actions. It reads `useLandingCta` like the hero and the
nav, so a signed-in visitor sees a single "Go to your dashboard" routed by role
instead of being asked to sign up. Mono support line: "No AI key needed · scores
compute without it". Actions stack on mobile, sit right-aligned beside the copy
from `lg`.

**LandingFooter.** Brand block (wordmark plus one sentence) on the left, two link
groups right-aligned from `md`: Product (the four section anchors, including
`#features`, which nothing linked to before) and Account (log in and create an
account, collapsing to the dashboard link when signed in). Under a hairline, the
synthetic-data disclaimer and the risk disclaimer. Every footer link is a 44 px
target.

Only these three landing components and the landing test changed. No shared
component, style, token or dependency was touched.

### Validation

- `npm run typecheck` — passed.
- `npm test` — 20 files, **55 tests** passed (50 before), including 5 new
  `LandingPage` cases: the six weights and "Sum 1.00", the three honesty claims,
  the final CTA routing to `/register` and `/login`, the four footer anchors plus
  both account links, and both footer disclaimers.
- `npm run build` — passed; all six `bg-landing-accent/*` tints are emitted in
  `dist/assets/*.css`.
- Browser, Chrome against a **freshly started** `npm run dev`:
  - 1440 px: two-column explainability with the ruler segments in weight order,
    CTA panel with the actions beside the copy, footer brand left / links right,
    `scrollWidth === clientWidth`, one `h1`.
  - 375 px: everything single column, ruler intact, CTA buttons stacked and
    44 px tall, footer links 44 px, no horizontal overflow.
  - CTA routing: the footer "Log in" link routes client-side to `/login`, which
    renders its own `h1` and form; `history.back()` returns to `/` with the hero
    `h1` and both figures intact.
  - Footer anchor: `#features` lands 96 px from the top against a 77 px header,
    so `scroll-mt-24` clears the fixed nav.
  - Zero API requests: the only non-Vite resource is the Google Fonts
    stylesheet; nothing reaches `localhost:8000`.
  - Console: with `console.error` / `console.warn` / `error` /
    `unhandledrejection` collectors installed and the landing tree remounted
    (`/` → `/login` → `/`), nothing was reported. No Vite error overlay.
  - Reduced motion (`Emulation.setEmulatedMedia`): all ten `.saa-reveal` nodes
    report opacity 1, so the three new sections are fully visible.
- `git status` on `backend/`, `frontend/src/api/`, `frontend/src/auth/`,
  `frontend/src/types/`, `frontend/src/pages/student/`,
  `frontend/src/pages/teacher/` and `openapi.json` — all clean.

### Known issues / blockers

- **Deviation:** the plan asks for "project documentation links where
  appropriate" in the footer. The repository (`PrinceKumar101/student-academic-advisor`)
  answers 404 unauthenticated, so it is private or missing, and the docs are not
  published anywhere else. Linking `RISK_ENGINE_SPEC.md` or `API_SPEC.md` would
  ship dead links, so the footer carries product anchors and account routes only.
  Revisit if the repository is made public.
- Signed-in CTA and footer state are covered by automated tests only; the live
  browser check is still blocked by the UI-03 issue where the sandboxed dev
  server cannot reach the backend through the `/api` proxy.
- One full-suite run recorded a flaky timeout in the pre-existing
  `TeacherStudentsPage` test while the dev server was running. It passes alone
  and the clean run is 55/55; unrelated to this phase.
- Reveal animation on scroll still cannot be observed in the automation tab
  (`requestAnimationFrame` never fires, so `IntersectionObserver` never reports
  intersection). Layout was verified under emulated reduced motion, as in UI-04.
  Still worth one manual scroll in UI-06/UI-07.
- The CTA and footer are the last untested sections for hover-only behaviour;
  both use colour-change hovers only, and every control is reachable by keyboard
  with the global `:focus-visible` ring.

---

## UI-06 — Responsive Design

Status: [x]

Completed on: 2026-09-19

- [x] 375px verified
- [x] 768px verified
- [x] 1024px verified
- [x] 1440px verified
- [x] Hero recomposes rather than simply shrinking
- [x] Mobile navigation verified
- [x] Touch targets verified
- [x] No horizontal overflow
- [x] No hover-only functionality
- [x] Phase documented

### Implemented

This was an audit phase, so most of it was measurement. Three defects were found
and fixed; everything else was confirmed as already correct.

**Hero panel is capped when the hero stacks** (`HeroSection.tsx`). Below `lg` the
panel column ran the full content width, so at 768 px the advisor panel was
720 px wide: the sparkline's `viewBox` is 264 units and it is drawn with
`preserveAspectRatio="none"`, so a 2.7× horizontal stretch flattened a −4.4
pts/week decline into a nearly level line, and the AI paragraph ran past 80
characters a line. The column is now `mx-auto w-full max-w-md lg:col-span-5
lg:mx-0 lg:max-w-none`, so the stacked panel is 448 px (1.7× stretch, close to
the 1.45× it already has at `lg`) and centred. Desktop is unchanged: 437 px at
1440, 383 px at 1024.

**Footer link touch targets** (`LandingFooter.tsx`). The links are `inline-flex`
with no horizontal padding, so their hit box is exactly the text width. "Log in"
was 35 × 44 — the only control on the page under 44 px in either axis. Added
`min-w-11`; the text still sits left, the hit box now starts at 44 px.

**Preview as-of date** (`ProductPreview.tsx`). At 375 px the mono letter-spacing
broke "As of 13 Mar 2026" after "Mar". `whitespace-nowrap` keeps the date whole
and lets the wordmark beside it wrap instead, which reads as intended app chrome.

**Decisions taken, no change made:**

- `HowItWorks` keeps three columns at 768 px (the open question from UI-04). Each
  stage is 213 px, about 30 characters a line, and screenshotting it at 768 shows
  it reads cleanly. The horizontal progression is the point of the section, so it
  is kept until `md` drops out at 767 px, where the vertical timeline takes over.
- The hero backdrop's light-pool div is wider than the viewport at every width
  below 1440. It sits inside `overflow-hidden` and never contributes to document
  scroll width, so it is expected, not overflow.

### Validation

Chrome via CDP against a freshly started `npm run dev` on `http://localhost:5173`,
using `Emulation.setDeviceMetricsOverride` at each width. Columns are read from
computed `grid-template-columns`; overflow is `scrollWidth - clientWidth` plus a
sweep of every element in `header`, `main` and `footer` for a box crossing the
viewport edge.

| Width | Overflow | Hero | Nav | Trust | Features | Stages | Preview cards | Explainability | Footer | Targets < 44px |
|---|---|---|---|---|---|---|---|---|---|---|
| 375 (×2, mobile) | 0 | stacked, panel 327 | hamburger | 1 | 1 | 1, rule on left | 1, rail hidden | 1 | 1 | none |
| 768 (×2, mobile) | 0 | stacked, panel 448 centred | inline links | 2 | 2 | 3, rule on top | 2, rail hidden | 1 | 12 | none |
| 1024 | 0 | 7/5 split, panel 383 | inline links | 4 | 3 | 3 | 3, rail shown | 12 | 12 | none |
| 1440 | 0 | 7/5 split, panel 437 | inline links | 4 | 3 | 3 | 3, rail shown | 12 | 12 | none |

Also checked 320 px (below the required range): no overflow, everything single
column, h1 at 40 px over four lines.

- H1 sizes: 40 px at 375/320, 41.5 px at 768, 55.3 px at 1024, 64 px at 1440 —
  two lines from 768 up, three at 375.
- Hero CTAs at 375: both 327 × 44, stacked full width.
- Mobile menu at 375: toggle 58 × 44, all five entries 327 × 44, no overflow while
  open, Escape closes it, `aria-expanded` returns to `"false"` and focus returns
  to the toggle. Following "How it works" from the open menu closes the menu and
  lands the section at y = 96 against a 65 px header, so `scroll-mt-24` clears it.
- Landscape phone (667 × 375): the open menu ends at 353 px against a 375 px
  viewport, so all five entries stay reachable without scrolling.
- Skip link: `:focus` does not match in a background automation tab
  (`document.hasFocus()` is false), so it was measured with
  `CSS.forcePseudoState`. Focused it is 170 × 44 at (16, 16) on
  `rgb(255,252,247)` — a real target, not the 1 × 1 `sr-only` box.
- Hover-only content: every `:hover` rule in the loaded stylesheets that touches
  `display`, `visibility`, `opacity` or a transform was enumerated. Six matched,
  all of them colour changes (`hover:bg-landing-accent-hover`,
  `hover:text-landing-accent`, `hover:border-landing-rule-strong`, and three
  Phase 17 app utilities). Nothing is revealed on hover, so nothing needs a mouse.
- Scroll reveals, on a fresh load at 375: scrolling the full 9.8k px in 400 px
  steps brought **all ten** `.saa-reveal` nodes to opacity 1. This closes the
  UI-04/UI-05 known issue where the automation tab produced no animation frames
  and `IntersectionObserver` never fired.
- Console during that scroll-through: `console.error`, `console.warn`, `error`
  and `unhandledrejection` collectors reported nothing. No Vite error overlay.
- Network on a fresh load: 88 resources, no failures, and the only non-Vite
  entries are the Google Fonts stylesheet and two woff2 files. Nothing reaches
  `localhost:8000`.
- `npm run typecheck` — passed.
- `npm test` — 20 files, 55 tests passed (unchanged; the fixes are layout-only and
  jsdom has no layout to assert against).
- `npm run build` — passed; `min-w-11`, `max-w-md`, `lg:max-w-none` and
  `whitespace-nowrap` are all present in `dist/assets/*.css`.
- `git status` on `backend/`, `frontend/src/api/`, `frontend/src/auth/`,
  `frontend/src/types/`, `frontend/src/pages/student/`,
  `frontend/src/pages/teacher/` and `openapi.json` — all clean.

### Known issues / blockers

- The stacked sparkline is still stretched 1.7× horizontally at 448 px. The trend
  reads as a decline, but it is shallower than the same data looks on the risk
  page. Fixing it properly means measuring the rendered width and rebuilding the
  points, which is more machinery than this phase needs; UI-07 owns the hero data
  animation and can revisit it.
- The landscape-phone menu clears the viewport by 22 px. Another entry, or a
  larger default font size, would push the last link off-screen with no way to
  scroll to it, because the menu is not itself scrollable.
- Signed-in layouts were measured signed out only. The signed-in variants are
  narrower (one "Go to your dashboard" button in place of two), so they cannot
  overflow where the signed-out ones do not, and they are covered by tests. The
  live check is still blocked by the UI-03 issue where the sandboxed dev server
  cannot reach the backend through the `/api` proxy.
- Some of this phase's fixes were started in an earlier session that stopped
  before recording anything; `HeroAdvisorPanel`'s stacked label pair and the
  factor notes hidden below `sm` come from that work and were re-verified here.

---

## UI-07 — Motion, Accessibility & Performance

Status: [ ]

- [ ] Entrance animations refined
- [ ] Hero data animation refined
- [ ] Ambient motion implemented/refined
- [ ] Hover interactions refined
- [ ] Reduced-motion behavior verified
- [ ] Keyboard traversal verified
- [ ] Focus states verified
- [ ] Contrast verified
- [ ] Screen-reader semantics verified
- [ ] Console checked
- [ ] Performance checked
- [ ] Landing page makes zero API requests
- [ ] Phase documented

---

## UI-08 — Final QA & Documentation

Status: [ ]

- [ ] Full test suite passes
- [ ] Typecheck passes
- [ ] Production build passes
- [ ] All relevant routes verified
- [ ] Git diff audited
- [ ] Backend unchanged
- [ ] API unchanged
- [ ] Business logic unchanged
- [ ] Risk engine unchanged
- [ ] Authentication mechanics unchanged
- [ ] UI_REDESIGN_PLAN.md updated
- [ ] UI_POLISH.md updated
- [ ] UI_GUIDELINES.md updated if required
- [ ] ARCHITECTURE.md updated if required
- [ ] README.md updated if required
- [ ] Final screenshots/visual verification completed
- [ ] Final UI redesign marked complete

---

## UI REDESIGN COMPLETION

Status: [ ]

Completion date:

Final validation:

- Tests:
- Typecheck:
- Build:
- Responsive:
- Accessibility:
- Performance:
- Git diff audit:

Known remaining issues:

-
-
-
