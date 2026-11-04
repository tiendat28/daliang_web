import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Cong noi bo (portal). Import trong src dung '@/' = src/ (vd '@/core/api/client').
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true,
      interval: 300,
    },
    // Goi API cung ten mien: /api -> backend (trong docker la http://backend:8000)
    proxy: { '/api': process.env.API_PROXY_TARGET || 'http://localhost:8001' },
  },
})
