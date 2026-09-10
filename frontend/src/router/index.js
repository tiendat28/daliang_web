import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/customers' },
  { path: '/customers', name: 'customers', component: () => import('../views/CustomersView.vue'), meta: { title: 'Khách hàng' } },
  { path: '/company-products', name: 'company-products', component: () => import('../views/CompanyProductsView.vue'), meta: { title: 'Sản phẩm công ty' } },
  { path: '/lab-chemicals', name: 'lab-chemicals', component: () => import('../views/LabChemicalsView.vue'), meta: { title: 'Hóa chất' } },
  { path: '/equipment', name: 'equipment', component: () => import('../views/EquipmentView.vue'), meta: { title: 'Thiết bị' } },
  { path: '/chemical-orders', name: 'chemical-orders', component: () => import('../views/ChemicalOrdersView.vue'), meta: { title: 'Đơn hàng HCTN' } },
  { path: '/chemical-sampling', name: 'chemical-sampling', component: () => import('../views/ChemicalSamplingView.vue'), meta: { title: 'Lấy mẫu HC' } },
  { path: '/analysis-reports', name: 'analysis-reports', component: () => import('../views/AnalysisReportsView.vue'), meta: { title: 'Báo cáo phân tích' } },
  { path: '/work-log', name: 'work-log', component: () => import('../views/WorkLogView.vue'), meta: { title: 'Nhật ký công tác' } },
  { path: '/documents', name: 'documents', component: () => import('../views/DocumentsView.vue'), meta: { title: 'Tài liệu' } },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
