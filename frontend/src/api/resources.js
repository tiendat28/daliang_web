import client from './client'

function crud(path) {
  return {
    list: () => client.get(path).then(r => r.data),
    create: (data) => client.post(path, data).then(r => r.data),
    update: (id, data) => client.put(`${path}/${id}`, data).then(r => r.data),
    remove: (id) => client.delete(`${path}/${id}`).then(r => r.data),
  }
}

export const customersApi = crud('/customers')
export const companyProductsApi = crud('/company-products')
export const labChemicalsApi = {
  ...crud('/lab-chemicals'),
  openBox: (id) => client.post(`/lab-chemicals/${id}/open-box`).then(r => r.data),
}
export const indicatorsApi = crud('/indicators')
export const equipmentApi = crud('/equipment')
export const chemicalOrdersApi = crud('/chemical-orders')
export const chemicalSamplingApi = crud('/chemical-sampling')
export const analysisReportsApi = crud('/analysis-reports')
export const workLogApi = crud('/work-logs')

export const documentsApi = {
  list: (category) => client.get('/documents', { params: category ? { category } : {} }).then(r => r.data),
  upload: (formData) => client.post('/documents', formData).then(r => r.data),
  remove: (id) => client.delete(`/documents/${id}`).then(r => r.data),
  fileUrl: (id, { inline = false } = {}) => `${client.defaults.baseURL}/documents/${id}/file${inline ? '?inline=true' : ''}`,
}

// ---------- Lưu trình test mẫu ----------

export const testProcessesApi = {
  list: (params) => client.get('/test-processes', { params }).then(r => r.data),
  get: (id) => client.get(`/test-processes/${id}`).then(r => r.data),
  create: (data) => client.post('/test-processes', data).then(r => r.data),
  update: (id, data) => client.put(`/test-processes/${id}`, data).then(r => r.data),
  remove: (id) => client.delete(`/test-processes/${id}`).then(r => r.data),
  setStatus: (id, status) => client.patch(`/test-processes/${id}/status`, { status }).then(r => r.data),
  duplicate: (id) => client.post(`/test-processes/${id}/duplicate`).then(r => r.data),
  saveAsTemplate: (id, data) => client.post(`/test-processes/${id}/save-as-template`, data).then(r => r.data),
  // HTML tờ A4, đổ thẳng vào srcdoc của iframe xem trước
  sheet: (id) => client.get(`/test-processes/${id}/sheet`).then(r => r.data),
  previewSheet: (data) => client.post('/test-processes/preview-sheet', data).then(r => r.data),
  operationSuggestions: (q) => client.get('/test-processes/operation-suggestions', { params: q ? { q } : {} }).then(r => r.data),
  lastStep: (operation) => client.get('/test-processes/last-step', { params: { operation } }).then(r => r.data),
  pdfUrl: (id, { download = true } = {}) => `${client.defaults.baseURL}/test-processes/${id}/pdf?download=${download ? 1 : 0}`,
}

export const processTemplatesApi = crud('/process-templates')

export const companyProfileApi = {
  get: () => client.get('/company-profile').then(r => r.data),
  update: (data) => client.put('/company-profile', data).then(r => r.data),
  uploadLogo: (formData) => client.post('/company-profile/logo', formData).then(r => r.data),
  // HTML tờ in với letterhead đang gõ (chưa lưu), cho khung xem trước
  preview: (data) => client.post('/company-profile/preview', data).then(r => r.data),
}
