// front-end/tailwind-config.js
// Ensure `window.tailwind` exists before assigning `config`.
window.tailwind = window.tailwind || {};

window.tailwind.config = {
  theme: {
    extend: {
      colors: {
        // Dark/navy tones
        dark: {
          900: '#0B132B', // Oxford Blue
          800: '#1C2541', // Space Cadet
          700: '#3A506B', // YInMn Blue
        },
        // Primary action color (teal)
        primary: '#5BC0BE', // Verdigris
        // Explicit white
        white: '#FFFFFF',
        // (Optional) Extended gray if needed
        gray: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
};
