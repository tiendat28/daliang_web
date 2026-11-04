/* API dang nhap - /api/v1/auth/... Phien nam trong cookie httpOnly (JS khong doc
 * duoc token), trinh duyet tu gui kem moi request cung ten mien. */
import client from '@/core/api/client'

const post = (path, data) => client.post(`/auth${path}`, data).then(r => r.data)

export const authApi = {
  login: (identifier, password, remember = false) => post('/login', { identifier, password, remember }),
  verify2fa: (code) => post('/2fa/verify', { code }),
  setup2fa: () => post('/2fa/setup'),
  enable2fa: (code) => post('/2fa/enable', { code }),
  disable2fa: (password) => post('/2fa/disable', { password }),
  newBackupCodes: (password) => post('/2fa/backup-codes', { password }),
  refresh: () => post('/refresh'),
  logout: () => post('/logout'),
  me: () => client.get('/auth/me').then(r => r.data),
  changePassword: (currentPassword, newPassword) =>
    post('/change-password', { current_password: currentPassword, new_password: newPassword }),
  forgotPassword: (email) => post('/forgot-password', { email }),
  resetPassword: (token, newPassword) => post('/reset-password', { token, new_password: newPassword }),
}
