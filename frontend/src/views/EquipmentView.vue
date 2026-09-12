<script setup>
import { ref, computed } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import { equipmentApi } from '../api/resources'
import { Plus, Trash2, FileSpreadsheet, Loader2 } from 'lucide-vue-next'
import { createReportSheet, styleDataCell, downloadWorkbook } from '../utils/excelReport'
import { productSearch } from '../store/productSearch'
import { useCrudResource } from '../composables/useCrudResource'

function currentPeriod() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}
const selectedPeriod = ref(currentPeriod())
const exporting = ref(false)

const columns = [
  { key: 'name', label: 'Tên thiết bị' },
  { key: 'classification', label: 'Phân loại' },
  { key: 'quantity', label: 'Số lượng' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'note', label: 'Ghi chú' },
]

function emptyForm() {
  return { name: '', note: '', variants: [{ classification: '', quantity: 0, unit: 'c', note: '' }] }
}

const { rows, showModal, editingId, form, openAdd, openEdit, save, remove } = useCrudResource(
  equipmentApi, emptyForm,
  {
    mapRowToForm: row => ({
      name: row.name,
      note: row.note,
      variants: row.variants.length ? row.variants.map(v => ({ ...v, note: v.note || '' })) : [{ classification: '', quantity: 0, unit: 'c', note: '' }],
    }),
    buildPayload: form => ({ ...form, variants: form.variants.filter(v => v.classification || v.quantity) }),
    confirmRemove: row => `Xoá thiết bị "${row.name}"?`,
  },
)

const displayRows = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter(r => {
    const variantVals = r.variants.flatMap(v => [v.classification, v.unit, v.note])
    return [r.name, r.note, ...variantVals].some(v => String(v ?? '').toLowerCase().includes(q))
  })
})

async function exportMonthlyExcel() {
  exporting.value = true
  try {
    const ExcelJS = await import('exceljs')
    const [year, month] = selectedPeriod.value.split('-')
    const title = `DỤNG CỤ THÍ NGHIỆM THÁNG ${Number(month)}/${year}`

    const wb = new ExcelJS.Workbook()
    const ws = await createReportSheet(wb, {
      sheetName: `Tháng ${month}-${year}`, title, titleFontSize: 12,
      columnWidths: [6, 26, 16, 11, 9, 30],
      headerLabels: ['STT', 'TÊN', 'PHÂN LOẠI', 'SỐ LƯỢNG', 'ĐƠN VỊ', 'GHI CHÚ'],
      titleSpan: 2, companySpan: 2,
    })

    let excelRow = 4
    rows.value.forEach((eq, i) => {
      const variants = eq.variants.length ? eq.variants : [{ classification: '', quantity: 0, unit: '', note: '' }]
      const startRow = excelRow

      variants.forEach((v, vi) => {
        const noteText = vi === 0 && eq.note ? [eq.note, v.note].filter(Boolean).join(' — ') : (v.note || '')
        const values = [vi === 0 ? i + 1 : null, null, v.classification || '', v.quantity ?? 0, v.unit || '', noteText]
        const row = ws.getRow(excelRow)
        values.forEach((val, ci) => styleDataCell(row.getCell(ci + 1), val, { align: ci === 1 || ci === 5 ? 'left' : 'center' }))
        excelRow++
      })

      const endRow = excelRow - 1
      if (endRow > startRow) {
        ws.mergeCells(startRow, 1, endRow, 1)
        ws.mergeCells(startRow, 2, endRow, 2)
      }
      ws.getCell(startRow, 2).value = eq.name
      ws.getCell(startRow, 2).font = { name: 'Times New Roman', bold: true, size: 11 }
    })

    await downloadWorkbook(wb, `${title}.xlsx`)
  } finally {
    exporting.value = false
  }
}

function addVariant() {
  form.value.variants.push({ classification: '', quantity: 0, unit: 'c', note: '' })
}

function removeVariant(index) {
  form.value.variants.splice(index, 1)
}
</script>

<template>
  <DataTable :columns="columns" :rows="displayRows" title="Thiết bị" @add="openAdd" @edit="openEdit" @delete="remove">
    <template #header-actions>
      <input
        v-model="selectedPeriod"
        type="month"
        class="field-input w-auto text-xs px-2 py-1.5 sm:text-sm sm:px-3 sm:py-2"
      />
      <button
        class="flex items-center justify-center gap-1 text-sm border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 w-9 h-9 sm:w-auto sm:h-auto sm:px-4 sm:py-2 rounded-full sm:rounded-xl hover:bg-brand-50 dark:hover:bg-slate-700 disabled:opacity-50 shrink-0"
        :disabled="exporting"
        title="Xuất Excel"
        @click="exportMonthlyExcel"
      >
        <Loader2 v-if="exporting" class="w-4 h-4 animate-spin" />
        <FileSpreadsheet v-else class="w-4 h-4" />
        <span class="hidden sm:inline">Xuất Excel</span>
      </button>
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
        <button type="button" class="px-4 py-2 rounded-xl text-slate-500 dark:text-slate-400" @click="showModal = false">Huỷ</button>
        <button type="submit" class="px-4 py-2 rounded-xl bg-brand-gradient text-white">Lưu</button>
      </div>
    </form>
  </Modal>
</template>
