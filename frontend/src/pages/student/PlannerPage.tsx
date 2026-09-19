import { FormEvent, useState } from "react";

import {
  createStudyPlan,
  getStudyPlan,
  listStudyPlans,
  patchStudyPlanItem,
  type StudyPlanOut,
} from "../../api/student";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { FallbackBanner } from "../../components/FallbackBanner";
import { Loading } from "../../components/Loading";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Field } from "../../components/ui/Field";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { useAsync } from "../../lib/useAsync";

export function PlannerPage() {
  const { client } = useAuth();
  const [examDate, setExamDate] = useState("");
  const [hours, setHours] = useState("3");
  const [subjectIds, setSubjectIds] = useState("");
  const [formError, setFormError] = useState<unknown>(null);
  const [creating, setCreating] = useState(false);
  const [listRefresh, setListRefresh] = useState(0);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [plan, setPlan] = useState<StudyPlanOut | null>(null);
  const [planError, setPlanError] = useState<unknown>(null);
  const summaries = useAsync(() => listStudyPlans(client), [client, listRefresh]);

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    setFormError(null);
    setCreating(true);
    const ids = subjectIds
      .split(",")
      .map((part) => part.trim())
      .filter(Boolean)
      .map(Number)
      .filter((value) => !Number.isNaN(value));
    try {
      const created = await createStudyPlan(client, {
        exam_date: examDate,
        available_hours_per_day: Number(hours),
        ...(ids.length > 0 ? { subject_ids: ids } : {}),
      });
      setPlan(created);
      setSelectedId(created.id);
      setListRefresh((value) => value + 1);
    } catch (err) {
      setFormError(err);
    } finally {
      setCreating(false);
    }
  }

  async function openPlan(id: number) {
    setPlanError(null);
    setSelectedId(id);
    try {
      setPlan(await getStudyPlan(client, id));
    } catch (err) {
      setPlan(null);
      setPlanError(err);
    }
  }

  async function toggleItem(itemId: number, isCompleted: boolean) {
    if (!plan) {
      return;
    }
    setPlanError(null);
    try {
      const updated = await patchStudyPlanItem(client, plan.id, itemId, isCompleted);
      setPlan({
        ...plan,
        items: plan.items.map((item) => (item.id === updated.id ? updated : item)),
      });
    } catch (err) {
      setPlanError(err);
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <PageHeader title="Study Planner" description="Dates and durations come from the backend budget." />
      <Card>
        <form onSubmit={(event) => void onCreate(event)} className="flex flex-col gap-3">
          <Field label="Exam date">
            <Input
              type="date"
              name="exam_date"
              value={examDate}
              onChange={(event) => setExamDate(event.target.value)}
              required
            />
          </Field>
          <Field label="Available hours per day">
            <Input
              name="available_hours_per_day"
              inputMode="decimal"
              value={hours}
              onChange={(event) => setHours(event.target.value)}
              required
            />
          </Field>
          <Field label="Subject IDs (optional, comma-separated; empty = auto-pick)">
            <Input
              name="subject_ids"
              value={subjectIds}
              onChange={(event) => setSubjectIds(event.target.value)}
            />
          </Field>
          <ErrorMessage error={formError} />
          <Button type="submit" disabled={creating}>
            {creating ? "Generating…" : "Generate plan"}
          </Button>
        </form>
      </Card>
      <Card title="Saved plans">
        <div className="mt-3">
          {summaries.status === "loading" ? <Loading /> : null}
          {summaries.status === "error" ? <ErrorMessage error={summaries.error} /> : null}
          {summaries.status === "success" ? (
            summaries.data.length === 0 ? (
              <EmptyState title="No study plans" />
            ) : (
              <ul className="flex flex-col gap-2">
                {summaries.data.map((summary) => (
                  <li key={summary.id}>
                    <Button
                      variant="secondary"
                      className="h-auto w-full whitespace-normal text-left"
                      onClick={() => void openPlan(summary.id)}
                    >
                      Plan {summary.id} · exam {summary.exam_date} · {summary.item_count} items ·{" "}
                      {summary.source}
                    </Button>
                  </li>
                ))}
              </ul>
            )
          ) : null}
        </div>
      </Card>
      <ErrorMessage error={planError} />
      {plan && selectedId === plan.id ? (
        <Card>
          <h2 className="text-lg">Plan {plan.id}</h2>
          <div className="mt-3 flex flex-col gap-3">
            <FallbackBanner source={plan.source} reason={plan.fallback_reason} />
            <p className="text-sm">
              Exam {plan.exam_date} · {plan.available_hours_per_day} h/day
            </p>
            {plan.tips.length > 0 ? (
              <ul className="list-disc pl-5 text-sm">
                {plan.tips.map((tip) => (
                  <li key={tip}>{tip}</li>
                ))}
              </ul>
            ) : null}
            {plan.items.length === 0 ? (
              <EmptyState title="No plan items" />
            ) : (
              <ul className="flex flex-col gap-2 text-sm">
                {plan.items.map((item) => (
                  <li key={item.id} className="rounded-md border border-rule p-3">
                    <label className="flex items-start gap-2">
                      <input
                        type="checkbox"
                        checked={item.is_completed}
                        onChange={(event) => void toggleItem(item.id, event.target.checked)}
                      />
                      <span>
                        {item.plan_date} {item.subject.code}: {item.topic} — {item.activity} (
                        {item.duration_minutes} min, {item.priority})
                      </span>
                    </label>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Card>
      ) : null}
    </section>
  );
}
