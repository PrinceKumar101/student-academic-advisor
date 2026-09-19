import type { SelectHTMLAttributes } from "react";

import { cx } from "../../lib/cx";

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={cx("saa-input", className)} {...props} />;
}
