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
