import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { ErrorMessage } from "../components/ErrorMessage";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Field } from "../components/ui/Field";
import { Input } from "../components/ui/Input";

export function RegisterPage() {
  const { register, login, user, ready } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<unknown>(null);
  const [submitting, setSubmitting] = useState(false);

  if (ready && user) {
    return <Navigate to="/student" replace />;
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") ?? "");
    const password = String(form.get("password") ?? "");
    try {
      await register({
        email,
        password,
        full_name: String(form.get("full_name") ?? ""),
        student_code: String(form.get("student_code") ?? ""),
        department: String(form.get("department") ?? ""),
        semester: Number(form.get("semester")),
        section: String(form.get("section") ?? ""),
      });
      await login(email, password);
      navigate("/student", { replace: true });
    } catch (err) {
      setError(err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-paper p-6">
      <Card className="w-full max-w-md">
        <h1 className="mb-4 text-3xl">Register as a student</h1>
        <form onSubmit={(event) => void onSubmit(event)} className="flex flex-col gap-3">
          <Field label="Email">
            <Input name="email" type="email" required />
          </Field>
          <Field label="Password">
            <Input name="password" type="password" minLength={8} required />
          </Field>
          <Field label="Full name">
            <Input name="full_name" required />
          </Field>
          <Field label="Student code">
            <Input name="student_code" required />
          </Field>
          <Field label="Department">
            <Input name="department" required />
          </Field>
          <Field label="Semester">
            <Input name="semester" type="number" min={1} max={8} required />
          </Field>
          <Field label="Section">
            <Input name="section" required />
          </Field>
          <ErrorMessage error={error} />
          <Button type="submit" disabled={submitting}>
            {submitting ? "Creating account…" : "Create account"}
          </Button>
        </form>
        <p className="mt-4 text-sm">
          Already have an account?{" "}
          <Link className="text-accent underline" to="/login">
            Log in
          </Link>
        </p>
      </Card>
    </main>
  );
}
