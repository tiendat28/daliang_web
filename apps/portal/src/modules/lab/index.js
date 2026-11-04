/* Khai bao module ky thuat voi cong: route, menu, phan rieng trong bang Cai dat. */
import { menu, routes } from './routes'
import { can } from '@/core/auth/store'
import LabDataSettings from './components/LabDataSettings.vue'

export default {
  name: 'lab',
  routes,
  menu,
  // Xuat Excel/PDF, sao luu du lieu lab - chi hien voi nguoi duoc xuat file du lieu lab
  settingsSections: [{ component: LabDataSettings, visible: () => can('lab.chemicals.export') }],
}
