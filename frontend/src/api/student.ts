import type { components } from "../types/api";
import type { ApiClient } from "./client";
import { toQuery } from "./query";

export type StudentOverviewOut = components["schemas"]["StudentOverviewOut"];
export type StudentProfileOut = components["schemas"]["StudentProfileOut"];
export type RiskOut = components["schemas"]["RiskOut"];
export type TrendsOut = components["schemas"]["TrendsOut"];
export type SubjectAnalysisListOut = components["schemas"]["SubjectAnalysisListOut"];
export type WhatIfOut = components["schemas"]["WhatIfOut"];
export type WhatIfOverrides = components["schemas"]["WhatIfOverrides"];
export type AnalysisOut = components["schemas"]["AnalysisOut"];
export type ChatOut = components["schemas"]["ChatOut"];
export type ChatHistoryOut = components["schemas"]["ChatHistoryOut"];
export type StudyHabitOut = components["schemas"]["StudyHabitOut"];
export type StudyHabitUpdate = components["schemas"]["StudyHabitUpdate"];
export type SemesterResultOut = components["schemas"]["SemesterResultOut"];
export type StudyPlanCreate = components["schemas"]["StudyPlanCreate"];
export type StudyPlanOut = components["schemas"]["StudyPlanOut"];
export type StudyPlanSummaryOut = components["schemas"]["StudyPlanSummaryOut"];
export type InterventionOut = components["schemas"]["InterventionOut"];
export type InterventionProgressOut = components["schemas"]["InterventionProgressOut"];
export type InterventionStatus = components["schemas"]["InterventionStatus"];

export function getOverview(
  client: ApiClient,
  studentId: number | "me" = "me",
): Promise<StudentOverviewOut> {
  return client.request<StudentOverviewOut>(`/students/${studentId}/overview`);
}

export function getStudentProfile(
  client: ApiClient,
  studentId: number | "me" = "me",
): Promise<StudentProfileOut> {
  return client.request<StudentProfileOut>(`/students/${studentId}`);
}

export function getRisk(client: ApiClient, studentId: number | "me" = "me"): Promise<RiskOut> {
  return client.request<RiskOut>(`/risk/${studentId}`);
}

export function getTrends(client: ApiClient, studentId: number | "me" = "me"): Promise<TrendsOut> {
  return client.request<TrendsOut>(`/trends/${studentId}`);
}

export function getSubjectAnalysis(
  client: ApiClient,
  studentId: number | "me" = "me",
): Promise<SubjectAnalysisListOut> {
  return client.request<SubjectAnalysisListOut>(`/analytics/students/${studentId}/subjects`);
}

export function postWhatIf(client: ApiClient, overrides: WhatIfOverrides): Promise<WhatIfOut> {
  return client.request<WhatIfOut>("/risk/me/what-if", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ overrides }),
  });
}

export function postAnalysis(
  client: ApiClient,
  refresh = false,
  studentId: number | "me" = "me",
): Promise<AnalysisOut> {
  return client.request<AnalysisOut>("/ai/analysis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: String(studentId), refresh }),
  });
}

export function getChatHistory(client: ApiClient): Promise<ChatHistoryOut> {
  return client.request<ChatHistoryOut>("/ai/chat/history");
}

export function postChat(client: ApiClient, question: string): Promise<ChatOut> {
  return client.request<ChatOut>("/ai/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}

export function deleteChatHistory(client: ApiClient): Promise<void> {
  return client.request<void>("/ai/chat/history", { method: "DELETE" });
}

export function getStudyHabits(client: ApiClient): Promise<StudyHabitOut> {
  return client.request<StudyHabitOut>("/students/me/study-habits");
}

export function putStudyHabits(client: ApiClient, payload: StudyHabitUpdate): Promise<StudyHabitOut> {
  return client.request<StudyHabitOut>("/students/me/study-habits", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function getSemesterResults(client: ApiClient): Promise<SemesterResultOut[]> {
  return client.request<SemesterResultOut[]>("/students/me/semester-results");
}

export function listStudyPlans(client: ApiClient): Promise<StudyPlanSummaryOut[]> {
  return client.request<StudyPlanSummaryOut[]>("/study-plans");
}

export function getStudyPlan(client: ApiClient, planId: number): Promise<StudyPlanOut> {
  return client.request<StudyPlanOut>(`/study-plans/${planId}`);
}

export function createStudyPlan(client: ApiClient, payload: StudyPlanCreate): Promise<StudyPlanOut> {
  return client.request<StudyPlanOut>("/study-plans", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function patchStudyPlanItem(
  client: ApiClient,
  planId: number,
  itemId: number,
  isCompleted: boolean,
): Promise<components["schemas"]["StudyPlanItemOut"]> {
  return client.request(`/study-plans/${planId}/items/${itemId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_completed: isCompleted }),
  });
}

export function listInterventions(
  client: ApiClient,
  filters: { student_id?: number; status?: InterventionStatus } = {},
): Promise<InterventionOut[]> {
  return client.request<InterventionOut[]>(`/interventions${toQuery(filters)}`);
}

export function patchIntervention(
  client: ApiClient,
  id: number,
  payload: components["schemas"]["InterventionPatch"],
): Promise<InterventionOut> {
  return client.request<InterventionOut>(`/interventions/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function getInterventionProgress(
  client: ApiClient,
  id: number,
): Promise<InterventionProgressOut> {
  return client.request<InterventionProgressOut>(`/interventions/${id}/progress`);
}
