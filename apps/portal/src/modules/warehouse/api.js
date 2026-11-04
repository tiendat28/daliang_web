import client from '@/core/api/client'

export const getWarehouseDashboard = params => client.get('/warehouse/dashboard', { params })
export const getStock = params => client.get('/warehouse/stock', { params })
export const createStock = data => client.post('/warehouse/stock', data)

export const getReceipts = () => client.get('/warehouse/receipts')
export const createReceipt = data => client.post('/warehouse/receipts', data)

export const getDispatches = () => client.get('/warehouse/dispatches')
export const createDispatch = data => client.post('/warehouse/dispatches', data)
export const pickDispatch = id => client.post(`/warehouse/dispatches/${id}/pick`)
export const loadDispatch = (id, data) => client.post(`/warehouse/dispatches/${id}/load`, data)

export const getLocations = () => client.get('/warehouse/locations')
export const getAudits = () => client.get('/warehouse/audits')
export const createAudit = data => client.post('/warehouse/audits', data)
