export const RISK_DISCLAIMER = "Risk indicator, not a prediction.";

export function displayValue(value: string | number | boolean | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  return String(value);
}

export function nextStudentInterventionStatus(
  status: "PENDING" | "IN_PROGRESS" | "COMPLETED",
): "IN_PROGRESS" | "COMPLETED" | null {
  if (status === "PENDING") {
    return "IN_PROGRESS";
  }
  if (status === "IN_PROGRESS") {
    return "COMPLETED";
  }
  return null;
}
