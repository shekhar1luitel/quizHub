/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#eef4ff',
          100: '#dbe8ff',
          200: '#bfcdff',
          300: '#9db1ff',
          400: '#7a94ff',
          500: '#4c6ef5',
          600: '#3b58d4',
          700: '#2f46ad',
          800: '#273a8b',
          900: '#1f306e',
        },
      },
      boxShadow: {
        glow: '0 20px 45px -20px rgba(76, 110, 245, 0.45)',
      },
      backgroundImage: {
        'app-noise':
          'radial-gradient(circle at 20% 20%, rgba(76,110,245,0.12), transparent 55%), radial-gradient(circle at 80% 20%, rgba(16,185,129,0.12), transparent 50%)',
      },
    },
  },
  plugins: [],
};
