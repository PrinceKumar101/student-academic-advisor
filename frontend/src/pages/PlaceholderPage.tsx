import { Card } from "../components/ui/Card";
import { PageHeader } from "../components/ui/PageHeader";

export function PlaceholderPage({ title }: { title: string }) {
  return (
    <section>
      <PageHeader title={title} />
      <Card>
        <p className="text-sm text-ink-700">This page will be implemented in a later phase.</p>
      </Card>
    </section>
  );
}
