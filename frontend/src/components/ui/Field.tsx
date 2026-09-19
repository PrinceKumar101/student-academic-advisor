import type { ReactNode } from "react";

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block text-sm font-medium text-ink-700">
      {label}
      <span className="mt-1 block font-normal">{children}</span>
    </label>
  );
}
