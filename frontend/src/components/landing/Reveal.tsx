import type { ReactNode } from "react";

import { cx } from "../../lib/cx";
import { useInView } from "../../lib/useInView";
import { usePrefersReducedMotion } from "../../lib/usePrefersReducedMotion";

type RevealProps = {
  delayMs?: number;
  className?: string;
  children: ReactNode;
};

export function Reveal({ delayMs = 0, className, children }: RevealProps) {
  const reducedMotion = usePrefersReducedMotion();
  const { ref, inView } = useInView<HTMLDivElement>();
  const pending = !reducedMotion && !inView;

  return (
    <div
      ref={ref}
      className={cx("saa-reveal", pending && "saa-reveal-pending", className)}
      style={!reducedMotion && delayMs > 0 ? { transitionDelay: `${delayMs}ms` } : undefined}
    >
      {children}
    </div>
  );
}
