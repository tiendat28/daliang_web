<script setup>
import { ref, computed } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import DynamicForm from '../components/DynamicForm.vue'
import { labChemicalsApi, indicatorsApi } from '../api/resources'
import { PackagePlus, FileSpreadsheet, Loader2 } from 'lucide-vue-next'
import { formatFormula } from '../utils/chemFormula'
import { createReportSheet, styleDataCell, downloadWorkbook } from '../utils/excelReport'
import { productSearch } from '../store/productSearch'
import { useCrudResource } from '../composables/useCrudResource'

const tabs = [
  { key: 'lab-chemicals', label: 'Hóa chất PTN' },
  { key: 'indicators', label: 'Chất chỉ thị' },
]
const activeTab = ref('lab-chemicals')

function currentPeriod() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}
const selectedPeriod = ref(currentPeriod())
const exporting = ref(false)

const labColumns = [
  { key: 'code', label: 'Mã', sortable: true },
  { key: 'name', label: 'Tên' },
  { key: 'type', label: 'Loại' },
  { key: 'box_count', label: 'Số lượng' },
  { key: 'volume_per_box', label: 'Dung tích' },
  { key: 'total_volume', label: 'Nguyên' },
  { key: 'remaining_volume', label: 'Lẻ' },
  { key: 'unit', label: 'Đơn vị' },
]

const labFields = [
  { key: 'code', label: 'Mã hóa chất' },
  { key: 'name', label: 'Tên hóa chất' },
  { key: 'type', label: 'Loại' },
  { key: 'box_count', label: 'Số lượng', type: 'number' },
  { key: 'volume_per_box', label: 'Dung tích', type: 'number' },
  { key: 'remaining_volume', label: 'Lẻ hiện tại (để trống = bằng dung tích)', type: 'number' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'note', label: 'Ghi chú', type: 'textarea' },
]

function emptyLabForm() {
  return { code: '', name: '', type: '', box_count: 0, volume_per_box: 500, remaining_volume: null, unit: '', note: '' }
}

const {
  rows: labRows, showModal: labShowModal, editingId: labEditingId, form: labForm,
  load: loadLabChemicals, openAdd: openAddLab, openEdit: openEditLab, save: saveLab, remove: removeLab,
} = useCrudResource(labChemicalsApi, emptyLabForm, { confirmRemove: row => `Xoá hóa chất "${row.name}"?` })

const labDisplayRows = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  const base = q
    ? labRows.value.filter(r => [r.code, r.name].some(v => String(v ?? '').toLowerCase().includes(q)))
    : labRows.value
  return [...base].sort((a, b) => String(a.code ?? '').localeCompare(String(b.code ?? ''), 'vi', { numeric: true }))
})

async function openBox(row) {
  if (confirm(`Mở hộp mới cho "${row.name}"? Sẽ trừ 1 hộp trong kho và reset phần lẻ.`)) {
    await labChemicalsApi.openBox(row.id)
    await loadLabChemicals()
  }
}

// ---------- Chất chỉ thị ----------
const indicatorColumns = [
  { key: 'name', label: 'Tên' },
  { key: 'type', label: 'Loại' },
  { key: 'quantity', label: 'Số lượng' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'note', label: 'Ghi chú' },
]

const indicatorFields = [
  { key: 'name', label: 'Tên chất chỉ thị' },
  { key: 'type', label: 'Loại' },
  { key: 'quantity', label: 'Số lượng', type: 'number' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'note', label: 'Ghi chú', type: 'textarea' },
]

function emptyIndicatorForm() {
  return { name: '', type: '', quantity: 0, unit: '', note: '' }
}

const {
  rows: indicatorRows, showModal: indicatorShowModal, editingId: indicatorEditingId, form: indicatorForm,
  openAdd: openAddIndicator, openEdit: openEditIndicator, save: saveIndicator, remove: removeIndicator,
} = useCrudResource(indicatorsApi, emptyIndicatorForm, { confirmRemove: row => `Xoá chất chỉ thị "${row.name}"?` })

const indicatorDisplayRows = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  if (!q) return indicatorRows.value
  return indicatorRows.value.filter(r => [r.name, r.type, r.unit, r.note].some(v => String(v ?? '').toLowerCase().includes(q)))
})

async function exportCombinedExcel() {
  exporting.value = true
  try {
    const ExcelJS = await import('exceljs')
    const [year, month] = selectedPeriod.value.split('-')
    const wb = new ExcelJS.Workbook()

    const wsLab = await createReportSheet(wb, {
      sheetName: 'Hóa chất PTN', title: `QUẢN LÝ HÓA CHẤT THÁNG ${Number(month)}/${year}`,
      columnWidths: [6, 26, 12, 11, 11, 11, 9, 38],
      headerLabels: ['STT', 'TÊN', 'PHÂN LOẠI', 'Nguyên', 'Lẻ', 'Tổng', 'ĐƠN VỊ', 'GHI CHÚ'],
      titleSpan: 3, companySpan: 3,
    })
    labDisplayRows.value.forEach((r, i) => {
      const nguyen = r.total_volume ?? 0
      const le = r.remaining_volume ?? 0
      const values = [i + 1, formatFormula(r.code), r.type || '', nguyen, le, nguyen + le, r.unit || '', r.note || '']
      const row = wsLab.getRow(4 + i)
      values.forEach((v, ci) => styleDataCell(row.getCell(ci + 1), v, { align: ci === 1 || ci === 7 ? 'left' : 'center' }))
    })

    const wsIndicator = await createReportSheet(wb, {
      sheetName: 'Chất chỉ thị', title: `CHẤT CHỈ THỊ THÁNG ${Number(month)}/${year}`,
      columnWidths: [6, 26, 16, 14, 12, 30],
      headerLabels: ['STT', 'TÊN', 'PHÂN LOẠI', 'KHỐI LƯỢNG', 'ĐƠN VỊ', 'GHI CHÚ'],
      titleSpan: 2, companySpan: 2,
    })
    indicatorDisplayRows.value.forEach((r, i) => {
      const values = [i + 1, r.name, r.type || '', r.quantity ?? 0, r.unit || '', r.note || '']
      const row = wsIndicator.getRow(4 + i)
      values.forEach((v, ci) => styleDataCell(row.getCell(ci + 1), v, { align: ci === 1 || ci === 5 ? 'left' : 'center' }))
    })

    await downloadWorkbook(wb, `QUẢN LÝ HÓA CHẤT THÁNG ${Number(month)}/${year}.xlsx`)
  } finally {
    exporting.value = false
  }
}

</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
    <div class="flex gap-2">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-colors"
        :class="activeTab === tab.key
          ? 'bg-brand-gradient text-white shadow'
          : 'bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-300 hover:text-brand-600'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>
    <div class="flex items-center gap-2">
      <input
        v-model="selectedPeriod"
        type="month"
        class="field-input"
      />
      <button
        class="flex items-center gap-1 text-sm border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 px-4 py-2 rounded-xl hover:bg-brand-50 dark:hover:bg-slate-700 disabled:opacity-50"
        :disabled="exporting"
        title="Xuất 1 file Excel gồm cả 2 sheet: Hóa chất PTN + Chất chỉ thị"
        @click="exportCombinedExcel"
      >
        <Loader2 v-if="exporting" class="w-4 h-4 animate-spin" />
        <FileSpreadsheet v-else class="w-4 h-4" />
        Xuất Excel
      </button>
    </div>
  </div>

  <DataTable
    v-if="activeTab === 'lab-chemicals'"
    :columns="labColumns" :rows="labDisplayRows" title="Hóa chất phòng thí nghiệm"
    @add="openAddLab" @edit="openEditLab" @delete="removeLab"
  >
    <template #cell-code="{ row }">{{ formatFormula(row.code) }}</template>
    <template #row-actions="{ row }">
      <button class="text-slate-400 hover:text-brand-600" title="Mở hộp mới" @click="openBox(row)">
        <PackagePlus class="w-4 h-4" />
      </button>
    </template>
  </DataTable>

  <DataTable
    v-else
    :columns="indicatorColumns" :rows="indicatorDisplayRows" title="Chất chỉ thị"
    @add="openAddIndicator" @edit="openEditIndicator" @delete="removeIndicator"
  />

  <Modal :show="labShowModal" :title="labEditingId ? 'Sửa hóa chất' : 'Thêm hóa chất'" @close="labShowModal = false">
    <DynamicForm v-model="labForm" :fields="labFields" @submit="saveLab">
      <template #actions>
        <button type="button" class="px-4 py-2 rounded-xl text-slate-500" @click="labShowModal = false">Huỷ</button>
        <button type="submit" class="px-4 py-2 rounded-xl bg-brand-gradient text-white">Lưu</button>
      </template>
    </DynamicForm>
  </Modal>

  <Modal :show="indicatorShowModal" :title="indicatorEditingId ? 'Sửa chất chỉ thị' : 'Thêm chất chỉ thị'" @close="indicatorShowModal = false">
    <DynamicForm v-model="indicatorForm" :fields="indicatorFields" @submit="saveIndicator">
      <template #actions>
        <button type="button" class="px-4 py-2 rounded-xl text-slate-500" @click="indicatorShowModal = false">Huỷ</button>
        <button type="submit" class="px-4 py-2 rounded-xl bg-brand-gradient text-white">Lưu</button>
      </template>
    </DynamicForm>
  </Modal>
</template>
