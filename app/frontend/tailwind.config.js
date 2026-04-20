/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#18181a',
        'dark-secondary': '#202022',
        'dark-card': '#202022',
        'dark-text': '#ecece9',
        'dark-text-secondary': '#a09d94',
        'dark-border': '#36342e',
        'light-bg': '#fdfcfb',
        'light-secondary': '#f3f2ee',
        'light-card': '#ffffff',
        'light-text': '#1a1918',
        'light-text-secondary': '#666460',
        'light-border': '#e2e0da',
        'accent': '#d97757',
        'accent-hover': '#c06b4e',
      },
    },
  },
  plugins: [],
}
