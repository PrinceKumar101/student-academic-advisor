import type { ReactNode } from "react";

import { cx } from "../../lib/cx";

type Tone = "info" | "warning" | "error";

const TONES: Record<Tone, string> = {
  info: "border-accent/30 bg-accent-50 text-ink-700",
  warning: "border-risk-medium/40 bg-risk-medium-fill text-risk-medium",
  error: "border-risk-high/40 bg-risk-high-fill text-risk-high",
};

export function Alert({
  tone = "info",
  children,
  className,
  label,
}: {
  tone?: Tone;
  children: ReactNode;
  className?: string;
  label?: string;
}) {
  const role = tone === "error" ? "alert" : "status";
  return (
    <p role={role} aria-label={label} className={cx("rounded-md border px-3 py-2 text-sm", TONES[tone], className)}>
      {children}
    </p>
  );
}
