/**
 * Tailwind Config Snippet for Discovery Feed Components
 * 
 * Copy this configuration into your tailwind.config.js file
 * to ensure all Stone color palette and custom styles work correctly.
 * 
 * USAGE:
 * 1. Open your tailwind.config.js
 * 2. Merge the "extend" object below into your existing config
 * 3. Update the "content" array to include the Discovery components
 */

module.exports = {
  // Add Discovery components to content scanning
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./src/components/Discovery/**/*.{js,jsx,ts,tsx}", // Ensure Discovery components are scanned
  ],
  
  theme: {
    extend: {
      // Stone Color Palette (Primary)
      colors: {
        stone: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917',
        },
        emerald: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#16a34a',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        violet: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        // Additional semantic colors
        red: {
          50: '#fef2f2',
          200: '#fecaca',
          600: '#dc2626',
          700: '#b91c1c',
        },
        orange: {
          50: '#fff7ed',
          200: '#fed7aa',
          600: '#ea580c',
          700: '#c2410c',
        },
        yellow: {
          50: '#fef3c7',
          100: '#fef9c3',
          700: '#a16207',
        },
        green: {
          50: '#f0fdf4',
          200: '#bbf7d0',
          600: '#16a34a',
        },
        gray: {
          50: '#f3f4f6',
          200: '#d1d5db',
          600: '#6b7280',
        },
      },

      // Typography
      fontFamily: {
        spectral: ['Spectral', 'serif'],
        inter: ['Inter', 'sans-serif'],
      },

      // Animations
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
      animation: {
        fadeIn: 'fadeIn 0.4s ease-out forwards',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },

      // Shadows
      boxShadow: {
        'card': '0 20px 40px -12px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 25px 50px -12px rgba(0, 0, 0, 0.15)',
      },

      // Spacing (additional utilities)
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },

      // Border Radius
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      },

      // Max Width
      maxWidth: {
        '7xl': '80rem',
      },

      // Z-index
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },

      // Transitions
      transitionDuration: {
        '400': '400ms',
      },
    },
  },
  
  // Plugins (optional but recommended)
  plugins: [
    // Uncomment if you want form styling
    // require('@tailwindcss/forms'),
    
    // Uncomment if you want typography plugin
    // require('@tailwindcss/typography'),
  ],
};

/**
 * IMPORTANT NOTES:
 * 
 * 1. If you're using Next.js 13+ with App Router, also add to your global CSS:
 *    @tailwind base;
 *    @tailwind components;
 *    @tailwind utilities;
 * 
 * 2. Font Loading: Add to your HTML <head> or _document.tsx:
 *    <link href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
 * 
 * 3. CSS Variables (Optional): If you prefer CSS variables, add to your global CSS:
 *    :root {
 *      --stone-50: #fafaf9;
 *      --stone-100: #f5f5f4;
 *      ... (see COMPONENT_SPEC.md for full list)
 *    }
 * 
 * 4. Dark Mode: These components are optimized for light mode. For dark mode support,
 *    add dark: variants to components or use a separate dark theme.
 * 
 * 5. PurgeCSS/Tree-shaking: Tailwind will automatically remove unused styles in production
 *    builds. Ensure your content paths are correct to avoid missing styles.
 */
