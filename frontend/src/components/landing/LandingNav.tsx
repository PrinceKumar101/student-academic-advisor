import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { cx } from "../../lib/cx";
import { outlineAction, primaryAction, textLink } from "./actionStyles";
import { useLandingCta } from "./useLandingCta";

const sectionLinks = [
  { href: "#product", label: "Product" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#explainability", label: "Explainability" },
];

/** Scroll distance after which the bar condenses onto its own surface. */
const CONDENSE_AT_PX = 8;

export function LandingNav() {
  const { signedIn, dashboardPath } = useLandingCta();
  const [menuOpen, setMenuOpen] = useState(false);
  const [condensed, setCondensed] = useState(false);
  const toggleRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    function onScroll() {
      setCondensed(window.scrollY > CONDENSE_AT_PX);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Escape closes the mobile menu and returns focus to the toggle that opened it.
  useEffect(() => {
    if (!menuOpen) {
      return;
    }
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMenuOpen(false);
        toggleRef.current?.focus();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  const solid = condensed || menuOpen;

  return (
    <header
      className={cx(
        "fixed inset-x-0 top-0 z-40 border-b transition-colors duration-landing ease-landing",
        solid
          ? "border-landing-rule bg-landing-paper/90 shadow-landing-nav backdrop-blur-sm"
          : "border-transparent bg-transparent",
      )}
    >
      <div
        className={cx(
          // Padding is the only property that changes here, and it is a layout
          // property, so it is named rather than left to `all` and it snaps
          // under prefers-reduced-motion instead of easing for 420ms.
          "mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-6 transition-[padding] duration-landing ease-landing motion-reduce:transition-none",
          condensed ? "py-2.5" : "py-4",
        )}
      >
        <Link to="/" className="flex min-h-11 items-center gap-2.5 text-landing-ink">
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
          <span className="font-serif text-[1.0625rem] font-semibold tracking-[-0.015em] sm:text-lg">
            Student Academic Advisor
          </span>
        </Link>

        {/* min-h-11 keeps these 44px targets on a touch tablet, where this bar is still expanded. */}
        <nav aria-label="Landing sections" className="hidden items-center gap-7 md:flex">
          {sectionLinks.map((link) => (
            <a key={link.href} href={link.href} className={textLink}>
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          {signedIn ? (
            <Link to={dashboardPath} className={cx(primaryAction, "px-4")}>
              Go to your dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className={cx(textLink, "px-3")}>
                Log in
              </Link>
              <Link to="/register" className={cx(primaryAction, "px-4")}>
                Get started
              </Link>
            </>
          )}
        </div>

        <button
          ref={toggleRef}
          type="button"
          className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-landing-md border border-landing-rule bg-landing-surface px-3 text-sm text-landing-ink-body md:hidden"
          aria-expanded={menuOpen}
          aria-controls="landing-menu"
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? "Close" : "Menu"}
        </button>
      </div>

      {/* Always mounted so aria-controls resolves; `hidden` keeps it out of the tab order. */}
      <div
        id="landing-menu"
        hidden={!menuOpen}
        className="border-t border-landing-rule bg-landing-paper px-6 pb-5 pt-3 md:hidden"
      >
        <nav aria-label="Landing sections (mobile)" className="flex flex-col">
          {sectionLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setMenuOpen(false)}
              className={cx(textLink, "flex border-b border-landing-rule-faint")}
            >
              {link.label}
            </a>
          ))}
        </nav>
        <div className="mt-4 flex flex-col gap-2">
          {signedIn ? (
            <Link
              to={dashboardPath}
              onClick={() => setMenuOpen(false)}
              className={cx(primaryAction, "px-4")}
            >
              Go to your dashboard
            </Link>
          ) : (
            <>
              <Link
                to="/register"
                onClick={() => setMenuOpen(false)}
                className={cx(primaryAction, "px-4")}
              >
                Get started
              </Link>
              <Link
                to="/login"
                onClick={() => setMenuOpen(false)}
                className={cx(outlineAction, "px-4")}
              >
                Log in
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
