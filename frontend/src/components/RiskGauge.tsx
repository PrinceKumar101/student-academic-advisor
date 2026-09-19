import { displayValue } from "../lib/display";
import { RiskBadge, type RiskLevel } from "./RiskBadge";

export function RiskGauge({
  score,
  level,
}: {
  score: number | null;
  level: RiskLevel;
}) {
  const width = score === null ? 0 : Math.min(100, Math.max(0, score));

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-baseline gap-2">
        <p className="font-serif text-3xl tabular-nums">Risk score {displayValue(score)}</p>
        <RiskBadge level={level} />
      </div>
      <div
        className="h-2 w-full overflow-hidden rounded-full bg-ink-100"
        role="img"
        aria-label={`Risk score ${displayValue(score)}, level ${level}`}
      >
        <div
          className="saa-gauge-fill h-full rounded-full bg-accent"
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}
