import { cx } from "../../lib/cx";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cx("animate-pulse rounded-md bg-ink-100", className)} aria-hidden="true" />;
}
