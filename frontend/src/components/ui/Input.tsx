import type { InputHTMLAttributes } from "react";

import { cx } from "../../lib/cx";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cx("saa-input", className)} {...props} />;
}
