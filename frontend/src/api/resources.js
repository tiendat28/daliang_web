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
