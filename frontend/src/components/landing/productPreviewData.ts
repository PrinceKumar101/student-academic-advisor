import { heroDemoData } from "./heroDemoData";

/**
 * Static data for the dashboard preview. It reuses the hero's worked risk case
 * (RISK_ENGINE_SPEC.md 6.8 R3) so both figures describe one example student.
 *
 * The overall trend is the trend engine's own worked series (7.1: 72, 69, 63,
 * 55 -> slope -5.7, DECLINING). The attendance slope is the least-squares slope
 * of the six weekly readings in heroDemoData. Warning messages copy the
 * templates in engines/warnings.py verbatim: overall attendance 64.0% is below
 * the 75% floor, and the previous weeks (72.5%) against the recent four-week
 * window (59.8%) is a 12.7 pp drop, which is WARNING rather than CRITICAL.
 */

export type PreviewStat = {
  label: string;
  value: string;
  detail: string;
};

export type PreviewWarning = {
  code: string;
  severity: "WARNING" | "CRITICAL";
  message: string;
};

export const productPreviewData = {
  /** Mirrors the student navigation in components/Layout.tsx. */
  navItems: [
    "Dashboard",
    "Risk",
    "Performance",
    "Subjects",
    "What-If",
    "AI Advisor",
    "Study Planner",
    "Interventions",
    "Profile",
  ],
  pageTitle: "Student dashboard",
  asOfLabel: heroDemoData.asOfLabel,
  identityLine: "Example student · CSE sem 5 sec B",
  risk: heroDemoData.risk,
  trends: [
    { label: "Overall trend", value: "DECLINING", detail: "slope -5.7" },
    { label: "Attendance trend", value: "DECLINING", detail: "slope -4.4" },
  ] satisfies PreviewStat[],
  /** GET /students/{id}/overview returns top_factors as component keys. */
  topFactors: heroDemoData.factors.map((factor) => factor.key),
  warnings: [
    {
      code: "ATTENDANCE_BELOW_FLOOR",
      severity: "WARNING",
      message: "Overall attendance is 64.0%, below 75.0%.",
    },
    {
      code: "ATTENDANCE_DROP",
      severity: "WARNING",
      message: "Attendance dropped from 72.5% to 59.8% over the last 4 weeks.",
    },
  ] satisfies PreviewWarning[],
};
