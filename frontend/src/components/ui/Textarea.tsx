import type { TextareaHTMLAttributes } from "react";

import { cx } from "../../lib/cx";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cx("saa-input min-h-[6rem]", className)} {...props} />;
}
