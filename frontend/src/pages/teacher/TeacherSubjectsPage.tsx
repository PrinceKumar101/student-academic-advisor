import { FormEvent, useState } from "react";
import { useParams } from "react-router-dom";

import { getSubjectAnalytics, listTaughtSubjects } from "../../api/teacher";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Field } from "../../components/ui/Field";
import { PageHeader } from "../../components/ui/PageHeader";
import { Select } from "../../components/ui/Select";
import { useAsync } from "../../lib/useAsync";
import { ClassSummary } from "./ClassSummary";

export function TeacherSubjectsPage() {
  const { subjectId } = useParams();
  const { client } = useAuth();
  const subjects = useAsync(() => listTaughtSubjects(client), [client]);
  const [selected, setSelected] = useState(subjectId ?? "");
  const [applied, setApplied] = useState(subjectId ?? "");
  const analytics = useAsync(async () => {
    if (!applied) {
      return null;
    }
    return getSubjectAnalytics(client, Number(applied));
  }, [client, applied]);

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    setApplied(selected);
  }

  return (
    <section className="flex flex-col gap-4">
      <PageHeader title="Subject analytics" description="Risk indicator, not a prediction." />
      {subjects.status === "loading" ? <Loading /> : null}
      {subjects.status === "error" ? <ErrorMessage error={subjects.error} /> : null}
      {subjects.status === "success" ? (
        subjects.data.items.length === 0 ? (
          <EmptyState title="No taught subjects" />
        ) : (
          <Card>
            <form onSubmit={onSubmit} className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <Field label="Subject">
                <Select
                  name="subject_id"
                  value={selected}
                  onChange={(event) => setSelected(event.target.value)}
                >
                  <option value="">Select a subject</option>
                  {subjects.data.items.map((subject) => (
                    <option key={subject.id} value={subject.id}>
                      {subject.code} {subject.name}
                    </option>
                  ))}
                </Select>
              </Field>
              <Button type="submit">Load analytics</Button>
            </form>
          </Card>
        )
      ) : null}
      {analytics.status === "loading" ? <Loading /> : null}
      {analytics.status === "error" ? <ErrorMessage error={analytics.error} /> : null}
      {analytics.status === "success" && analytics.data ? <ClassSummary data={analytics.data} /> : null}
      {analytics.status === "success" && !analytics.data ? (
        <EmptyState title="Choose a subject to view analytics" />
      ) : null}
    </section>
  );
}
