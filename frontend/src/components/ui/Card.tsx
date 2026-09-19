import type { HTMLAttributes, ReactNode } from "react";

import { cx } from "../../lib/cx";

type CardProps = HTMLAttributes<HTMLElement> & {
  title?: string;
  description?: string;
  as?: "section" | "article" | "div" | "aside";
  children: ReactNode;
};

export function Card({
  title,
  description,
  as: Tag = "section",
  className,
  children,
  ...props
}: CardProps) {
  return (
    <Tag
      className={cx("rounded-lg border border-rule bg-surface p-5 shadow-card", className)}
      {...props}
    >
      {title ? <h2 className="text-lg">{title}</h2> : null}
      {description ? <p className="mt-1 text-sm text-ink-500">{description}</p> : null}
      {children}
    </Tag>
  );
}
