import { CtaBand } from "../components/landing/CtaBand";
import { ExplainabilitySection } from "../components/landing/ExplainabilitySection";
import { FeatureGrid } from "../components/landing/FeatureGrid";
import { HeroSection } from "../components/landing/HeroSection";
import { HowItWorks } from "../components/landing/HowItWorks";
import { LandingFooter } from "../components/landing/LandingFooter";
import { LandingNav } from "../components/landing/LandingNav";
import { ProductPreview } from "../components/landing/ProductPreview";
import { TrustStrip } from "../components/landing/TrustStrip";

export function LandingPage() {
  return (
    <div className="saa-landing min-h-screen max-w-full overflow-x-clip bg-landing-paper">
      <a
        href="#landing-main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:inline-flex focus:min-h-11 focus:items-center focus:rounded-landing-sm focus:bg-landing-surface focus:px-4"
      >
        Skip to main content
      </a>
      <LandingNav />
      <main id="landing-main" tabIndex={-1}>
        <HeroSection />
        <TrustStrip />
        <ProductPreview />
        <FeatureGrid />
        <HowItWorks />
        <ExplainabilitySection />
        <CtaBand />
      </main>
      <LandingFooter />
    </div>
  );
}
