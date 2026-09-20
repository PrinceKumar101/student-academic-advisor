import { Reveal } from "./Reveal";
import { Section } from "./Section";

/**
 * Six capabilities, each stated as something the system actually does. Figures
 * come from RISK_ENGINE_SPEC.md (6.3 weights, 6.8 W1 what-if, 7.1 slope
 * thresholds, 7.2 subject bands, 7.4 comparison group) and AI_GUIDELINES.md
 * (5.2 capabilities, 5.4 grounding, 5.5 fallback).
 */
const features = [
  {
    title: "Risk you can audit",
    body: "Six components are normalised to a 0\u2013100 risk, weighted and summed into one score and a level. Every component reports its raw value, weight, contribution and a templated note, so the number can be taken apart.",
    detail: "Weights 0.25 · 0.25 · 0.15 · 0.15 · 0.10 · 0.10",
  },
  {
    title: "Trend detection",
    body: "Assessments overall, per type, per subject, weekly attendance and the risk history each get a least-squares slope and a label. A latest value far off the earlier mean is flagged as a sudden rise or drop.",
    detail: "Improving ≥ +2.0 · declining ≤ −2.0 · sudden change 15 pts",
  },
  {
    title: "Weak-area analysis",
    body: "Each subject is scored from its graded marks and banded, with its own attendance alert. Subject attendance is reported as an alert and never quietly changes the overall level.",
    detail: "Below 50 high concern · below 65 medium · attendance alert under 75%",
  },
  {
    title: "What-if simulation",
    body: "Raise hypothetical attendance or marks and the same Python function recomputes the score, returning current, simulated and the difference. Nothing is written to the database.",
    detail: "Attendance 64 → 80 moves the worked case −10.0, HIGH to MEDIUM",
  },
  {
    title: "AI advisor and study planner",
    body: "The AI reads only the numbers Python already computed and turns them into an explanation, prioritised recommendations, answers to questions, and the topic and activity for each study slot. Dates, subjects and minutes stay with Python.",
    detail: "Percentages in AI text are checked against the facts, or the fallback is used",
  },
  {
    title: "Teacher class analytics",
    body: "A class view with risk-level counts, mean attendance and marks, per-subject means and the trend distribution, filterable down to one student, plus interventions that keep the risk snapshot from the day they were raised.",
    detail: "Peer comparison only once a group has at least 5 students",
  },
];

export function FeatureGrid() {
  return (
    <Section id="features" tone="canvas" labelledBy="features-heading">
      <Reveal>
        <p className="saa-eyebrow">Capabilities</p>
        <h2 id="features-heading" className="saa-headline mt-4">
          What the advisor does
        </h2>
        <p className="saa-lede mt-4 max-w-2xl">
          Six working areas, all computed from the academic records a department already keeps.
        </p>
      </Reveal>

      <Reveal delayMs={80} className="mt-12">
        <ul className="grid gap-x-10 gap-y-9 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <li key={feature.title} className="border-t border-landing-rule pt-5">
              <p className="saa-label">{String(index + 1).padStart(2, "0")}</p>
              <h3 className="saa-subhead mt-3">{feature.title}</h3>
              <p className="mt-2.5 text-sm leading-relaxed text-landing-ink-body">
                {feature.body}
              </p>
              <p className="saa-metric mt-3.5 text-xs leading-relaxed text-landing-ink-muted">
                {feature.detail}
              </p>
            </li>
          ))}
        </ul>
      </Reveal>
    </Section>
  );
}
