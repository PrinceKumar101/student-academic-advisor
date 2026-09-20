import type { CSSProperties } from "react";

/**
 * Inline hooks for the landing motion primitives in index.css. Both variables
 * are read by `.saa-landing-enter`, `.saa-landing-draw`, `.saa-landing-sweep`
 * and `.saa-landing-fade`, and `--saa-enter-delay` inherits, so a wrapper can
 * time an element it does not own (the hero's reused risk gauge).
 */
export function enterDelay(delayMs: number, durationMs?: number): CSSProperties {
  const style: Record<string, string> = { "--saa-enter-delay": `${delayMs}ms` };
  if (durationMs !== undefined) {
    style["--saa-enter-duration"] = `${durationMs}ms`;
  }
  return style as CSSProperties;
}
