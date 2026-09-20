# UI-REDESIGN-PHASE

## Purpose

This document breaks the approved Landing Page Redesign plan into small implementation phases so that each phase can be executed in a fresh Cursor Agent chat with minimal context repetition.

The goal is to:

- Reduce context/token usage.
- Keep each Agent conversation focused.
- Make implementation easier to review.
- Prevent large uncontrolled changes.
- Track progress in `.cursor/indexes/PHASE_TRACK.md`.
- Preserve existing backend and application functionality.
- Create clear checkpoints between UI implementation stages.

---

# GLOBAL UI REDESIGN RULES

These rules apply to EVERY UI redesign phase.

## Never modify

Do not modify:

- `backend/`
- API contracts
- API endpoints
- database logic
- authentication mechanics
- business logic
- academic risk calculation logic
- existing data models
- generated API types
- existing student-page functionality
- existing teacher-page functionality
- existing state-management architecture

Unless explicitly required by a later approved UI task, do not modify files under:

- `frontend/src/api/`
- `frontend/src/auth/`
- `frontend/src/pages/student/`
- `frontend/src/pages/teacher/`
- `frontend/src/types/api.ts`

## Landing-page data rule

The public landing page must not depend on real student data.

Hero/product visualizations must:

- use static demo data;
- make zero API requests;
- require no authentication;
- clearly identify example/demo data;
- never imply that displayed numbers belong to the visitor.

## Dependency rule

Do not add runtime dependencies unless absolutely necessary.

Before adding a dependency:

1. Check whether the existing stack can solve the problem.
2. Explain why the dependency is necessary.
3. Record the decision.
4. Obtain approval before adding it.

The current approved direction is:

- React
- TypeScript
- Vite
- Tailwind
- CSS
- SVG
- IntersectionObserver
- matchMedia
- existing project utilities

No animation library is required at this stage.

## Design philosophy

The approved visual direction is:

**Academic Instrument**

Use:

- warm archival paper;
- ink-blue as the primary brand hue;
- measurement and data as visual language;
- hairline rules;
- restrained depth;
- typography-led hierarchy;
- subtle motion;
- product-driven animation.

Avoid:

- generic AI aesthetics;
- glowing blobs;
- floating spheres;
- robot/brain imagery;
- excessive glassmorphism;
- animated gradient meshes;
- unnecessary 3D effects;
- excessive shadows;
- decorative animation with no product meaning.

## Motion philosophy

The principle is:

> The data breathes, nothing bounces.

Use:

- restrained entrance animations;
- subtle hover states;
- SVG data drawing;
- slow ambient motion;
- reduced-motion support.

Avoid:

- bounce;
- spring animations;
- parallax;
- cursor followers;
- typewriter headlines;
- scroll-scrubbed video;
- restarting counters on every scroll.

## Phase tracking rule

ALL progress MUST be tracked in:

`.cursor/indexes/PHASE_TRACK.md`

Do not create another phase-tracking file.

Append a new heading:

# UI-redesign-phase

Under that heading maintain the phase checklist.

Each phase must have:

- status;
- objective;
- tasks;
- validation;
- completion state.

Use:

- `[ ]` for incomplete;
- `[x]` for completed;
- `[~]` for in progress;
- `[!]` for blocked.

Never delete previous phase history.

After completing a phase:

1. Run the relevant tests/checks.
2. Update the phase status to `[x]`.
3. Record what was implemented.
4. Record validation performed.
5. Record known issues, if any.
6. Commit the completed phase before starting the next major phase.

Do not mark a phase complete merely because files were created.

---

# PHASE UI-01 — FOUNDATION & LANDING ARCHITECTURE

## Objective

Create the technical foundation for the landing page without implementing the detailed visual design yet.

## Scope

Implement:

- Landing page directory structure.
- `LandingPage.tsx`.
- Landing-page component boundaries.
- `Section` primitive.
- `Reveal` primitive.
- `useInView`.
- `usePrefersReducedMotion`.
- Landing-specific supporting utilities.
- `/` route pointing to the landing page.
- Minimal placeholder landing page.

## Expected component structure

Use the approved architecture as a starting point:

frontend/src/pages/LandingPage.tsx

frontend/src/components/landing/
- LandingNav.tsx
- HeroSection.tsx
- HeroAdvisorPanel.tsx
- HeroBackdrop.tsx
- heroDemoData.ts
- TrustStrip.tsx
- ProductPreview.tsx
- FeatureGrid.tsx
- HowItWorks.tsx
- ExplainabilitySection.tsx
- CtaBand.tsx
- LandingFooter.tsx
- Section.tsx
- Reveal.tsx

Only create components that are actually needed by the implementation.

Do not fill every component with final UI yet.

## Routing

Change `/` so it renders the landing page.

Preserve:

- `/login`
- `/register`
- `/forbidden`
- `/student/*`
- `/teacher/*`
- authentication behavior.

Do not remove existing HomeRedirect code silently.

## Validation

Run:

- typecheck;
- existing tests;
- route tests.

Verify:

- `/` renders;
- `/login` still works;
- `/register` still works;
- protected routes still work;
- no backend/API changes occurred.

## Completion

Update `.cursor/indexes/PHASE_TRACK.md`.

Mark UI-01 complete only after validation succeeds.

---

# PHASE UI-02 — LANDING DESIGN FOUNDATION

## Objective

Establish the visual foundation required by the landing page.

## Scope

Implement landing-page visual tokens and styles.

Focus on:

### Typography

Source Serif 4:

- 600
- 700

Source Sans 3:

- 400
- 500
- 600

System monospace for:

- metrics;
- labels;
- dates;
- numerical readouts.

### Landing visual language

Establish:

- paper background;
- canvas sections;
- surface;
- raised surface;
- rules;
- ink hierarchy;
- accent;
- accent hover;
- landing-specific shadows;
- landing-specific radii.

### Important

Do not blindly restyle every existing application page.

Prefer additive landing-specific styles/tokens where possible.

If modifying global tokens would visually alter existing dashboards, stop and report the impact instead of silently proceeding.

## Motion foundation

Add only reusable infrastructure:

- reduced-motion handling;
- entrance animation primitives;
- necessary keyframes.

Do not implement the full hero animation yet.

## Validation

Check:

- contrast;
- existing pages;
- existing tests;
- typography rendering;
- no unintended global regressions.

## Completion

Update `.cursor/indexes/PHASE_TRACK.md`.

Record:

- token changes;
- typography changes;
- validation;
- known visual regressions, if any.

---

# PHASE UI-03 — NAVIGATION & HERO

## Objective

Build the primary visual experience of the landing page.

This is the highest-priority visual phase.

## Navigation

Implement:

- floating landing navigation;
- brand/wordmark;
- section anchors;
- Log in;
- Get started;
- mobile menu;
- scroll-condensed behavior.

Reuse the existing accessible menu interaction patterns where appropriate.

## Hero

Implement:

### Eyebrow

"Python computes. AI explains."

### Headline

"Know what's slipping,"

"and what to do about it."

Use the approved two-tone hierarchy.

### Supporting copy

Explain:

- attendance;
- internal marks;
- assignments;
- assessment history;
- transparent risk score;
- AI explanation;
- recommendations.

### CTA

Primary:

"Get started"

Secondary:

"Log in"

When authentication state is already available:

"Go to your dashboard"

must route according to role.

Do not introduce new authentication logic.

## Hero visual

Build:

- `HeroBackdrop`;
- engraved grid;
- subtle light pool;
- `HeroAdvisorPanel`;
- existing `RiskGauge`;
- risk badge;
- attendance sparkline;
- contributing-factor rows;
- AI insight card;
- example-data label.

Use static `heroDemoData`.

No API calls.

## Hero animation

Implement only the initial hero entrance sequence:

1. eyebrow;
2. headline;
3. supporting text;
4. CTA;
5. panel;
6. data visualization.

Do not implement the long ambient motion yet.

## Accessibility

Ensure:

- semantic heading hierarchy;
- keyboard navigation;
- visible focus;
- reduced-motion support;
- example data is clearly labelled.

## Validation

Test:

- desktop;
- mobile;
- signed-out state;
- signed-in state;
- no API requests from landing page;
- no console errors.

## Completion

Update `.cursor/indexes/PHASE_TRACK.md`.

Record screenshots/visual observations if useful.

---

# PHASE UI-04 — CORE PRODUCT SECTIONS

## Objective

Build the informational sections below the hero.

## Implement

### TrustStrip

Use honest product facts rather than fake customer logos.

Examples:

- Deterministic 0–100 score
- Six weighted factors
- Works with AI turned off
- Student and teacher views

### ProductPreview

Show the actual product/dashboard experience using existing project screenshots/assets where appropriate.

Add restrained callout labels for:

- risk gauge;
- trend;
- contributing factors.

Do not connect this section to live API data.

### FeatureGrid

Create six feature areas:

1. Risk you can audit
2. Trend detection
3. Weak-area analysis
4. What-if simulation
5. AI advisor and study planner
6. Teacher class analytics

Each feature should communicate a concrete capability rather than generic marketing language.

### HowItWorks

Three stages:

1. Academic data is recorded.
2. Python computes risk/trends/early warnings.
3. AI explains results and helps create a study plan.

Desktop:

- horizontal progression.

Mobile:

- vertical timeline.

## Motion

Use restrained reveal animations.

Do not introduce ambient animation yet.

## Validation

Check:

- visual consistency with hero;
- mobile layout;
- no horizontal overflow;
- semantic structure;
- accessibility;
- no API calls.

## Completion

Update `.cursor/indexes/PHASE_TRACK.md`.

---

# PHASE UI-05 — EXPLAINABILITY, CTA & FOOTER

## Objective

Complete the lower landing-page experience.

## ExplainabilitySection

This is an important product-differentiation section.

Show the actual risk weights:

- Attendance — 0.25
- Internal — 0.25
- Assignments — 0.15
- Quizzes — 0.15
- Previous performance — 0.10
- Study habits — 0.10

Explain clearly:

- these are expert-chosen heuristics;
- they are configurable/testable;
- the system does not claim that the weights were learned from data;
- insufficient available data should not produce a fabricated result;
- the AI does not calculate the numerical risk score.

Use:

> Risk indicator, not a prediction.

Do not overstate predictive capability.

## CTA

Implement:

- final CTA;
- primary action;
- secondary action;
- concise supporting text.

## Footer

Implement:

- brand;
- product links;
- section anchors;
- project documentation links where appropriate;
- synthetic-data disclaimer.

## Validation

Check:

- CTA routes;
- footer links;
- accessibility;
- responsive layout;
- semantic HTML.

## Completion

Update `.cursor/indexes/PHASE_TRACK.md`.

---

# PHASE UI-06 — RESPONSIVE DESIGN PASS

## Objective

Perform a dedicated responsive-design pass after all sections exist.

Do not treat this as merely shrinking the desktop design.

## Required breakpoints

Verify at:

- 375px
- 768px
- 1024px
- 1440px

## Desktop

Verify:

- asymmetric hero;
- full hero visualization;
- navigation;
- feature grid;
- explainability visualization.

## Tablet

Verify:

- hero stacking;
- navigation collapse;
- two-column feature grid;
- timeline adaptation.

## Mobile

Verify:

- single-column composition;
- readable H1;
- stacked CTAs;
- reduced hero visualization;
- no horizontal scrolling;
- simplified product preview;
- one-column feature layout;
- vertical How It Works timeline;
- collapsed footer.

## Touch

Ensure:

- touch targets >=44px;
- no hover-only content;
- no interaction requires a mouse.

## Important

Do not change application business logic to solve responsive problems.

## Completion

Update `.cursor/indexes/PHASE_TRACK.md`.

Record each tested viewport.

---

# PHASE UI-07 — MOTION, ACCESSIBILITY & PERFORMANCE POLISH

## Objective

Perform the final interaction and quality pass.

## Motion

Implement/refine:

- entrance timing;
- stagger timing;
- SVG data drawing;
- risk gauge animation;
- subtle hover states;
- ambient data motion.

Ambient motion should follow:

> The data breathes, nothing bounces.

Use:

- low amplitude;
- slow continuous motion;
- approximately 45–60 second ambient cycles;
- transform/opacity where possible.

Do not add:

- parallax;
- cursor followers;
- animated gradient meshes;
- typewriter effects;
- excessive motion.

## Reduced motion

When:

`prefers-reduced-motion: reduce`

ensure:

- animations resolve immediately;
- ambient loop does not start;
- SVG drawing does not animate;
- counters do not animate;
- final states remain visible.

## Accessibility

Verify:

- semantic HTML;
- one H1;
- keyboard traversal;
- focus states;
- mobile menu keyboard behavior;
- Escape handling;
- focus restoration;
- contrast;
- screen-reader labels;
- decorative elements marked appropriately.

## Performance

Check:

- console errors;
- unnecessary re-renders;
- layout thrashing;
- animation performance;
- image loading;
- cumulative layout shift;
- unnecessary network requests.

The landing page must continue making zero API requests.

## Completion

Update `.cursor/indexes/PHASE_TRACK.md`.

Record:

- accessibility checks;
- reduced-motion checks;
- performance checks;
- known issues.

---

# PHASE UI-08 — FINAL QA, DOCUMENTATION & CLEANUP

## Objective

Perform final verification and close the UI redesign phase.

## Functional verification

Confirm:

- `/` loads;
- `/login` works;
- `/register` works;
- student routes work;
- teacher routes work;
- authentication behavior is unchanged;
- landing-page CTAs work;
- mobile navigation works.

## Technical verification

Run:

- tests;
- typecheck;
- production build.

Check:

- no TypeScript errors;
- no console errors;
- no failed network requests;
- no accidental backend modifications;
- no API contract changes;
- no accidental business-logic changes.

## Diff audit

Inspect the final Git diff.

Confirm there are no changes to:

- backend logic;
- API implementation;
- database logic;
- risk calculation logic;
- authentication mechanics;
- generated API types;
- student business functionality;
- teacher business functionality.

## Documentation

Update only the documentation that is actually relevant.

### `.cursor/indexes/PHASE_TRACK.md`

Ensure the complete UI-redesign phase history exists.

### `docs/UI_REDESIGN_PLAN.md`

Record the approved final design:

- visual identity;
- design tokens;
- typography;
- motion system;
- landing sections;
- hero specification;
- component architecture;
- responsive strategy;
- accessibility requirements;
- performance requirements.

### `docs/UI_POLISH.md`

Append a chronological record containing:

- phase;
- date;
- changes;
- validation;
- screenshots/observations if relevant;
- known issues.

Do not delete existing history.

### `UI_GUIDELINES.md`

Only update design-system information that actually changed.

### `ARCHITECTURE.md`

Add an architecture decision only if the implementation introduced an actual architectural decision.

### `README.md`

Update landing-page behavior only if the existing README is now inaccurate.

Do not make unrelated documentation changes.

## Final phase status

Before marking the UI redesign complete:

- all eight phases must be `[x]`;
- tests pass;
- typecheck passes;
- production build passes;
- responsive checks are complete;
- accessibility checks are complete;
- final Git diff has been audited;
- documentation is updated.

Then update:

`.cursor/indexes/PHASE_TRACK.md`

with the final completion record.

---

# PHASE EXECUTION PROTOCOL

Each phase MUST be executed in a separate Cursor Agent chat whenever practical.

At the beginning of a new chat:

1. Read `.cursor/rules/ui-redesign.mdc`.
2. Read the current `UI-redesign` section of `.cursor/indexes/PHASE_TRACK.md`.
3. Read only the files relevant to the current phase.
4. Do not reread the entire project unnecessarily.
5. Inspect the previous phase's changes before modifying anything.
6. Implement ONLY the current phase.
7. Run the phase-specific validation.
8. Update `.cursor/indexes/PHASE_TRACK.md`.
9. Stop after the phase is complete.

Do not continue automatically into the next phase.

---

# CONTEXT OPTIMIZATION RULE

Do not attach the entire project to every new chat.

Use the smallest relevant context for each phase.

## UI-01 context

Attach:

- `@.cursor/rules/ui-redesign.mdc`
- `@.cursor/indexes/PHASE_TRACK.md`
- `@frontend/src/routes/`
- relevant frontend architecture files

## UI-02 context

Attach:

- `@.cursor/rules/ui-redesign.mdc`
- `@.cursor/indexes/PHASE_TRACK.md`
- landing foundation files created by UI-01
- relevant UI components
- `@design_templates/`

## UI-03 context

Attach:

- `@.cursor/rules/ui-redesign.mdc`
- `@.cursor/indexes/PHASE_TRACK.md`
- landing components
- `RiskGauge`
- `RiskBadge`
- auth context
- relevant design references

## UI-04 context

Attach:

- `@.cursor/rules/ui-redesign.mdc`
- `@.cursor/indexes/PHASE_TRACK.md`
- existing landing components
- relevant product documentation
- existing screenshots

## UI-05 context

Attach:

- `@.cursor/rules/ui-redesign.mdc`
- `@.cursor/indexes/PHASE_TRACK.md`
- existing landing components
- risk-engine documentation
- project specification

## UI-06 context

Attach:

- `@.cursor/rules/ui-redesign.mdc`
- `@.cursor/indexes/PHASE_TRACK.md`
- complete landing-page implementation

## UI-07 context

Attach:

- `@.cursor/rules/ui-redesign.mdc`
- `@.cursor/indexes/PHASE_TRACK.md`
- complete landing-page implementation
- relevant UI styles/hooks

## UI-08 context

Attach:

- `@.cursor/rules/ui-redesign.mdc`
- `@.cursor/indexes/PHASE_TRACK.md`
- `docs/UI_REDESIGN_PLAN.md`
- `docs/UI_POLISH.md`
- `UI_GUIDELINES.md`
- `ARCHITECTURE.md`
- `README.md`

---

# PHASE TRACKER FORMAT

Append the following heading to:

`.cursor/indexes/PHASE_TRACK.md`

# UI-redesign-phase

## Overview

Landing-page redesign and UI polish for Student Academic Advisor.

Scope:

- Public landing page
- Visual identity
- Hero
- Product visualization
- Marketing sections
- Responsive behavior
- Motion
- Accessibility
- Performance
- UI documentation

Explicitly excluded:

- Backend changes
- API changes
- Database changes
- Business-logic changes
- Risk-engine changes
- Authentication-mechanics changes

---

## UI-01 — Foundation & Landing Architecture

Status: [ ]

- [ ] Landing page architecture created
- [ ] Landing components structure created
- [ ] Section primitive created
- [ ] Reveal primitive created
- [ ] useInView created
- [ ] usePrefersReducedMotion created
- [ ] `/` renders LandingPage
- [ ] Existing routes verified
- [ ] Existing tests pass
- [ ] Phase documented

---

## UI-02 — Landing Design Foundation

Status: [ ]

- [ ] Landing typography established
- [ ] Landing visual tokens established
- [ ] Paper/canvas/surface hierarchy established
- [ ] Accent system established
- [ ] Landing shadows/radii established
- [ ] Initial motion primitives established
- [ ] Contrast checked
- [ ] Existing UI regression checked
- [ ] Phase documented

---

## UI-03 — Navigation & Hero

Status: [ ]

- [ ] Landing navigation implemented
- [ ] Mobile navigation implemented
- [ ] Hero composition implemented
- [ ] Hero typography implemented
- [ ] Hero CTAs implemented
- [ ] HeroBackdrop implemented
- [ ] HeroAdvisorPanel implemented
- [ ] RiskGauge reused
- [ ] RiskBadge reused
- [ ] Sparkline implemented
- [ ] Factor rows implemented
- [ ] AI insight card implemented
- [ ] Example data clearly labelled
- [ ] Hero makes zero API requests
- [ ] Initial hero animation implemented
- [ ] Phase documented

---

## UI-04 — Core Product Sections

Status: [ ]

- [ ] TrustStrip implemented
- [ ] ProductPreview implemented
- [ ] FeatureGrid implemented
- [ ] HowItWorks implemented
- [ ] Responsive section structure implemented
- [ ] Product claims verified against project documentation
- [ ] No unnecessary API usage
- [ ] Phase documented

---

## UI-05 — Explainability, CTA & Footer

Status: [ ]

- [ ] ExplainabilitySection implemented
- [ ] Real risk weights represented accurately
- [ ] Risk disclaimer included
- [ ] CTA section implemented
- [ ] Footer implemented
- [ ] Synthetic-data disclaimer included
- [ ] CTA routing verified
- [ ] Phase documented

---

## UI-06 — Responsive Design

Status: [ ]

- [ ] 375px verified
- [ ] 768px verified
- [ ] 1024px verified
- [ ] 1440px verified
- [ ] Hero recomposes rather than simply shrinking
- [ ] Mobile navigation verified
- [ ] Touch targets verified
- [ ] No horizontal overflow
- [ ] No hover-only functionality
- [ ] Phase documented

---

## UI-07 — Motion, Accessibility & Performance

Status: [ ]

- [ ] Entrance animations refined
- [ ] Hero data animation refined
- [ ] Ambient motion implemented/refined
- [ ] Hover interactions refined
- [ ] Reduced-motion behavior verified
- [ ] Keyboard traversal verified
- [ ] Focus states verified
- [ ] Contrast verified
- [ ] Screen-reader semantics verified
- [ ] Console checked
- [ ] Performance checked
- [ ] Landing page makes zero API requests
- [ ] Phase documented

---

## UI-08 — Final QA & Documentation

Status: [ ]

- [ ] Full test suite passes
- [ ] Typecheck passes
- [ ] Production build passes
- [ ] All relevant routes verified
- [ ] Git diff audited
- [ ] Backend unchanged
- [ ] API unchanged
- [ ] Business logic unchanged
- [ ] Risk engine unchanged
- [ ] Authentication mechanics unchanged
- [ ] UI_REDESIGN_PLAN.md updated
- [ ] UI_POLISH.md updated
- [ ] UI_GUIDELINES.md updated if required
- [ ] ARCHITECTURE.md updated if required
- [ ] README.md updated if required
- [ ] Final screenshots/visual verification completed
- [ ] Final UI redesign marked complete

---

## UI REDESIGN COMPLETION

Status: [ ]

Completion date:

Final validation:

- Tests:
- Typecheck:
- Build:
- Responsive:
- Accessibility:
- Performance:
- Git diff audit:

Known remaining issues:

-
-
-

---

# IMPORTANT AGENT BEHAVIOR

Never start the next UI phase automatically.

After completing a phase:

1. Update `.cursor/indexes/PHASE_TRACK.md`.
2. Summarize what changed.
3. Report validation results.
4. Report any unresolved issues.
5. Stop.

Wait for the user to start the next phase in a new Agent chat.

The purpose of this structure is controlled, incremental implementation rather than one large uncontrolled UI rewrite.