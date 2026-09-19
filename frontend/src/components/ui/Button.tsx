import { forwardRef, type ButtonHTMLAttributes } from "react";

import { cx } from "../../lib/cx";

type Variant = "primary" | "secondary" | "ghost";

const VARIANTS: Record<Variant, string> = {
  primary: "bg-accent text-surface hover:bg-accent-700 disabled:bg-ink-100 disabled:text-ink-500",
  secondary: "border border-rule bg-surface text-ink hover:bg-ink-50 disabled:text-ink-500",
  ghost: "text-accent hover:bg-accent-50 disabled:text-ink-500",
};

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant };

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", className, type = "button", ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      type={type}
      className={cx(
        "inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium disabled:cursor-not-allowed",
        VARIANTS[variant],
        className,
      )}
      {...props}
    />
  );
});
