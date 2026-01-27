/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#ff4500',
          dark: '#e03d00',
          light: '#ff6b35',
        },
        cargo: {
          DEFAULT: '#5e00be',
          dark: '#4a0095',
          light: '#7a1fd4',
        },
      },
    },
  },
  plugins: [],
}
