import client from '@/core/api/client'

/**
 * Backend chạy ở cổng khác frontend, nên các đường dẫn tĩnh nó trả về
 * ("/api/v1/static/img/logo.png") phải ghép thêm host của API mới tải được.
 */
export function apiOrigin() {
  return (client.defaults.baseURL || '').replace(/\/api(\/v\d+)?\/?$/, '')
}

/** "/api/v1/static/img/logo.png" -> "http://localhost:8001/api/v1/static/img/logo.png" */
export function assetUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//.test(path)) return path
  return `${apiOrigin()}/${path.replace(/^\//, '')}`
}
