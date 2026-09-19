# Phase index

Single tracker for completed phases and the current task. Update this file at the end of every task and every phase (see `.cursor/rules/project.mdc`).

**Last updated:** 2026-09-19  
**Current phase:** 19 Final documentation & demo (complete)  
**Current task:** none (all planned tasks done)  
**Latest completed phase:** 19 Final documentation & demo  
**Latest completed task:** 19.6 Definition of Done checklist  

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
