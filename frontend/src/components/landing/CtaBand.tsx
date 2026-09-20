import { Link } from "react-router-dom";

import { cx } from "../../lib/cx";
import { outlineAction, primaryAction } from "./actionStyles";
import { Reveal } from "./Reveal";
import { Section } from "./Section";
import { useLandingCta } from "./useLandingCta";

export function CtaBand() {
  const { signedIn, dashboardPath } = useLandingCta();

  return (
    <Section labelledBy="cta-heading">
      <Reveal>
        <div className="rounded-landing-xl border border-landing-rule bg-landing-surface px-6 py-10 shadow-landing-card sm:px-10 sm:py-12">
          <div className="grid items-center gap-8 lg:grid-cols-12 lg:gap-10">
            <div className="lg:col-span-7">
              <p className="saa-eyebrow">Next step</p>
              <h2 id="cta-heading" className="saa-headline mt-4">
                Start with the data you already have
              </h2>
              <p className="saa-lede mt-4 max-w-xl">
                Attendance and internal marks are enough for a first reading. Whatever is missing is
                left out of the weighting and reported as missing, never guessed at.
              </p>
            </div>
            <div className="lg:col-span-5 lg:justify-self-end">
              <div className="flex flex-col gap-3 sm:flex-row lg:flex-col lg:items-end xl:flex-row xl:justify-end">
                {signedIn ? (
                  <Link to={dashboardPath} className={cx(primaryAction, "px-5")}>
                    Go to your dashboard
                  </Link>
                ) : (
                  <>
                    <Link to="/register" className={cx(primaryAction, "px-5")}>
                      Get started
                    </Link>
                    <Link to="/login" className={cx(outlineAction, "px-5")}>
                      Log in
                    </Link>
                  </>
                )}
              </div>
              <p className="saa-label mt-4 lg:text-right">
                No AI key needed &middot; scores compute without it
              </p>
            </div>
          </div>
        </div>
      </Reveal>
    </Section>
  );
}
