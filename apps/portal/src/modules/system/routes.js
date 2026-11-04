/* Route + menu cua module he thong (Admin cao nhat) - duoi /system.
 * meta.requires: quyen dich danh can co de vao trang (trang quan tri khong theo
 * kieu xem/them/sua/xoa). meta.permission: nhom quyen nhu module khac. */
import { Building2, Globe, ScrollText, ShieldCheck, Users } from 'lucide-vue-next'

const page = name => () => import(`./pages/${name}.vue`)

export const routes = [
  { path: '/system/users', name: 'system-users', component: page('UsersPage'), meta: { title: 'Người dùng & phân quyền', requires: 'system.users.manage', hideTopbar: true, documentTopbar: true } },
  { path: '/system/roles', redirect: { name: 'system-users' } },
  { path: '/system/website', name: 'system-website', component: page('WebsitePage'), meta: { title: 'Nội dung website', permission: 'website.contact_leads' } },
  { path: '/system/audit-log', name: 'system-audit-log', component: page('AuditLogPage'), meta: { title: 'Nhật ký thao tác', requires: 'system.audit_log.view' } },
  { path: '/system/settings', name: 'system-settings', component: page('SettingsPage'), meta: { title: 'Cấu hình', permission: 'common.company_profile' } },
]

// Mot muc "Quan tri he thong" o nhom He thong tren thanh ben
export const menu = {
  section: 'system',
  label: 'Quản trị hệ thống',
  icon: ShieldCheck,
  items: [
    { name: 'system-users', label: 'Người dùng & quyền', icon: Users },
    { name: 'system-website', label: 'Nội dung website', icon: Globe },
    { name: 'system-audit-log', label: 'Nhật ký thao tác', icon: ScrollText },
    { name: 'system-settings', label: 'Cấu hình', icon: Building2 },
  ],
}
