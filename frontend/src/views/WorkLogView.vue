<script setup>
import { ref, computed } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import DynamicForm from '../components/DynamicForm.vue'
import { workLogApi } from '../api/resources'
import { FileText, Loader2 } from 'lucide-vue-next'
import { exportTablePdf } from '../utils/pdfReport'
import { formatDate } from '../utils/format'
import { productSearch } from '../store/productSearch'
import { useCrudResource } from '../composables/useCrudResource'

const exporting = ref(false)

const columns = [
  { key: 'log_date', label: 'Ngày', sortable: true },
  { key: 'content', label: 'Nội dung' },
]

const fields = [
  { key: 'log_date', label: 'Ngày', type: 'date' },
  { key: 'content', label: 'Nội dung', type: 'textarea', full: true },
]

function emptyForm() {
  return { log_date: '', content: '' }
}

function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`
}

const { rows, showModal, editingId, form, openAdd, openEdit, save, remove } = useCrudResource(
  workLogApi, emptyForm,
  { confirmRemove: () => 'Xoá bản ghi nhật ký này?' },
)

const displayRows = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  const base = q
    ? rows.value.filter(r => [r.log_date, r.content].some(v => String(v ?? '').toLowerCase().includes(q)))
    : rows.value
  return [...base].sort((a, b) => String(b.log_date ?? '').localeCompare(String(a.log_date ?? '')))
})

async function exportPdf() {
  exporting.value = true
  try {
    const headers = ['STT', 'Ngày', 'Nội dung']
    const rowsData = displayRows.value.map((r, i) => [i + 1, formatDate(r.log_date), r.content || ''])
    await exportTablePdf({
      title: 'Nhật ký công tác',
      headers, rows: rowsData,
      filename: `Nhat_ky_cong_tac_${todayStr()}.pdf`,
      orientation: 'portrait',
    })
  } finally {
    exporting.value = false
  }
}

</script>

<template>
  <DataTable
    :columns="columns" :rows="displayRows" title="Nhật ký công tác"
    mobile-primary-key="content" mobile-secondary-key="log_date"
    @add="openAdd" @edit="openEdit" @delete="remove"
  >
    <template #header-actions>
      <button
        class="flex items-center gap-1 text-sm border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 px-4 py-2 rounded-xl hover:bg-brand-50 dark:hover:bg-slate-700 disabled:opacity-50"
        :disabled="exporting"
        @click="exportPdf"
      >
        <Loader2 v-if="exporting" class="w-4 h-4 animate-spin" />
        <FileText v-else class="w-4 h-4" />
        Xuất PDF
      </button>
    </template>
    <template #cell-log_date="{ row }">{{ formatDate(row.log_date) }}</template>
  </DataTable>

  <Modal :show="showModal" :title="editingId ? 'Sửa nhật ký' : 'Thêm nhật ký'" @close="showModal = false">
    <DynamicForm v-model="form" :fields="fields" @submit="save">
      <template #actions>
        <button type="button" class="px-4 py-2 rounded-xl text-slate-500" @click="showModal = false">Huỷ</button>
        <button type="submit" class="px-4 py-2 rounded-xl bg-brand-gradient text-white">Lưu</button>
      </template>
    </DynamicForm>
  </Modal>
</template>
