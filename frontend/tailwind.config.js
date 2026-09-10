/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eefcfa',
          100: '#d3f7f1',
          200: '#a8efe4',
          300: '#71e0d2',
          400: '#3fc8bc',
          500: '#22ada3',
          600: '#178b85',
          700: '#166f6c',
          800: '#165957',
          900: '#154a49',
        },
      },
      backgroundImage: {
        'app-gradient': 'linear-gradient(135deg, #eafaf6 0%, #eef3fb 50%, #f1eefb 100%)',
        'brand-gradient': 'linear-gradient(135deg, #166f6c 0%, #22ada3 100%)',
      },
    },
  },
  plugins: [],
}
