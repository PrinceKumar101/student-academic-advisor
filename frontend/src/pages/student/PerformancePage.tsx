import { getTrends } from "../../api/student";
import { useAuth } from "../../auth/AuthContext";
import { TrendLineChart } from "../../components/charts/TrendLineChart";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { PageHeader } from "../../components/ui/PageHeader";
import { Tabs } from "../../components/ui/Tabs";
import { displayValue } from "../../lib/display";
import { useAsync } from "../../lib/useAsync";

export function PerformancePage() {
  const { client } = useAuth();
  const state = useAsync(() => getTrends(client), [client]);

  return (
    <section className="flex flex-col gap-4">
      <PageHeader title="Performance" description="Trend labels and slopes come from the backend." />
      {state.status === "loading" ? <Loading /> : null}
      {state.status === "error" ? <ErrorMessage error={state.error} /> : null}
      {state.status === "success" ? (
        <>
          <p className="text-sm text-ink-500">As of {state.data.as_of}</p>
          <TrendLineChart title="Assessment trend" series={state.data.overall} />
          <TrendLineChart title="Attendance trend" series={state.data.attendance} />
          <Tabs
            items={[
              {
                id: "type",
                label: "By type",
                content:
                  state.data.by_type.length === 0 ? (
                    <EmptyState title="No type series" />
                  ) : (
                    <ul className="list-disc pl-5 text-sm">
                      {state.data.by_type.map((series) => (
                        <li key={series.type}>
                          {series.type}: {series.label} (slope {displayValue(series.slope)})
                        </li>
                      ))}
                    </ul>
                  ),
              },
              {
                id: "subject",
                label: "By subject",
                content:
                  state.data.by_subject.length === 0 ? (
                    <EmptyState title="No subject series" />
                  ) : (
                    <ul className="list-disc pl-5 text-sm">
                      {state.data.by_subject.map((series) => (
                        <li key={series.subject_id}>
                          {series.subject_code}: {series.label} (slope {displayValue(series.slope)})
                        </li>
                      ))}
                    </ul>
                  ),
              },
            ]}
          />
        </>
      ) : null}
    </section>
  );
}
