<script setup>
import { ref } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import FormActions from '../components/FormActions.vue'
import MonthPicker from '../components/MonthPicker.vue'
import ToolbarButton from '../components/ToolbarButton.vue'
import { equipmentApi } from '../api/resources'
import { Plus, Trash2, FileSpreadsheet } from 'lucide-vue-next'
import { downloadWorkbook } from '../utils/excelReport'
import { addEquipmentSheet } from '../utils/reportSheets'
import { currentPeriod, periodParts } from '../utils/format'
import { useCrudResource } from '../composables/useCrudResource'
import { useSearchedRows } from '../composables/useSearchedRows'

const selectedPeriod = ref(currentPeriod())
const exporting = ref(false)

const columns = [
  { key: 'name', label: 'Tên thiết bị' },
  { key: 'classification', label: 'Phân loại' },
  { key: 'quantity', label: 'Số lượng' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'note', label: 'Ghi chú' },
]

function emptyVariant() {
  return { classification: '', quantity: 0, unit: 'c', note: '' }
}

function emptyForm() {
  return { name: '', note: '', variants: [emptyVariant()] }
}

const { rows, showModal, editingId, form, openAdd, openEdit, save, remove } = useCrudResource(
  equipmentApi, emptyForm,
  {
    mapRowToForm: row => ({
      name: row.name,
      note: row.note,
      variants: row.variants.length ? row.variants.map(v => ({ ...v, note: v.note || '' })) : [emptyVariant()],
    }),
    buildPayload: form => ({ ...form, variants: form.variants.filter(v => v.classification || v.quantity) }),
    confirmRemove: row => `Xoá thiết bị "${row.name}"?`,
  },
)

const displayRows = useSearchedRows(rows, r => [
  r.name, r.note,
  ...r.variants.flatMap(v => [v.classification, v.unit, v.note]),
])

async function exportMonthlyExcel() {
  exporting.value = true
  try {
    const ExcelJS = await import('exceljs')
    const { year, month } = periodParts(selectedPeriod.value)
    const wb = new ExcelJS.Workbook()
    await addEquipmentSheet(wb, rows.value, { year, month })
    await downloadWorkbook(wb, `DUNG CU THI NGHIEM THANG ${month}-${year}.xlsx`)
  } finally {
    exporting.value = false
  }
}

function addVariant() {
  form.value.variants.push(emptyVariant())
}

function removeVariant(index) {
  form.value.variants.splice(index, 1)
}
</script>

<template>
  <DataTable :columns="columns" :rows="displayRows" title="Thiết bị" @add="openAdd" @edit="openEdit" @delete="remove">
    <template #header-actions>
      <MonthPicker v-model="selectedPeriod" />
      <ToolbarButton :icon="FileSpreadsheet" label="Xuất Excel" :loading="exporting" @click="exportMonthlyExcel" />
    </template>
    <template #cell-classification="{ row }">
      <div v-for="v in row.variants" :key="v.id" class="text-slate-700 dark:text-slate-200 mb-1 last:mb-0">{{ v.classification }}</div>
    </template>
    <template #cell-quantity="{ row }">
      <div v-for="v in row.variants" :key="v.id" class="text-slate-700 dark:text-slate-200 mb-1 last:mb-0">{{ v.quantity }}</div>
    </template>
    <template #cell-unit="{ row }">
      <div v-for="v in row.variants" :key="v.id" class="text-slate-700 dark:text-slate-200 mb-1 last:mb-0">{{ v.unit }}</div>
    </template>
    <template #cell-note="{ row }">
      <div v-for="v in row.variants" :key="v.id" class="text-slate-700 dark:text-slate-200 mb-1 last:mb-0">{{ v.note }}</div>
      <div v-if="row.note" class="text-slate-500 dark:text-slate-400 italic">{{ row.note }}</div>
    </template>

    <!-- Mobile: tên + nút sửa/xoá nằm ở thẻ trên, các phân loại xếp thành cột thẳng hàng ở khối này -->
    <template #mobile-details="{ row }">
      <div class="rounded-xl bg-slate-50 dark:bg-slate-700/40 px-3 py-2">
        <div class="grid grid-cols-[minmax(0,1fr)_2rem_2.25rem_minmax(0,1fr)] gap-x-2 pb-1 text-[11px] uppercase tracking-wide text-slate-400 dark:text-slate-500 border-b border-slate-200 dark:border-slate-600">
          <span>Phân loại</span>
          <span class="text-right">SL</span>
          <span class="text-right">Đ.vị</span>
          <span class="text-right">Ghi chú</span>
        </div>
        <div
          v-for="v in row.variants"
          :key="v.id"
          class="grid grid-cols-[minmax(0,1fr)_2rem_2.25rem_minmax(0,1fr)] gap-x-2 py-1 text-sm text-slate-700 dark:text-slate-200 border-b border-slate-100 dark:border-slate-700/60 last:border-0"
        >
          <span class="truncate">{{ v.classification || '—' }}</span>
          <span class="text-right tabular-nums">{{ v.quantity }}</span>
          <span class="text-right">{{ v.unit }}</span>
          <span class="truncate text-right text-slate-400 dark:text-slate-500">{{ v.note }}</span>
        </div>
        <p v-if="row.note" class="pt-1.5 text-xs italic text-slate-500 dark:text-slate-400">{{ row.note }}</p>
      </div>
    </template>
  </DataTable>

  <Modal :show="showModal" :title="editingId ? 'Sửa thiết bị' : 'Thêm thiết bị'" @close="showModal = false">
    <form class="space-y-4" @submit.prevent="save">
      <div>
        <label class="field-label mb-1">Tên thiết bị</label>
        <input v-model="form.name" class="w-full field-input" />
      </div>

      <div>
        <label class="field-label mb-2">Phân loại / Số lượng</label>
        <div v-for="(v, i) in form.variants" :key="i" class="flex flex-wrap gap-2 mb-2 items-center">
          <input v-model="v.classification" placeholder="Phân loại" class="flex-1 min-w-[120px] field-input" />
          <input v-model.number="v.quantity" type="number" placeholder="SL" class="w-20 field-input" />
          <input v-model="v.unit" placeholder="Đ.vị" class="w-16 field-input" />
          <input v-model="v.note" placeholder="Ghi chú" class="flex-1 min-w-[100px] field-input" />
          <button type="button" class="text-red-400 shrink-0" @click="removeVariant(i)">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
        <button type="button" class="flex items-center gap-1 text-sm text-brand-600" @click="addVariant">
          <Plus class="w-4 h-4" /> Thêm phân loại
        </button>
      </div>

      <div>
        <label class="field-label mb-1">Ghi chú chung (cả thiết bị)</label>
        <textarea v-model="form.note" rows="2" class="w-full field-input" />
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <FormActions @cancel="showModal = false" />
      </div>
    </form>
  </Modal>
</template>
