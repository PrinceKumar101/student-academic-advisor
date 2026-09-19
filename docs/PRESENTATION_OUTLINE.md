# Presentation outline (10–12 slides)

Keep each slide to one idea. Demo after slide 6 if time allows; otherwise after slide 8.

| # | Title | Speak (≈45 s) | Show |
|---|---|---|---|
| 1 | Title | Student Academic Advisor — decision support, not a trained predictor. | Title + names + stack |
| 2 | Problem | Scattered marks/attendance; late discovery; teachers cannot scan everyone. | 3 pain bullets |
| 3 | Principle | **Python computes. AI explains.** App works with AI off. | Two-column diagram |
| 4 | Architecture | UI → routers → services → engines / ai → SQLite. Engines are pure. | `ARCHITECTURE.md` diagram |
| 5 | Risk engine | Weighted components, floors, INSUFFICIENT_DATA. R1–R13. | One formula + HIGH badge |
| 6 | Story student | Rahul: live **84.1 HIGH**; SRS 82 is the paper example. | Dashboard screenshot |
| 7 | Trends & subjects | Attendance DECLINING; subject HIGH_CONCERN. Charts = backend points. | Performance screenshot |
| 8 | What-if | 80 / 60 → **53.9 MEDIUM**. Database unchanged. | What-if screenshot |
| 9 | AI safety | Facts vs advice; grounding; fallback; no PII in prompts. | Advisor screenshot + banner |
| 10 | Teacher loop | Filter HIGH + search; intervention baseline; `demo_advance` → 68.5. | Teacher list screenshot |
| 11 | Tests & honesty | pytest + vitest; fake AI; limitations (weights, SQLite, synthetic). | Test command list |
| 12 | Q&A | Point to `docs/VIVA_NOTES.md`. | “Questions” |

**If asked for a live demo:** follow `docs/DEMO_SCRIPT.md` steps 1 → 5 → 6 → 8 (skip extras).

**Backup slide (optional):** folder map (`engines/`, `ai/`, `api/deps.py`) and Decision Log highlights D1, D5, D33, D35.
