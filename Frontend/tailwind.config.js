/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#0a0a0a',
          100: '#0f0f0f',
          200: '#1a1a1a',
          300: '#2a2a2a',
          400: '#3a3a3a',
          500: '#4a4a4a',
          600: '#5a5a5a',
          700: '#6a6a6a',
          800: '#7a7a7a',
          900: '#8a8a8a',
        },
        primary: {
          50: '#4b5563',   // gray-600 (brighter)
          100: '#374151',  // gray-700
          200: '#312e81',  // indigo-900
          300: '#4338ca',  // indigo-700
          400: '#6366f1',  // indigo-500
        },
        accent: {
          50: '#7c3aed',   // violet-600
          100: '#a78bfa',  // violet-300
          200: '#8b5cf6',  // violet-500
          300: '#6d28d9',  // violet-700
          400: '#581c87',  // violet-900
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
