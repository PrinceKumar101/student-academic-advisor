import { FormEvent, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import {
  listTaughtSubjects,
  listTeacherStudents,
  type TeacherStudentFilters,
  type TeacherStudentOut,
} from "../../api/teacher";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { Loading } from "../../components/Loading";
import { RiskBadge } from "../../components/RiskBadge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Field } from "../../components/ui/Field";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { Select } from "../../components/ui/Select";
import { displayValue } from "../../lib/display";
import { useAsync } from "../../lib/useAsync";

const emptyFilters: TeacherStudentFilters = {
  risk_level: "",
  department: "",
  semester: "",
  section: "",
  subject_id: "",
  search: "",
  page: 1,
  page_size: 20,
};

export function TeacherStudentsPage() {
  const { client } = useAuth();
  const [draft, setDraft] = useState<TeacherStudentFilters>(emptyFilters);
  const [applied, setApplied] = useState<TeacherStudentFilters>(emptyFilters);
  const [sort, setSort] = useState<"none" | "risk_desc" | "risk_asc">("risk_desc");
  const subjects = useAsync(() => listTaughtSubjects(client), [client]);
  const state = useAsync(() => listTeacherStudents(client, applied), [client, applied]);

  const rows = useMemo(() => {
    const items = state.status === "success" ? [...state.data.items] : [];
    if (sort === "none") {
      return items;
    }
    return items.sort((left, right) => compareRisk(left, right, sort === "risk_desc"));
  }, [state, sort]);

  function onApply(event: FormEvent) {
    event.preventDefault();
    setApplied({ ...draft, page: 1, page_size: draft.page_size ?? 20 });
  }

  function onClear() {
    setDraft(emptyFilters);
    setApplied(emptyFilters);
  }

  return (
    <section className="flex flex-col gap-4">
      <PageHeader title="Students" description="Risk indicator, not a prediction." />
      <Card>
        <form onSubmit={onApply} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <label htmlFor="filter-risk-level" className="block text-sm font-medium text-ink-700">
            Risk level
            <Select
              id="filter-risk-level"
              className="mt-1"
              name="risk_level"
              value={draft.risk_level ?? ""}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  risk_level: event.target.value as TeacherStudentFilters["risk_level"],
                }))
              }
            >
              <option value="">Any</option>
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="INSUFFICIENT_DATA">INSUFFICIENT_DATA</option>
            </Select>
          </label>
          <Field label="Department">
            <Input
              name="department"
              value={draft.department ?? ""}
              onChange={(event) => setDraft((current) => ({ ...current, department: event.target.value }))}
            />
          </Field>
          <Field label="Semester">
            <Input
              name="semester"
              inputMode="numeric"
              value={draft.semester ?? ""}
              onChange={(event) => setDraft((current) => ({ ...current, semester: event.target.value }))}
            />
          </Field>
          <Field label="Section">
            <Input
              name="section"
              value={draft.section ?? ""}
              onChange={(event) => setDraft((current) => ({ ...current, section: event.target.value }))}
            />
          </Field>
          <Field label="Subject">
            <Select
              name="subject_id"
              value={draft.subject_id ?? ""}
              onChange={(event) => setDraft((current) => ({ ...current, subject_id: event.target.value }))}
            >
              <option value="">Any taught subject</option>
              {subjects.status === "success"
                ? subjects.data.items.map((subject) => (
                    <option key={subject.id} value={subject.id}>
                      {subject.code} {subject.name}
                    </option>
                  ))
                : null}
            </Select>
          </Field>
          <Field label="Search">
            <Input
              name="search"
              value={draft.search ?? ""}
              onChange={(event) => setDraft((current) => ({ ...current, search: event.target.value }))}
            />
          </Field>
          <div className="flex flex-wrap items-end gap-2 sm:col-span-2 lg:col-span-3">
            <Button type="submit">Apply filters</Button>
            <Button type="button" variant="secondary" onClick={onClear}>
              Clear filters
            </Button>
          </div>
        </form>
      </Card>
      <Card>
        <Field label="Sort by risk">
          <Select value={sort} onChange={(event) => setSort(event.target.value as typeof sort)}>
            <option value="risk_desc">Highest first</option>
            <option value="risk_asc">Lowest first</option>
            <option value="none">As returned</option>
          </Select>
        </Field>
        <div className="mt-4">
          {state.status === "loading" ? <Loading /> : null}
          {state.status === "error" ? <ErrorMessage error={state.error} /> : null}
          {state.status === "success" ? (
            state.data.total === 0 ? (
              <EmptyState title="No students match these filters" />
            ) : (
              <>
                <p className="mb-3 text-sm text-ink-500">
                  Page {state.data.page} of {Math.max(1, Math.ceil(state.data.total / state.data.page_size))} ·{" "}
                  {state.data.total} students
                </p>
                <div className="max-w-full overflow-x-auto">
                  <table className="saa-table min-w-[40rem]">
                    <caption>Visible students</caption>
                    <thead>
                      <tr>
                        <th scope="col">Name</th>
                        <th scope="col">Code</th>
                        <th scope="col">Dept</th>
                        <th scope="col">Sem</th>
                        <th scope="col">Sec</th>
                        <th scope="col">Risk</th>
                        <th scope="col">Attendance %</th>
                        <th scope="col">Marks %</th>
                        <th scope="col">Trend</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((item) => (
                        <tr key={item.id}>
                          <td>
                            <Link className="text-accent underline" to={`/teacher/students/${item.id}`}>
                              {item.full_name}
                            </Link>
                          </td>
                          <td>{item.student_code}</td>
                          <td>{item.department}</td>
                          <td>{item.semester}</td>
                          <td>{item.section}</td>
                          <td>
                            {displayValue(item.risk_score)}{" "}
                            {item.risk_level ? <RiskBadge level={item.risk_level} /> : "—"}
                          </td>
                          <td>{displayValue(item.attendance_percent)}</td>
                          <td>{displayValue(item.marks_percent)}</td>
                          <td>{displayValue(item.trend_label)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="mt-3 flex gap-2">
                  <Button
                    variant="secondary"
                    disabled={state.data.page <= 1}
                    onClick={() => setApplied((current) => ({ ...current, page: (current.page ?? 1) - 1 }))}
                  >
                    Previous page
                  </Button>
                  <Button
                    variant="secondary"
                    disabled={state.data.page * state.data.page_size >= state.data.total}
                    onClick={() => setApplied((current) => ({ ...current, page: (current.page ?? 1) + 1 }))}
                  >
                    Next page
                  </Button>
                </div>
              </>
            )
          ) : null}
        </div>
      </Card>
    </section>
  );
}

function compareRisk(left: TeacherStudentOut, right: TeacherStudentOut, highFirst: boolean): number {
  const leftScore = left.risk_score;
  const rightScore = right.risk_score;
  if (leftScore === null && rightScore === null) {
    return 0;
  }
  if (leftScore === null) {
    return 1;
  }
  if (rightScore === null) {
    return -1;
  }
  return highFirst ? rightScore - leftScore : leftScore - rightScore;
}
