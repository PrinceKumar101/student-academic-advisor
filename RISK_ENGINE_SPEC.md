# RISK_ENGINE_SPEC: Student Academic Advisor

Copied from `docs/archive/MASTER_DESIGN.md` §6 and §7 (formulas, thresholds, test cases R1–R13, W1).

## 6. RISK ENGINE DESIGN

Deterministic. Location: `engines/`. Config: `risk_config.py` (versioned, validated at import). Pure functions on dataclasses. No I/O, no clock.

### 6.1 Inputs (`RiskInputs`, all optional)

| Field | Definition |
|---|---|
| `attendance_percent` | Σ classes_attended ÷ Σ classes_held × 100 across all subjects. `None` if Σ held = 0. |
| `internal_percent` | Σ obtained ÷ Σ max over GRADED INTERNAL + EXAM. `None` if none. |
| `quiz_percent` | Same for GRADED QUIZ. |
| `assignment_percent` | Same for GRADED ASSIGNMENT. |
| `assignment_submission_rate` | GRADED ÷ (GRADED + MISSING) for assignments. PENDING excluded. `None` if denominator is 0. |
| `previous_percentage` | Most recent `semester_results.percentage`. |
| `study_hours_per_day`, `self_confidence` | From `study_habits`. |
| `n_internal`, `n_quiz`, `n_assignment` | Sample sizes (for flags). |

### 6.2 Component normalization (risk 0–100, higher = worse; clamp to [0,100])

```text
attendance_risk  = clamp((90 - A) / (90 - 50) * 100)        # 90%+ -> 0, 50%- -> 100
performance_risk = clamp((75 - P) / (75 - 35) * 100)        # 75%+ -> 0, 35%- -> 100
                   (used for internal, quizzes, previous)
assignment_risk  = 0.5 * (100 - submission_rate)  +  0.5 * performance_risk(assignment_percent)
                   (if one part is missing, use the other at full weight)
study_risk       = mean of available:
                     clamp((2.0 - hours) / 2.0 * 100)          # target 2 h/day
                     (5 - confidence) / 4 * 100                 # confidence 1..5
```

### 6.3 Weights and aggregation

Default weights (sum = 1.00, validated at import): attendance 0.25, internal 0.25, assignments 0.15, quizzes 0.15, previous 0.10, study_habits 0.10.

```text
available = components with data
if sum(weights of available) < 0.40  ->  level INSUFFICIENT_DATA, score None
else effective_weight_i = weight_i / sum(weights of available)
     score = round1( sum(effective_weight_i * risk_i) )
     data_completeness = sum(weights of available)
     contribution_i = effective_weight_i * risk_i
```

### 6.4 Classification and escalation

```text
base_level:  score <= 30 -> LOW ; <= 60 -> MEDIUM ; else HIGH      (on the rounded score)
floors (never lower a level, never raise above MEDIUM):
   attendance_percent < 75          -> at least MEDIUM
   internal_percent   < 40 (pass)   -> at least MEDIUM
final level = max(base_level, floor)
if floor raised the level: escalated = true; escalation_reason lists each floor that fired
   ("Attendance below 75% cutoff" and/or "Internal marks below 40% pass cutoff"), joined with "; ".
The numeric score is never altered by escalation.
```
Study habits (self-reported) can never trigger a floor.

### 6.5 Risk factors and explanations

Component level uses the same thresholds on the component risk (≤30 LOW, ≤60 MEDIUM, else HIGH). `top_factors` = components with level ≥ MEDIUM, sorted by `contribution` descending, max 3. Each component has a **templated** note that quotes the raw value, e.g. "Attendance is 64.0%, below the 75% cutoff." Notes are deterministic and never AI-generated.

### 6.6 Avoiding misleading conclusions

- `INSUFFICIENT_DATA` rather than a fake score.
- Flags: `LOW_SAMPLE:<component>` (fewer than 2 graded items), `PARTIAL_DATA` (completeness < 1), `STALE_DATA` (newest record older than 30 days before `as_of`).
- Zero classes held gives `None`, not 0% and not a crash.
- The UI must show completeness and the wording "risk indicator, not a prediction of failure".
- `config_version` is saved on every snapshot.
- Honest framing: weights are expert-chosen heuristics, configurable and testable, not learned from data.

### 6.7 What-if

`simulate(inputs, overrides, config)` builds `replace(inputs, **overrides)`, runs `compute_risk` twice and diffs. Allowed override keys are those in `API_SPEC.md` §4.3. An override may activate a component whose real value is `None`; the response marks it as `hypothetical`. No DB access.

### 6.8 Required risk-engine test cases (worked expected values)

| ID | Scenario | Expected |
|---|---|---|
| R1 Low | att 92, internal 82, assign sub 100%/85, quiz 80, prev 78, study 3 h/conf 4 | attendance 0; internal 0; assignments 0; quizzes 0; previous 0; study 12.5. **Score 1.3 (1.25 rounded), LOW** |
| R2 Medium | att 75, internal 60, assign 100%/65, quiz 55, prev 65, study 1.5 h/conf 3 | component risks 37.5 / 37.5 / 12.5 / 50 / 25 / 37.5. **Score 34.4, MEDIUM** |
| R3 High | att 64, internal 45, assign 60%/50, quiz 40, prev 55, study 1 h/conf 2 | risks 65 / 75 / 51.25 / 87.5 / 50 / 62.5. **Score 67.1, HIGH** |
| R4 Boundaries | classify 30.0, 30.1, 60.0, 60.1 | LOW, MEDIUM, MEDIUM, HIGH |
| R5 Missing data | only attendance 64 and internal 45 | completeness 0.50; score (0.25×65+0.25×75)/0.5 = **70.0, HIGH**; flag PARTIAL_DATA |
| R6 Insufficient | only study habits | completeness 0.10 < 0.40, **INSUFFICIENT_DATA**, score None |
| R7 Escalation | attendance 60, all else risk 0 | score 18.8 (base LOW), attendance < 75 → **MEDIUM, escalated=true**, score unchanged |
| R8 Zero classes | Σ held = 0 | attendance None (not 0%), no exception |
| R9 Clamp | attendance 100 / 30 | risk 0 / 100 |
| R10 Invalid | attended > held, percent < 0 or > 100 | validation error |
| R11 Weights | weights not summing to 1 | config validation error at import |
| R12 Determinism | same inputs twice; inputs not mutated | identical outputs |
| R13 Monotonic | random seeded inputs: improving any single input never increases score | property holds over ≥ 500 cases |
| W1 What-if | R3 with attendance 64 → 80 | attendance risk 65 → 25; contribution 16.25 → 6.25; **difference −10.0; score 57.1, MEDIUM**; DB unchanged |

---

## 7. TREND, WARNING, SUBJECT AND CLASS ANALYTICS DESIGN

All in `engines/` (pure). Thresholds live in config.

### 7.1 Trend engine

Series = ordered (by date) percentage values. Requires ≥ 3 points, else `INSUFFICIENT_DATA`.
- Slope by least squares over index 0..n−1 (points per assessment).
- `slope ≥ +2.0` IMPROVING · `slope ≤ −2.0` DECLINING · otherwise STABLE.
- **Sudden change:** last value differs from the mean of the previous values by ≥ 15 points → `SUDDEN_DROP` / `SUDDEN_RISE` flag.
- Worked check: 72, 69, 63, 55 → mean 64.75, slope **−5.7**, DECLINING; last vs mean of previous = 55 − 68 = −13, no sudden flag.
- Series produced: overall assessments (all GRADED types), per type, per subject, weekly attendance (held/attended summed across subjects on each record date), risk history (snapshot scores; same slope rule, higher score is not inverted).
- Thresholds live in `engines/trend_config.py` (`TREND_CONFIG`, version `1.0`): min points 3; slope cutoffs ±2.0; sudden change 15; subject bands 50/65; subject attendance alert 75; recent attendance window 4 weeks; drop WARNING/CRITICAL 10/20; missing-assignment streak 2/3; comparison group minimum 5.

### 7.2 Subject analysis

Subject % = Σ obtained ÷ Σ max over all GRADED assessments in the subject. Band: `< 50` HIGH_CONCERN · `< 65` MEDIUM · else GOOD. Also returns subject attendance % and an alert if below 75%. Subject attendance never changes the overall risk level (it is shown as an alert only).

### 7.3 Early warnings

Compare the recent window with the previous window:

| Rule | WARNING | CRITICAL |
|---|---|---|
| Attendance drop (last 4 weeks vs previous weeks) | ≥ 10 pp | ≥ 20 pp |
| Internal marks drop (latest vs mean of earlier) | ≥ 10 pts | ≥ 20 pts |
| Quiz drop | ≥ 10 pts | ≥ 20 pts |
| Overall attendance crosses below 75% | WARNING | n/a |
| 2 consecutive MISSING assignments | WARNING | 3+ → CRITICAL |
| Risk level higher than previous snapshot | WARNING | LOW→HIGH = CRITICAL |

Example from the SRS: attendance 82 → 67 (15 pp) = WARNING; quiz 76 → 48 (28 pts) = CRITICAL.

### 7.4 Class analytics (teacher)

Counts by risk level; mean attendance (mean of student-level values); mean marks; per-subject mean %; trend-label distribution. Implemented with Pandas over the bulk-loaded data. Student-vs-class comparison is returned only if the comparison group has ≥ 5 students (prevents identifying individuals).

### 7.5 Intervention before/after

Baseline (score, level, timestamp) is **copied** onto the intervention at creation. Outcome is captured when the intervention is completed. `progress` compares the baseline with the current live risk. Wording is observational only (see the contract in `API_SPEC.md` §4.3).

---
