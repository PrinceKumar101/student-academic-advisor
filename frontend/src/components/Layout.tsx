import { FormEvent, useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate, useSearchParams } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { RISK_DISCLAIMER } from "../lib/display";
import { cx } from "../lib/cx";
import { Button } from "./ui/Button";
import { Field } from "./ui/Field";
import { Input } from "./ui/Input";
import { Modal } from "./ui/Modal";

const studentLinks = [
  { to: "/student", label: "Dashboard" },
  { to: "/student/risk", label: "Risk" },
  { to: "/student/performance", label: "Performance" },
  { to: "/student/subjects", label: "Subjects" },
  { to: "/student/what-if", label: "What-If" },
  { to: "/student/advisor", label: "AI Advisor" },
  { to: "/student/planner", label: "Study Planner" },
  { to: "/student/interventions", label: "Interventions" },
  { to: "/student/profile", label: "Profile" },
];

const teacherLinks = [
  { to: "/teacher", label: "Dashboard" },
  { to: "/teacher/students", label: "Students" },
  { to: "/teacher/interventions", label: "Interventions" },
  { to: "/teacher/subjects", label: "Subjects" },
];

export function Layout() {
  const { user, logout } = useAuth();
  const links = user?.role === "TEACHER" ? teacherLinks : studentLinks;
  const [disclaimerOpen, setDisclaimerOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMenuOpen(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="min-h-screen max-w-full overflow-x-clip bg-paper">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-surface focus:px-3 focus:py-2"
      >
        Skip to main content
      </a>
      <header className="border-b border-rule bg-surface">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
          <div className="min-w-0">
            <p className="font-serif text-lg text-ink">Student Academic Advisor</p>
            <p className="break-words text-sm text-ink-500">
              {user?.full_name} ({user?.role})
            </p>
          </div>
          <AsOfControl />
          <div className="flex flex-wrap gap-2">
            <Button
              className="md:hidden"
              variant="secondary"
              aria-expanded={menuOpen}
              aria-controls="app-nav"
              onClick={() => setMenuOpen((open) => !open)}
            >
              {menuOpen ? "Close menu" : "Open menu"}
            </Button>
            <Button variant="secondary" onClick={() => setDisclaimerOpen(true)}>
              About risk
            </Button>
            <Button variant="ghost" onClick={() => void logout()}>
              Log out
            </Button>
          </div>
        </div>
      </header>
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 md:flex-row">
        <nav
          id="app-nav"
          aria-label="Main"
          className={cx(
            "flex-col gap-2 md:flex md:w-52 md:flex-nowrap",
            menuOpen ? "flex" : "hidden md:flex",
          )}
        >
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/student" || link.to === "/teacher"}
              onClick={() => setMenuOpen(false)}
              className={({ isActive }) =>
                cx(
                  "rounded-md px-3 py-2 text-sm",
                  isActive ? "bg-accent text-surface" : "text-ink-700 hover:bg-ink-50",
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <main id="main-content" tabIndex={-1} className="min-w-0 max-w-full flex-1 break-words">
          <Outlet />
        </main>
      </div>
      <Modal open={disclaimerOpen} title="About risk" onClose={() => setDisclaimerOpen(false)}>
        <p className="text-sm text-ink-700">
          {RISK_DISCLAIMER} Scores, percentages and trend labels come from the backend. Colour is a
          secondary cue; the printed level is authoritative.
        </p>
      </Modal>
    </div>
  );
}

function AsOfControl() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const current = params.get("as_of") ?? "";
  const [draft, setDraft] = useState(current);

  useEffect(() => {
    setDraft(current);
  }, [current]);

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    const next = new URLSearchParams(params);
    if (draft) {
      next.set("as_of", draft);
    } else {
      next.delete("as_of");
    }
    navigate({ search: next.toString() });
  }

  return (
    <form onSubmit={onSubmit} className="flex min-w-0 flex-wrap items-end gap-2">
      <Field label="As of">
        <Input type="date" name="as_of" value={draft} onChange={(event) => setDraft(event.target.value)} />
      </Field>
      <Button type="submit" variant="secondary">
        Apply date
      </Button>
    </form>
  );
}
