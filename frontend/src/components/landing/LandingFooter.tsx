import { Link } from "react-router-dom";

import { cx } from "../../lib/cx";
import { RISK_DISCLAIMER } from "../../lib/display";
import { textLink } from "./actionStyles";
import { useLandingCta } from "./useLandingCta";

const sectionLinks = [
  { href: "#product", label: "The product" },
  { href: "#features", label: "Capabilities" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#explainability", label: "Explainability" },
];

/* min-w-11 keeps the shortest label ("Log in", 35px of text) a 44px touch target. */
const linkClass = cx(textLink, "min-w-11");

export function LandingFooter() {
  const { signedIn, dashboardPath } = useLandingCta();

  return (
    <footer className="border-t border-landing-rule bg-landing-paper">
      <div className="mx-auto w-full max-w-6xl px-6 py-12">
        <div className="grid gap-10 md:grid-cols-12">
          <div className="md:col-span-5">
            <Link to="/" className="inline-flex min-h-11 items-center gap-2.5 text-landing-ink">
              <span
                aria-hidden="true"
                className="flex h-7 w-7 shrink-0 items-center justify-center rounded-landing-sm border border-landing-rule bg-landing-surface"
              >
                <svg viewBox="0 0 16 16" className="h-4 w-4">
                  <path
                    d="M2 12.5 6 8l4 1.5L14 3.5"
                    fill="none"
                    stroke="rgb(var(--landing-accent))"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              <span className="font-serif text-[1.0625rem] font-semibold tracking-[-0.015em]">
                Student Academic Advisor
              </span>
            </Link>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-landing-ink-muted">
              One auditable risk score from the academic records a department already keeps. Python
              computes every figure; the AI only explains them.
            </p>
          </div>

          <nav
            aria-label="Footer"
            className="flex flex-wrap gap-x-16 gap-y-8 md:col-span-7 md:justify-end"
          >
            <div>
              <h2 className="saa-label">Product</h2>
              <ul className="mt-3 flex flex-col">
                {sectionLinks.map((link) => (
                  <li key={link.href}>
                    <a href={link.href} className={linkClass}>
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="saa-label">Account</h2>
              <ul className="mt-3 flex flex-col">
                {signedIn ? (
                  <li>
                    <Link to={dashboardPath} className={linkClass}>
                      Go to your dashboard
                    </Link>
                  </li>
                ) : (
                  <>
                    <li>
                      <Link to="/login" className={linkClass}>
                        Log in
                      </Link>
                    </li>
                    <li>
                      <Link to="/register" className={linkClass}>
                        Create an account
                      </Link>
                    </li>
                  </>
                )}
              </ul>
            </div>
          </nav>
        </div>

        <div className="mt-10 flex flex-col gap-3 border-t border-landing-rule pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-landing-ink-muted">
            Demonstration project. Every figure on this page is synthetic example data, not a real
            student record.
          </p>
          <p className="saa-label shrink-0">{RISK_DISCLAIMER}</p>
        </div>
      </div>
    </footer>
  );
}
