import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        risk: {
          high: {
            light: "#dc2626",
            dark: "#ef4444",
            DEFAULT: "#ef4444",
          },
          medium: {
            light: "#d97706",
            dark: "#f59e0b",
            DEFAULT: "#f59e0b",
          },
          low: {
            light: "#16a34a",
            dark: "#22c55e",
            DEFAULT: "#22c55e",
          },
        },
        surface: {
          light: "#ffffff",
          dark: "#0a0a0a",
        },
        card: {
          light: "#f8fafc",
          dark: "#18181b",
        },
        accent: "#3b82f6",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        shimmer: "shimmer 2s linear infinite",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
