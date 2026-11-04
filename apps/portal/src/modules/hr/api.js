import client from '@/core/api/client'
import { crud } from '@/core/api/crud'

export const hrDashboardApi = { get: () => client.get('/hr/dashboard').then(r => r.data) }
export const employeesApi = crud('/hr/employees')
export const departmentsApi = crud('/hr/departments')
export const attendanceApi = crud('/hr/attendance')
export const leaveRequestsApi = {
  ...crud('/hr/leave-requests'),
  decide: (id, status) => client.patch(`/hr/leave-requests/${id}/decision`, { status }).then(r => r.data),
}
export const contractsApi = crud('/hr/contracts')
export const certificatesApi = crud('/hr/certificates')
