import type { RiskLevel } from "../RiskBadge";

/**
 * Static demo data for the public hero. The landing page must never read a real
 * student, so these values are the risk engine's own worked R3 case
 * (RISK_ENGINE_SPEC.md 6.8): attendance 64, internal 45, assignment submission
 * 60% at 50 marks, quizzes 40, previous 55, study 1 h/day at confidence 2.
 * That case scores 67.1 / HIGH with component risks 65, 75, 51.25, 87.5, 50,
 * 62.5 and full data completeness, so every number below is one the engine
 * really produces. Notes copy the engine's templates verbatim.
 */

export type HeroFactor = {
  key: string;
  label: string;
  /** effective_weight * risk, rounded to one decimal like the API. */
  contribution: number;
  weight: number;
  level: RiskLevel;
  note: string;
};

export type HeroDemoData = {
  asOfLabel: string;
  risk: {
    score: number;
    level: RiskLevel;
    dataCompleteness: number;
  };
  attendance: {
    percent: number;
    /** The real floor from risk_config.ATTENDANCE_FLOOR_PERCENT. */
    cutoffPercent: number;
    trendLabel: string;
    slopePerWeek: number;
    /** Six weekly readings whose mean is the 64.0% overall figure. */
    weeks: number[];
  };
  factors: HeroFactor[];
  insight: {
    body: string;
    disclosure: string;
  };
};

export const heroDemoData: HeroDemoData = {
  asOfLabel: "13 Mar 2026",
  risk: {
    score: 67.1,
    level: "HIGH",
    dataCompleteness: 1,
  },
  attendance: {
    percent: 64,
    cutoffPercent: 75,
    trendLabel: "DECLINING",
    slopePerWeek: -4.4,
    weeks: [74, 71, 67, 62, 58, 52],
  },
  // top_factors: components at MEDIUM or above, by contribution, capped at three.
  factors: [
    {
      key: "internal",
      label: "Internal",
      contribution: 18.8,
      weight: 0.25,
      level: "HIGH",
      note: "Internal marks are 45.0%.",
    },
    {
      key: "attendance",
      label: "Attendance",
      contribution: 16.3,
      weight: 0.25,
      level: "HIGH",
      note: "Attendance is 64.0%, below the 75% cutoff.",
    },
    {
      key: "quizzes",
      label: "Quizzes",
      contribution: 13.1,
      weight: 0.15,
      level: "HIGH",
      note: "Quiz average is 40.0%.",
    },
  ],
  insight: {
    body:
      "Attendance has declined across the last six weeks and now sits below the 75% cutoff, " +
      "while internal marks remain the largest single contributor. Start with the subjects " +
      "where classes were missed, and clear the outstanding assignments before the next internal.",
    disclosure:
      "Python computed every number here. The AI only wrote this paragraph, and the product still works with it switched off.",
  },
};
