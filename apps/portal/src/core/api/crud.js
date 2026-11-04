import client from '@/core/api/client'

/** Thao tac CRUD chuan cho mot tai nguyen REST: list / get / create / update / remove. */
export function crud(path) {
  return {
    list: (params) => client.get(path, { params }).then(r => r.data),
    get: (id) => client.get(`${path}/${id}`).then(r => r.data),
    create: (data) => client.post(path, data).then(r => r.data),
    update: (id, data) => client.put(`${path}/${id}`, data).then(r => r.data),
    remove: (id) => client.delete(`${path}/${id}`).then(r => r.data),
  }
}
