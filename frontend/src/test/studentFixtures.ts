import type {
  AnalysisOut,
  ChatHistoryOut,
  StudyPlanOut,
  StudyPlanSummaryOut,
  StudentOverviewOut,
  WhatIfOut,
} from "../api/student";

export function overviewFixture(): StudentOverviewOut {
  return {
    student_id: 12,
    as_of: "2026-09-19",
    profile: {
      id: 12,
      student_code: "CS2025001",
      full_name: "Rahul Venn",
      department: "CSE",
      semester: 5,
      section: "B",
    },
    risk: {
      score: 82,
      level: "HIGH",
      escalated: false,
      escalation_reason: null,
      data_completeness: 1,
      config_version: "1.0",
      flags: [],
    },
    top_factors: ["internal", "attendance"],
    subjects: [],
    trend_summary: {
      overall_label: "DECLINING",
      overall_slope: -5.7,
      attendance_label: "DECLINING",
      attendance_slope: -2.2,
    },
    warnings: [
      {
        code: "ATTENDANCE_DROP",
        severity: "WARNING",
        message: "Attendance dropped",
        metric: "attendance",
        previous_value: 82,
        current_value: 67,
      },
    ],
    open_interventions: [],
  };
}

export function whatIfFixture(): WhatIfOut {
  return {
    current: { score: 64, level: "HIGH" },
    simulated: { score: 54, level: "MEDIUM" },
    difference: -10,
    persisted: false,
    changed_factors: [
      {
        key: "attendance",
        from_value: 64,
        to_value: 80,
        risk_from: 65,
        risk_to: 25,
        contribution_delta: -10,
        hypothetical: false,
      },
    ],
  };
}

export function analysisFixture(source: "AI" | "FALLBACK" = "FALLBACK"): AnalysisOut {
  return {
    source,
    generated_at: "2026-09-19T00:00:00Z",
    cached: false,
    facts: { risk_score: 82, top_factors: ["attendance"] },
    advice: {
      summary: "Focus on attendance.",
      main_concerns: [{ factor: "attendance", explanation: "Attendance is a top factor." }],
      recommendations: [{ action: "Attend class", reason: "Raise attendance", priority: "HIGH" }],
      priority: "HIGH",
    },
    fallback_reason: source === "FALLBACK" ? "NOT_CONFIGURED" : null,
  };
}

export function emptyChatHistory(): ChatHistoryOut {
  return { messages: [] };
}

export function planSummary(): StudyPlanSummaryOut {
  return {
    id: 5,
    exam_date: "2026-10-15",
    available_hours_per_day: 3,
    source: "FALLBACK",
    created_at: "2026-09-19T00:00:00Z",
    item_count: 1,
  };
}

export function planDetail(): StudyPlanOut {
  return {
    id: 5,
    exam_date: "2026-10-15",
    available_hours_per_day: 3,
    source: "FALLBACK",
    prompt_version: "plan_v1",
    created_at: "2026-09-19T00:00:00Z",
    tips: ["Start with the weakest subject."],
    fallback_reason: "NOT_CONFIGURED",
    items: [
      {
        id: 1,
        plan_date: "2026-09-20",
        subject: { id: 1, code: "CS301" },
        topic: "Trees",
        activity: "Revise notes",
        duration_minutes: 60,
        priority: "HIGH",
        is_completed: false,
        completed_at: null,
      },
    ],
  };
}
