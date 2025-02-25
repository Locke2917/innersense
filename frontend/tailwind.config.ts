import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",  
    "./components/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",   // (For Next.js Pages Router, if used)
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;