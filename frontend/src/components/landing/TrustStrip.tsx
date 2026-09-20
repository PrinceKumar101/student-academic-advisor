import { Reveal } from "./Reveal";
import { Section } from "./Section";

/**
 * Product facts rather than customer logos. Every figure is checked against the
 * documentation: the 0-100 deterministic score and the six weights come from
 * RISK_ENGINE_SPEC.md 6.3, "no AI call" from the rule that risk, trends and
 * what-if never reach the AI, and the two roles from PROJECT_SPEC.md D2/D3.
 */
const facts = [
  {
    value: "0\u2013100",
    label: "Deterministic score",
    detail: "The same inputs always give the same score. Every snapshot stores its config version.",
  },
  {
    value: "6",
    label: "Weighted factors",
    detail:
      "Attendance, internal marks, assignments, quizzes, previous results and study habits.",
  },
  {
    value: "0",
    label: "AI calls to score",
    detail: "Risk, trends and what-if are pure Python, so the product works with the AI off.",
  },
  {
    value: "2",
    label: "Roles",
    detail: "A student view of one record and a teacher view of a class, separated on the server.",
  },
];

export function TrustStrip() {
  return (
    <Section tone="canvas" label="Product facts" innerClassName="py-10 sm:py-12">
      <Reveal>
        <ul className="grid gap-x-8 gap-y-7 sm:grid-cols-2 lg:grid-cols-4">
          {facts.map((fact) => (
            <li key={fact.label} className="border-t border-landing-rule pt-4">
              <p className="saa-metric text-2xl leading-none">{fact.value}</p>
              <p className="saa-label mt-2.5">{fact.label}</p>
              <p className="mt-2 text-sm leading-relaxed text-landing-ink-muted">{fact.detail}</p>
            </li>
          ))}
        </ul>
      </Reveal>
    </Section>
  );
}
