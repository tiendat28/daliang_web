/* Nguoi dang dang nhap + quyen. Quyen dat ten `module.doi_tuong.hanh_dong`;
 * "*" la moi quyen. Backend moi la noi chan that - o day chi de an/hien. */
import { reactive } from 'vue'
import { useRoute } from 'vue-router'
import { authApi } from './api'

export const auth = reactive({
  user: null,      // null = chua dang nhap
  loaded: false,   // da hoi /auth/me it nhat mot lan
})

export function setUser(user) {
  auth.user = user
  auth.loaded = true
}

/** Hoi backend xem cookie con phien khong (goi mot lan luc mo cong). */
export async function loadMe() {
  try {
    setUser(await authApi.me())
  } catch {
    setUser(null)
  }
}

export async function logout() {
  try { await authApi.logout() } catch { /* van xoa phia trinh duyet */ }
  setUser(null)
}

export function can(code) {
  if (!code) return true
  const permissions = auth.user?.permissions || []
  return permissions.includes('*') || permissions.includes(code)
}

/** Quyen tren trang hien tai theo meta.permission cua route (vd 'lab.chemicals'):
 *    const can = usePageCan()
 *    can('create') / can('update') / can('delete') / can('export') / can('approve')
 *  Dung o TableCard (them), DataTable (sua/xoa) va cac nut rieng cua tung trang.
 *  Trang khong khai meta.permission thi cho het. */
export function usePageCan() {
  const route = useRoute()
  return action => !route.meta.permission || can(`${route.meta.permission}.${action}`)
}
