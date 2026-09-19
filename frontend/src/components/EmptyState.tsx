export function EmptyState({ title, detail }: { title: string; detail?: string }) {
  return (
    <div role="status" className="rounded-md border border-dashed border-rule bg-ink-50 px-4 py-6 text-sm">
      <p className="font-medium text-ink-700">{title}</p>
      {detail ? <p className="mt-1 text-ink-500">{detail}</p> : null}
    </div>
  );
}
