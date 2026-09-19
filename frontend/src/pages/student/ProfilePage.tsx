import { FormEvent, useEffect, useState } from "react";

import { getSemesterResults, getStudentProfile, getStudyHabits, putStudyHabits } from "../../api/student";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { SimpleTable } from "../../components/SimpleTable";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Field } from "../../components/ui/Field";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { ApiError } from "../../lib/errors";
import { useAsync } from "../../lib/useAsync";

export function ProfilePage() {
  const { client } = useAuth();
  const profile = useAsync(() => getStudentProfile(client), [client]);
  const results = useAsync(() => getSemesterResults(client), [client]);
  const habits = useAsync(async () => {
    try {
      return await getStudyHabits(client);
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        return null;
      }
      throw error;
    }
  }, [client]);
  const [hours, setHours] = useState("");
  const [confidence, setConfidence] = useState("");
  const [available, setAvailable] = useState("");
  const [saveError, setSaveError] = useState<unknown>(null);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (habits.status === "success" && habits.data) {
      setHours(String(habits.data.study_hours_per_day));
      setConfidence(String(habits.data.self_confidence));
      setAvailable(String(habits.data.available_hours_per_day));
    }
  }, [habits]);

  async function onSave(event: FormEvent) {
    event.preventDefault();
    setSaveError(null);
    setSaved(false);
    setSaving(true);
    try {
      await putStudyHabits(client, {
        study_hours_per_day: Number(hours),
        self_confidence: Number(confidence),
        available_hours_per_day: Number(available),
      });
      setSaved(true);
    } catch (err) {
      setSaveError(err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <PageHeader title="Profile" description="Study habits are the only academic fields a student can edit." />
      {profile.status === "loading" ? <Loading /> : null}
      {profile.status === "error" ? <ErrorMessage error={profile.error} /> : null}
      {profile.status === "success" ? (
        <Card>
          <p>
            {profile.data.full_name} · {profile.data.student_code} · {profile.data.department} sem{" "}
            {profile.data.semester} sec {profile.data.section}
          </p>
        </Card>
      ) : null}
      <Card title="Semester results">
        <div className="mt-3">
          {results.status === "loading" ? <Loading /> : null}
          {results.status === "error" ? <ErrorMessage error={results.error} /> : null}
          {results.status === "success" ? (
            results.data.length === 0 ? (
              <EmptyState title="No semester results" />
            ) : (
              <SimpleTable
                caption="Semester results"
                columns={["Semester", "Percentage", "SGPA"]}
                rows={results.data.map((row) => [row.semester, row.percentage, row.sgpa])}
              />
            )
          ) : null}
        </div>
      </Card>
      <Card title="Study habits">
        <form onSubmit={(event) => void onSave(event)} className="mt-3 flex flex-col gap-3">
          {habits.status === "loading" ? <Loading /> : null}
          {habits.status === "error" ? <ErrorMessage error={habits.error} /> : null}
          <Field label="Study hours per day">
            <Input
              name="study_hours_per_day"
              value={hours}
              onChange={(event) => setHours(event.target.value)}
              required
            />
          </Field>
          <Field label="Self confidence">
            <Input
              name="self_confidence"
              value={confidence}
              onChange={(event) => setConfidence(event.target.value)}
              required
            />
          </Field>
          <Field label="Available hours per day">
            <Input
              name="available_hours_per_day"
              value={available}
              onChange={(event) => setAvailable(event.target.value)}
              required
            />
          </Field>
          <ErrorMessage error={saveError} />
          {saved ? <p role="status">Habits saved.</p> : null}
          <Button type="submit" disabled={saving}>
            {saving ? "Saving…" : "Save habits"}
          </Button>
        </form>
      </Card>
    </section>
  );
}
