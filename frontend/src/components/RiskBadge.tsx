import type { components } from "../types/api";
import { Badge } from "./ui/Badge";

export type RiskLevel = components["schemas"]["RiskLevel"];

const LABELS: Record<RiskLevel, string> = {
  LOW: "LOW",
  MEDIUM: "MEDIUM",
  HIGH: "HIGH",
  INSUFFICIENT_DATA: "INSUFFICIENT_DATA",
};

const MARKERS: Record<RiskLevel, string> = {
  LOW: "●",
  MEDIUM: "▲",
  HIGH: "■",
  INSUFFICIENT_DATA: "◇",
};

const TONES: Record<RiskLevel, "low" | "medium" | "high" | "unknown"> = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  INSUFFICIENT_DATA: "unknown",
};

export function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <Badge role="status" aria-label={`Risk level ${LABELS[level]}`} tone={TONES[level]}>
      <span aria-hidden="true">{MARKERS[level]}</span>
      {LABELS[level]}
    </Badge>
  );
}
