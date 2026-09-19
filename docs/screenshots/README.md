# Screenshots (Phase 19.3)

Captured 2026-09-19 from the local UI (`127.0.0.1:5173`) against the seeded API (`as_of=2026-09-19` unless noted).

| File | Scene | Expected live values |
|---|---|---|
| `01-login.png` | Login | Demo accounts in `README.md` |
| `02-student-dashboard.png` | Rahul dashboard | **84.1 HIGH**; attendance DECLINING (−2.7); overall STABLE (−0.5) |
| `03-student-risk.png` | Risk components | Score 84.1, completeness 1 |
| `04-student-performance.png` | Trend charts | Assessment STABLE; attendance decline on the series |
| `05-teacher-dashboard.png` | Teacher home | Group **42**; mean attendance **77.1**; mean marks **63.4** |
| `06-teacher-students.png` | Unfiltered list | Page-local sort (D34) |
| `07-teacher-filter-rahul.png` | HIGH + search Rahul | **1** student: Rahul Venn |
| `08-forbidden.png` | Teacher opened `/student` | Role guard + dashboard / logout |
| `09-student-what-if.png` | What-if form | Submit 80 / 60 → **53.9 MEDIUM** (see `DEMO_SCRIPT.md`) |

**Note:** Some PNG captures show extra letter-end glyphs (webfont rasterization in the screenshot tool). The accessibility tree and live browser show the correct words (“Log in”, “Rahul Venn”, “Risk score 84.1”). For a slide deck, recapture in Chrome if the glyphs look wrong.

To recapture: seed, start both servers, log in, set **As of** to `2026-09-19`, save PNGs with the same names.
