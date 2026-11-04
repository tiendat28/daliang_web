<script setup>
import { ref, computed } from 'vue'
import DataTable from '@/core/components/DataTable.vue'
import Modal from '@/core/components/Modal.vue'
import DynamicForm from '@/core/components/DynamicForm.vue'
import FormActions from '@/core/components/FormActions.vue'
import MonthPicker from '@/core/components/MonthPicker.vue'
import ToolbarButton from '@/core/components/ToolbarButton.vue'
import { workLogApi } from '@/modules/lab/api'
import { FileText, Calendar, X } from 'lucide-vue-next'
import { exportTablePdf } from '@/modules/lab/utils/pdfReport'
import { formatDate, formatOtHours, todayStamp, periodParts } from '@/core/utils/format'
import { useCrudResource } from '@/core/composables/useCrudResource'
import { useSearchedRows } from '@/core/composables/useSearchedRows'
import { usePageCan } from '@/core/auth/store'

// Nut xuat file chi hien khi co quyen `<meta.permission>.export`
const can = usePageCan()

const exporting = ref(false)
const selectedMonth = ref('')

const columns = [
  { key: 'log_date', label: 'Ngày', sortable: true },
  { key: 'content', label: 'Nội dung' },
  { key: 'ot_hours', label: 'OT', sortable: true, format: formatOtHours },
]

const fields = [
  { key: 'log_date', label: 'Ngày', type: 'date' },
  { key: 'ot_hours', label: 'OT (giờ)', type: 'number' },
  { key: 'content', label: 'Nội dung', type: 'textarea', full: true },
]

function emptyForm() {
  return { log_date: '', content: '', ot_hours: null }
}

const { rows, showModal, editingId, form, openAdd, openEdit, save, remove } = useCrudResource(
  workLogApi, emptyForm,
  { confirmRemove: () => 'Xoá bản ghi nhật ký này?' },
)

// Danh sách các tháng có dữ liệu (YYYY-MM), sắp xếp mới nhất trước
const availableMonths = computed(() => {
  const set = new Set()
  for (const r of rows.value) {
    const m = String(r.log_date || '').slice(0, 7)
    if (/^\d{4}-\d{2}$/.test(m)) set.add(m)
  }
  return [...set].sort((a, b) => b.localeCompare(a))
})

function formatMonthLabel(ym) {
  if (!ym) return 'Tất cả'
  const [y, m] = ym.split('-')
  return `Tháng ${Number(m)}/${y}`
}

const monthFilteredRows = computed(() => {
  if (!selectedMonth.value) return rows.value
  return rows.value.filter(r => String(r.log_date || '').startsWith(selectedMonth.value))
})

const searchedRows = useSearchedRows(monthFilteredRows, r => [r.log_date, r.content, r.ot_hours])

// Nhật ký xem theo thứ tự mới nhất trước
const displayRows = computed(() =>
  [...searchedRows.value].sort((a, b) => String(b.log_date ?? '').localeCompare(String(a.log_date ?? '')))
)

// Tổng giờ OT của danh sách đang hiển thị
const totalOtHours = computed(() =>
  displayRows.value.reduce((sum, r) => sum + (Number(r.ot_hours) || 0), 0)
)

async function exportPdf() {
  exporting.value = true
  try {
    const headers = ['STT', 'Ngày', 'Nội dung', 'OT']
    const rowsData = displayRows.value.map((r, i) => [i + 1, formatDate(r.log_date), r.content || '', formatOtHours(r.ot_hours)])
    const period = selectedMonth.value ? periodParts(selectedMonth.value) : null
    const title = period?.month
      ? `Nhật ký công tác - Tháng ${period.month}/${period.year}`
      : 'Nhật ký công tác'
    const suffix = period?.month ? `T${period.month}_${period.year}` : todayStamp()
    await exportTablePdf({
      title,
      headers,
      rows: rowsData,
      filename: `Nhat_ky_cong_tac_${suffix}.pdf`,
      orientation: 'portrait',
    })
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <!-- Thanh lọc theo tháng -->
  <div class="flex flex-wrap items-center justify-between gap-2.5 mb-3.5 shrink-0">
    <div class="flex items-center gap-1.5 overflow-x-auto max-w-full pb-1 sm:pb-0">
      <button
        type="button"
        class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap cursor-pointer shrink-0"
        :class="!selectedMonth
          ? 'bg-gradient-to-r from-teal-500 to-emerald-600 text-white shadow-xs'
          : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700 hover:border-teal-500/50'"
        @click="selectedMonth = ''"
      >
        Tất cả ({{ rows.length }})
      </button>
      <button
        v-for="m in availableMonths.slice(0, 6)"
        :key="m"
        type="button"
        class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition-all whitespace-nowrap cursor-pointer shrink-0"
        :class="selectedMonth === m
          ? 'bg-gradient-to-r from-teal-500 to-emerald-600 text-white shadow-xs font-semibold'
          : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700 hover:border-teal-500/50'"
        @click="selectedMonth = m"
      >
        {{ formatMonthLabel(m) }}
      </button>
    </div>

    <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto justify-between sm:justify-end">
      <div class="flex items-center gap-1.5">
        <div class="relative flex items-center">
          <MonthPicker v-model="selectedMonth" />
          <button
            v-if="selectedMonth"
            type="button"
            class="ml-1.5 p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-rose-500 dark:text-slate-400 transition-colors"
            title="Bỏ lọc tháng (Xem tất cả)"
            @click="selectedMonth = ''"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
        <span
          v-if="totalOtHours > 0"
          class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-teal-50 dark:bg-teal-950/60 text-teal-700 dark:text-teal-300 border border-teal-200/60 dark:border-teal-800/60 text-xs font-semibold whitespace-nowrap"
        >
          Tổng OT: {{ formatOtHours(totalOtHours) }}
        </span>
      </div>

      <ToolbarButton
        v-if="can('export')"
        :icon="FileText"
        label="Xuất PDF"
        :loading="exporting"
        @click="exportPdf"
      />
    </div>
  </div>

  <DataTable
    :columns="columns"
    :rows="displayRows"
    :title="selectedMonth ? `Nhật ký công tác — ${formatMonthLabel(selectedMonth)}` : 'Nhật ký công tác'"
    mobile-primary-key="content"
    mobile-secondary-key="log_date"
    @add="openAdd"
    @edit="openEdit"
    @delete="remove"
  >
    <template #cell-log_date="{ row }">{{ formatDate(row.log_date) }}</template>
    <template #cell-ot_hours="{ row }">{{ formatOtHours(row.ot_hours) }}</template>
  </DataTable>

  <Modal :show="showModal" :title="editingId ? 'Sửa nhật ký' : 'Thêm nhật ký'" @close="showModal = false">
    <DynamicForm v-model="form" :fields="fields" @submit="save">
      <template #actions>
        <FormActions @cancel="showModal = false" />
      </template>
    </DynamicForm>
  </Modal>
</template>
