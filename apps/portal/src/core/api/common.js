/* API du lieu dung chung cua cong ty - /api/v1/common/...
 * (khach hang, san pham, thong tin cong ty, tai lieu). Moi module dung tu day,
 * khong module nao tu khai bao lai. */
import client from '@/core/api/client'
import { crud } from '@/core/api/crud'

export const customersApi = crud('/common/customers')
export const productsApi = crud('/common/products')

export const documentsApi = {
  list: (category) => client.get('/common/documents', { params: category ? { category } : {} }).then(r => r.data),
  upload: (formData) => client.post('/common/documents', formData).then(r => r.data),
  remove: (id) => client.delete(`/common/documents/${id}`).then(r => r.data),
  fileUrl: (id, { inline = false } = {}) => `${client.defaults.baseURL}/common/documents/${id}/file${inline ? '?inline=true' : ''}`,
}

export const companyProfileApi = {
  get: () => client.get('/common/company-profile').then(r => r.data),
  update: (data) => client.put('/common/company-profile', data).then(r => r.data),
  uploadLogo: (formData) => client.post('/common/company-profile/logo', formData).then(r => r.data),
}
