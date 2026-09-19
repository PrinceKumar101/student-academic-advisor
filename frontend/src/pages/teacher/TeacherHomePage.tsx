import { getTeacherDashboard } from "../../api/teacher";
import { useAuth } from "../../auth/AuthContext";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { PageHeader } from "../../components/ui/PageHeader";
import { RISK_DISCLAIMER } from "../../lib/display";
import { useAsync } from "../../lib/useAsync";
import { ClassSummary } from "./ClassSummary";

export function TeacherHomePage() {
  const { client } = useAuth();
  const state = useAsync(() => getTeacherDashboard(client), [client]);

  return (
    <section className="flex flex-col gap-4">
      <PageHeader
        title="Teacher dashboard"
        description={`Values come from the backend. ${RISK_DISCLAIMER}`}
      />
      {state.status === "loading" ? <Loading /> : null}
      {state.status === "error" ? <ErrorMessage error={state.error} /> : null}
      {state.status === "success" ? <ClassSummary data={state.data} /> : null}
    </section>
  );
}
