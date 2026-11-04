/* Goi API cua backend - chi phan cong khai /api/v1/website/public/... */
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
const PUBLIC = `${API_BASE}/website/public`

async function request(path, options = {}) {
  const response = await fetch(`${PUBLIC}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  })
  if (!response.ok) throw new Error(`${response.status} ${path}`)
  return response.json()
}

export const siteApi = {
  // Thong tin cong ty + san pham len web + giay to, mot lan goi
  site: () => request('/site'),
  // Tra MSDS/TDS theo ma tren ca danh muc; khong thay thi tra null
  lookup: (code) => request(`/lookup/${encodeURIComponent(code)}`),
  createLead: (data) => request('/contact-leads', { method: 'POST', body: JSON.stringify(data) }),
  // Link mo file MSDS/TDS/ban scan - chi 3 loai tai lieu cong khai
  fileUrl: (documentId) => `${PUBLIC}/files/${documentId}`,
}
