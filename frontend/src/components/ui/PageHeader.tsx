export function PageHeader({ title, description }: { title: string; description?: string }) {
  return (
    <header className="mb-4">
      <h1 className="text-3xl">{title}</h1>
      {description ? <p className="mt-1 text-sm text-ink-500">{description}</p> : null}
    </header>
  );
}
