import js from '@eslint/js'
import globals from 'globals'
import tseslint from 'typescript-eslint'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      '*.config.js',
      '*.config.ts',
      'postcss.config.js',
      'tailwind.config.js',
      'vite.config.ts',
    ],
  },

  // Base JS recommended rules.
  js.configs.recommended,

  // TypeScript + React (flat config via typescript-eslint).
  ...tseslint.config(
    {
      files: ['src/**/*.{ts,tsx}'],
      languageOptions: {
        parser: tseslint.parser,
        parserOptions: {
          ecmaVersion: 'latest',
          sourceType: 'module',
          ecmaFeatures: { jsx: true },
        },
        globals: {
          ...globals.browser,
          ...globals.es2021,
        },
      },
      plugins: {
        '@typescript-eslint': tseslint.plugin,
        'react-hooks': reactHooks,
        'react-refresh': reactRefresh,
      },
      rules: {
        ...tseslint.configs.recommended.rules,
        ...reactHooks.configs.recommended.rules,

        // Base JS rules don't understand TS/JSX well.
        'no-undef': 'off',
        'no-unused-vars': 'off',
        '@typescript-eslint/no-unused-vars': [
          'error',
          {
            argsIgnorePattern: '^_',
            varsIgnorePattern: '^_',
            caughtErrorsIgnorePattern: '^_',
          },
        ],

        // Vite + React Fast Refresh best practice.
        'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      },
    },
    {
      // Keep config files lightly checked (no TS type-aware linting required).
      files: ['*.{js,mjs,cjs}', '*.ts'],
      languageOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        globals: {
          ...globals.node,
          ...globals.es2021,
        },
      },
    },
  ),
]

