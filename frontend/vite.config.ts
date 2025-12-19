import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // In development, proxy backend + auth routes to FastAPI (port 8000).
    // This mirrors the production "single runtime" diagram where the frontend
    // and backend are same-origin via a proxy.
    proxy: {
      '/api': 'http://localhost:8000',
      '/auth': 'http://localhost:8000',
      '/__repl_auth_callback': 'http://localhost:8000',
      '/callback': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/docs': 'http://localhost:8000',
      '/openapi.json': 'http://localhost:8000',
      '/redoc': 'http://localhost:8000',
    },
  },
})
