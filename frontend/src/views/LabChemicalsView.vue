<script setup>
import { ref, computed } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import DynamicForm from '../components/DynamicForm.vue'
import FormActions from '../components/FormActions.vue'
import MonthPicker from '../components/MonthPicker.vue'
import ToolbarButton from '../components/ToolbarButton.vue'
import { labChemicalsApi, indicatorsApi } from '../api/resources'
import { PackagePlus, FileSpreadsheet } from 'lucide-vue-next'
import { formatFormula } from '../utils/chemFormula'
import { downloadWorkbook } from '../utils/excelReport'
import { addLabChemicalsSheet, addIndicatorsSheet } from '../utils/reportSheets'
import { currentPeriod, periodParts } from '../utils/format'
import { useCrudResource } from '../composables/useCrudResource'
import { useSearchedRows } from '../composables/useSearchedRows'

const tabs = [
  { key: 'lab-chemicals', label: 'Hóa chất PTN' },
  { key: 'indicators', label: 'Chất chỉ thị' },
]
const activeTab = ref('lab-chemicals')

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

const searchedLabRows = useSearchedRows(labRows, r => [r.code, r.name])

// Hóa chất PTN luôn xếp theo mã cho dễ tra
const labDisplayRows = computed(() =>
  [...searchedLabRows.value].sort((a, b) => String(a.code ?? '').localeCompare(String(b.code ?? ''), 'vi', { numeric: true }))
)

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

const indicatorDisplayRows = useSearchedRows(indicatorRows, r => [r.name, r.type, r.unit, r.note])

// Xuất 1 file gồm 2 sheet, dùng chung mẫu sheet với phần Xuất dữ liệu ở Cài đặt
async function exportCombinedExcel() {
  exporting.value = true
  try {
    const ExcelJS = await import('exceljs')
    const period = periodParts(selectedPeriod.value)
    const wb = new ExcelJS.Workbook()
    await addLabChemicalsSheet(wb, labDisplayRows.value, period)
    await addIndicatorsSheet(wb, indicatorDisplayRows.value, period)
    await downloadWorkbook(wb, `QUAN LY HOA CHAT THANG ${period.month}-${period.year}.xlsx`)
  } finally {
    exporting.value = false
  }
}

</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3 mb-4 shrink-0">
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
      <MonthPicker v-model="selectedPeriod" />
      <ToolbarButton
        :icon="FileSpreadsheet" label="Xuất Excel" :loading="exporting"
        title="Xuất 1 file Excel gồm cả 2 sheet: Hóa chất PTN + Chất chỉ thị"
        @click="exportCombinedExcel"
      />
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
        <FormActions @cancel="labShowModal = false" />
      </template>
    </DynamicForm>
  </Modal>

  <Modal :show="indicatorShowModal" :title="indicatorEditingId ? 'Sửa chất chỉ thị' : 'Thêm chất chỉ thị'" @close="indicatorShowModal = false">
    <DynamicForm v-model="indicatorForm" :fields="indicatorFields" @submit="saveIndicator">
      <template #actions>
        <FormActions @cancel="indicatorShowModal = false" />
      </template>
    </DynamicForm>
  </Modal>
</template>
