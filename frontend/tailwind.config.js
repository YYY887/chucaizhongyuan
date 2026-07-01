/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          light: '#F7F5F1',
          dark: '#000000',
        },
        surface: {
          light: '#FFFFFF',
          dark: '#1A1A1A',
        },
        border: {
          light: '#E7E3DA',
          dark: '#2A2A2A',
        },
        ink: {
          light: '#1E2227',
          dark: '#E5E5E5',
        },
        muted: {
          light: '#6B7077',
          dark: '#A0A0A0',
        },
        accent: {
          DEFAULT: '#3C5A78',
          hover: '#2E4760',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
