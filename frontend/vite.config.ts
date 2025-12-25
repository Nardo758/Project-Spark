import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  define: {
    'import.meta.env.VITE_MAPBOX_ACCESS_TOKEN': JSON.stringify(process.env.MAPBOX_ACCESS_TOKEN || ''),
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@stores': path.resolve(__dirname, './src/stores'),
      '@services': path.resolve(__dirname, './src/services'),
      '@assets': path.resolve(__dirname, './src/assets'),
    },
  },
  server: {
    host: '0.0.0.0',
    // Use 5000 by default to align with the system diagrams and Replit routing.
    // (You can override with `npm run dev -- --port <port>`.)
    port: 5000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth/login': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth/callback': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth/logout': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth/status': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth/debug': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/__repl_auth_callback': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/callback': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/docs': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/openapi.json': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/redoc': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
    allowedHosts: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
