/* API module ky thuat - /api/v1/lab/... Du lieu dung chung (khach hang, san
 * pham, tai lieu, thong tin cong ty) o @/core/api/common. */
import client from '@/core/api/client'
import { crud } from '@/core/api/crud'

export const chemicalsApi = {
  ...crud('/lab/chemicals'),
  openBox: (id) => client.post(`/lab/chemicals/${id}/open-box`).then(r => r.data),
}
export const indicatorsApi = crud('/lab/indicators')
export const equipmentApi = crud('/lab/equipment')
export const formulationsApi = crud('/lab/formulations')
export const samplesApi = crud('/lab/samples')
export const analysisReportsApi = crud('/lab/analysis-reports')
export const workLogApi = crud('/lab/work-logs')

// ---------- Lưu trình test mẫu ----------

export const testProcessesApi = {
  list: (params) => client.get('/lab/test-processes', { params }).then(r => r.data),
  get: (id) => client.get(`/lab/test-processes/${id}`).then(r => r.data),
  create: (data) => client.post('/lab/test-processes', data).then(r => r.data),
  update: (id, data) => client.put(`/lab/test-processes/${id}`, data).then(r => r.data),
  remove: (id) => client.delete(`/lab/test-processes/${id}`).then(r => r.data),
  setStatus: (id, status) => client.patch(`/lab/test-processes/${id}/status`, { status }).then(r => r.data),
  duplicate: (id) => client.post(`/lab/test-processes/${id}/duplicate`).then(r => r.data),
  saveAsTemplate: (id, data) => client.post(`/lab/test-processes/${id}/save-as-template`, data).then(r => r.data),
  // HTML tờ A4, đổ thẳng vào srcdoc của iframe xem trước
  sheet: (id) => client.get(`/lab/test-processes/${id}/sheet`).then(r => r.data),
  previewSheet: (data) => client.post('/lab/test-processes/preview-sheet', data).then(r => r.data),
  operationSuggestions: (q) => client.get('/lab/test-processes/operation-suggestions', { params: q ? { q } : {} }).then(r => r.data),
  lastStep: (operation) => client.get('/lab/test-processes/last-step', { params: { operation } }).then(r => r.data),
  // HTML tờ in trắng với thông tin công ty đang gõ (chưa lưu) - khung xem trước ở trang Cài đặt
  letterheadPreview: (data) => client.post('/lab/test-processes/letterhead-preview', data).then(r => r.data),
  pdfUrl: (id, { download = true } = {}) => `${client.defaults.baseURL}/lab/test-processes/${id}/pdf?download=${download ? 1 : 0}`,
}

export const processTemplatesApi = crud('/lab/process-templates')
