/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1DA1F2',
        dark: '#14171A',
        lightGray: '#657786',
        extraLightGray: '#AAB8C2',
        background: '#F7F9FA'
      }
    },
  },
  plugins: [],
}
