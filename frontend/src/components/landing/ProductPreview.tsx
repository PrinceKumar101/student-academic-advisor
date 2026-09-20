import type { ReactNode } from "react";

import { cx } from "../../lib/cx";
import { RiskGauge } from "../RiskGauge";
import { Reveal } from "./Reveal";
import { Section } from "./Section";
import { productPreviewData } from "./productPreviewData";

/**
 * A static reconstruction of the student dashboard, built from the same
 * components and figures the running app uses (StudentHomePage: risk gauge,
 * trend cards, completeness, top factors, warnings). It is deliberately not
 * wired to the API: the landing page must render for a visitor with no account.
 */

const callouts = [
  {
    title: "Risk gauge",
    detail:
      "The 0\u2013100 score with its level, and the share of the weighting the available data covers.",
  },
  {
    title: "Trend",
    detail:
      "A least-squares slope per series, labelled improving, stable or declining from the same threshold.",
  },
  {
    title: "Contributing factors",
    detail:
      "The components pushing the score up, ranked by contribution. The risk page shows each weight and note.",
  },
];

function Marker({ index }: { index: number }) {
  return (
    <span
      aria-hidden="true"
      className="saa-metric absolute right-3 top-3 inline-flex h-5 w-5 items-center justify-center rounded-landing-sm bg-landing-accent text-[0.6875rem] leading-none text-landing-accent-ink"
    >
      {index}
    </span>
  );
}

function PreviewCard({
  children,
  marker,
  className,
}: {
  children: ReactNode;
  marker?: number;
  className?: string;
}) {
  return (
    <div
      className={cx(
        "relative rounded-landing-md border border-landing-rule bg-landing-raised p-4",
        className,
      )}
    >
      {marker ? <Marker index={marker} /> : null}
      {children}
    </div>
  );
}

export function ProductPreview() {
  const { navItems, pageTitle, asOfLabel, identityLine, risk, trends, topFactors, warnings } =
    productPreviewData;

  return (
    <Section id="product" labelledBy="product-heading">
      <Reveal>
        <p className="saa-eyebrow">The product</p>
        <h2 id="product-heading" className="saa-headline mt-4">
          One page that says what is slipping
        </h2>
        <p className="saa-lede mt-4 max-w-2xl">
          The score, the trend behind it and the factors that produced it sit together, with the
          data completeness beside them so a thin record is never mistaken for a confident one.
        </p>
      </Reveal>

      <Reveal delayMs={80} className="mt-10">
        <figure aria-labelledby="product-preview-caption" className="m-0">
          <div className="overflow-hidden rounded-landing-lg border border-landing-rule bg-landing-surface shadow-landing-card">
            <div className="flex items-center justify-between gap-4 border-b border-landing-rule bg-landing-paper px-4 py-3">
              <p className="font-serif text-sm font-semibold text-landing-ink">
                Student Academic Advisor
              </p>
              {/* Mono tracking breaks this after "Mar" on a phone; let the wordmark wrap instead. */}
              <p className="saa-label whitespace-nowrap">As of {asOfLabel}</p>
            </div>

            <div className="flex">
              {/* The navigation rail is scenery; the real one lives in components/Layout.tsx. */}
              <div
                aria-hidden="true"
                className="hidden w-40 shrink-0 border-r border-landing-rule px-4 py-5 lg:block"
              >
                <ul className="space-y-3 text-sm">
                  {navItems.map((item, index) => (
                    <li
                      key={item}
                      className={
                        index === 0
                          ? "font-medium text-landing-accent"
                          : "text-landing-ink-muted"
                      }
                    >
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="min-w-0 flex-1 px-4 py-5 sm:px-5">
                <p className="font-serif text-xl font-semibold text-landing-ink">{pageTitle}</p>
                <p className="mt-1.5 text-sm text-landing-ink-muted">{identityLine}</p>

                {/*
                  Three across only from `lg`. Between `sm` and `lg` a third of
                  the frame is too narrow for the gauge's "Risk score 67.1", so
                  the risk card takes the full row and the two trends pair up.
                */}
                <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  <PreviewCard marker={1} className="sm:col-span-2 lg:col-span-1">
                    <p className="saa-label">Risk</p>
                    <div className="mt-2">
                      <RiskGauge score={risk.score} level={risk.level} />
                    </div>
                  </PreviewCard>
                  {trends.map((trend, index) => (
                    <PreviewCard key={trend.label} marker={index === 0 ? 2 : undefined}>
                      <p className="saa-label">{trend.label}</p>
                      <p className="mt-2 font-serif text-2xl font-semibold text-landing-ink">
                        {trend.value}
                      </p>
                      <p className="saa-metric mt-1.5 text-xs">{trend.detail}</p>
                    </PreviewCard>
                  ))}
                </div>

                <p className="saa-label mt-4">
                  Completeness {risk.dataCompleteness.toFixed(2)} · config v1.0
                </p>

                <div className="mt-4 grid gap-3 lg:grid-cols-2">
                  <PreviewCard marker={3}>
                    <p className="saa-label">Top factors</p>
                    <ul className="mt-2.5 space-y-1.5 text-sm text-landing-ink-body">
                      {topFactors.map((factor) => (
                        <li key={factor} className="flex items-center gap-2">
                          <span
                            aria-hidden="true"
                            className="h-1 w-1 shrink-0 rounded-full bg-landing-rule-strong"
                          />
                          {factor}
                        </li>
                      ))}
                    </ul>
                  </PreviewCard>
                  <PreviewCard>
                    <p className="saa-label">Warnings</p>
                    <ul className="mt-2.5 space-y-2.5">
                      {warnings.map((warning) => (
                        <li key={warning.code}>
                          <p className="saa-label text-landing-ink-body">
                            {warning.code} · {warning.severity}
                          </p>
                          <p className="mt-1 text-sm text-landing-ink-muted">{warning.message}</p>
                        </li>
                      ))}
                    </ul>
                  </PreviewCard>
                </div>
              </div>
            </div>
          </div>

          <figcaption id="product-preview-caption" className="saa-label mt-4">
            Student dashboard layout · example data, not a live account
          </figcaption>
        </figure>

        <ol className="mt-8 grid gap-6 border-t border-landing-rule pt-6 sm:grid-cols-3">
          {callouts.map((callout, index) => (
            <li key={callout.title}>
              <p className="saa-label">
                <span className="text-landing-accent">{index + 1}</span> · {callout.title}
              </p>
              <p className="mt-2 text-sm leading-relaxed text-landing-ink-muted">
                {callout.detail}
              </p>
            </li>
          ))}
        </ol>
      </Reveal>
    </Section>
  );
}
