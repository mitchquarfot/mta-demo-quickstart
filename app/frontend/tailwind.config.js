/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        sf: {
          blue: "#29B5E8",
          dark: "#1B2A4A",
          navy: "#0F1B2D",
          accent: "#00D4AA",
          light: "#F0F4F8",
        },
      },
    },
  },
  plugins: [],
}

