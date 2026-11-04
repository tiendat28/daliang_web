import {
  ArrowDownToLine,
  ArrowUpFromLine,
  ClipboardCheck,
  Layers,
  MapPin,
  Warehouse,
} from 'lucide-vue-next'

const page = name => () => import(`./pages/${name}.vue`)

export const routes = [
  {
    path: '/warehouse',
    redirect: '/warehouse/stock',
  },
  {
    path: '/warehouse/stock',
    name: 'warehouse-stock',
    component: page('WarehousePage'),
    meta: { title: 'Kho - Tồn kho', permission: 'warehouse.stock', tab: 'stock', documentTopbar: true },
  },
  {
    path: '/warehouse/receipts',
    name: 'warehouse-receipts',
    component: page('WarehousePage'),
    meta: { title: 'Kho - Phiếu nhập', permission: 'warehouse.receipts', tab: 'receipts', documentTopbar: true },
  },
  {
    path: '/warehouse/dispatches',
    name: 'warehouse-dispatches',
    component: page('WarehousePage'),
    meta: { title: 'Kho - Phiếu xuất', permission: 'warehouse.dispatches', tab: 'dispatches', documentTopbar: true },
  },
  {
    path: '/warehouse/audit',
    name: 'warehouse-audit',
    component: page('WarehousePage'),
    meta: { title: 'Kho - Kiểm kê', permission: 'warehouse.audits', tab: 'audit', documentTopbar: true },
  },
  {
    path: '/warehouse/locations',
    name: 'warehouse-locations',
    component: page('WarehousePage'),
    meta: { title: 'Kho - Vị trí kho', permission: 'warehouse.locations', tab: 'locations', documentTopbar: true },
  },
]

export const menu = {
  section: 'departments',
  label: 'Kho',
  icon: Warehouse,
  items: [
    { name: 'warehouse-stock', label: 'Tồn kho', icon: Layers },
    { name: 'warehouse-receipts', label: 'Phiếu nhập', icon: ArrowDownToLine },
    { name: 'warehouse-dispatches', label: 'Phiếu xuất', icon: ArrowUpFromLine },
    { name: 'warehouse-audit', label: 'Kiểm kê', icon: ClipboardCheck },
    { name: 'warehouse-locations', label: 'Vị trí kho', icon: MapPin },
  ],
}
