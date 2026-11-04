<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  BriefcaseBusiness,
  CalendarCheck2,
  Check,
  Clock3,
  Download,
  FileBadge2,
  FileText,
  Pencil,
  Plus,
  Search,
  Trash2,
  UsersRound,
  X,
} from 'lucide-vue-next'
import Modal from '@/core/components/Modal.vue'
import FormActions from '@/core/components/FormActions.vue'
import { usePageCan } from '@/core/auth/store'
import { errorMessage } from '@/core/api/errors'
import { notify } from '@/core/store/notify'
import { exportToCsv } from '@/core/utils/export'
import {
  attendanceApi,
  certificatesApi,
  contractsApi,
  departmentsApi,
  employeesApi,
  hrDashboardApi,
  leaveRequestsApi,
} from '../api'

const can = usePageCan()
const tabs = [
  { key: 'employees', label: 'Hồ sơ nhân viên', icon: UsersRound },
  { key: 'attendance', label: 'Chấm công', icon: Clock3 },
  { key: 'leave', label: 'Nghỉ phép', icon: CalendarCheck2 },
  { key: 'contracts', label: 'Hợp đồng', icon: FileText },
  { key: 'certificates', label: 'Đào tạo & chứng chỉ', icon: FileBadge2 },
  { key: 'departments', label: 'Phòng ban', icon: BriefcaseBusiness },
]

const activeTab = ref('employees')
const dashboard = ref(null)
const rows = ref([])
const departments = ref([])
const loading = ref(true)
const saving = ref(false)
const query = ref('')
const error = ref('')
const showModal = ref(false)
const editingId = ref(null)
const form = ref({})

const employeeRows = computed(() => (dashboard.value?.employees || []).filter(row => {
  const needle = query.value.trim().toLowerCase()
  return !needle || `${row.employee_code} ${row.full_name} ${row.email || ''} ${row.department_name || ''} ${row.position || ''}`.toLowerCase().includes(needle)
}))

const filteredRows = computed(() => {
  const needle = query.value.trim().toLowerCase()
  if (!needle) return rows.value
  return rows.value.filter(row => {
    const text = Object.values(row).filter(v => typeof v === 'string' || typeof v === 'number').join(' ').toLowerCase()
    const emp = row.employee_id ? employeeName(row.employee_id).toLowerCase() : ''
    return text.includes(needle) || emp.includes(needle)
  })
})

const pendingLeaves = computed(() => dashboard.value?.pending_leaves || [])
const expiringCertificates = computed(() => dashboard.value?.expiring_certificates || [])

const stats = computed(() => [
  { label: 'Tổng nhân sự', value: dashboard.value?.total_employees ?? 0, note: `${dashboard.value?.active_employees ?? 0} đang làm`, icon: UsersRound, tone: 'teal' },
  { label: 'Đi làm hôm nay', value: dashboard.value?.present_today ?? 0, note: 'đã chấm công', icon: Clock3, tone: 'ok' },
  { label: 'Nghỉ phép', value: dashboard.value?.leave_today ?? 0, note: 'hôm nay', icon: CalendarCheck2, tone: 'info' },
  { label: 'Hợp đồng sắp hết', value: dashboard.value?.contracts_expiring ?? 0, note: 'trong 45 ngày', icon: FileText, tone: 'warn' },
])

const emptyEmployee = () => ({ employee_code: '', full_name: '', email: '', phone: '', department_code: '', position: '', start_date: '', contract_end: '', status: 'active', note: '' })
const emptyAttendance = () => ({ employee_id: '', work_date: new Date().toISOString().slice(0, 10), check_in: '', check_out: '', status: 'present', note: '' })
const emptyLeave = () => ({ employee_id: '', leave_type: 'annual', start_date: '', end_date: '', reason: '' })
const emptyContract = () => ({ employee_id: '', contract_type: 'Hợp đồng xác định thời hạn', start_date: '', end_date: '', status: 'active', note: '' })
const emptyCertificate = () => ({ employee_id: '', name: '', issuer: '', issued_date: '', expires_at: '', note: '' })

function employeeName(id) { return dashboard.value?.employees?.find(row => row.id === id)?.full_name || id || '—' }
function employeeOptions() { return (dashboard.value?.employees || []).map(row => ({ value: row.id, label: `${row.employee_code} · ${row.full_name}` })) }

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    dashboard.value = await hrDashboardApi.get()
    departments.value = await departmentsApi.list()
    if (activeTab.value !== 'employees') await loadTab()
  } catch (e) { error.value = errorMessage(e) } finally { loading.value = false }
}

async function loadTab() {
  if (activeTab.value === 'employees') return
  const apis = { attendance: attendanceApi, leave: leaveRequestsApi, contracts: contractsApi, certificates: certificatesApi, departments: departmentsApi }
  rows.value = await apis[activeTab.value].list()
}

async function switchTab(key) { activeTab.value = key; query.value = ''; await loadTab() }

function openAdd() {
  const forms = { employees: emptyEmployee, attendance: emptyAttendance, leave: emptyLeave, contracts: emptyContract, certificates: emptyCertificate, departments: () => ({ code: '', name: '', is_active: true }) }
  editingId.value = null; form.value = forms[activeTab.value](); showModal.value = true
}

function openEdit(row) { editingId.value = row.id; form.value = { ...row }; showModal.value = true }

async function save() {
  saving.value = true; error.value = ''
  try {
    const apis = { employees: employeesApi, attendance: attendanceApi, leave: leaveRequestsApi, contracts: contractsApi, certificates: certificatesApi, departments: departmentsApi }
    const payload = { ...form.value }
    if (activeTab.value === 'employees') delete payload.department_name
    if (editingId.value) await apis[activeTab.value].update(editingId.value, payload)
    else await apis[activeTab.value].create(payload)
    showModal.value = false
    await loadDashboard()
    if (activeTab.value !== 'employees') await loadTab()
  } catch (e) {
    if (e?.response?.status !== 403) {
      notify.error(errorMessage(e))
    }
  } finally { saving.value = false }
}

async function decideLeave(row, status) {
  try {
    await leaveRequestsApi.decide(row.id, status)
    await loadDashboard()
    if (activeTab.value === 'leave') await loadTab()
  } catch (e) {
    if (e?.response?.status !== 403) {
      notify.error(errorMessage(e))
    }
  }
}

async function removeRow(row) {
  if (!confirm('Xóa bản ghi này?')) return
  const apis = { employees: employeesApi, attendance: attendanceApi, leave: leaveRequestsApi, contracts: contractsApi, certificates: certificatesApi, departments: departmentsApi }
  try {
    await apis[activeTab.value].remove(row.id)
    await loadDashboard()
    if (activeTab.value !== 'employees') await loadTab()
  } catch (e) {
    if (e?.response?.status !== 403) {
      notify.error(errorMessage(e))
    }
  }
}

function exportCsv() {
  if (!employeeRows.value.length) return
  const headers = ['Mã nhân viên', 'Họ tên', 'Email', 'Điện thoại', 'Phòng ban', 'Chức vụ', 'Ngày vào', 'Hợp đồng đến', 'Trạng thái']
  const rows = employeeRows.value.map(r => [
    r.employee_code,
    r.full_name,
    r.email || '',
    r.phone || '',
    r.department_name || '',
    r.position || '',
    r.start_date || '',
    r.contract_end || '',
    r.status === 'active' ? 'Đang làm' : 'Nghỉ việc',
  ])
  exportToCsv(`danh_sach_nhan_vien_${new Date().toISOString().slice(0, 10)}.csv`, headers, rows)
}

onMounted(loadDashboard)
</script>

<template>
  <div class="hr-page">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div><h1 class="hr-title">Nhân sự</h1><p class="hr-subtitle">Quản lý hồ sơ, chấm công, nghỉ phép và phát triển nhân viên.</p></div>
      <button v-if="can('create')" type="button" class="dl-btn" @click="openAdd"><Plus class="w-4 h-4" /> Thêm {{ activeTab === 'employees' ? 'nhân viên' : 'bản ghi' }}</button>
    </div>

    <div v-if="loading" class="grid grid-cols-2 xl:grid-cols-4 gap-4"><div v-for="item in 4" :key="item" class="h-[132px] rounded-[20px] bg-white/70 dark:bg-slate-800/70 animate-pulse" /></div>
    <div v-else class="grid grid-cols-2 xl:grid-cols-4 gap-4">
      <article v-for="stat in stats" :key="stat.label" class="dl-stat-card"><span class="dl-stat-icon" :class="`hr-stat-${stat.tone}`"><component :is="stat.icon" class="w-5 h-5" /></span><span class="dl-stat-label">{{ stat.label }}</span><strong>{{ stat.value }}</strong><small>{{ stat.note }}</small></article>
    </div>

    <div class="hr-tabs"><button v-for="tab in tabs" :key="tab.key" type="button" :class="activeTab === tab.key ? 'hr-tab-active' : 'hr-tab'" @click="switchTab(tab.key)"><component :is="tab.icon" class="w-4 h-4" />{{ tab.label }}</button></div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_360px] gap-5 items-start">
      <section class="dl-card !p-0 overflow-hidden">
        <div class="flex flex-wrap items-center justify-between gap-2.5 sm:gap-3 p-3.5 sm:p-5 pb-3 sm:pb-4"><h2 class="hr-section-title">{{ tabs.find(tab => tab.key === activeTab)?.label }}</h2><div class="flex flex-wrap items-center gap-2 w-full sm:w-auto"><label class="hr-search flex-1 sm:flex-initial"><Search class="w-4 h-4 shrink-0" /><input v-model="query" placeholder="Tìm kiếm…" /></label><button v-if="activeTab === 'employees'" type="button" class="hr-export shrink-0" @click="exportCsv"><Download class="w-4 h-4" />Xuất Excel</button></div></div>
        <div v-if="activeTab === 'employees'" class="overflow-auto px-5 pb-5">
          <table class="hr-table">
            <thead>
              <tr><th>Nhân viên</th><th>Bộ phận</th><th>Chức vụ</th><th>Ngày vào</th><th>Hợp đồng đến</th><th>Trạng thái</th><th /></tr>
            </thead>
            <tbody>
              <tr v-for="row in employeeRows" :key="row.id">
                <td>
                  <div class="flex items-center gap-3">
                    <span class="hr-avatar">{{ row.full_name.split(' ').map(part => part[0]).slice(-2).join('') }}</span>
                    <div><strong>{{ row.full_name }}</strong><small>{{ row.employee_code }}</small></div>
                  </div>
                </td>
                <td>{{ row.department_name || '—' }}</td>
                <td>{{ row.position || '—' }}</td>
                <td>{{ row.start_date || '—' }}</td>
                <td>{{ row.contract_end || 'Không thời hạn' }}</td>
                <td><span class="hr-badge" :class="row.status === 'active' ? 'hr-badge-ok' : 'hr-badge-muted'">{{ row.status === 'active' ? 'Đang làm' : 'Nghỉ việc' }}</span></td>
                <td>
                  <div class="flex items-center justify-end gap-1">
                    <button class="hr-icon" title="Sửa" @click="openEdit(row)"><Pencil class="w-3.5 h-3.5" /></button>
                    <button v-if="can('delete')" class="hr-icon text-rose-500 hover:text-rose-600 hover:border-rose-300" title="Xóa" @click="removeRow(row)"><Trash2 class="w-3.5 h-3.5" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="!employeeRows.length" class="py-8 text-center text-sm text-dl-muted">Chưa có nhân viên.</p>
        </div>

        <div v-else class="overflow-auto px-5 pb-5">
          <table class="hr-table">
            <thead>
              <tr>
                <th v-if="activeTab !== 'departments'">Nhân viên</th>
                <th v-for="head in activeTab === 'attendance' ? ['Ngày','Vào','Ra','Trạng thái'] : activeTab === 'leave' ? ['Loại','Từ ngày','Đến ngày','Trạng thái'] : activeTab === 'contracts' ? ['Loại hợp đồng','Bắt đầu','Kết thúc','Trạng thái'] : activeTab === 'certificates' ? ['Chứng chỉ','Đơn vị cấp','Hết hạn'] : ['Mã','Tên']" :key="head">{{ head }}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in filteredRows" :key="row.id">
                <td v-if="activeTab !== 'departments'"><strong>{{ employeeName(row.employee_id) }}</strong></td>
                <template v-if="activeTab === 'attendance'"><td>{{ row.work_date }}</td><td>{{ row.check_in || '—' }}</td><td>{{ row.check_out || '—' }}</td><td>{{ row.status }}</td></template>
                <template v-else-if="activeTab === 'leave'"><td>{{ row.leave_type }}</td><td>{{ row.start_date }}</td><td>{{ row.end_date }}</td><td><span class="hr-badge hr-badge-warn">{{ row.status }}</span><button v-if="row.status === 'pending'" class="hr-approve ml-2" @click="decideLeave(row, 'approved')"><Check class="w-3.5 h-3.5" /></button><button v-if="row.status === 'pending'" class="hr-reject ml-1" @click="decideLeave(row, 'rejected')"><X class="w-3.5 h-3.5" /></button></td></template>
                <template v-else-if="activeTab === 'contracts'"><td>{{ row.contract_type }}</td><td>{{ row.start_date }}</td><td>{{ row.end_date || 'Không thời hạn' }}</td><td>{{ row.status }}</td></template>
                <template v-else-if="activeTab === 'certificates'"><td>{{ row.name }}</td><td>{{ row.issuer || '—' }}</td><td>{{ row.expires_at || '—' }}</td></template>
                <template v-else><td>{{ row.code }}</td><td>{{ row.name }}</td></template>
                <td>
                  <div class="flex items-center justify-end gap-1">
                    <button class="hr-icon" title="Sửa" @click="openEdit(row)"><Pencil class="w-3.5 h-3.5" /></button>
                    <button v-if="can('delete')" class="hr-icon text-rose-500 hover:text-rose-600 hover:border-rose-300" title="Xóa" @click="removeRow(row)"><Trash2 class="w-3.5 h-3.5" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="!filteredRows.length" class="py-8 text-center text-sm text-dl-muted">Chưa có bản ghi.</p>
        </div>
      </section>

      <aside class="flex flex-col gap-5">
        <section class="dl-card"><div class="flex items-center justify-between mb-3"><h2 class="hr-section-title">Đơn nghỉ phép chờ duyệt</h2><span class="hr-count hr-count-warn">{{ pendingLeaves.length }}</span></div><div v-for="row in pendingLeaves" :key="row.id" class="hr-side-row"><div><strong>{{ row.employee_name }}</strong><small>{{ row.leave_type }} · {{ row.start_date }}–{{ row.end_date }}</small></div><div class="flex gap-1"><button class="hr-approve" @click="decideLeave(row, 'approved')"><Check class="w-4 h-4" /></button><button class="hr-reject" @click="decideLeave(row, 'rejected')"><X class="w-4 h-4" /></button></div></div><p v-if="!pendingLeaves.length" class="text-sm text-dl-muted">Không có đơn chờ duyệt.</p></section>
        <section class="dl-card"><div class="flex items-center justify-between mb-3"><h2 class="hr-section-title">Chứng chỉ sắp hết hạn</h2><span class="hr-count">30 ngày tới</span></div><div v-for="row in expiringCertificates" :key="row.id" class="hr-side-row"><div><strong>{{ row.name }}</strong><small>{{ row.employee_name }} · hết hạn {{ row.expires_at }}</small></div><span class="hr-badge hr-badge-warn">1 người</span></div><p v-if="!expiringCertificates.length" class="text-sm text-dl-muted">Chưa có chứng chỉ sắp hết hạn.</p></section>
      </aside>
    </div>

    <Modal :show="showModal" :title="editingId ? 'Sửa bản ghi' : 'Thêm bản ghi'" @close="showModal = false">
      <form class="grid grid-cols-1 sm:grid-cols-2 gap-4" @submit.prevent="save">
        <template v-if="activeTab === 'employees'">
          <div><label class="field-label mb-1">Mã nhân viên</label><input v-model="form.employee_code" class="w-full field-input" required /></div>
          <div><label class="field-label mb-1">Họ tên</label><input v-model="form.full_name" class="w-full field-input" required /></div>
          <div><label class="field-label mb-1">Email</label><input v-model="form.email" type="email" class="w-full field-input" /></div>
          <div><label class="field-label mb-1">Điện thoại</label><input v-model="form.phone" class="w-full field-input" /></div>
          <div><label class="field-label mb-1">Phòng ban</label><select v-model="form.department_code" class="w-full field-input"><option value="">-- Chọn --</option><option v-for="department in departments" :key="department.id" :value="department.code">{{ department.name }}</option></select></div>
          <div><label class="field-label mb-1">Chức vụ</label><input v-model="form.position" class="w-full field-input" /></div>
          <div><label class="field-label mb-1">Ngày vào</label><input v-model="form.start_date" type="date" class="w-full field-input" /></div>
          <div><label class="field-label mb-1">Hợp đồng đến</label><input v-model="form.contract_end" type="date" class="w-full field-input" /></div>
        </template>
        <template v-else-if="activeTab === 'departments'">
          <div><label class="field-label mb-1">Mã phòng ban</label><input v-model="form.code" class="w-full field-input" required /></div>
          <div><label class="field-label mb-1">Tên phòng ban</label><input v-model="form.name" class="w-full field-input" required /></div>
        </template>
        <template v-else>
          <div class="sm:col-span-2"><label class="field-label mb-1">Nhân viên</label><select v-model="form.employee_id" class="w-full field-input" required><option value="">-- Chọn nhân viên --</option><option v-for="option in employeeOptions()" :key="option.value" :value="option.value">{{ option.label }}</option></select></div>
          <div v-if="activeTab === 'attendance'"><label class="field-label mb-1">Ngày chấm công</label><input v-model="form.work_date" type="date" class="w-full field-input" /></div>
          <div v-if="activeTab === 'leave'"><label class="field-label mb-1">Loại nghỉ</label><input v-model="form.leave_type" class="w-full field-input" /></div>
          <div v-if="activeTab === 'contracts'"><label class="field-label mb-1">Loại hợp đồng</label><input v-model="form.contract_type" class="w-full field-input" /></div>
          <div v-if="activeTab === 'certificates'"><label class="field-label mb-1">Tên chứng chỉ</label><input v-model="form.name" class="w-full field-input" /></div>
          <div v-if="activeTab === 'leave' || activeTab === 'contracts'"><label class="field-label mb-1">Ngày bắt đầu</label><input v-model="form.start_date" type="date" class="w-full field-input" /></div>
          <div v-if="activeTab === 'certificates'"><label class="field-label mb-1">Ngày cấp</label><input v-model="form.issued_date" type="date" class="w-full field-input" /></div>
          <div v-if="activeTab === 'leave' || activeTab === 'contracts'"><label class="field-label mb-1">Ngày kết thúc</label><input v-model="form.end_date" type="date" class="w-full field-input" /></div>
          <div v-if="activeTab === 'certificates'"><label class="field-label mb-1">Ngày hết hạn</label><input v-model="form.expires_at" type="date" class="w-full field-input" /></div>
        </template>
        <div class="sm:col-span-2 flex justify-end gap-2"><FormActions :disabled="saving" @cancel="showModal = false" /></div>
      </form>
    </Modal>
  </div>
</template>

<style scoped>
.hr-page { @apply flex flex-col gap-5 max-w-[1600px] w-full mx-auto; }
.hr-title { @apply m-0 text-xl sm:text-[28px] leading-tight font-bold text-dl-ink dark:text-slate-100; }
.hr-subtitle { @apply mt-1 text-sm text-dl-muted dark:text-slate-400; }
.hr-alert { @apply px-4 py-3 rounded-xl bg-dl-bad text-dl-badink text-sm; }
.hr-tabs { @apply flex sm:inline-flex overflow-x-auto sm:flex-wrap gap-1 self-start p-1 rounded-[14px] bg-white/60 dark:bg-slate-800/60 max-w-full; }
.hr-tab, .hr-tab-active { @apply inline-flex items-center gap-2 h-9 px-3 sm:px-3.5 rounded-[10px] text-[13px] font-medium whitespace-nowrap shrink-0; }
.hr-tab { @apply text-dl-muted dark:text-slate-400; }
.hr-tab-active { @apply bg-white dark:bg-slate-700 text-dl-ink dark:text-slate-100 shadow-sm font-semibold; }
.hr-stat-teal { @apply bg-dl-soft text-dl-teal; }.hr-stat-ok { @apply bg-dl-ok text-dl-okink; }.hr-stat-info { @apply bg-dl-info text-dl-infoink; }.hr-stat-warn { @apply bg-dl-warn text-dl-warnink; }
.hr-section-title { @apply m-0 text-base font-bold text-dl-ink dark:text-slate-100; }
.hr-search { @apply inline-flex items-center gap-2 h-9 px-3 rounded-xl border border-dl-line dark:border-slate-600 text-dl-muted min-w-0; }.hr-search input { @apply w-full sm:w-36 min-w-0 bg-transparent border-0 outline-none text-sm text-dl-ink dark:text-slate-100; }
.hr-export { @apply inline-flex items-center gap-1.5 h-9 px-3 rounded-xl border border-dl-line dark:border-slate-600 text-xs font-semibold text-dl-body dark:text-slate-200; }
.hr-table { @apply w-full min-w-[760px] text-sm; }.hr-table th { @apply text-left text-xs font-semibold text-dl-muted dark:text-slate-400 py-2.5 px-3 border-b border-dl-line dark:border-slate-700 whitespace-nowrap; }.hr-table td { @apply py-3 px-3 border-b border-dl-rule dark:border-slate-700/70 text-dl-body dark:text-slate-200 align-middle; }.hr-table strong { @apply block font-semibold text-dl-ink dark:text-slate-100; }.hr-table small { @apply block mt-0.5 text-xs text-dl-muted dark:text-slate-400; }
.hr-avatar { @apply w-8 h-8 rounded-full bg-dl-soft text-dl-softink inline-flex items-center justify-center text-xs font-bold shrink-0; }.hr-badge { @apply inline-flex items-center h-6 px-2.5 rounded-full text-xs font-semibold whitespace-nowrap; }.hr-badge-ok { @apply bg-dl-ok text-dl-okink; }.hr-badge-muted { @apply bg-dl-grey text-dl-greyink; }.hr-badge-warn { @apply bg-dl-warn text-dl-warnink; }.hr-count { @apply inline-flex items-center h-6 px-2.5 rounded-full bg-dl-grey text-dl-greyink text-xs font-semibold; }.hr-count-warn { @apply bg-dl-warn text-dl-warnink; }
.hr-side-row { @apply flex items-center justify-between gap-3 py-3 border-b border-dl-rule dark:border-slate-700 last:border-0; }.hr-side-row strong { @apply block text-sm font-semibold text-dl-ink dark:text-slate-100; }.hr-side-row small { @apply block mt-1 text-xs text-dl-muted dark:text-slate-400; }.hr-icon { @apply inline-flex items-center justify-center w-8 h-8 rounded-lg border border-dl-line dark:border-slate-600 text-dl-muted hover:text-dl-teal; }.hr-approve, .hr-reject { @apply inline-flex items-center justify-center w-8 h-8 rounded-lg; }.hr-approve { @apply bg-dl-soft text-dl-softink; }.hr-reject { @apply bg-dl-bad text-dl-badink; }
</style>
