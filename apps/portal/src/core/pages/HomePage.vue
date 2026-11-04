<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  Activity, Beaker, BookOpen, Boxes, Clock3, Database,
  FileCheck2, FlaskConical, Package, UsersRound,
} from 'lucide-vue-next'
import { auth, can } from '@/core/auth/store'
import { customersApi, productsApi } from '@/core/api/common'
import {
  analysisReportsApi, chemicalsApi, equipmentApi,
  samplesApi, testProcessesApi, workLogApi,
} from '@/modules/lab/api'

const loading = ref(true)
const error = ref('')
const data = ref({})

const resources = [
  { key: 'customers', label: 'Khách hàng', icon: UsersRound, tone: 'teal', permission: 'common.customers.view', api: customersApi },
  { key: 'products', label: 'Sản phẩm', icon: Package, tone: 'blue', permission: 'common.products.view', api: productsApi },
  { key: 'chemicals', label: 'Hóa chất PTN', icon: FlaskConical, tone: 'amber', permission: 'lab.chemicals.view', api: chemicalsApi },
  { key: 'equipment', label: 'Thiết bị', icon: Boxes, tone: 'violet', permission: 'lab.equipment.view', api: equipmentApi },
  { key: 'samples', label: 'Mẫu thử', icon: Beaker, tone: 'rose', permission: 'lab.samples.view', api: samplesApi },
  { key: 'reports', label: 'Báo cáo phân tích', icon: FileCheck2, tone: 'slate', permission: 'lab.analysis_reports.view', api: analysisReportsApi },
]

const visibleResources = computed(() => resources.filter(resource => can(resource.permission)))
const statCards = computed(() => visibleResources.value.map(resource => ({
  ...resource,
  value: data.value[resource.key]?.length ?? 0,
})))

const productGroups = computed(() => {
  const products = data.value.products || []
  const groups = new Map()
  products.forEach(product => {
    const label = product.category || 'Chưa phân nhóm'
    groups.set(label, (groups.get(label) || 0) + 1)
  })
  return [...groups.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([label, count]) => ({ label, count, percent: products.length ? Math.round(count / products.length * 100) : 0 }))
})

const recentLogs = computed(() => [...(data.value.workLogs || [])]
  .sort((a, b) => String(b.log_date || '').localeCompare(String(a.log_date || '')))
  .slice(0, 5))

const processSummary = computed(() => {
  const processes = data.value.processes || []
  const groups = { draft: 0, in_progress: 0, completed: 0, cancelled: 0 }
  processes.forEach(process => {
    const status = String(process.status || 'draft').toLowerCase()
    if (status === 'completed' || status === 'done') groups.completed++
    else if (status === 'cancelled' || status === 'canceled') groups.cancelled++
    else if (status === 'in_progress' || status === 'running') groups.in_progress++
    else groups.draft++
  })
  return { ...groups, total: processes.length }
})

const processSegments = computed(() => {
  const total = processSummary.value.total || 1
  return [
    { label: 'Đang thực hiện', value: processSummary.value.in_progress, color: 'bg-dl-teal' },
    { label: 'Hoàn thành', value: processSummary.value.completed, color: 'bg-emerald-400' },
    { label: 'Bản nháp', value: processSummary.value.draft, color: 'bg-slate-300' },
    { label: 'Đã hủy', value: processSummary.value.cancelled, color: 'bg-rose-400' },
  ].map(segment => ({ ...segment, width: `${segment.value / total * 100}%` }))
})

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const entries = await Promise.all(visibleResources.value.map(async resource => [resource.key, await resource.api.list()]))
    const result = Object.fromEntries(entries)
    if (can('lab.work_logs.view')) result.workLogs = await workLogApi.list()
    if (can('lab.test_processes.view')) result.processes = await testProcessesApi.list()
    data.value = result
  } catch (loadError) {
    error.value = loadError.response?.status === 403
      ? 'Một số dữ liệu chưa được cấp quyền truy cập.'
      : 'Không tải được dữ liệu tổng quan.'
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <div class="flex flex-col gap-5 max-w-[1600px] w-full mx-auto">
    <div v-if="loading" class="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      <div v-for="item in 6" :key="item" class="h-[132px] rounded-[20px] bg-white/70 dark:bg-slate-800/70 animate-pulse" />
    </div>
    <div v-else class="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      <div v-for="card in statCards" :key="card.key" class="dl-stat-card group hover:-translate-y-0.5 transition-transform">
        <span class="dl-stat-icon" :class="`stat-icon-${card.tone}`"><component :is="card.icon" class="w-5 h-5" /></span>
        <span class="dl-stat-label">{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
        <small>tổng số bản ghi</small>
      </div>
    </div>

    <p v-if="error" class="text-sm text-dl-warnink bg-dl-warn rounded-xl px-4 py-3">{{ error }}</p>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,1.4fr)] gap-5">
      <section class="dl-card">
        <div class="flex items-start justify-between gap-3 mb-5">
          <div class="flex items-start gap-3"><span class="dashboard-icon bg-dl-soft text-dl-teal"><Activity class="w-5 h-5" /></span><div><h2 class="dashboard-title">Trạng thái lưu trình</h2><p class="dashboard-subtitle">{{ processSummary.total }} lưu trình trong hệ thống</p></div></div>
          <span class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-dl-panel text-dl-muted dark:bg-slate-700 dark:text-slate-300">{{ processSummary.total }} tổng</span>
        </div>
        <div class="h-3 flex overflow-hidden rounded-full bg-dl-panel dark:bg-slate-700 mb-4">
          <span v-for="segment in processSegments" :key="segment.label" :class="segment.color" :style="{ width: segment.width }" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div v-for="segment in processSegments" :key="segment.label" class="rounded-xl border border-dl-line dark:border-slate-700 p-3">
            <div class="flex items-center gap-2 text-xs text-dl-muted dark:text-slate-400"><span class="w-2 h-2 rounded-full" :class="segment.color" />{{ segment.label }}</div>
            <strong class="block mt-2 text-xl text-dl-ink dark:text-slate-100">{{ segment.value }}</strong>
          </div>
        </div>
      </section>

      <section class="dl-card">
        <div class="flex items-start gap-3 mb-5"><span class="dashboard-icon bg-dl-info text-dl-infoink"><Database class="w-5 h-5" /></span><div><h2 class="dashboard-title">Cơ cấu sản phẩm</h2><p class="dashboard-subtitle">Phân bố theo nhóm phân loại</p></div></div>
        <div v-if="productGroups.length" class="flex flex-col gap-4">
          <div v-for="group in productGroups" :key="group.label">
            <div class="flex items-center justify-between gap-3 text-sm mb-1.5"><span class="font-semibold text-dl-body dark:text-slate-200 truncate">{{ group.label }}</span><span class="text-xs text-dl-muted dark:text-slate-400">{{ group.count }} mã ({{ group.percent }}%)</span></div>
            <div class="h-2 rounded-full bg-dl-panel dark:bg-slate-700 overflow-hidden"><div class="h-full rounded-full bg-dl-teal" :style="{ width: `${group.percent}%` }" /></div>
          </div>
        </div>
        <p v-else class="text-sm text-dl-muted dark:text-slate-400">Chưa có dữ liệu sản phẩm.</p>
      </section>
    </div>

    <section class="dl-card">
      <div class="flex items-start justify-between gap-3 mb-3"><div class="flex items-start gap-3"><span class="dashboard-icon bg-dl-violet text-dl-violetink"><BookOpen class="w-5 h-5" /></span><div><h2 class="dashboard-title">Nhật ký công tác gần đây</h2><p class="dashboard-subtitle">Các hoạt động mới nhất được ghi nhận</p></div></div><span class="text-xs text-dl-muted dark:text-slate-400">{{ recentLogs.length }} bản ghi</span></div>
      <div v-if="recentLogs.length" class="overflow-x-auto"><table class="w-full text-sm"><thead><tr class="text-left text-xs text-dl-muted dark:text-slate-400 border-b border-dl-line dark:border-slate-700"><th class="py-3 pr-4 font-semibold">Ngày</th><th class="py-3 pr-4 font-semibold">Nội dung</th><th class="py-3 font-semibold">OT</th></tr></thead><tbody><tr v-for="log in recentLogs" :key="log.id" class="border-b border-dl-line/70 dark:border-slate-700/70 last:border-0"><td class="py-3 pr-4 whitespace-nowrap text-dl-muted dark:text-slate-400">{{ log.log_date || '—' }}</td><td class="py-3 pr-4 text-dl-body dark:text-slate-200">{{ log.content || '—' }}</td><td class="py-3 text-dl-muted dark:text-slate-400">{{ log.ot_hours ?? '—' }}</td></tr></tbody></table></div>
      <p v-else class="py-6 text-center text-sm text-dl-muted dark:text-slate-400">Chưa có nhật ký công tác.</p>
    </section>
  </div>
</template>

<style scoped>
.dashboard-icon { @apply w-10 h-10 rounded-xl inline-flex items-center justify-center shrink-0; }
.dashboard-title { @apply m-0 text-base font-bold text-dl-ink dark:text-slate-100; }
.dashboard-subtitle { @apply mt-0.5 text-xs text-dl-muted dark:text-slate-400; }
.stat-icon-teal { @apply bg-dl-soft text-dl-teal; }
.stat-icon-blue { @apply bg-dl-info text-dl-infoink; }
.stat-icon-amber { @apply bg-dl-warn text-dl-warnink; }
.stat-icon-violet { @apply bg-dl-violet text-dl-violetink; }
.stat-icon-rose { @apply bg-dl-bad text-dl-badink; }
.stat-icon-slate { @apply bg-dl-grey text-dl-greyink; }
</style>
