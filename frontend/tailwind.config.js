/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F4F0E6",
        surface: "#FFFCF7",
        rule: "#D7D0C3",
        ink: {
          DEFAULT: "#122033",
          50: "#F3F1EC",
          100: "#E6E1D6",
          500: "#5C6B7A",
          700: "#2A3A4D",
        },
        accent: {
          DEFAULT: "#1F4E79",
          50: "#E8F0F7",
          700: "#163A5A",
        },
        risk: {
          low: "#2F6F4E",
          "low-fill": "#E3F0E8",
          medium: "#8A5A12",
          "medium-fill": "#F6EBD6",
          high: "#8B2E2E",
          "high-fill": "#F6E2E2",
          unknown: "#4B5563",
          "unknown-fill": "#E8EAED",
        },
        // Landing-only layer (UI-02). Values live in src/index.css :root.
        landing: {
          paper: "rgb(var(--landing-paper) / <alpha-value>)",
          canvas: "rgb(var(--landing-canvas) / <alpha-value>)",
          surface: "rgb(var(--landing-surface) / <alpha-value>)",
          raised: "rgb(var(--landing-raised) / <alpha-value>)",
          rule: "rgb(var(--landing-rule) / <alpha-value>)",
          "rule-strong": "rgb(var(--landing-rule-strong) / <alpha-value>)",
          "rule-faint": "rgb(var(--landing-rule-faint) / <alpha-value>)",
          ink: "rgb(var(--landing-ink) / <alpha-value>)",
          "ink-body": "rgb(var(--landing-ink-body) / <alpha-value>)",
          "ink-muted": "rgb(var(--landing-ink-muted) / <alpha-value>)",
          accent: "rgb(var(--landing-accent) / <alpha-value>)",
          "accent-hover": "rgb(var(--landing-accent-hover) / <alpha-value>)",
          "accent-soft": "rgb(var(--landing-accent-soft) / <alpha-value>)",
          "accent-ink": "rgb(var(--landing-accent-ink) / <alpha-value>)",
        },
      },
      fontFamily: {
        serif: ['"Source Serif 4"', "Georgia", "ui-serif", "serif"],
        sans: ['"Source Sans 3"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(18, 32, 51, 0.06)",
        "landing-card": "var(--landing-shadow-card)",
        "landing-panel": "var(--landing-shadow-panel)",
        "landing-nav": "var(--landing-shadow-nav)",
      },
      borderRadius: {
        "landing-sm": "var(--landing-radius-sm)",
        "landing-md": "var(--landing-radius-md)",
        "landing-lg": "var(--landing-radius-lg)",
        "landing-xl": "var(--landing-radius-xl)",
      },
      transitionTimingFunction: {
        landing: "var(--landing-ease)",
      },
      transitionDuration: {
        "landing-fast": "var(--landing-duration-fast)",
        landing: "var(--landing-duration-base)",
        "landing-slow": "var(--landing-duration-slow)",
      },
    },
  },
  plugins: [],
};
