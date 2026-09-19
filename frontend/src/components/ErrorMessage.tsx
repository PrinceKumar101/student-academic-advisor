import { errorMessage } from "../lib/errors";
import { Alert } from "./ui/Alert";

export function ErrorMessage({ error }: { error: unknown }) {
  if (!error) {
    return null;
  }
  return <Alert tone="error">{errorMessage(error)}</Alert>;
}
