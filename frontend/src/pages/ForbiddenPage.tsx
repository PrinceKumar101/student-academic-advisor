import { Link } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";

export function ForbiddenPage() {
  const { user, logout } = useAuth();
  const home = user?.role === "TEACHER" ? "/teacher" : user ? "/student" : "/login";

  return (
    <main className="flex min-h-screen items-center justify-center bg-paper p-6">
      <Card className="w-full max-w-md">
        <h1 className="text-3xl">Forbidden</h1>
        <p className="mt-2 text-sm text-ink-700">You do not have access to that page.</p>
        <p className="mt-4">
          <Link className="text-accent underline" to={home}>
            {user ? "Go to your dashboard" : "Log in"}
          </Link>
        </p>
        {user ? (
          <Button className="mt-4" variant="secondary" onClick={() => void logout()}>
            Log out
          </Button>
        ) : null}
      </Card>
    </main>
  );
}
