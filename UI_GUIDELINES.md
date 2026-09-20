# UI_GUIDELINES: Student Academic Advisor

Phase 17 design system. The frontend **displays backend values**; it never computes percentages, risk scores, or trends.

## 1. Direction

The product should feel **modern, academic, professional, and data-focused**.

It should not feel like:

- a generic AI chatbot
- a gaming dashboard
- a stock admin template

Primary metaphor: a college analytics desk — paper, ink, serif titles, quiet colour.

## 2. Information hierarchy

**Student (visible within seconds)**

1. Am I doing well?
2. What is my current risk?
3. Why?
4. What should I do next?

**Teacher**

1. How is the class performing?
2. Which students need attention?
3. Why?
4. What interventions are active?

Do not dump every field at the same visual weight. Risk and class counts come first; tables and AI prose come after.

Always show: *Risk indicator, not a prediction.*

Keep **Calculated facts** visually separate from **AI advice**.

## 3. Principles

1. **Facts over decoration.** Charts, scores, and tables are the product.
2. **One source of numbers.** Render API fields with `displayValue`. No client-side risk or percent math.
3. **Text is the source of truth.** Colour never carries meaning alone.
4. **Quiet motion.** No decorative animation. Loading may pulse.
5. **Shared components only.** Pages compose `Button`, `Card`, `Field`, `Input`, `Select`, `Table`, `Alert`, `Badge`, `Tabs`, `Modal`, `Skeleton`.
6. **Works without AI.** Fallback copy uses `Alert` / `FallbackBanner`.

## 4. Tokens

Named in `frontend/tailwind.config.js` and applied in `frontend/src/index.css`.

| Token | Value | Use |
|---|---|---|
| `paper` | `#F4F0E6` | App background |
| `surface` | `#FFFcf7` | Cards |
| `ink` | `#122033` | Primary text |
| `ink-500` / `ink-700` | muted / body | Secondary text |
| `accent` | `#1F4E79` | Primary actions, active nav |
| `rule` | `#D7D0C3` | Borders |
| `risk-low` | `#2F6F4E` | Low risk (plus ●) |
| `risk-medium` | `#8A5A12` | Medium risk (plus ▲) |
| `risk-high` | `#8B2E2E` | High risk (plus ■) |
| `risk-unknown` | `#4B5563` | Insufficient data (plus ◇) |

**Typography**

- Headings: Source Serif 4 600 (fallback Georgia / `ui-serif`)
- Body / UI: Source Sans 3 400 / 500 / 600 (fallback system-ui)
- Page title: `text-3xl` serif
- Section: `text-lg` serif
- Body: `text-sm` / `text-base`
- Tabular numbers for scores

### Landing token layer (UI-02, D39)

The public landing page uses a **second, additive** token layer. It never redefines
the tokens above, so changing it cannot move the dashboards.

- Values: `--landing-*` custom properties on `:root` in `frontend/src/index.css`.
- Tailwind namespace: `landing-*` (`bg-landing-canvas`, `text-landing-ink-muted`,
  `shadow-landing-panel`, `rounded-landing-md`, `duration-landing-fast`, `ease-landing`).
- Surfaces: `paper` → `canvas` → `surface` → `raised`. Rules: `rule-faint` → `rule` → `rule-strong`.
- Ink: `ink` (headings) → `ink-body` (copy) → `ink-muted` (labels). Accent adds `accent-hover`,
  `accent-soft` and `accent-ink` (text on accent).
- Type scale: `.saa-display`, `.saa-headline`, `.saa-subhead`, `.saa-lede`, `.saa-eyebrow`,
  `.saa-label`, `.saa-metric`. The last three use system monospace.
- Landing heading weights (serif 700) are scoped under `.saa-landing` on the landing root.
  Do not apply that class outside the landing page.
- Motion: `.saa-landing-enter` on load (stagger with `--saa-enter-delay`), `.saa-reveal` on
  scroll, `.saa-landing-draw` for SVG paths. All three resolve instantly under
  `prefers-reduced-motion: reduce`.

**Spacing:** 8 px grid (`2`, `4`, `6`, `8`). Page max width `7xl`. Card padding `p-5`.

**Radii:** controls `rounded-md` (6 px); cards `rounded-lg` (10 px).

**Focus:** `focus-visible` ring `accent` at 2 px. Never remove outlines without a replacement.

## 5. Risk semantics

`RiskBadge` always prints the backend level text (`LOW`, `MEDIUM`, `HIGH`, `INSUFFICIENT_DATA`).

| Level | Marker | Colour |
|---|---|---|
| LOW | ● | green ink |
| MEDIUM | ▲ | amber ink |
| HIGH | ■ | crimson ink |
| INSUFFICIENT_DATA | ◇ | slate ink |

Do not encode level with colour-only pills.

## 6. Components

| Component | Role |
|---|---|
| `Button` | primary / secondary / ghost; disabled opacity |
| `Card` | surface + rule border + optional title |
| `Badge` | compact status (used by `RiskBadge`) |
| `Table` / `SimpleTable` | caption required for data tables; overflow-x |
| `Input` / `Select` / `Textarea` | labelled via wrapping `Field` |
| `Tabs` | peer panels; selected tab is not colour-only |
| `Modal` | labelled dialog, Escape and backdrop close |
| `Alert` | info / warning / error (`role="alert"` for error) |
| `Skeleton` | pulse placeholder; `Loading` keeps visible status text |
| `EmptyState` | titled empty; `role="status"` |

## 7. Accessibility

- Contrast: body text on paper and coloured badges on their tinted fills must meet WCAG AA.
- Every input has a visible label. Buttons have an accessible name.
- Keyboard: nav links, tabs (arrow keys), modal focus trap, visible focus.
- Charts: `role="img"` plus `aria-label` from backend series label; point `<title>` for values.
- Do not rely on hover for essential actions.
- Language: `html lang="en"`.

## 8. Charts

SVG series from backend `{on, value}` points (D33). Shared look:

- Horizontal rules in `rule`
- Line and markers in `accent`
- Caption: title, backend label, slope if present
- Empty series → `EmptyState`

No frontend interpolation of academic meaning (DECLINING is a backend label).

## 9. Responsive

- Auth: single column card.
- App shell: stacked header; hamburger `Open menu` under `md`; sidebar from `md` up.
- Page root uses `overflow-x-clip`; tables scroll horizontally inside the card.
- No page-level horizontal scroll at 375 px (Phase 18; see `docs/UI_POLISH.md`).
- Dashboard stats: one column, then `sm:grid-cols-3`.
- Skip link targets `#main-content`.

## 10. Copy

- Headings stay functional (`Student dashboard`, `What-If`, `AI Advisor`).
- Fallback: “this response was generated without the AI”.
- Empty states name the missing set (“No open interventions”).
