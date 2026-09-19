import { getSubjectAnalysis } from "../../api/student";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { SimpleTable } from "../../components/SimpleTable";
import { Card } from "../../components/ui/Card";
import { PageHeader } from "../../components/ui/PageHeader";
import { useAsync } from "../../lib/useAsync";

export function SubjectsPage() {
  const { client } = useAuth();
  const state = useAsync(() => getSubjectAnalysis(client), [client]);

  return (
    <section className="flex flex-col gap-4">
      <PageHeader title="Subjects" description="Bands and attendance alerts come from the backend." />
      {state.status === "loading" ? <Loading /> : null}
      {state.status === "error" ? <ErrorMessage error={state.error} /> : null}
      {state.status === "success" ? (
        <Card>
          {state.data.subjects.length === 0 ? (
            <EmptyState title="No subject analysis" detail={`As of ${state.data.as_of}`} />
          ) : (
            <SimpleTable
              caption={`Subject analysis as of ${state.data.as_of}`}
              columns={["Code", "Name", "Performance %", "Band", "Attendance %", "Attendance alert"]}
              rows={state.data.subjects.map((subject) => [
                subject.code,
                subject.name,
                subject.performance_percent,
                subject.band,
                subject.attendance_percent,
                subject.attendance_alert ? "yes" : "no",
              ])}
            />
          )}
        </Card>
      ) : null}
    </section>
  );
}
