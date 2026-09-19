import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  getOverview,
  getRisk,
  getSubjectAnalysis,
  getTrends,
  listInterventions,
  postAnalysis,
  type AnalysisOut,
  type InterventionOut,
} from "../../api/student";
import { listTaughtSubjects, postInterventionSuggestions } from "../../api/teacher";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { FallbackBanner } from "../../components/FallbackBanner";
import { Loading } from "../../components/Loading";
import { RiskGauge } from "../../components/RiskGauge";
import { SimpleTable } from "../../components/SimpleTable";
import { TrendLineChart } from "../../components/charts/TrendLineChart";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { PageHeader } from "../../components/ui/PageHeader";
import { displayValue } from "../../lib/display";
import { useAsync } from "../../lib/useAsync";
import { CreateInterventionForm } from "./CreateInterventionForm";

export function TeacherStudentDetailPage() {
  const { studentId } = useParams();
  const id = Number(studentId);
  const { client } = useAuth();
  const [refresh, setRefresh] = useState(0);
  const [analysis, setAnalysis] = useState<AnalysisOut | null>(null);
  const [analysisError, setAnalysisError] = useState<unknown>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [suggestionsError, setSuggestionsError] = useState<unknown>(null);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Awaited<
    ReturnType<typeof postInterventionSuggestions>
  > | null>(null);

  const state = useAsync(async () => {
    if (!Number.isInteger(id) || id <= 0) {
      throw new Error("Invalid student");
    }
    const [overview, risk, trends, subjects, interventions, taught] = await Promise.all([
      getOverview(client, id),
      getRisk(client, id),
      getTrends(client, id),
      getSubjectAnalysis(client, id),
      listInterventions(client, { student_id: id }),
      listTaughtSubjects(client),
    ]);
    return { overview, risk, trends, subjects, interventions, taught };
  }, [client, id, refresh]);

  async function loadAnalysis() {
    setAnalysisError(null);
    setAnalysisLoading(true);
    try {
      setAnalysis(await postAnalysis(client, false, id));
    } catch (err) {
      setAnalysis(null);
      setAnalysisError(err);
    } finally {
      setAnalysisLoading(false);
    }
  }

  async function loadSuggestions() {
    setSuggestionsError(null);
    setSuggestionsLoading(true);
    try {
      setSuggestions(await postInterventionSuggestions(client, id));
    } catch (err) {
      setSuggestions(null);
      setSuggestionsError(err);
    } finally {
      setSuggestionsLoading(false);
    }
  }

  return (
    <section className="flex flex-col gap-6">
      <p>
        <Link className="text-sm text-accent underline" to="/teacher/students">
          Back to students
        </Link>
      </p>
      <PageHeader title="Student detail" description="Risk indicator, not a prediction." />
      {state.status === "loading" ? <Loading /> : null}
      {state.status === "error" ? <ErrorMessage error={state.error} /> : null}
      {state.status === "success" ? (
        <>
          <OverviewBlock
            overview={state.data.overview}
            risk={state.data.risk}
            interventions={state.data.interventions}
          />
          <Card title="Trends">
            <div className="mt-3 flex flex-col gap-4">
              <TrendLineChart title="Assessment trend" series={state.data.trends.overall} />
              <TrendLineChart title="Attendance trend" series={state.data.trends.attendance} />
            </div>
          </Card>
          <Card title="Subjects">
            <div className="mt-3">
              {state.data.subjects.subjects.length === 0 ? (
                <EmptyState title="No subject analysis" />
              ) : (
                <SimpleTable
                  caption="Subject analysis"
                  columns={["Code", "Name", "Performance %", "Band", "Attendance %", "Attendance alert"]}
                  rows={state.data.subjects.subjects.map((subject) => [
                    subject.code,
                    subject.name,
                    subject.performance_percent,
                    subject.band,
                    subject.attendance_percent,
                    subject.attendance_alert ? "yes" : "no",
                  ])}
                />
              )}
            </div>
          </Card>
          <Card title="AI analysis">
            <div className="mt-3">
              <Button onClick={() => void loadAnalysis()} disabled={analysisLoading}>
                {analysisLoading ? "Loading analysis…" : "Get analysis"}
              </Button>
              {analysisLoading ? <div className="mt-3"><Loading label="Loading analysis…" /></div> : null}
              <div className="mt-3">
                <ErrorMessage error={analysisError} />
              </div>
              {analysis ? (
                <div className="mt-3 flex flex-col gap-4 md:flex-row">
                  <Card as="aside" className="flex-1">
                    <h3 className="text-base">Facts</h3>
                    <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs">
                      {JSON.stringify(analysis.facts, null, 2)}
                    </pre>
                  </Card>
                  <Card as="aside" className="flex-1">
                    <h3 className="text-base">AI advice</h3>
                    <div className="mt-2 flex flex-col gap-2">
                      <FallbackBanner source={analysis.source} reason={analysis.fallback_reason} />
                      <p>{analysis.advice.summary}</p>
                    </div>
                  </Card>
                </div>
              ) : null}
            </div>
          </Card>
          <CreateInterventionForm
            studentId={id}
            subjects={state.data.taught.items}
            onCreated={() => setRefresh((value) => value + 1)}
          />
          <Card title="Suggested interventions">
            <div className="mt-3">
              <Button onClick={() => void loadSuggestions()} disabled={suggestionsLoading}>
                {suggestionsLoading ? "Loading suggestions…" : "Get suggestions"}
              </Button>
              <div className="mt-3">
                <ErrorMessage error={suggestionsError} />
              </div>
              {suggestions ? (
                <div className="mt-3 flex flex-col gap-3">
                  <FallbackBanner source={suggestions.source} reason={suggestions.fallback_reason} />
                  {suggestions.suggestions.length === 0 ? (
                    <EmptyState title="No suggestions" />
                  ) : (
                    <SimpleTable
                      caption="Suggested interventions"
                      columns={["Title", "Priority", "Reason"]}
                      rows={suggestions.suggestions.map((item) => [
                        item.title,
                        item.priority,
                        item.reason,
                      ])}
                    />
                  )}
                </div>
              ) : null}
            </div>
          </Card>
        </>
      ) : null}
    </section>
  );
}

function OverviewBlock({
  overview,
  risk,
  interventions,
}: {
  overview: Awaited<ReturnType<typeof getOverview>>;
  risk: Awaited<ReturnType<typeof getRisk>>;
  interventions: InterventionOut[];
}) {
  return (
    <>
      <Card>
        <p>
          {overview.profile.full_name} · {overview.profile.student_code} · {overview.profile.department}{" "}
          sem {overview.profile.semester} sec {overview.profile.section} · as of {overview.as_of}
        </p>
        <div className="mt-2">
          <RiskGauge score={overview.risk.score} level={overview.risk.level} />
        </div>
        <p className="mt-1 text-sm text-ink-500">Completeness {displayValue(risk.data_completeness)}</p>
      </Card>
      <Card title="Top factors">
        <div className="mt-3">
          {overview.top_factors.length === 0 ? (
            <EmptyState title="No top factors" />
          ) : (
            <ul className="list-disc pl-5 text-sm">
              {overview.top_factors.map((factor) => (
                <li key={factor}>{factor}</li>
              ))}
            </ul>
          )}
        </div>
      </Card>
      <Card title="Warnings">
        <div className="mt-3">
          {overview.warnings.length === 0 ? (
            <EmptyState title="No warnings" />
          ) : (
            <SimpleTable
              caption="Early warnings"
              columns={["Code", "Severity", "Message"]}
              rows={overview.warnings.map((warning) => [warning.code, warning.severity, warning.message])}
            />
          )}
        </div>
      </Card>
      <Card title="Risk components">
        <div className="mt-3">
          {risk.components.length === 0 ? (
            <EmptyState title="No components" />
          ) : (
            <SimpleTable
              caption="Risk components"
              columns={["Key", "Risk", "Weight", "Contribution", "Level", "Note"]}
              rows={risk.components.map((component) => [
                component.key,
                component.risk,
                component.weight,
                component.contribution,
                component.level,
                component.note,
              ])}
            />
          )}
        </div>
      </Card>
      <Card title="Interventions">
        <div className="mt-3">
          {interventions.length === 0 ? (
            <EmptyState title="No interventions" />
          ) : (
            <SimpleTable
              caption="Interventions"
              columns={["Title", "Status", "Priority", "Due"]}
              rows={interventions.map((item) => [item.title, item.status, item.priority, item.due_date])}
            />
          )}
        </div>
      </Card>
    </>
  );
}
