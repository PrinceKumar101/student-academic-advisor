import { FormEvent, useState } from "react";

import { postWhatIf, type WhatIfOut, type WhatIfOverrides } from "../../api/student";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { RiskBadge } from "../../components/RiskBadge";
import { SimpleTable } from "../../components/SimpleTable";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Field } from "../../components/ui/Field";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { displayValue } from "../../lib/display";

const FIELDS: Array<{ key: keyof WhatIfOverrides; label: string }> = [
  { key: "attendance_percent", label: "Attendance percent" },
  { key: "internal_percent", label: "Internal percent" },
  { key: "quiz_percent", label: "Quiz percent" },
  { key: "assignment_percent", label: "Assignment percent" },
  { key: "assignment_submission_rate", label: "Assignment submission rate" },
  { key: "study_hours_per_day", label: "Study hours per day" },
  { key: "self_confidence", label: "Self confidence" },
];

export function WhatIfPage() {
  const { client } = useAuth();
  const [draft, setDraft] = useState<Record<string, string>>(
    Object.fromEntries(FIELDS.map((field) => [field.key, ""])),
  );
  const [result, setResult] = useState<WhatIfOut | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const overrides: WhatIfOverrides = {};
    for (const field of FIELDS) {
      const raw = draft[field.key]?.trim();
      if (raw) {
        overrides[field.key] = Number(raw);
      }
    }
    setError(null);
    setSubmitting(true);
    try {
      setResult(await postWhatIf(client, overrides));
    } catch (err) {
      setResult(null);
      setError(err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <PageHeader
        title="What-If"
        description="Only filled fields are sent. Nothing is saved. Risk indicator, not a prediction."
      />
      <Card>
        <form onSubmit={(event) => void onSubmit(event)} className="grid gap-3 sm:grid-cols-2">
          {FIELDS.map((field) => (
            <Field key={field.key} label={field.label}>
              <Input
                name={field.key}
                inputMode="decimal"
                value={draft[field.key]}
                onChange={(event) =>
                  setDraft((current) => ({ ...current, [field.key]: event.target.value }))
                }
              />
            </Field>
          ))}
          <div className="sm:col-span-2">
            <Button type="submit" disabled={submitting}>
              {submitting ? "Simulating…" : "Simulate"}
            </Button>
          </div>
        </form>
      </Card>
      {submitting ? <Loading label="Simulating…" /> : null}
      <ErrorMessage error={error} />
      {!result && !error && !submitting ? (
        <EmptyState title="No simulation yet" detail="Fill any fields and simulate. Nothing is saved." />
      ) : null}
      {result ? (
        <Card className="saa-enter">
          <p className="break-words">
            Current {displayValue(result.current.score)} <RiskBadge level={result.current.level} />{" "}
            → simulated {displayValue(result.simulated.score)}{" "}
            <RiskBadge level={result.simulated.level} /> · difference{" "}
            {displayValue(result.difference)} · persisted {result.persisted ? "yes" : "no"}
          </p>
          <h2 className="mt-4 text-lg">Changed factors</h2>
          <div className="mt-2">
            {result.changed_factors.length === 0 ? (
              <EmptyState title="No changed factors" />
            ) : (
              <SimpleTable
                caption="Changed factors"
                columns={["Key", "From", "To", "Risk from", "Risk to", "Contribution delta", "Hypothetical"]}
                rows={result.changed_factors.map((factor) => [
                  factor.key,
                  factor.from_value,
                  factor.to_value,
                  factor.risk_from,
                  factor.risk_to,
                  factor.contribution_delta,
                  factor.hypothetical ? "yes" : "no",
                ])}
              />
            )}
          </div>
        </Card>
      ) : null}
    </section>
  );
}
