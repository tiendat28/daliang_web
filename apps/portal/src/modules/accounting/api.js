/* API phan he ke toan - /api/v1/accounting/... */
import client from '@/core/api/client'

const data = r => r.data

export const accountingApi = {
  getDashboard: () => client.get('/accounting/dashboard').then(data),
  listInvoices: (params) => client.get('/accounting/invoices', { params }).then(data),
  getInvoice: (id) => client.get(`/accounting/invoices/${id}`).then(data),
  createInvoice: (payload) => client.post('/accounting/invoices', payload).then(data),
  deleteInvoice: (id) => client.delete(`/accounting/invoices/${id}`).then(data),
  remindDebt: (id, payload) => client.post(`/accounting/invoices/${id}/remind-debt`, payload).then(data),
  listVouchers: (params) => client.get('/accounting/vouchers', { params }).then(data),
  createVoucher: (payload) => client.post('/accounting/vouchers', payload).then(data),
  deleteVoucher: (id) => client.delete(`/accounting/vouchers/${id}`).then(data),
  listBankAccounts: () => client.get('/accounting/bank-accounts').then(data),
}
