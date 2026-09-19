# Phase index

Single tracker for completed phases and the current task. Update this file at the end of every task and every phase (see `.cursor/rules/project.mdc`).

**Last updated:** 2026-09-19  
**Current phase:** 2 Database & seed data  
**Current task:** 2.2 Academic models  
**Latest completed phase:** 1 Backend setup  
**Latest completed task:** 2.1 SQLAlchemy foundation and identity models  

## Status legend

`[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked

## Phases

| Phase | Name | Status | Completed on | Notes |
|---|---|---|---|---|
| 0 | Planning & Documentation | [x] | 2026-09-19 | 0.1–0.3 done; living-doc fixes C1–C10 |
| 1 | Backend setup | [x] | 2026-09-19 | FastAPI, health, errors, CORS, pytest |
| 2 | Database & seed data | [ ] | | 2.1 identity models done |
| 3 | Authentication & authorization | [ ] | | |
| 4 | Academic data APIs | [ ] | | |
| 5 | Risk engine | [ ] | | |
| 6 | Trends, subject analysis, early warnings | [ ] | | |
| 7 | What-if simulator | [ ] | | |
| 8 | AI service (analysis) | [ ] | | |
| 9 | AI study planner | [ ] | | |
| 10 | AI assistant (chat) | [ ] | | |
| 11 | Interventions & teacher APIs | [ ] | | |
| 12 | Backend integration, hardening, freeze | [ ] | | |
| 13 | Frontend foundation | [ ] | | |
| 14 | Student pages (functional) | [ ] | | |
| 15 | Teacher pages (functional) | [ ] | | |
| 16 | Frontend integration & E2E, functional freeze | [ ] | | |
| 17 | UI design | [ ] | | |
| 18 | UI polish | [ ] | | |
| 19 | Final documentation & demo | [ ] | | |

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
| 2.2 Academic models | [ ] | |
| 2.3 RiskAssessment, indexes, reset_db | [ ] | |
| 2.4 Seed generator core | [ ] | |
| 2.5 Seed generator data | [ ] | |
| 2.6 Story/edge students and seed_demo CLI | [ ] | |
| 2.7 Database tests | [ ] | |

## How to update

1. After each **task**: set that task `[x]`, set **Current task** to the next unchecked task, set **Latest completed task**.
2. After each **phase**: set the phase `[x]`, fill **Completed on**, set **Latest completed phase**, refresh **Current phase**, and also update `CLAUDE_CONTEXT.md` and tick `DEVELOPMENT_PLAN.md`.
