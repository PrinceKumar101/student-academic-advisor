import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import {
  getInterventionProgress,
  listInterventions,
  patchIntervention,
  type InterventionOut,
  type InterventionProgressOut,
  type InterventionStatus,
} from "../../api/student";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { RiskBadge } from "../../components/RiskBadge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Field } from "../../components/ui/Field";
import { PageHeader } from "../../components/ui/PageHeader";
import { Select } from "../../components/ui/Select";
import { displayValue } from "../../lib/display";
import { useAsync } from "../../lib/useAsync";

export function TeacherInterventionsPage() {
  const { client } = useAuth();
  const [draftStatus, setDraftStatus] = useState<InterventionStatus | "">("");
  const [status, setStatus] = useState<InterventionStatus | "">("");
  const [refresh, setRefresh] = useState(0);
  const [error, setError] = useState<unknown>(null);
  const [progress, setProgress] = useState<Record<number, InterventionProgressOut>>({});
  const state = useAsync(
    () => listInterventions(client, status ? { status } : {}),
    [client, status, refresh],
  );

  function onFilter(event: FormEvent) {
    event.preventDefault();
    setStatus(draftStatus);
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

  async function updateStatus(item: InterventionOut, next: InterventionStatus) {
    setError(null);
    try {
      await patchIntervention(client, item.id, { status: next });
      setRefresh((value) => value + 1);
    } catch (err) {
      setError(err);
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <PageHeader title="Teacher interventions" description="Risk indicator, not a prediction." />
      <Card>
        <form onSubmit={onFilter} className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <Field label="Status">
            <Select
              name="status"
              value={draftStatus}
              onChange={(event) => setDraftStatus(event.target.value as InterventionStatus | "")}
            >
              <option value="">Any</option>
              <option value="PENDING">PENDING</option>
              <option value="IN_PROGRESS">IN_PROGRESS</option>
              <option value="COMPLETED">COMPLETED</option>
            </Select>
          </Field>
          <Button type="submit">Apply status filter</Button>
        </form>
      </Card>
      {state.status === "loading" ? <Loading /> : null}
      {state.status === "error" ? <ErrorMessage error={state.error} /> : null}
      <ErrorMessage error={error} />
      {state.status === "success" ? (
        state.data.length === 0 ? (
          <EmptyState title="No interventions" />
        ) : (
          <ul className="flex flex-col gap-4">
            {state.data.map((item) => {
              const itemProgress = progress[item.id];
              return (
                <li key={item.id} className="saa-enter">
                  <Card>
                    <p>
                      <Link className="text-accent underline" to={`/teacher/students/${item.student_id}`}>
                        {item.title}
                      </Link>{" "}
                      · {item.status} · {item.priority}
                    </p>
                    {item.description ? <p className="mt-1 text-sm">{item.description}</p> : null}
                    <p className="mt-1 text-sm text-ink-500">Due {displayValue(item.due_date)}</p>
                    <div className="mt-3 flex flex-wrap items-end gap-3">
                      <Field label="Update status">
                        <Select
                          value={item.status}
                          onChange={(event) =>
                            void updateStatus(item, event.target.value as InterventionStatus)
                          }
                        >
                          <option value="PENDING">PENDING</option>
                          <option value="IN_PROGRESS">IN_PROGRESS</option>
                          <option value="COMPLETED">COMPLETED</option>
                        </Select>
                      </Field>
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
