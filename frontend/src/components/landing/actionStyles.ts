/**
 * One definition of the landing actions, shared by the navigation, the hero and
 * the closing call to action so a hover change lands in all three at once.
 * Padding and width stay with the caller, because each placement differs.
 *
 * Hover is a colour change plus a one-pixel lift. The lift is gated on
 * `motion-safe`, so with prefers-reduced-motion colour is the only cue, and the
 * transition names its properties rather than using `all`.
 */
const actionBase =
  "inline-flex min-h-11 items-center justify-center rounded-landing-md text-sm font-medium transition-[background-color,border-color,color,transform] duration-landing-fast ease-landing motion-safe:hover:-translate-y-px";

export const primaryAction = `${actionBase} bg-landing-accent text-landing-accent-ink hover:bg-landing-accent-hover`;

export const outlineAction = `${actionBase} border border-landing-rule bg-landing-surface text-landing-ink-body hover:border-landing-rule-strong hover:text-landing-accent`;

/**
 * Text link: section anchors, the navigation's "Log in" and the footer. The
 * hairline underline on hover reads as an engraved rule under the label and,
 * unlike a border, adds nothing to the box.
 */
export const textLink =
  "inline-flex min-h-11 items-center text-sm text-landing-ink-body decoration-landing-rule-strong decoration-1 underline-offset-[6px] transition-colors duration-landing-fast ease-landing hover:text-landing-accent hover:underline";
