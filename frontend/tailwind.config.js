/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Rajdhani', 'sans-serif'],
        'mono': ['"Share Tech Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
