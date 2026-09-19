import { getRisk } from "../../api/student";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { RiskGauge } from "../../components/RiskGauge";
import { SimpleTable } from "../../components/SimpleTable";
import { Card } from "../../components/ui/Card";
import { PageHeader } from "../../components/ui/PageHeader";
import { RISK_DISCLAIMER, displayValue } from "../../lib/display";
import { useAsync } from "../../lib/useAsync";

export function RiskPage() {
  const { client } = useAuth();
  const state = useAsync(() => getRisk(client), [client]);

  return (
    <section className="flex flex-col gap-4">
      <PageHeader title="Risk" description={`${RISK_DISCLAIMER} Values come from the backend.`} />
      {state.status === "loading" ? <Loading /> : null}
      {state.status === "error" ? <ErrorMessage error={state.error} /> : null}
      {state.status === "success" ? (
        <>
          <Card>
            <RiskGauge score={state.data.score} level={state.data.level} />
            <p className="mt-2 text-sm text-ink-500">As of {state.data.as_of}</p>
            <p className="mt-2 text-sm text-ink-500">Completeness {displayValue(state.data.data_completeness)}</p>
            {state.data.escalated ? (
              <p className="mt-2 text-sm">Escalated: {displayValue(state.data.escalation_reason)}</p>
            ) : null}
          </Card>
          <Card title="Flags">
            <div className="mt-3">
              {state.data.flags.length === 0 ? (
                <EmptyState title="No flags" />
              ) : (
                <ul className="list-disc pl-5 text-sm">
                  {state.data.flags.map((flag) => (
                    <li key={flag}>{flag}</li>
                  ))}
                </ul>
              )}
            </div>
          </Card>
          <Card title="Top factors">
            <div className="mt-3">
              {state.data.top_factors.length === 0 ? (
                <EmptyState title="No top factors" />
              ) : (
                <ul className="list-disc pl-5 text-sm">
                  {state.data.top_factors.map((factor) => (
                    <li key={factor}>{factor}</li>
                  ))}
                </ul>
              )}
            </div>
          </Card>
          <Card title="Components">
            <div className="mt-3">
              {state.data.components.length === 0 ? (
                <EmptyState title="No components" />
              ) : (
                <SimpleTable
                  caption="Risk components"
                  columns={[
                    "Key",
                    "Label",
                    "Available",
                    "Raw",
                    "Unit",
                    "Risk",
                    "Weight",
                    "Effective weight",
                    "Contribution",
                    "Level",
                    "Note",
                  ]}
                  rows={state.data.components.map((component) => [
                    component.key,
                    component.label,
                    component.available ? "yes" : "no",
                    component.raw_value,
                    component.unit,
                    component.risk,
                    component.weight,
                    component.effective_weight,
                    component.contribution,
                    component.level,
                    component.note,
                  ])}
                />
              )}
            </div>
          </Card>
        </>
      ) : null}
    </section>
  );
}
