import { Reveal } from "./Reveal";
import { Section } from "./Section";

/**
 * Three stages, in the order the data actually moves. Horizontal on desktop,
 * a vertical timeline below `md`, using one hairline rule that switches sides.
 */
const stages = [
  {
    title: "Academic data is recorded",
    body: "Teachers enter attendance, internal marks, quizzes, assignments and previous-semester results. Students keep their own study habits. Nothing else is asked for.",
    detail: "Attendance percentage is computed on read, never stored",
  },
  {
    title: "Python computes the numbers",
    body: "The risk score and level, the trend slopes, the per-subject bands and the early warnings all come from the same records, deterministically and with no AI involved.",
    detail: "Too little data returns INSUFFICIENT_DATA instead of a guess",
  },
  {
    title: "AI explains and helps plan",
    body: "The AI is handed the computed facts and writes the explanation, the prioritised recommendations, the answers in the advisor and the activity for each study slot.",
    detail: "Unavailable or ungrounded output falls back to templated text",
  },
];

export function HowItWorks() {
  return (
    <Section id="how-it-works" labelledBy="how-it-works-heading">
      <Reveal>
        <p className="saa-eyebrow">How it works</p>
        <h2 id="how-it-works-heading" className="saa-headline mt-4">
          Python computes. AI explains.
        </h2>
        <p className="saa-lede mt-4 max-w-2xl">
          The split is deliberate: no AI capability can change a score, a percentage or a record.
        </p>
      </Reveal>

      <Reveal delayMs={80} className="mt-12">
        <ol className="grid gap-y-10 md:grid-cols-3 md:gap-x-10 md:gap-y-0">
          {stages.map((stage, index) => (
            <li
              key={stage.title}
              className="relative border-l border-landing-rule pl-6 md:border-l-0 md:border-t md:pl-0 md:pt-7"
            >
              <span
                aria-hidden="true"
                className="absolute -left-[4.5px] top-1.5 h-2 w-2 rounded-full bg-landing-accent md:-top-[4.5px] md:left-0"
              />
              <p className="saa-label">Step {String(index + 1).padStart(2, "0")}</p>
              <h3 className="saa-subhead mt-3">{stage.title}</h3>
              <p className="mt-2.5 text-sm leading-relaxed text-landing-ink-body">{stage.body}</p>
              <p className="saa-metric mt-3.5 text-xs leading-relaxed text-landing-ink-muted">
                {stage.detail}
              </p>
            </li>
          ))}
        </ol>
      </Reveal>
    </Section>
  );
}
