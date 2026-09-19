import type { RiskOut, StudentOverviewOut, TrendsOut } from "../api/student";
import type {
  SubjectAnalyticsOut,
  SubjectPage,
  TeacherDashboardOut,
  TeacherStudentPage,
} from "../api/teacher";
import { overviewFixture } from "./studentFixtures";

export function dashboardFixture(): TeacherDashboardOut {
  return {
    as_of: "2026-09-19",
    group_size: 20,
    risk_counts: { HIGH: 4, MEDIUM: 10, LOW: 6 },
    mean_attendance: 78.5,
    mean_marks: 64.2,
    subject_performance: [{ subject_id: 1, code: "CS301", name: "DSA", mean_percent: 61 }],
    trend_distribution: { DECLINING: 8, STABLE: 7, IMPROVING: 5 },
  };
}

export function studentPageFixture(overrides: Partial<TeacherStudentPage> = {}): TeacherStudentPage {
  return {
    items: [
      {
        id: 12,
        student_code: "CS2025001",
        full_name: "Rahul Venn",
        department: "CSE",
        semester: 5,
        section: "B",
        risk_score: 82,
        risk_level: "HIGH",
        attendance_percent: 64,
        marks_percent: 55,
        trend_label: "DECLINING",
      },
      {
        id: 3,
        student_code: "CS2025003",
        full_name: "Low Risk",
        department: "CSE",
        semester: 5,
        section: "A",
        risk_score: 20,
        risk_level: "LOW",
        attendance_percent: 92,
        marks_percent: 80,
        trend_label: "STABLE",
      },
    ],
    total: 2,
    page: 1,
    page_size: 20,
    ...overrides,
  };
}

export function taughtSubjectsFixture(): SubjectPage {
  return {
    items: [{ id: 1, code: "CS301", name: "DSA", semester: 5 }],
    total: 1,
    page: 1,
    page_size: 100,
  };
}

export function subjectAnalyticsFixture(): SubjectAnalyticsOut {
  return {
    ...dashboardFixture(),
    subject_id: 1,
    code: "CS301",
    name: "DSA",
    group_size: 12,
  };
}

export function teacherOverviewFixture(): StudentOverviewOut {
  return overviewFixture();
}

export function teacherRiskFixture(): RiskOut {
  return {
    student_id: 12,
    as_of: "2026-09-19",
    score: 82,
    level: "HIGH",
    escalated: false,
    escalation_reason: null,
    data_completeness: 1,
    config_version: "1.0",
    components: [
      {
        key: "attendance",
        label: "Attendance",
        available: true,
        raw_value: 64,
        unit: "%",
        risk: 65,
        weight: 0.25,
        effective_weight: 0.25,
        contribution: 16.25,
        level: "HIGH",
        note: "Attendance is low",
      },
    ],
    top_factors: ["attendance"],
    flags: [],
  };
}

export function teacherTrendsFixture(): TrendsOut {
  const series = {
    label: "DECLINING" as const,
    slope: -5.7,
    point_count: 4,
    first: 72,
    last: 55,
    mean: 62,
    sudden_change: null,
    points: [
      { on: "2026-08-01", value: 72 },
      { on: "2026-08-15", value: 69 },
      { on: "2026-09-01", value: 63 },
      { on: "2026-09-15", value: 55 },
    ],
  };
  return {
    student_id: 12,
    as_of: "2026-09-19",
    overall: series,
    by_type: [],
    by_subject: [],
    attendance: series,
    risk: series,
  };
}

export function subjectAnalysisFixture() {
  return {
    student_id: 12,
    as_of: "2026-09-19",
    subjects: [
      {
        subject_id: 1,
        code: "CS301",
        name: "DSA",
        performance_percent: 55,
        band: "HIGH_CONCERN" as const,
        attendance_percent: 64,
        attendance_alert: true,
      },
    ],
  };
}
