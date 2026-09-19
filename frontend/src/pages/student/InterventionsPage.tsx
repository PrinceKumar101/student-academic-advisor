import { useState } from "react";

import {
  getInterventionProgress,
  listInterventions,
  patchIntervention,
  type InterventionOut,
  type InterventionProgressOut,
} from "../../api/student";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { RiskBadge } from "../../components/RiskBadge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Field } from "../../components/ui/Field";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { displayValue, nextStudentInterventionStatus } from "../../lib/display";
import { useAsync } from "../../lib/useAsync";

export function InterventionsPage() {
  const { client } = useAuth();
  const [refresh, setRefresh] = useState(0);
  const [error, setError] = useState<unknown>(null);
  const [progress, setProgress] = useState<Record<number, InterventionProgressOut>>({});
  const [notes, setNotes] = useState<Record<number, string>>({});
  const state = useAsync(() => listInterventions(client), [client, refresh]);

  async function advance(item: InterventionOut) {
    const next = nextStudentInterventionStatus(item.status);
    if (!next) {
      return;
    }
    setError(null);
    try {
      await patchIntervention(client, item.id, {
        status: next,
        completion_note: notes[item.id] || undefined,
      });
      setRefresh((value) => value + 1);
    } catch (err) {
      setError(err);
    }
  }

  async function loadProgress(id: number) {
    setError(null);
    try {
      const result = await getInterventionProgress(client, id);
      setProgress((current) => ({ ...current, [id]: result }));
    } catch (err) {
      setError(err);
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <PageHeader title="Interventions" description="Risk indicator, not a prediction." />
      {state.status === "loading" ? <Loading /> : null}
      {state.status === "error" ? <ErrorMessage error={state.error} /> : null}
      <ErrorMessage error={error} />
      {state.status === "success" ? (
        state.data.length === 0 ? (
          <EmptyState title="No interventions" />
        ) : (
          <ul className="flex flex-col gap-4">
            {state.data.map((item) => {
              const next = nextStudentInterventionStatus(item.status);
              const itemProgress = progress[item.id];
              return (
                <li key={item.id} className="saa-enter">
                  <Card>
                    <p className="font-medium">
                      {item.title} · {item.status} · {item.priority}
                    </p>
                    {item.description ? <p className="mt-1 text-sm text-ink-700">{item.description}</p> : null}
                    <p className="mt-1 text-sm text-ink-500">Due {displayValue(item.due_date)}</p>
                    <div className="mt-3">
                      <Field label="Completion note">
                        <Input
                          value={notes[item.id] ?? item.completion_note ?? ""}
                          onChange={(event) =>
                            setNotes((current) => ({ ...current, [item.id]: event.target.value }))
                          }
                        />
                      </Field>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {next ? (
                        <Button onClick={() => void advance(item)}>Mark {next}</Button>
                      ) : null}
                      <Button variant="secondary" onClick={() => void loadProgress(item.id)}>
                        Show progress
                      </Button>
                    </div>
                    {itemProgress ? (
                      <p className="mt-3 text-sm">
                        Baseline {displayValue(itemProgress.baseline.score)}{" "}
                        <RiskBadge level={itemProgress.baseline.level} /> → current{" "}
                        {displayValue(itemProgress.current.score)}{" "}
                        <RiskBadge level={itemProgress.current.level} /> · change{" "}
                        {displayValue(itemProgress.change)} · {itemProgress.direction}.{" "}
                        {itemProgress.note}
                      </p>
                    ) : null}
                  </Card>
                </li>
              );
            })}
          </ul>
        )
      ) : null}
    </section>
  );
}
