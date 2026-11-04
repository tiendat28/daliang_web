import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Website cong khai (daliang.com). Khong dung Tailwind: CSS la ban goc cua
// thiet ke (src/styles/site.css).
export default defineConfig({
  plugins: [vue()],
  // Anh, logo, font phuc vu thang tu assets/ (vd /fonts/..., /images/...)
  publicDir: 'assets',
  server: {
    host: true,
    port: 5174,
    watch: { usePolling: true, interval: 300 },
    // Goi API cung ten mien: /api -> backend (trong docker la http://backend:8000)
    proxy: { '/api': process.env.API_PROXY_TARGET || 'http://localhost:8001' },
  },
})
