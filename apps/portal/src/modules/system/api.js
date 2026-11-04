/* API quan tri - /api/v1/system/... va don khach gui tu website. */
import client from '@/core/api/client'

const data = r => r.data

export const usersApi = {
  list: () => client.get('/system/users').then(data),
  create: (payload) => client.post('/system/users', payload).then(data),
  update: (id, payload) => client.put(`/system/users/${id}`, payload).then(data),
  remove: (id) => client.delete(`/system/users/${id}`).then(data),
  setActive: (id, isActive) => client.patch(`/system/users/${id}/active`, { is_active: isActive }).then(data),
  resetPassword: (id) => client.post(`/system/users/${id}/reset-password`).then(data),
  reset2fa: (id) => client.post(`/system/users/${id}/reset-2fa`).then(data),
  unlock: (id) => client.post(`/system/users/${id}/unlock`).then(data),
}

export const rolesApi = {
  list: () => client.get('/system/roles').then(data),
  permissions: () => client.get('/system/permissions').then(data),
  create: (payload) => client.post('/system/roles', payload).then(data),
  update: (id, payload) => client.put(`/system/roles/${id}`, payload).then(data),
  remove: (id) => client.delete(`/system/roles/${id}`).then(data),
}

export const auditLogApi = {
  list: (params) => client.get('/system/audit-logs', { params }).then(data),
}

export const contactLeadsApi = {
  list: () => client.get('/website/contact-leads').then(data),
  setHandled: (id, isHandled) => client.patch(`/website/contact-leads/${id}`, { is_handled: isHandled }).then(data),
}

export const productWebsiteApi = {
  // web_group: 'pre' | 'add' | 'pas' | null (khong len web)
  update: (id, payload) => client.patch(`/common/products/${id}/website`, payload).then(data),
}
