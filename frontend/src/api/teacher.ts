import type { components } from "../types/api";
import type { ApiClient } from "./client";
import { toQuery } from "./query";

export type TeacherDashboardOut = components["schemas"]["TeacherDashboardOut"];
export type TeacherStudentOut = components["schemas"]["TeacherStudentOut"];
export type TeacherStudentPage = components["schemas"]["Page_TeacherStudentOut_"];
export type SubjectAnalyticsOut = components["schemas"]["SubjectAnalyticsOut"];
export type SubjectOut = components["schemas"]["SubjectOut"];
export type SubjectPage = components["schemas"]["Page_SubjectOut_"];
export type InterventionCreate = components["schemas"]["InterventionCreate"];
export type InterventionOut = components["schemas"]["InterventionOut"];
export type InterventionSuggestionsOut = components["schemas"]["InterventionSuggestionsOut"];
export type RiskLevel = components["schemas"]["RiskLevel"];
export type Priority = components["schemas"]["Priority"];

export type TeacherStudentFilters = {
  risk_level?: RiskLevel | "";
  department?: string;
  semester?: string;
  section?: string;
  subject_id?: string;
  search?: string;
  page?: number;
  page_size?: number;
};

export function getTeacherDashboard(client: ApiClient): Promise<TeacherDashboardOut> {
  return client.request<TeacherDashboardOut>("/teacher/dashboard");
}

export function listTeacherStudents(
  client: ApiClient,
  filters: TeacherStudentFilters,
): Promise<TeacherStudentPage> {
  const semester = filters.semester === "" || filters.semester === undefined ? undefined : Number(filters.semester);
  const subjectId =
    filters.subject_id === "" || filters.subject_id === undefined ? undefined : Number(filters.subject_id);
  return client.request<TeacherStudentPage>(
    `/teacher/students${toQuery({
      risk_level: filters.risk_level || undefined,
      department: filters.department || undefined,
      semester,
      section: filters.section || undefined,
      subject_id: subjectId,
      search: filters.search || undefined,
      page: filters.page,
      page_size: filters.page_size,
    })}`,
  );
}

export function getSubjectAnalytics(
  client: ApiClient,
  subjectId: number,
): Promise<SubjectAnalyticsOut> {
  return client.request<SubjectAnalyticsOut>(`/teacher/subjects/${subjectId}/analytics`);
}

export function listTaughtSubjects(client: ApiClient): Promise<SubjectPage> {
  return client.request<SubjectPage>(`/subjects${toQuery({ mine: true, page: 1, page_size: 100 })}`);
}

export function createIntervention(
  client: ApiClient,
  payload: InterventionCreate,
): Promise<InterventionOut> {
  return client.request<InterventionOut>("/interventions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function postInterventionSuggestions(
  client: ApiClient,
  studentId: number,
): Promise<InterventionSuggestionsOut> {
  return client.request<InterventionSuggestionsOut>("/ai/intervention-suggestions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: String(studentId) }),
  });
}
