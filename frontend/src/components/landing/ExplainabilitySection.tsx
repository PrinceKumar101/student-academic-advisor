import { cx } from "../../lib/cx";
import { RISK_DISCLAIMER } from "../../lib/display";
import { Reveal } from "./Reveal";
import { Section } from "./Section";

/**
 * The shipped weights and normalisation ranges, from RISK_ENGINE_SPEC.md 6.2
 * and 6.3. Nothing here may promise more than the engine does; the honesty
 * rules below come from 6.6.
 */
const components = [
  {
    name: "Attendance",
    weight: 0.25,
    scale: "90% or more reads as 0 risk, 50% or less as 100.",
  },
  {
    name: "Internal marks",
    weight: 0.25,
    scale: "75% or more reads as 0 risk, 35% or less as 100.",
  },
  {
    name: "Assignments",
    weight: 0.15,
    scale: "Half the submission rate, half the marks on the same scale.",
  },
  {
    name: "Quizzes",
    weight: 0.15,
    scale: "75% or more reads as 0 risk, 35% or less as 100.",
  },
  {
    name: "Previous performance",
    weight: 0.1,
    scale: "The most recent semester percentage, on the marks scale.",
  },
  {
    name: "Study habits",
    weight: 0.1,
    scale: "Self-reported hours against a 2 h/day target, and confidence 1 to 5.",
  },
];

/** Descending tints, so the eye reads the ruler in weight order. */
const segmentTints = [
  "bg-landing-accent",
  "bg-landing-accent/80",
  "bg-landing-accent/60",
  "bg-landing-accent/50",
  "bg-landing-accent/35",
  "bg-landing-accent/25",
];

const notes = [
  {
    title: "Chosen, not learned",
    body: "The six weights are expert-chosen heuristics. They sit in one configuration file, are validated to sum to 1.00 when the app starts, and can be changed and re-tested. They were not learned from data, and the project does not claim they were.",
  },
  {
    title: "Thin data is reported, not filled in",
    body: "Only components that actually have records are counted, and their weights are renormalised over what is available. Below 0.40 of the total weight there is no score at all, only INSUFFICIENT_DATA. Every result carries its completeness, so a thin record is never read as a confident one.",
  },
  {
    title: "The AI never produces the number",
    body: "Risk, trends and what-if are plain Python and make no AI call. The AI is handed figures that have already been computed, and what it writes is checked against them before anyone sees it.",
  },
  {
    title: "Escalation moves the level, never the score",
    body: "Attendance under 75%, or internal marks under the 40% pass mark, lift the level to at least medium and name the reason. The number itself is untouched, and self-reported study habits can never trigger it.",
  },
];

export function ExplainabilitySection() {
  return (
    <Section id="explainability" tone="canvas" labelledBy="explainability-heading">
      <Reveal>
        <p className="saa-eyebrow">Explainability</p>
        <h2 id="explainability-heading" className="saa-headline mt-4">
          {RISK_DISCLAIMER}
        </h2>
        <p className="saa-lede mt-4 max-w-2xl">
          The score is a weighted reading of six things a department already records. Here is the
          whole of it, together with the claims it deliberately does not make.
        </p>
      </Reveal>

      <Reveal delayMs={80} className="mt-12">
        <div className="grid gap-x-12 gap-y-12 lg:grid-cols-12">
          <div className="lg:col-span-7">
            <div className="flex items-baseline justify-between gap-3">
              <p className="saa-label">Weight of each component</p>
              <p className="saa-metric text-xs">Sum 1.00</p>
            </div>
            {/* The list below carries the same figures, so the ruler is decorative. */}
            <div
              aria-hidden="true"
              className="mt-3 flex h-7 w-full overflow-hidden rounded-landing-sm border border-landing-rule"
            >
              {components.map((component, index) => (
                <div
                  key={component.name}
                  style={{ flexGrow: component.weight * 100, flexBasis: 0 }}
                  className={cx(
                    "border-r border-landing-canvas last:border-r-0",
                    segmentTints[index],
                  )}
                />
              ))}
            </div>

            <ul className="mt-7 divide-y divide-landing-rule border-t border-landing-rule">
              {components.map((component) => (
                <li key={component.name} className="py-3.5">
                  <div className="flex items-baseline justify-between gap-4">
                    <p className="text-sm text-landing-ink-body">{component.name}</p>
                    <p className="saa-metric text-sm">{component.weight.toFixed(2)}</p>
                  </div>
                  <p className="mt-1.5 text-xs leading-relaxed text-landing-ink-muted">
                    {component.scale}
                  </p>
                </li>
              ))}
            </ul>
          </div>

          <div className="lg:col-span-5">
            <ul className="space-y-7">
              {notes.map((note) => (
                <li key={note.title} className="border-t border-landing-rule pt-4">
                  <h3 className="saa-subhead">{note.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-landing-ink-body">{note.body}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Reveal>
    </Section>
  );
}
