import type { ReactNode } from "react";

import { cx } from "../../lib/cx";

type SectionProps = {
  id?: string;
  /** `canvas` lifts a band off the paper background. */
  tone?: "paper" | "canvas";
  label?: string;
  labelledBy?: string;
  /** Full-bleed decorative layer painted behind the content. */
  backdrop?: ReactNode;
  className?: string;
  innerClassName?: string;
  children: ReactNode;
};

export function Section({
  id,
  tone = "paper",
  label,
  labelledBy,
  backdrop,
  className,
  innerClassName,
  children,
}: SectionProps) {
  const layered = Boolean(backdrop);

  return (
    <section
      id={id}
      aria-label={label}
      aria-labelledby={labelledBy}
      className={cx(
        // scroll-mt keeps anchor targets clear of the fixed landing navigation.
        "w-full scroll-mt-24",
        tone === "canvas" ? "bg-landing-canvas" : "bg-landing-paper",
        layered && "relative isolate",
        className,
      )}
    >
      {backdrop}
      <div
        className={cx(
          "mx-auto w-full max-w-6xl px-6 py-16 sm:py-20",
          layered && "relative",
          innerClassName,
        )}
      >
        {children}
      </div>
    </section>
  );
}
