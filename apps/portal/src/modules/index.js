/* Danh sach module cua cong - khop 1-1 voi backend/app/modules.
 *
 * Moi module la mot thu muc cung khung:
 *   pages/ components/ api.js routes.js (routes + menu) index.js (khai bao)
 * index.js tra ve { name, routes, menu, settingsSections? }. Them bo phan moi:
 * copy khung mot module co san roi them vao danh sach duoi day - khong phai
 * sua router hay sidebar.
 *
 * Quyen vao trang khai o meta cua route: `requires` (quyen dich danh) hoac
 * `permission` (nhom quyen, can `<nhom>.view`). Menu tu an muc khong vao duoc.
 */
import { can } from '@/core/auth/store'
import lab from './lab'
import hr from './hr'
import accounting from './accounting'
import warehouse from './warehouse'
import dispatch from './dispatch'
import system from './system'

export const modules = [lab, hr, accounting, warehouse, dispatch, system]

export const routeByName = Object.fromEntries(modules.flatMap(m => m.routes).filter(r => r.name).map(r => [r.name, r]))

/** Nguoi dang dang nhap co vao duoc trang nay khong (theo meta cua route). */
export function canVisit(meta = {}) {
  if (meta.requires) return can(meta.requires)
  if (meta.permission) return can(`${meta.permission}.view`)
  return true
}

/** Kiem tra co the truy cap vao item (hoac it nhat 1 tab trong nhom). */
export function canVisitItem(item) {
  if (item.tabs?.length) {
    return item.tabs.some(t => canVisit(routeByName[t.name]?.meta))
  }
  return canVisit(routeByName[item.name]?.meta)
}

/** Lay route de dieu huong khi click vao item tren Sidebar */
export function getItemRoute(item) {
  if (!item) return { name: 'home' }
  if (item.tabs?.length) {
    const allowed = item.tabs.find(t => canVisit(routeByName[t.name]?.meta))
    return { name: allowed ? allowed.name : item.targetName || item.name }
  }
  return { name: item.targetName || item.name }
}

/** Menu cua cac module (moi module mot muc cha: { section, label, icon, items }),
 *  bo muc con khong co quyen, bo module khong con muc nao.
 *  section: 'departments' (nhom Bo phan) | 'system' (nhom He thong). */
export function visibleMenus() {
  return modules
    .map(module => module.menu)
    .filter(Boolean)
    .map(menu => ({
      ...menu,
      items: menu.items.filter(item => canVisitItem(item)),
    }))
    .filter(menu => menu.items.length)
}

/** Muc con dang mo: dung ten route, hoac nam trong activeFor cua muc, hoac nam trong tabs cua muc. */
export function isItemActive(item, route) {
  if (!item || !route) return false
  if (route.name === item.name) return true
  if ((item.activeFor || []).includes(route.name)) return true
  if (item.tabs?.some(t => t.name === route.name || (t.activeFor || []).includes(route.name))) return true
  return false
}
