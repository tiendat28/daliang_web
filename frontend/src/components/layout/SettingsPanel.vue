<script setup>
import { ref } from 'vue'
import { Sun, Moon, FileSpreadsheet, FileText, DatabaseBackup, Upload, Loader2 } from 'lucide-vue-next'
import Modal from '../Modal.vue'
import { themeStore, setTheme } from '../../store/theme'
import {
  customersApi, companyProductsApi, labChemicalsApi, indicatorsApi,
  equipmentApi, chemicalOrdersApi, chemicalSamplingApi, analysisReportsApi, workLogApi,
} from '../../api/resources'
import { exportMultiTablePdf } from '../../utils/pdfReport'
import { downloadWorkbook } from '../../utils/excelReport'
import {
  addLabChemicalsSheet, addIndicatorsSheet, addEquipmentSheet, addChemicalOrdersSheet, addGenericSheet,
} from '../../utils/reportSheets'

defineProps({ show: Boolean })
const emit = defineEmits(['close'])

const PROCESS_STAGE_LABEL = { pre_treatment: 'Tiền xử lý', plating: 'Mạ', post_plating: 'Sau mạ' }

const exportTables = [
  { key: 'customers', label: 'Khách hàng', build: buildCustomers },
  { key: 'company-products', label: 'Sản phẩm công ty', build: buildCompanyProducts },
  { key: 'lab-chemicals', label: 'Hóa chất PTN', build: buildLabChemicals },
  { key: 'indicators', label: 'Chất chỉ thị', build: buildIndicators },
  { key: 'equipment', label: 'Thiết bị', build: buildEquipment },
  { key: 'chemical-orders', label: 'Đơn hàng HCTN', build: buildChemicalOrders },
  { key: 'chemical-sampling', label: 'Lấy mẫu HC', build: buildChemicalSampling },
  { key: 'analysis-reports', label: 'Báo cáo phân tích', build: buildAnalysisReports },
  { key: 'work-log', label: 'Nhật ký công tác', build: buildWorkLogs },
]

const selectedKeys = ref([exportTables[0].key])
const customFilename = ref('')
const exporting = ref('') // '' | 'excel' | 'pdf'
const backingUp = ref(false)
const restoring = ref(false)
const fileInput = ref(null)
const statusMessage = ref('')

function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`
}

function currentPeriod() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}
const includePeriod = ref(true)
const selectedPeriod = ref(currentPeriod())

function activePeriod() {
  if (!includePeriod.value || !selectedPeriod.value) return null
  const [year, month] = selectedPeriod.value.split('-')
  return { month, year }
}

function sanitizeFilename(name) {
  return name.replace(/[\\/:*?"<>|]/g, '').trim()
}

function suggestedFilename() {
  const labels = exportTables.filter(t => selectedKeys.value.includes(t.key)).map(t => t.label)
  return labels.join(' - ') || 'Xuat_du_lieu'
}

function outputFilename(ext) {
  const base = sanitizeFilename(customFilename.value) || suggestedFilename()
  return `${base}_${todayStr()}.${ext}`
}

async function buildCustomers() {
  const list = await customersApi.list()
  const headers = ['STT', 'Tên KH', 'Địa chỉ', 'Ghi chú', 'Lĩnh vực', 'SP dùng']
  const rows = list.map((c, i) => [
    i + 1, c.name, c.address || '', c.note || '',
    c.fields.map(f => f.field_name).join('; '),
    c.fields.map(f => f.products.map(p => p.product_code_text).join(',')).join('; '),
  ])
  return { headers, rows }
}

async function buildCompanyProducts() {
  const list = await companyProductsApi.list()
  const headers = ['STT', 'Mã', 'Tên', 'Lĩnh vực', 'Công dụng', 'Nồng độ', 'Đơn vị', 'Công đoạn', 'Giá']
  const rows = list.map((p, i) => [
    i + 1, p.code, p.name, p.field || '', p.usage_purpose || '', p.concentration || '',
    p.unit || '', PROCESS_STAGE_LABEL[p.process_stage] || '', p.price ?? '',
  ])
  return { headers, rows }
}

async function buildLabChemicals() {
  const list = await labChemicalsApi.list()
  const headers = ['STT', 'Mã', 'Tên', 'Loại', 'Số hộp', 'DT/hộp', 'Nguyên', 'Lẻ', 'Đơn vị', 'Ghi chú']
  const rows = list.map((c, i) => [
    i + 1, c.code, c.name, c.type || '', c.box_count ?? '', c.volume_per_box ?? '',
    c.total_volume ?? '', c.remaining_volume ?? '', c.unit || '', c.note || '',
  ])
  return { headers, rows }
}

async function buildEquipment() {
  const list = await equipmentApi.list()
  const headers = ['STT', 'Tên thiết bị', 'Phân loại', 'Số lượng', 'Đơn vị', 'Ghi chú']
  const rows = []
  list.forEach((e, i) => {
    if (e.variants.length === 0) {
      rows.push([i + 1, e.name, '', '', '', e.note || ''])
    } else {
      e.variants.forEach((v, vi) => rows.push([
        vi === 0 ? i + 1 : '', vi === 0 ? e.name : '',
        v.classification || '', v.quantity ?? '', v.unit || '', vi === 0 ? (e.note || '') : '',
      ]))
    }
  })
  return { headers, rows }
}

async function buildChemicalOrders() {
  const [orders, chemicals, customers] = await Promise.all([
    chemicalOrdersApi.list(), labChemicalsApi.list(), customersApi.list(),
  ])
  // Cùng thứ tự cột với sheet Excel "Đơn hàng HCTN" (xem addChemicalOrdersSheet)
  const headers = ['STT', 'Tên sản phẩm', 'Nồng độ', 'Số lượng', 'Hóa chất', 'Lượng', 'Sử dụng', 'Khách hàng', 'Ngày pha', 'Ngày xuất', 'Ghi chú']
  const rows = orders.map((o, i) => [
    i + 1, o.product_name || '',
    o.concentration || '', o.order_quantity || '',
    chemicals.find(c => c.id === o.lab_chemical_id)?.code || o.lab_chemical_id,
    o.amount || '',
    [o.used_amount ?? '', o.unit || ''].filter(v => v !== '').join(' '),
    customers.find(c => c.id === o.customer_id)?.name || o.customer_id,
    o.mix_date || '', o.issue_date || '', o.note || '',
  ])
  return { headers, rows }
}

async function buildChemicalSampling() {
  const [list, products] = await Promise.all([chemicalSamplingApi.list(), companyProductsApi.list()])
  const headers = ['STT', 'Sản phẩm', 'Tên mẫu', 'SL', 'Đơn vị', 'Ngày', 'Ghi chú']
  const rows = list.map((s, i) => [
    i + 1,
    products.find(p => p.id === s.company_product_id)?.name || s.company_product_id,
    s.name || '', s.quantity ?? '', s.unit || '', s.sample_date || '', s.note || '',
  ])
  return { headers, rows }
}

async function buildIndicators() {
  const list = await indicatorsApi.list()
  const headers = ['STT', 'Tên', 'Loại', 'Số lượng', 'Đơn vị', 'Ghi chú']
  const rows = list.map((r, i) => [i + 1, r.name, r.type || '', r.quantity ?? '', r.unit || '', r.note || ''])
  return { headers, rows }
}

async function buildAnalysisReports() {
  const [list, customers] = await Promise.all([analysisReportsApi.list(), customersApi.list()])
  const headers = ['STT', 'Khách hàng', 'Ngày nhận mẫu', 'Ngày phân tích', 'NV phân tích', 'Người duyệt', 'Ghi chú']
  const rows = list.map((r, i) => [
    i + 1,
    customers.find(c => c.id === r.customer_id)?.name || r.customer_id,
    r.sample_receive_date || '', r.issue_date || '',
    (r.completed_by || []).join(', '), r.approved_by || '', r.note || '',
  ])
  return { headers, rows }
}

async function buildWorkLogs() {
  const list = await workLogApi.list()
  const headers = ['STT', 'Ngày', 'Nội dung']
  const rows = list.map((r, i) => [i + 1, r.log_date || '', r.content || ''])
  return { headers, rows }
}

async function exportExcel() {
  if (!selectedKeys.value.length) { statusMessage.value = 'Chọn ít nhất 1 mục để xuất.'; return }
  exporting.value = 'excel'
  statusMessage.value = ''
  try {
    const ExcelJS = await import('exceljs')
    const wb = new ExcelJS.Workbook()
    const usedNames = new Set()
    const period = activePeriod()

    for (const key of selectedKeys.value) {
      const table = exportTables.find(t => t.key === key)
      if (key === 'lab-chemicals') {
        await addLabChemicalsSheet(wb, await labChemicalsApi.list(), period)
      } else if (key === 'indicators') {
        await addIndicatorsSheet(wb, await indicatorsApi.list(), period)
      } else if (key === 'equipment') {
        await addEquipmentSheet(wb, await equipmentApi.list(), period)
      } else if (key === 'chemical-orders') {
        const [orders, chemicals, customers] = await Promise.all([
          chemicalOrdersApi.list(), labChemicalsApi.list(), customersApi.list(),
        ])
        await addChemicalOrdersSheet(wb, orders, chemicals, customers, period)
      } else {
        const { headers, rows } = await table.build()
        let sheetName = table.label.replace(/[\\/?*[\]:]/g, '').slice(0, 31)
        while (usedNames.has(sheetName)) sheetName = `${sheetName.slice(0, 28)}_${usedNames.size}`
        usedNames.add(sheetName)
        await addGenericSheet(wb, { sheetName, title: table.label.toUpperCase(), headerLabels: headers, rows, period })
      }
    }

    await downloadWorkbook(wb, outputFilename('xlsx'))
    statusMessage.value = `Đã xuất Excel (${selectedKeys.value.length} sheet).`
  } catch (e) {
    statusMessage.value = 'Xuất Excel thất bại, thử lại.'
  } finally {
    exporting.value = ''
  }
}

async function exportPdf() {
  if (!selectedKeys.value.length) { statusMessage.value = 'Chọn ít nhất 1 mục để xuất.'; return }
  exporting.value = 'pdf'
  statusMessage.value = ''
  try {
    const sections = []
    for (const key of selectedKeys.value) {
      const table = exportTables.find(t => t.key === key)
      const { headers, rows } = await table.build()
      sections.push({ title: table.label, headers, rows })
    }
    await exportMultiTablePdf({ sections, filename: outputFilename('pdf') })
    statusMessage.value = `Đã xuất PDF (${selectedKeys.value.length} mục).`
  } catch (e) {
    statusMessage.value = 'Xuất PDF thất bại, thử lại.'
  } finally {
    exporting.value = ''
  }
}

function downloadBlob(content, filename, type) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

async function backupData() {
  backingUp.value = true
  statusMessage.value = ''
  try {
    const [
      customers, companyProducts, labChemicals, indicators,
      equipment, chemicalOrders, chemicalSampling, analysisReports, workLogs,
    ] = await Promise.all([
      customersApi.list(), companyProductsApi.list(), labChemicalsApi.list(), indicatorsApi.list(),
      equipmentApi.list(), chemicalOrdersApi.list(), chemicalSamplingApi.list(), analysisReportsApi.list(), workLogApi.list(),
    ])
    const backup = {
      exported_at: new Date().toISOString(),
      customers, company_products: companyProducts, lab_chemicals: labChemicals, indicators,
      equipment, chemical_orders: chemicalOrders, chemical_sampling: chemicalSampling,
      analysis_reports: analysisReports, work_logs: workLogs,
    }
    downloadBlob(JSON.stringify(backup, null, 2), `daliang-backup_${todayStr()}.json`, 'application/json')
    statusMessage.value = 'Đã tải file sao lưu.'
  } catch (e) {
    statusMessage.value = 'Sao lưu thất bại, thử lại.'
  } finally {
    backingUp.value = false
  }
}

function triggerImport() {
  fileInput.value?.click()
}

async function restoreList(list, createFn, mapFn) {
  let created = 0
  let skipped = 0
  for (const item of list || []) {
    try {
      await createFn(mapFn(item))
      created++
    } catch (e) {
      skipped++
    }
  }
  return { created, skipped }
}

async function handleImportFile(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return

  restoring.value = true
  statusMessage.value = ''
  try {
    const data = JSON.parse(await file.text())
    let created = 0
    let skipped = 0
    const tally = (r) => { created += r.created; skipped += r.skipped }

    // Cac bang khong phu thuoc truoc, bang tham chieu (don hang, lay mau, bao cao) sau
    tally(await restoreList(data.customers, customersApi.create, c => ({
      name: c.name, address: c.address, note: c.note,
      fields: (c.fields || []).map(f => ({
        field_name: f.field_name,
        product_codes: (f.products || []).map(p => p.product_code_text).filter(Boolean),
      })),
    })))
    tally(await restoreList(data.company_products, companyProductsApi.create, p => ({
      code: p.code, name: p.name, field: p.field, usage_purpose: p.usage_purpose,
      concentration: p.concentration, unit: p.unit, process_stage: p.process_stage, price: p.price,
    })))
    tally(await restoreList(data.lab_chemicals, labChemicalsApi.create, c => ({
      code: c.code, name: c.name, type: c.type, box_count: c.box_count,
      volume_per_box: c.volume_per_box, remaining_volume: c.remaining_volume, unit: c.unit, note: c.note,
    })))
    tally(await restoreList(data.indicators, indicatorsApi.create, r => ({
      name: r.name, type: r.type, quantity: r.quantity, unit: r.unit, note: r.note,
    })))
    tally(await restoreList(data.equipment, equipmentApi.create, eq => ({
      name: eq.name, note: eq.note,
      variants: (eq.variants || []).map(v => ({
        classification: v.classification, quantity: v.quantity, unit: v.unit, note: v.note,
      })),
    })))
    tally(await restoreList(data.work_logs, workLogApi.create, w => ({ log_date: w.log_date, content: w.content })))
    tally(await restoreList(data.chemical_orders, chemicalOrdersApi.create, o => ({
      product_name: o.product_name, lab_chemical_id: o.lab_chemical_id, customer_id: o.customer_id,
      concentration: o.concentration, amount: o.amount, order_quantity: o.order_quantity,
      used_amount: o.used_amount, unit: o.unit, mix_date: o.mix_date, issue_date: o.issue_date, note: o.note,
    })))
    tally(await restoreList(data.chemical_sampling, chemicalSamplingApi.create, s => ({
      company_product_id: s.company_product_id, name: s.name, quantity: s.quantity,
      unit: s.unit, sample_date: s.sample_date, note: s.note,
    })))
    tally(await restoreList(data.analysis_reports, analysisReportsApi.create, r => ({
      customer_id: r.customer_id, sample_receive_date: r.sample_receive_date, issue_date: r.issue_date,
      approved_by: r.approved_by, note: r.note, completed_by: r.completed_by || [],
      samples: (r.samples || []).map(s => ({
        name: s.name,
        components: (s.components || []).map(c => ({ name: c.name, result: c.result, note: c.note })),
      })),
    })))

    statusMessage.value = `Đã nhập ${created} bản ghi${skipped ? `, bỏ qua ${skipped} (trùng/lỗi)` : ''}. Tải lại trang để xem dữ liệu mới.`
  } catch (e) {
    statusMessage.value = 'Nhập file sao lưu thất bại. Kiểm tra định dạng file.'
  } finally {
    restoring.value = false
  }
}
</script>

<template>
  <Modal :show="show" title="Cài đặt" @close="emit('close')">
    <div class="space-y-6">
      <section>
        <h4 class="text-sm font-semibold text-slate-600 dark:text-slate-300 mb-2">Giao diện</h4>
        <div class="flex gap-2">
          <button
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-colors"
            :class="themeStore.mode === 'light'
              ? 'bg-brand-gradient text-white border-transparent shadow'
              : 'text-slate-500 dark:text-slate-300 border-slate-200 dark:border-slate-600'"
            @click="setTheme('light')"
          >
            <Sun class="w-4 h-4" /> Sáng
          </button>
          <button
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-colors"
            :class="themeStore.mode === 'dark'
              ? 'bg-brand-gradient text-white border-transparent shadow'
              : 'text-slate-500 dark:text-slate-300 border-slate-200 dark:border-slate-600'"
            @click="setTheme('dark')"
          >
            <Moon class="w-4 h-4" /> Tối
          </button>
        </div>
      </section>

      <section>
        <h4 class="text-sm font-semibold text-slate-600 dark:text-slate-300 mb-2">Xuất dữ liệu</h4>
        <p class="text-xs text-slate-400 dark:text-slate-500 mb-1">Chọn 1 hoặc nhiều mục — sẽ gộp chung 1 file</p>
        <div class="grid grid-cols-2 gap-x-2 gap-y-1 mb-2 max-h-40 overflow-y-auto pr-1 border border-slate-200 dark:border-slate-600 rounded-xl p-2">
          <label
            v-for="t in exportTables"
            :key="t.key"
            class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 cursor-pointer"
          >
            <input v-model="selectedKeys" type="checkbox" :value="t.key" class="rounded" />
            {{ t.label }}
          </label>
        </div>
        <input
          v-model="customFilename"
          type="text"
          placeholder="Tên file xuất (để trống sẽ tự đặt tên)"
          class="w-full field-input mb-2"
        />
        <label class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 mb-2">
          <input v-model="includePeriod" type="checkbox" class="rounded" />
          Ghi tháng/năm vào tiêu đề (chỉ áp dụng khi xuất Excel)
          <input
            v-if="includePeriod"
            v-model="selectedPeriod"
            type="month"
            class="field-input ml-auto"
          />
        </label>
        <div class="flex gap-2">
          <button
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-brand-50 dark:hover:bg-slate-700 disabled:opacity-50"
            :disabled="!!exporting"
            @click="exportExcel"
          >
            <Loader2 v-if="exporting === 'excel'" class="w-4 h-4 animate-spin" />
            <FileSpreadsheet v-else class="w-4 h-4" />
            Xuất Excel
          </button>
          <button
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-brand-50 dark:hover:bg-slate-700 disabled:opacity-50"
            :disabled="!!exporting"
            @click="exportPdf"
          >
            <Loader2 v-if="exporting === 'pdf'" class="w-4 h-4 animate-spin" />
            <FileText v-else class="w-4 h-4" />
            Xuất PDF
          </button>
        </div>
      </section>

      <section>
        <h4 class="text-sm font-semibold text-slate-600 dark:text-slate-300 mb-2">Sao lưu</h4>
        <div class="flex gap-2">
          <button
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-brand-50 dark:hover:bg-slate-700 disabled:opacity-50"
            :disabled="backingUp"
            @click="backupData"
          >
            <Loader2 v-if="backingUp" class="w-4 h-4 animate-spin" />
            <DatabaseBackup v-else class="w-4 h-4" />
            Xuất file sao lưu
          </button>
          <button
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-brand-50 dark:hover:bg-slate-700 disabled:opacity-50"
            :disabled="restoring"
            @click="triggerImport"
          >
            <Loader2 v-if="restoring" class="w-4 h-4 animate-spin" />
            <Upload v-else class="w-4 h-4" />
            Nhập file sao lưu
          </button>
          <input ref="fileInput" type="file" accept="application/json" class="hidden" @change="handleImportFile" />
        </div>
      </section>

      <p v-if="statusMessage" class="text-xs text-center text-brand-600 dark:text-brand-400">{{ statusMessage }}</p>
    </div>
  </Modal>
</template>
