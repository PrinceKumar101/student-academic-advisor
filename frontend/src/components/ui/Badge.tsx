import type { HTMLAttributes } from "react";

import { cx } from "../../lib/cx";

type Tone = "neutral" | "low" | "medium" | "high" | "unknown";

const TONES: Record<Tone, string> = {
  neutral: "border-rule bg-ink-50 text-ink-700",
  low: "border-risk-low/30 bg-risk-low-fill text-risk-low",
  medium: "border-risk-medium/30 bg-risk-medium-fill text-risk-medium",
  high: "border-risk-high/30 bg-risk-high-fill text-risk-high",
  unknown: "border-risk-unknown/30 bg-risk-unknown-fill text-risk-unknown",
};

export function Badge({
  tone = "neutral",
  className,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      className={cx(
        "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-medium tracking-wide",
        TONES[tone],
        className,
      )}
      {...props}
    />
  );
}
