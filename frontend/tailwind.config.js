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
      },
      fontFamily: {
        serif: ['"Source Serif 4"', "Georgia", "ui-serif", "serif"],
        sans: ['"Source Sans 3"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(18, 32, 51, 0.06)",
      },
    },
  },
  plugins: [],
};
