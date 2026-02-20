/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './shop/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'Segoe UI', 'Roboto', 'Arial', 'sans-serif'],
      },
      colors: {
        ink: {
          900: '#0b0b0f',
          800: '#111118',
          700: '#1a1a25',
        },
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.5rem',
      },
      boxShadow: {
        soft: '0 10px 30px rgba(0,0,0,.08)',
        lift: '0 14px 45px rgba(0,0,0,.14)',
      },
    },
  },
  plugins: [],
};
