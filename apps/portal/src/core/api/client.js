import axios from 'axios'
import { notify } from '@/core/store/notify'

// API cung ten mien (/api/v1): nginx, proxy cua Vite, hoac rewrite cua Vercel.
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
})

// Access token song 15 phut: gap 401 thi xin cap lai bang refresh token (cookie)
// roi gui lai dung request do mot lan. Nhieu request cung het han thi chi goi
// /auth/refresh mot lan.
let refreshing = null
const NO_RETRY = ['/auth/login', '/auth/refresh', '/auth/2fa/', '/auth/logout', '/auth/forgot-password', '/auth/reset-password']

client.interceptors.response.use(
  response => response,
  async (error) => {
    const { config, response } = error
    const url = config?.url || ''

    // Bat loi 403: Khong co quyen thuc hien
    if (response?.status === 403) {
      const detail = response?.data?.detail
      let msg = 'Bạn không có quyền thực hiện thao tác này'
      if (typeof detail === 'string') {
        msg = detail.replace(/\s*\([^)]*\)$/, '').trim() || msg
      } else if (Array.isArray(detail) && detail.length) {
        msg = detail[0].msg?.replace(/^Value error, /, '').replace(/\s*\([^)]*\)$/, '').trim() || msg
      }
      notify.permissionDenied(msg)
      throw error
    }

    if (response?.status !== 401 || config._retried || NO_RETRY.some(path => url.startsWith(path))) {
      throw error
    }
    config._retried = true
    refreshing = refreshing || client.post('/auth/refresh').finally(() => { refreshing = null })
    try {
      await refreshing
    } catch {
      // Het han han: ve trang dang nhap, giu lai trang dang xem de quay lai
      const here = window.location.pathname + window.location.search
      if (!window.location.pathname.startsWith('/login')) {
        window.location.assign(`/login?redirect=${encodeURIComponent(here)}`)
      }
      throw error
    }
    return client(config)
  },
)

export default client
