# UI polish notes (Phase 18)

Manual review against `UI_GUIDELINES.md`. No `axe-core` or Lighthouse CI dependency was added (D37).

## Responsive (18.1)

- App shell: stacked header; `Open menu` under `md`; sidebar from `md` up.
- Page root clips horizontal overflow; tables and charts scroll inside their containers.
- Auth pages stay a single centred card (`max-w-md`).
- Dashboard stats: one column, then `sm:grid-cols-3`.
- Check at 375 px: no page-level horizontal scroll; table swipe is local.

## Data views (18.2)

Every loaded view uses `Loading` (status + skeletons), `ErrorMessage` / `Alert` for failures, and `EmptyState` for empty sets (including What-If and analysis before first submit).

## Accessibility (18.3)

Checked in RTL (skip link, captions, labels, dialog Escape, tab wrap in `Modal`) and by inspection:

| Rule | Result |
|---|---|
| `html lang="en"` | Pass (`frontend/index.html`) |
| Visible labels via `Field` | Pass |
| Focus ring (`:focus-visible`) | Pass |
| Skip to `#main-content` | Pass |
| Tables have captions | Pass (`SimpleTable` requires `caption`) |
| Charts `role="img"` + `aria-label` | Pass |
| Risk colour + printed level | Pass (`RiskBadge` / `RiskGauge`) |
| Keyboard tabs and modal | Pass |
| Contrast (ink on paper, badge fills) | Pass by token design (WCAG AA intended) |

Critical automated issues: none found in Vitest a11y assertions. Live Lighthouse/axe was not run in this environment.

## Micro-interactions (18.4)

- Risk gauge bar width transitions from the backend score (clamped only for CSS width).
- List/table rows use a short fade-in; `prefers-reduced-motion` disables motion.

## Consistency (18.5)

Shared disclaimer: `RISK_DISCLAIMER` = “Risk indicator, not a prediction.”
Fallback copy stays “this response was generated without the AI”.

---

# Landing-page redesign (UI-01 to UI-08)

Plan and final design: `docs/UI_REDESIGN_PLAN.md`. Detailed per-phase validation:
`.cursor/indexes/PHASE_TRACK.md` under "UI-redesign-phase". Scope was the public
landing page only; no backend, API, auth, risk-engine, student-page or teacher-page
file changed.

| Phase | Date | Changes | Validation | Known issues |
|---|---|---|---|---|
| UI-01 Foundation | 2026-09-19 | `/` renders `LandingPage`; `HomeRedirect` moved to `/home` (D38); `components/landing/` skeleton; `Section`, `Reveal`, `useInView`, `usePrefersReducedMotion` | typecheck; 39 tests; `/`, `/login`, `/home`, `/student` in browser; zero API requests | anchor jumps could skip reveals (resolved by UI-06 re-check) |
| UI-02 Design foundation | 2026-09-19 | Additive `--landing-*` token layer and `landing-*` Tailwind namespace (D39); Source Sans 3 500 and Serif 4 700; type scale; entrance and draw motion primitives | 40 tests; build; contrast computed on every surface (ink-muted 4.8 on paper); reduced motion emulated | weight 500 is a global font change (approved) |
| UI-03 Navigation & hero | 2026-09-19 | Fixed condensing nav with mobile menu; hero grid, copy, role-aware CTAs (`useLandingCta`, D40); `HeroBackdrop`; `HeroAdvisorPanel` on the engine's R3 case reusing `RiskGauge`/`RiskBadge` | 45 tests; 1920 and 375 px in Chrome; menu Escape/focus restore; zero API requests | signed-in CTAs test-only (closed in UI-08) |
| UI-04 Product sections | 2026-09-19 | `TrustStrip`, `ProductPreview` (DOM reconstruction, not screenshots), `FeatureGrid`, `HowItWorks`; every figure checked against the specs | 50 tests; 1440 / 768 / 375 px; console clean | — |
| UI-05 Explainability, CTA, footer | 2026-09-19 | Real weights ruler and four honesty claims; `CtaBand`; `LandingFooter` with both disclaimers | 55 tests; CTA routing; `#features` anchor clears nav | docs repo is private, so no doc links in footer |
| UI-06 Responsive | 2026-09-19 | Hero panel capped `max-w-md` when stacked; footer link `min-w-11`; preview date `whitespace-nowrap` | 375 / 768 / 1024 / 1440 (+320) measured: no overflow, all targets ≥ 44 px, no hover-only content | stacked sparkline stretched ~1.5× |
| UI-07 Motion, a11y, perf | 2026-09-22 | Nav condense transitions `padding` only and snaps under reduced motion; audit of entrance, hero data, ambient and hover motion | 60 tests; build; reduced motion → 0 running animations; 18-stop tab order; contrast 0 failures; CLS 0.0001; 0 long tasks | fonts from network could shift text on slow connections |
| UI-08 Final QA | 2026-09-22 | Docs only: final design record, this log, `UI_GUIDELINES.md` motion list, `ARCHITECTURE.md` tree, `README.md` landing note | 60 frontend tests; 189 backend tests + ruff; typecheck; build; every student and teacher route live with the real backend, both roles' landing CTAs, logout, guards; diff audit since `bba285f` | pre-existing `TrendLineChart` duplicate-key dev warning (see below) |

### UI-08 observations

- Signed-in behaviour was checked live for the first time (the Vite proxy reached
  the backend once the dev server ran outside the sandbox): student landing shows
  one "Go to your dashboard" → `/student`, teacher → `/teacher`; `/home` redirects
  by role; a teacher opening `/student` lands on `/forbidden`; after logout,
  `/student` and `/home` redirect to `/login`.
- 53 API calls across both roles, all 2xx. The landing page issued none.
- The only console output was a React dev warning, "Encountered two children with
  the same key", from `components/charts/TrendLineChart.tsx` (Phase 17), whose
  point key is `${on}-${value}` and repeats when a series has two equal points on
  one date. It appears on the performance and teacher student-detail pages, not on
  the landing page, and is outside the redesign scope, so it was left unchanged.
