/* Router cua cong: route chung (dang nhap, tong quan) + route cua moi module.
 *
 * Chan truoc moi trang:
 *   - chua dang nhap           -> /login?redirect=<trang dang muon vao>
 *   - dang dung mat khau tam   -> /profile (doi xong moi di tiep)
 *   - khong co quyen vao trang -> ve trang tong quan
 * Backend van tu chan tung API - day chi de khong mo trang ma khong dung duoc.
 */
import { createRouter, createWebHistory } from 'vue-router'
import { coreRoutes } from '@/core/routes'
import { auth, loadMe } from '@/core/auth/store'
import { canVisit, modules } from '@/modules'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...coreRoutes,
    ...modules.flatMap(module => module.routes),
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  if (!auth.loaded) await loadMe()

  if (to.meta.public) {
    // Da dang nhap ma mo trang dang nhap -> vao thang
    return auth.user && to.name === 'login' ? (to.query.redirect || '/') : true
  }
  if (!auth.user) return { name: 'login', query: { redirect: to.fullPath } }
  if (auth.user.must_change_password && to.name !== 'profile') return { name: 'profile' }
  if (!canVisit(to.meta)) return { name: 'home' }
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} — Daliang VN` : 'Daliang VN'
})

export default router
