import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(fileURLToPath(import.meta.url));

/** @type {import('tailwindcss').Config} */
export default {
  content: [join(root, "index.html"), join(root, "src/**/*.{ts,tsx}")],
  theme: {
    extend: {
      colors: {
        // Palette ispirata all'identità ufficiale FIFA World Cup 26
        wc: {
          bg: "#0a0823",
          bg2: "#150a35",
          card: "#1a1340",
          magenta: "#ff2d8e",
          pink: "#ff5fa2",
          cyan: "#19e0ff",
          blue: "#2f6bff",
          lime: "#43f59b",
          gold: "#ffd23f",
          purple: "#7b2cff",
          ink: "#e8e6ff",
          muted: "#9a93c7",
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', "system-ui", "sans-serif"],
        body: ['"Inter"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(255,255,255,0.06), 0 18px 50px -20px rgba(255,45,142,0.55)",
        glowcy: "0 0 0 1px rgba(255,255,255,0.06), 0 18px 50px -20px rgba(25,224,255,0.5)",
      },
      backgroundImage: {
        "wc-grad": "linear-gradient(120deg,#ff2d8e 0%,#7b2cff 45%,#19e0ff 100%)",
        "wc-grad-soft":
          "linear-gradient(120deg,rgba(255,45,142,.18),rgba(123,44,255,.16),rgba(25,224,255,.16))",
      },
      keyframes: {
        floaty: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-6px)" } },
        pop: { "0%": { transform: "scale(.9)", opacity: "0" }, "100%": { transform: "scale(1)", opacity: "1" } },
        shimmer: { "0%": { backgroundPosition: "0% 50%" }, "100%": { backgroundPosition: "200% 50%" } },
      },
      animation: {
        floaty: "floaty 6s ease-in-out infinite",
        pop: "pop .25s ease-out",
        shimmer: "shimmer 6s linear infinite",
      },
    },
  },
  plugins: [],
};
