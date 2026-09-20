/**
 * Decorative hero backdrop: an engraved measurement grid under a single soft
 * light pool. Clipped to the section box and masked so it never reaches an
 * edge as a hard line.
 *
 * Both layers carry the ambient loops (UI-07): the grid creeps one cell every
 * 60 seconds, like paper advancing through an instrument, and the light pool
 * breathes over 52 seconds. Transform and opacity only, so neither costs
 * layout, and both stop entirely under prefers-reduced-motion.
 */
export function HeroBackdrop() {
  return (
    <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
      {/* The centring transform stays on the wrapper so the breath can own its own. */}
      <div className="absolute -top-24 left-1/2 h-[38rem] w-[76rem] -translate-x-1/2">
        <div
          className="saa-ambient-glow h-full w-full"
          style={{
            background:
              "radial-gradient(58% 52% at 50% 42%, rgb(var(--landing-surface)) 0%, rgb(var(--landing-surface) / 0) 72%)",
          }}
        />
      </div>
      {/* The mask sits on this box so it holds still while the grid drifts inside. */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{
          maskImage: "radial-gradient(74% 62% at 50% 34%, #000 0%, transparent 76%)",
          WebkitMaskImage: "radial-gradient(74% 62% at 50% 34%, #000 0%, transparent 76%)",
        }}
      >
        {/* One cell of bleed on every side, so a cell of drift never runs out of tiling. */}
        <svg className="saa-ambient-grid absolute -inset-8">
          <defs>
            <pattern id="hero-engraved-grid" width="32" height="32" patternUnits="userSpaceOnUse">
              <path
                d="M32 0H0v32"
                fill="none"
                stroke="rgb(var(--landing-rule-faint))"
                strokeWidth="1"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#hero-engraved-grid)" />
        </svg>
      </div>
      <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-b from-transparent to-landing-paper" />
    </div>
  );
}
