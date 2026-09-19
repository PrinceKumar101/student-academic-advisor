import { Alert } from "./ui/Alert";

export function FallbackBanner({
  source,
  reason,
}: {
  source: "AI" | "FALLBACK";
  reason?: string | null;
}) {
  if (source !== "FALLBACK") {
    return null;
  }
  return (
    <Alert tone="warning" label="Fallback banner">
      Fallback: this response was generated without the AI
      {reason ? ` (${reason})` : ""}.
    </Alert>
  );
}
