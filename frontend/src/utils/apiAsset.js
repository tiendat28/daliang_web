import client from '../api/client'

/**
 * Backend chạy ở cổng khác frontend, nên các đường dẫn tĩnh nó trả về
 * ("/api/static/img/logo.png") phải ghép thêm host của API mới tải được.
 */
export function apiOrigin() {
  return (client.defaults.baseURL || '').replace(/\/api\/?$/, '')
}

/** "/api/static/img/logo.png" -> "http://localhost:8001/api/static/img/logo.png" */
export function assetUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//.test(path)) return path
  return `${apiOrigin()}/${path.replace(/^\//, '')}`
}
