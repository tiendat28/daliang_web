/* Route + menu cua module ky thuat - moi trang nam duoi /lab.
 *
 * meta.permission: nhom quyen cua trang - xem can `<nhom>.view`, nut them/sua/xoa
 *   can `<nhom>.edit` (khach hang, san pham, tai lieu la du lieu chung: `common.*`).
 * meta.nav / meta.navChild: Sidebar dua vao day de to sang muc dang mo (cac
 *   trang cua "Luu trinh test mau" dung chung mot muc).
 * hideTopbar: trang tu co dau trang rieng.
 */
import {
  Users, Package, FlaskConical, Wrench, ClipboardList, TestTubes,
  FileBarChart2, NotebookPen, FileText, ListChecks, LayoutTemplate,
  Boxes,
} from 'lucide-vue-next'

const page = name => () => import(`./pages/${name}.vue`)
const TEST_PROCESS = { title: 'Lưu trình test mẫu', permission: 'lab.test_processes', hideTopbar: true, documentTopbar: true, documentFull: true, nav: 'lab-test-processes', navChild: 'list' }

export const routes = [
  { path: '/lab/customers', name: 'lab-customers', component: page('CustomersPage'), meta: { permission: 'common.customers', title: 'Khách hàng' } },
  { path: '/lab/products', name: 'lab-products', component: page('ProductsPage'), meta: { permission: 'common.products', title: 'Sản phẩm công ty', documentFull: true } },
  { path: '/lab/chemicals', name: 'lab-chemicals', component: page('ChemicalsPage'), meta: { permission: 'lab.chemicals', title: 'Hóa chất' } },
  { path: '/lab/equipment', name: 'lab-equipment', component: page('EquipmentPage'), meta: { permission: 'lab.equipment', title: 'Thiết bị' } },
  { path: '/lab/formulations', name: 'lab-formulations', component: page('FormulationsPage'), meta: { permission: 'lab.formulations', title: 'Đơn hàng HCTN' } },
  { path: '/lab/samples', name: 'lab-samples', component: page('SamplesPage'), meta: { permission: 'lab.samples', title: 'Lấy mẫu HC' } },
  { path: '/lab/analysis-reports', name: 'lab-analysis-reports', component: page('AnalysisReportsPage'), meta: { permission: 'lab.analysis_reports', title: 'Báo cáo phân tích' } },
  { path: '/lab/documents', name: 'lab-documents', component: page('DocumentsPage'), meta: { permission: 'common.documents', title: 'Tài liệu' } },
  { path: '/lab/work-log', name: 'lab-work-log', component: page('WorkLogPage'), meta: { permission: 'lab.work_logs', title: 'Nhật ký công tác' } },

  // '/new' phai dung truoc ':id', va :id chi nhan chu so - khong thi 'new' bi coi la id
  { path: '/lab/test-processes', name: 'lab-test-processes', component: page('TestProcessesPage'), meta: TEST_PROCESS },
  { path: '/lab/test-processes/new', name: 'lab-test-process-new', component: page('TestProcessFormPage'), meta: TEST_PROCESS },
  { path: '/lab/test-processes/:id(\\d+)', name: 'lab-test-process-detail', component: page('TestProcessesPage'), meta: TEST_PROCESS },
  { path: '/lab/test-processes/:id(\\d+)/edit', name: 'lab-test-process-edit', component: page('TestProcessFormPage'), meta: TEST_PROCESS },
  { path: '/lab/process-templates', name: 'lab-process-templates', component: page('ProcessTemplatesPage'), meta: { ...TEST_PROCESS, title: 'Quy trình chuẩn', permission: 'lab.process_templates', documentFull: false, navChild: 'templates' } },
]

/**
 * 4 nhom chuc nang cua bo phan Ky thuat cho Tabs ngang va Sidebar:
 * 1. Vat tu & Thiet bi (Hoa chat, Thiet bi)
 * 2. Thu nghiem & Mau (Lay mau HC, Luu trinh test mau, Don hang HCTN, Bao cao phan tich)
 * 3. Tai lieu & Quy trinh (Tai lieu, Quy trinh chuan)
 * 4. Nhat ky cong tac (Mo truc tiep)
 */
export const LAB_GROUPS = [
  {
    id: 'supplies-equipment',
    name: 'lab-supplies-equipment',
    label: 'Vật tư & Thiết bị',
    icon: Boxes,
    tabs: [
      { name: 'lab-chemicals', label: 'Hóa chất', icon: FlaskConical },
      { name: 'lab-equipment', label: 'Thiết bị', icon: Wrench },
    ],
  },
  {
    id: 'testing-samples',
    name: 'lab-testing-samples',
    label: 'Thử nghiệm & Mẫu',
    icon: TestTubes,
    tabs: [
      { name: 'lab-samples', label: 'Lấy mẫu HC', icon: TestTubes },
      {
        name: 'lab-test-processes',
        label: 'Lưu trình test mẫu',
        icon: ListChecks,
        activeFor: ['lab-test-process-new', 'lab-test-process-detail', 'lab-test-process-edit'],
      },
      { name: 'lab-formulations', label: 'Đơn hàng HCTN', icon: ClipboardList },
      { name: 'lab-analysis-reports', label: 'Báo cáo phân tích', icon: FileBarChart2 },
    ],
  },
  {
    id: 'docs-processes',
    name: 'lab-docs-processes',
    label: 'Tài liệu & Quy trình',
    icon: FileText,
    tabs: [
      { name: 'lab-documents', label: 'Tài liệu', icon: FileText },
      { name: 'lab-process-templates', label: 'Quy trình chuẩn', icon: LayoutTemplate },
    ],
  },
  {
    id: 'work-log',
    name: 'lab-work-log',
    label: 'Nhật ký công tác',
    icon: NotebookPen,
    tabs: [
      { name: 'lab-work-log', label: 'Nhật ký công tác', icon: NotebookPen },
    ],
  },
]

// Mot muc "Ky thuat" o nhom Bo phan tren thanh ben, gom 4 nhom con
export const menu = {
  section: 'departments',
  label: 'Kỹ thuật',
  icon: FlaskConical,
  items: [
    { name: 'lab-customers', label: 'Khách hàng', icon: Users },
    { name: 'lab-products', label: 'Sản phẩm công ty', icon: Package },
    {
      name: 'lab-supplies-equipment',
      label: 'Vật tư & Thiết bị',
      icon: Boxes,
      targetName: 'lab-chemicals',
      tabs: LAB_GROUPS[0].tabs,
      activeFor: ['lab-chemicals', 'lab-equipment'],
    },
    {
      name: 'lab-testing-samples',
      label: 'Thử nghiệm & Mẫu',
      icon: TestTubes,
      targetName: 'lab-samples',
      tabs: LAB_GROUPS[1].tabs,
      activeFor: [
        'lab-samples',
        'lab-test-processes',
        'lab-test-process-new',
        'lab-test-process-detail',
        'lab-test-process-edit',
        'lab-formulations',
        'lab-analysis-reports',
      ],
    },
    {
      name: 'lab-docs-processes',
      label: 'Tài liệu & Quy trình',
      icon: FileText,
      targetName: 'lab-documents',
      tabs: LAB_GROUPS[2].tabs,
      activeFor: ['lab-documents', 'lab-process-templates'],
    },
    {
      name: 'lab-work-log',
      label: 'Nhật ký công tác',
      icon: NotebookPen,
      tabs: LAB_GROUPS[3].tabs,
    },
  ],
}
