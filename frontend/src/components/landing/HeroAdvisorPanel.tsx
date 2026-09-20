import { RiskGauge } from "../RiskGauge";
import { heroDemoData } from "./heroDemoData";
import { enterDelay } from "./motion";

/**
 * The panel's data draws itself once the panel is on its way in (HeroSection
 * starts it at 320ms): the score sweeps, the attendance line draws, the factor
 * bars follow in contribution order, and the AI paragraph arrives last, after
 * the figures it is explaining.
 */
const SEQUENCE = {
  gaugeMs: 480,
  sparkMs: 600,
  /** The end-point dot lands as the stroke reaches it (600ms + the draw). */
  sparkDotMs: 1200,
  factorsMs: 720,
  factorStepMs: 50,
  insightMs: 940,
};

/*
 * Domain is tighter than the data so the 75% cutoff stays inside the frame. The
 * viewBox width is close to the rendered width, so `preserveAspectRatio="none"`
 * barely distorts the trend stroke; the trend line cannot use
 * `vector-effect: non-scaling-stroke` because that makes dash lengths
 * screen-relative and breaks the pathLength-normalised draw-on animation.
 */
const SPARK = { width: 264, height: 56, padX: 3, padY: 5, min: 45, max: 80 };

/*
 * Two mono labels on one line need ~288px, which a 375px phone does not give
 * the panel. Stacking them below `sm` keeps each phrase whole instead of
 * letting "As of 13 Mar 2026" break after "Mar".
 */
const pairedLabels = "flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between sm:gap-3";

function sparkX(index: number, count: number): number {
  const span = SPARK.width - SPARK.padX * 2;
  return SPARK.padX + (count === 1 ? span / 2 : (index / (count - 1)) * span);
}

function sparkY(value: number): number {
  const span = SPARK.height - SPARK.padY * 2;
  const ratio = (value - SPARK.min) / (SPARK.max - SPARK.min);
  return SPARK.padY + (1 - ratio) * span;
}

export function HeroAdvisorPanel() {
  const { asOfLabel, risk, attendance, factors, insight } = heroDemoData;
  const weeks = attendance.weeks;
  const points = weeks.map((value, index) => `${sparkX(index, weeks.length)},${sparkY(value)}`);
  const widestContribution = Math.max(...factors.map((factor) => factor.contribution));

  return (
    /* saa-hero-panel scopes the gauge sweep, which has to live in index.css
       because the fill belongs to the shared RiskGauge. */
    <figure
      aria-labelledby="hero-panel-caption"
      className="saa-hero-panel m-0 rounded-landing-xl border border-landing-rule bg-landing-surface p-4 shadow-landing-panel sm:p-6"
    >
      <figcaption id="hero-panel-caption" className="saa-label flex items-center gap-2">
        <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-landing-rule-strong" />
        Example data &middot; not a real student
      </figcaption>

      {/* The delay inherits down to the gauge's own fill element. */}
      <div className="mt-4" style={enterDelay(SEQUENCE.gaugeMs)}>
        <RiskGauge score={risk.score} level={risk.level} />
        <div className={`mt-2.5 ${pairedLabels}`}>
          <p className="saa-label">As of {asOfLabel}</p>
          <p className="saa-label">Completeness {risk.dataCompleteness.toFixed(2)}</p>
        </div>
      </div>

      <hr className="my-4 border-0 border-t border-landing-rule" />

      <div>
        <div className="flex items-baseline justify-between gap-3">
          <p className="saa-label">Attendance &middot; last 6 weeks</p>
          <p className="saa-metric text-sm">{attendance.percent.toFixed(1)}%</p>
        </div>
        <svg
          className="mt-3 h-14 w-full"
          viewBox={`0 0 ${SPARK.width} ${SPARK.height}`}
          preserveAspectRatio="none"
          role="img"
          aria-label={`Weekly attendance falling from ${weeks[0]}% to ${weeks[weeks.length - 1]}%, against the ${attendance.cutoffPercent}% cutoff`}
        >
          <polyline
            className="saa-landing-draw"
            style={enterDelay(SEQUENCE.sparkMs)}
            pathLength={1}
            points={points.join(" ")}
            fill="none"
            stroke="rgb(var(--landing-accent))"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* Appears as the stroke reaches it rather than waiting at the end. */}
          <circle
            className="saa-landing-fade"
            style={enterDelay(SEQUENCE.sparkDotMs)}
            cx={sparkX(weeks.length - 1, weeks.length)}
            cy={sparkY(weeks[weeks.length - 1])}
            r="2.5"
            fill="rgb(var(--landing-accent))"
          />
        </svg>
        {/* The cutoff is already stated in the attendance factor note below. */}
        <p className="saa-label mt-2">
          {attendance.trendLabel} &middot; {attendance.slopePerWeek.toFixed(1)} pts/week
        </p>
      </div>

      <hr className="my-4 border-0 border-t border-landing-rule" />

      <div>
        <div className={pairedLabels}>
          <p className="saa-label">Contributing factors</p>
          <p className="saa-label">Points of {risk.score.toFixed(1)}</p>
        </div>
        <ol className="mt-3.5 space-y-3.5">
          {factors.map((factor, index) => (
            <li key={factor.key}>
              <div className="flex items-baseline justify-between gap-3">
                <p className="text-sm text-landing-ink-body">{factor.label}</p>
                <p className="saa-metric text-sm">{factor.contribution.toFixed(1)}</p>
              </div>
              <div
                aria-hidden="true"
                className="mt-2 h-1 w-full overflow-hidden rounded-full bg-landing-rule-faint"
              >
                <div
                  className="saa-landing-sweep h-full rounded-full bg-landing-accent"
                  style={{
                    width: `${(factor.contribution / widestContribution) * 100}%`,
                    ...enterDelay(SEQUENCE.factorsMs + index * SEQUENCE.factorStepMs),
                  }}
                />
              </div>
              {/*
                Dropped on a phone to keep the panel inside one screen. Nothing
                is lost: the AI paragraph below names the 75% cutoff and the
                largest contributor in prose.
              */}
              <p className="mt-2 hidden text-xs text-landing-ink-muted sm:block">{factor.note}</p>
            </li>
          ))}
        </ol>
      </div>

      <hr className="my-4 border-0 border-t border-landing-rule" />

      {/* Last in, because the explanation should follow the figures it reads. */}
      <div
        className="saa-landing-fade rounded-landing-md border border-landing-accent/20 bg-landing-accent-soft p-4"
        style={enterDelay(SEQUENCE.insightMs)}
      >
        <p className="saa-label">AI explanation</p>
        <p className="mt-2 text-sm leading-relaxed text-landing-ink-body">{insight.body}</p>
        <p className="mt-3 text-xs text-landing-ink-muted">{insight.disclosure}</p>
      </div>
    </figure>
  );
}
