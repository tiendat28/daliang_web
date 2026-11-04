import {
  Car,
  LayoutDashboard,
  Navigation,
  Truck,
  Users,
} from 'lucide-vue-next'

const page = name => () => import(`./pages/${name}.vue`)

export const routes = [
  {
    path: '/delivery',
    redirect: '/delivery/board',
  },
  {
    path: '/dispatch',
    redirect: '/delivery/board',
  },
  {
    path: '/delivery/board',
    name: 'dispatch-board',
    component: page('DispatchPage'),
    meta: { title: 'Điều phối - Bảng điều phối', permission: 'dispatch.trips', tab: 'board', documentTopbar: true },
  },
  {
    path: '/delivery/trips',
    name: 'dispatch-trips',
    component: page('DispatchPage'),
    meta: { title: 'Điều phối - Chuyến giao', permission: 'dispatch.trips', tab: 'trips', documentTopbar: true },
  },
  {
    path: '/delivery/vehicles',
    name: 'dispatch-vehicles',
    component: page('DispatchPage'),
    meta: { title: 'Điều phối - Xe', permission: 'dispatch.vehicles', tab: 'vehicles', documentTopbar: true },
  },
  {
    path: '/delivery/drivers',
    name: 'dispatch-drivers',
    component: page('DispatchPage'),
    meta: { title: 'Điều phối - Tài xế', permission: 'dispatch.drivers', tab: 'drivers', documentTopbar: true },
  },
]

export const menu = {
  section: 'departments',
  label: 'Điều phối xe',
  icon: Truck,
  items: [
    { name: 'dispatch-board', label: 'Bảng điều phối', icon: LayoutDashboard },
    { name: 'dispatch-trips', label: 'Chuyến giao', icon: Navigation },
    { name: 'dispatch-vehicles', label: 'Xe', icon: Car },
    { name: 'dispatch-drivers', label: 'Tài xế', icon: Users },
  ],
}
