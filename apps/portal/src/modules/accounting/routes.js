import {
  ArrowDownLeft,
  ArrowUpRight,
  BarChart3,
  FileText,
  LayoutDashboard,
  Receipt,
  ShoppingCart,
  Wallet,
} from 'lucide-vue-next'

const page = name => () => import(`./pages/${name}.vue`)

export const routes = [
  {
    path: '/accounting',
    redirect: '/accounting/overview',
  },
  {
    path: '/accounting/overview',
    name: 'accounting-overview',
    component: page('AccountingPage'),
    meta: { title: 'Kế toán - Tổng quan', permission: 'accounting.invoices', tab: 'overview', documentTopbar: true },
  },
  {
    path: '/accounting/sales-invoices',
    name: 'accounting-sales-invoices',
    component: page('AccountingPage'),
    meta: { title: 'Hoá đơn bán', permission: 'accounting.invoices', tab: 'sales-invoices', documentTopbar: true },
  },
  {
    path: '/accounting/purchase-invoices',
    name: 'accounting-purchase-invoices',
    component: page('AccountingPage'),
    meta: { title: 'Hoá đơn mua', permission: 'accounting.invoices', tab: 'purchase-invoices', documentTopbar: true },
  },
  {
    path: '/accounting/receivables',
    name: 'accounting-receivables',
    component: page('AccountingPage'),
    meta: { title: 'Công nợ phải thu', permission: 'accounting.receivables', tab: 'receivables', documentTopbar: true },
  },
  {
    path: '/accounting/payables',
    name: 'accounting-payables',
    component: page('AccountingPage'),
    meta: { title: 'Công nợ phải trả', permission: 'accounting.payables', tab: 'payables', documentTopbar: true },
  },
  {
    path: '/accounting/cashbook',
    name: 'accounting-cashbook',
    component: page('AccountingPage'),
    meta: { title: 'Sổ quỹ', permission: 'accounting.cashbook', tab: 'cashbook', documentTopbar: true },
  },
  {
    path: '/accounting/reports',
    name: 'accounting-reports',
    component: page('AccountingPage'),
    meta: { title: 'Báo cáo', permission: 'accounting.reports', tab: 'reports', documentTopbar: true },
  },
]

export const menu = {
  section: 'departments',
  label: 'Kế toán',
  icon: Receipt,
  items: [
    { name: 'accounting-overview', label: 'Tổng quan', icon: LayoutDashboard },
    { name: 'accounting-sales-invoices', label: 'Hoá đơn bán', icon: FileText },
    { name: 'accounting-purchase-invoices', label: 'Hoá đơn mua', icon: ShoppingCart },
    { name: 'accounting-receivables', label: 'Công nợ phải thu', icon: ArrowDownLeft },
    { name: 'accounting-payables', label: 'Công nợ phải trả', icon: ArrowUpRight },
    { name: 'accounting-cashbook', label: 'Sổ quỹ', icon: Wallet },
    { name: 'accounting-reports', label: 'Báo cáo', icon: BarChart3 },
  ],
}
