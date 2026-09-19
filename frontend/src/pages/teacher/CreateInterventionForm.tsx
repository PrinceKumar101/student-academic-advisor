import { FormEvent, useState } from "react";

import { createIntervention, type Priority, type SubjectOut } from "../../api/teacher";
import { useAuth } from "../../auth/AuthContext";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Field } from "../../components/ui/Field";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Textarea } from "../../components/ui/Textarea";

type Props = {
  studentId: number;
  subjects: SubjectOut[];
  onCreated: () => void;
};

const emptyForm = {
  title: "",
  description: "",
  priority: "MEDIUM" as Priority,
  due_date: "",
  subject_id: "",
};

export function CreateInterventionForm({ studentId, subjects, onCreated }: Props) {
  const { client } = useAuth();
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<unknown>(null);
  const [saving, setSaving] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await createIntervention(client, {
        student_id: studentId,
        title: form.title,
        description: form.description || null,
        priority: form.priority,
        due_date: form.due_date || null,
        subject_id: form.subject_id ? Number(form.subject_id) : null,
      });
      setForm(emptyForm);
      onCreated();
    } catch (err) {
      setError(err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card>
      <form onSubmit={(event) => void onSubmit(event)} className="flex flex-col gap-3">
        <h2 className="text-lg">Create intervention</h2>
        <Field label="Title">
          <Input
            name="title"
            value={form.title}
            onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
            required
            maxLength={120}
          />
        </Field>
        <Field label="Description">
          <Textarea
            name="description"
            value={form.description}
            onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
          />
        </Field>
        <Field label="Priority">
          <Select
            name="priority"
            value={form.priority}
            onChange={(event) =>
              setForm((current) => ({ ...current, priority: event.target.value as Priority }))
            }
          >
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
          </Select>
        </Field>
        <Field label="Due date">
          <Input
            type="date"
            name="due_date"
            value={form.due_date}
            onChange={(event) => setForm((current) => ({ ...current, due_date: event.target.value }))}
          />
        </Field>
        <Field label="Subject">
          <Select
            name="subject_id"
            value={form.subject_id}
            onChange={(event) => setForm((current) => ({ ...current, subject_id: event.target.value }))}
          >
            <option value="">None</option>
            {subjects.map((subject) => (
              <option key={subject.id} value={subject.id}>
                {subject.code} {subject.name}
              </option>
            ))}
          </Select>
        </Field>
        <ErrorMessage error={error} />
        <Button type="submit" disabled={saving}>
          {saving ? "Creating…" : "Create intervention"}
        </Button>
      </form>
    </Card>
  );
}
