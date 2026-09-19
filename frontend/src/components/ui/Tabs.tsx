import { useId, useState, type ReactNode } from "react";

import { cx } from "../../lib/cx";

export type TabItem = {
  id: string;
  label: string;
  content: ReactNode;
};

export function Tabs({ items, labelledBy }: { items: TabItem[]; labelledBy?: string }) {
  const baseId = useId();
  const [active, setActive] = useState(items[0]?.id ?? "");

  return (
    <div>
      <div
        role="tablist"
        aria-labelledby={labelledBy}
        className="flex flex-wrap gap-1 border-b border-rule"
      >
        {items.map((item) => {
          const selected = item.id === active;
          return (
            <button
              key={item.id}
              type="button"
              role="tab"
              id={`${baseId}-${item.id}`}
              aria-selected={selected}
              aria-controls={`${baseId}-panel-${item.id}`}
              tabIndex={selected ? 0 : -1}
              className={cx(
                "rounded-t-md px-3 py-2 text-sm",
                selected ? "border border-b-surface border-rule bg-surface font-medium text-ink" : "text-ink-500",
              )}
              onClick={() => setActive(item.id)}
              onKeyDown={(event) => {
                const index = items.findIndex((entry) => entry.id === active);
                if (event.key === "ArrowRight") {
                  setActive(items[(index + 1) % items.length].id);
                }
                if (event.key === "ArrowLeft") {
                  setActive(items[(index - 1 + items.length) % items.length].id);
                }
              }}
            >
              {item.label}
            </button>
          );
        })}
      </div>
      {items.map((item) => (
        <div
          key={item.id}
          role="tabpanel"
          id={`${baseId}-panel-${item.id}`}
          aria-labelledby={`${baseId}-${item.id}`}
          hidden={item.id !== active}
          className="pt-4"
        >
          {item.content}
        </div>
      ))}
    </div>
  );
}
