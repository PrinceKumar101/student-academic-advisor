import { EmptyState } from "../../components/EmptyState";
import { SimpleTable } from "../../components/SimpleTable";
import { Card } from "../../components/ui/Card";
import { displayValue } from "../../lib/display";
import type { SubjectAnalyticsOut, TeacherDashboardOut } from "../../api/teacher";

type Summary = TeacherDashboardOut | SubjectAnalyticsOut;

export function ClassSummary({ data }: { data: Summary }) {
  return (
    <div className="flex flex-col gap-4">
      <Card>
        <p className="text-sm text-ink-500">
          As of {data.as_of} · group size {data.group_size}
          {"subject_id" in data ? ` · ${data.code} ${data.name}` : ""}
        </p>
        <p className="mt-2 break-words font-serif text-xl">
          Mean attendance {displayValue(data.mean_attendance)} · Mean marks{" "}
          {displayValue(data.mean_marks)}
        </p>
      </Card>
      <Card title="Risk counts">
        <div className="mt-3">
          {Object.keys(data.risk_counts).length === 0 ? (
            <EmptyState title="No risk counts" />
          ) : (
            <SimpleTable
              caption="Risk counts"
              columns={["Level", "Count"]}
              rows={Object.entries(data.risk_counts).map(([level, count]) => [level, count])}
            />
          )}
        </div>
      </Card>
      <Card title="Subject performance">
        <div className="mt-3">
          {data.subject_performance.length === 0 ? (
            <EmptyState title="No subject performance" />
          ) : (
            <SimpleTable
              caption="Subject performance"
              columns={["Code", "Name", "Mean %"]}
              rows={data.subject_performance.map((subject) => [
                subject.code,
                subject.name,
                subject.mean_percent,
              ])}
            />
          )}
        </div>
      </Card>
      <Card title="Trend distribution">
        <div className="mt-3">
          {Object.keys(data.trend_distribution).length === 0 ? (
            <EmptyState title="No trend distribution" />
          ) : (
            <SimpleTable
              caption="Trend distribution"
              columns={["Label", "Count"]}
              rows={Object.entries(data.trend_distribution).map(([label, count]) => [label, count])}
            />
          )}
        </div>
      </Card>
    </div>
  );
}
