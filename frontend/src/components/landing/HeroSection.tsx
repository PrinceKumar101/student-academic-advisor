import { Link } from "react-router-dom";

import { cx } from "../../lib/cx";
import { RISK_DISCLAIMER } from "../../lib/display";
import { outlineAction, primaryAction } from "./actionStyles";
import { HeroAdvisorPanel } from "./HeroAdvisorPanel";
import { HeroBackdrop } from "./HeroBackdrop";
import { enterDelay } from "./motion";
import { Section } from "./Section";
import { useLandingCta } from "./useLandingCta";

/**
 * Entrance order: eyebrow, headline, supporting copy, calls to action, panel.
 * The panel's data draws itself after that, on the timeline in
 * HeroAdvisorPanel. The panel is the largest element, so it rises over a longer
 * duration than the text above it.
 */
const PANEL_ENTER_MS = 320;
const PANEL_DURATION_MS = 560;

/** Full width and stacked on a phone, side by side from `sm`. */
const heroAction = "w-full px-5 sm:w-auto";

export function HeroSection() {
  const { signedIn, dashboardPath } = useLandingCta();

  return (
    <Section
      labelledBy="hero-heading"
      backdrop={<HeroBackdrop />}
      innerClassName="pb-16 pt-28 sm:pb-20 sm:pt-32 lg:pb-24 lg:pt-36"
    >
      {/* The hero is above the fold, so it enters on load rather than on scroll. */}
      <div className="grid items-start gap-12 lg:grid-cols-12 lg:items-center lg:gap-10">
        <div className="lg:col-span-7">
          <p className="saa-eyebrow saa-landing-enter" style={enterDelay(0)}>
            Python computes. AI explains.
          </p>
          <h1
            id="hero-heading"
            className="saa-display saa-landing-enter mt-5 max-w-2xl"
            style={enterDelay(80)}
          >
            Know what&rsquo;s slipping,{" "}
            <span className="text-landing-ink-muted">and what to do about it.</span>
          </h1>
          <p className="saa-lede saa-landing-enter mt-6 max-w-xl" style={enterDelay(160)}>
            Attendance, internal marks, assignments and the whole assessment history become one
            transparent risk score. Python computes it; the AI explains what it means and
            recommends what to do next.
          </p>
          <div className="saa-landing-enter mt-8" style={enterDelay(240)}>
            <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              {signedIn ? (
                <Link to={dashboardPath} className={cx(primaryAction, heroAction)}>
                  Go to your dashboard
                </Link>
              ) : (
                <>
                  <Link to="/register" className={cx(primaryAction, heroAction)}>
                    Get started
                  </Link>
                  <Link to="/login" className={cx(outlineAction, heroAction)}>
                    Log in
                  </Link>
                </>
              )}
            </div>
            <p className="mt-4 text-sm text-landing-ink-muted">
              {RISK_DISCLAIMER} Every score is auditable, and the product still works with the AI
              switched off.
            </p>
          </div>
        </div>
        {/*
          Stacked, the panel is capped near its desktop width instead of running
          the full column: at 768px a 720px panel flattens the sparkline and
          pushes the AI paragraph past 80 characters a line.
        */}
        <div
          className="saa-landing-enter mx-auto w-full max-w-md lg:col-span-5 lg:mx-0 lg:max-w-none"
          style={enterDelay(PANEL_ENTER_MS, PANEL_DURATION_MS)}
        >
          <HeroAdvisorPanel />
        </div>
      </div>
    </Section>
  );
}
