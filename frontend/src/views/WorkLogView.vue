<script setup>
import { ref, computed } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import DynamicForm from '../components/DynamicForm.vue'
import FormActions from '../components/FormActions.vue'
import ToolbarButton from '../components/ToolbarButton.vue'
import { workLogApi } from '../api/resources'
import { FileText } from 'lucide-vue-next'
import { exportTablePdf } from '../utils/pdfReport'
import { formatDate, formatOtHours, todayStamp } from '../utils/format'
import { useCrudResource } from '../composables/useCrudResource'
import { useSearchedRows } from '../composables/useSearchedRows'

const exporting = ref(false)

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

const searchedRows = useSearchedRows(rows, r => [r.log_date, r.content, r.ot_hours])

// Nhật ký xem theo thứ tự mới nhất trước
const displayRows = computed(() =>
  [...searchedRows.value].sort((a, b) => String(b.log_date ?? '').localeCompare(String(a.log_date ?? '')))
)

async function exportPdf() {
  exporting.value = true
  try {
    const headers = ['STT', 'Ngày', 'Nội dung', 'OT']
    const rowsData = displayRows.value.map((r, i) => [i + 1, formatDate(r.log_date), r.content || '', formatOtHours(r.ot_hours)])
    await exportTablePdf({
      title: 'Nhật ký công tác',
      headers, rows: rowsData,
      filename: `Nhat_ky_cong_tac_${todayStamp()}.pdf`,
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
      <ToolbarButton :icon="FileText" label="Xuất PDF" :loading="exporting" @click="exportPdf" />
    </template>
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
