import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/customers', alias: '/', name: 'customers', component: () => import('../views/CustomersView.vue'), meta: { title: 'Khách hàng' } },
  { path: '/company-products', name: 'company-products', component: () => import('../views/CompanyProductsView.vue'), meta: { title: 'Sản phẩm công ty' } },
  { path: '/lab-chemicals', name: 'lab-chemicals', component: () => import('../views/LabChemicalsView.vue'), meta: { title: 'Hóa chất' } },
  { path: '/equipment', name: 'equipment', component: () => import('../views/EquipmentView.vue'), meta: { title: 'Thiết bị' } },
  { path: '/chemical-orders', name: 'chemical-orders', component: () => import('../views/ChemicalOrdersView.vue'), meta: { title: 'Đơn hàng HCTN' } },
  { path: '/chemical-sampling', name: 'chemical-sampling', component: () => import('../views/ChemicalSamplingView.vue'), meta: { title: 'Lấy mẫu HC' } },
  { path: '/analysis-reports', name: 'analysis-reports', component: () => import('../views/AnalysisReportsView.vue'), meta: { title: 'Báo cáo phân tích' } },
  { path: '/work-log', name: 'work-log', component: () => import('../views/WorkLogView.vue'), meta: { title: 'Nhật ký công tác' } },
  { path: '/documents', name: 'documents', component: () => import('../views/DocumentsView.vue'), meta: { title: 'Tài liệu' } },

  // Luu trinh test mau. Duong dan '/new' phai dung truoc ':id' va :id chi nhan
  // chu so, khong thi vue-router coi 'new' la mot id.
  // meta.nav* de Sidebar tu biet to sang muc nao - khong phai chep lai danh
  // sach ten route ben do nua; hideTopbar vi cac trang nay tu co dau trang rieng.
  { path: '/test-processes', name: 'test-processes', component: () => import('../views/TestProcessesView.vue'), meta: { title: 'Lưu trình test mẫu', hideTopbar: true, nav: 'test-processes', navChild: 'list' } },
  { path: '/test-processes/new', name: 'test-process-new', component: () => import('../views/TestProcessFormView.vue'), meta: { title: 'Lưu trình test mẫu', hideTopbar: true, nav: 'test-processes', navChild: 'list' } },
  { path: '/test-processes/:id(\\d+)', name: 'test-process-detail', component: () => import('../views/TestProcessesView.vue'), meta: { title: 'Lưu trình test mẫu', hideTopbar: true, nav: 'test-processes', navChild: 'list' } },
  { path: '/test-processes/:id(\\d+)/edit', name: 'test-process-edit', component: () => import('../views/TestProcessFormView.vue'), meta: { title: 'Lưu trình test mẫu', hideTopbar: true, nav: 'test-processes', navChild: 'list' } },
  { path: '/process-templates', name: 'process-templates', component: () => import('../views/ProcessTemplatesView.vue'), meta: { title: 'Quy trình chuẩn', hideTopbar: true, nav: 'test-processes', navChild: 'templates' } },
  { path: '/company-profile', name: 'company-profile', component: () => import('../views/CompanyProfileView.vue'), meta: { title: 'Thông tin công ty', hideTopbar: true, nav: 'test-processes' } },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
