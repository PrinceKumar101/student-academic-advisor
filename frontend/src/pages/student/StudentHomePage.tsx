import { getOverview } from "../../api/student";
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

export function StudentHomePage() {
  const { client } = useAuth();
  const state = useAsync(() => getOverview(client), [client]);

  return (
    <section className="flex flex-col gap-4">
      <PageHeader
        title="Student dashboard"
        description={RISK_DISCLAIMER}
      />
      {state.status === "loading" ? <Loading /> : null}
      {state.status === "error" ? <ErrorMessage error={state.error} /> : null}
      {state.status === "success" ? <OverviewBody data={state.data} /> : null}
    </section>
  );
}

function OverviewBody({ data }: { data: Awaited<ReturnType<typeof getOverview>> }) {
  return (
    <>
      <p className="break-words text-sm text-ink-500">
        {data.profile.full_name} · {data.profile.student_code} · {data.profile.department}{" "}
        sem {data.profile.semester} sec {data.profile.section} · as of {data.as_of}
      </p>
      <h2 className="text-lg">How am I doing?</h2>
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <p className="text-sm text-ink-500">Risk</p>
          <div className="mt-1">
            <RiskGauge score={data.risk.score} level={data.risk.level} />
          </div>
          {data.risk.escalated ? (
            <p className="mt-2 text-sm">
              Escalated: {displayValue(data.risk.escalation_reason)}
            </p>
          ) : null}
        </Card>
        <Card>
          <p className="text-sm text-ink-500">Overall trend</p>
          <p className="mt-1 font-serif text-2xl">{data.trend_summary.overall_label}</p>
          <p className="mt-1 text-sm text-ink-500">
            slope {displayValue(data.trend_summary.overall_slope)}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-ink-500">Attendance trend</p>
          <p className="mt-1 font-serif text-2xl">{data.trend_summary.attendance_label}</p>
          <p className="mt-1 text-sm text-ink-500">
            slope {displayValue(data.trend_summary.attendance_slope)}
          </p>
        </Card>
      </div>
      <p className="text-sm text-ink-500">Completeness {displayValue(data.risk.data_completeness)}</p>
      <Card title="Top factors">
        {data.top_factors.length === 0 ? (
          <EmptyState title="No top factors" />
        ) : (
          <ul className="mt-3 list-disc pl-5 text-sm">
            {data.top_factors.map((factor) => (
              <li key={factor}>{factor}</li>
            ))}
          </ul>
        )}
      </Card>
      <Card title="Warnings">
        <div className="mt-3">
          {data.warnings.length === 0 ? (
            <EmptyState title="No warnings" />
          ) : (
            <SimpleTable
              caption="Early warnings"
              columns={["Code", "Severity", "Message", "Metric", "Previous", "Current"]}
              rows={data.warnings.map((warning) => [
                warning.code,
                warning.severity,
                warning.message,
                warning.metric,
                warning.previous_value,
                warning.current_value,
              ])}
            />
          )}
        </div>
      </Card>
      <Card title="Open interventions">
        <div className="mt-3">
          {data.open_interventions.length === 0 ? (
            <EmptyState title="No open interventions" />
          ) : (
            <SimpleTable
              caption="Open interventions"
              columns={["Title", "Status", "Priority", "Due"]}
              rows={data.open_interventions.map((item) => [
                item.title,
                item.status,
                item.priority,
                item.due_date,
              ])}
            />
          )}
        </div>
      </Card>
    </>
  );
}
