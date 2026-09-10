<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import ReportPrintPreview from '../components/analysis-reports/ReportPrintPreview.vue'
import { analysisReportsApi, customersApi } from '../api/resources'
import { Plus, Trash2, Eye } from 'lucide-vue-next'
import { formatDate } from '../utils/format'
import { productSearch } from '../store/productSearch'
import { useCrudResource } from '../composables/useCrudResource'

const customers = ref([])
const showViewModal = ref(false)
const viewingReport = ref(null)

const columns = [
  { key: 'customer_id', label: 'KH' },
  { key: 'sample_receive_date', label: 'Ngày nhận mẫu' },
  { key: 'issue_date', label: 'Ngày phân tích' },
  { key: 'completed_by', label: 'NV phân tích' },
  { key: 'approved_by', label: 'Người duyệt' },
]

function customerName(id) {
  return customers.value.find(c => c.id === id)?.name || id
}

const displayRows = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter(r => {
    const sampleVals = r.samples.flatMap(s => [s.name, ...s.components.flatMap(c => [c.name, c.result, c.note])])
    return [
      customerName(r.customer_id), r.approved_by, r.note,
      ...(r.completed_by || []), ...sampleVals,
    ].some(v => String(v ?? '').toLowerCase().includes(q))
  })
})

function emptyForm() {
  return {
    customer_id: '', sample_receive_date: '', issue_date: '',
    completed_by: [''], approved_by: '', note: '',
    samples: [{ name: '', components: [{ name: '', result: '', note: '' }] }],
  }
}

const { rows, showModal, editingId, form, openAdd, openEdit, save, remove } = useCrudResource(
  analysisReportsApi, emptyForm,
  {
    mapRowToForm: row => ({
      customer_id: row.customer_id,
      sample_receive_date: row.sample_receive_date || '',
      issue_date: row.issue_date || '',
      completed_by: row.completed_by.length ? [...row.completed_by] : [''],
      approved_by: row.approved_by || '',
      note: row.note || '',
      samples: row.samples.length
        ? row.samples.map(s => ({
            name: s.name,
            components: s.components.length
              ? s.components.map(c => ({ name: c.name, result: c.result, note: c.note || '' }))
              : [{ name: '', result: '', note: '' }],
          }))
        : [{ name: '', components: [{ name: '', result: '', note: '' }] }],
    }),
    buildPayload: form => ({
      ...form,
      sample_receive_date: form.sample_receive_date || null,
      issue_date: form.issue_date || null,
      completed_by: form.completed_by.map(n => n.trim()).filter(Boolean),
      samples: form.samples
        .filter(s => s.name)
        .map(s => ({ ...s, components: s.components.filter(c => c.name) })),
    }),
    confirmRemove: row => `Xoá báo cáo phân tích của "${customerName(row.customer_id)}"?`,
  },
)

onMounted(async () => { customers.value = await customersApi.list() })

function addSample() {
  form.value.samples.push({ name: '', components: [{ name: '', result: '', note: '' }] })
}
function removeSample(i) {
  form.value.samples.splice(i, 1)
}
function addComponent(sampleIndex) {
  form.value.samples[sampleIndex].components.push({ name: '', result: '', note: '' })
}
function removeComponent(sampleIndex, componentIndex) {
  form.value.samples[sampleIndex].components.splice(componentIndex, 1)
}

function addCompletedBy() {
  form.value.completed_by.push('')
}
function removeCompletedBy(i) {
  form.value.completed_by.splice(i, 1)
}

function openView(row) {
  viewingReport.value = row
  showViewModal.value = true
}
</script>

<template>
  <DataTable :columns="columns" :rows="displayRows" title="Báo cáo phân tích" @add="openAdd" @edit="openEdit" @delete="remove">
    <template #cell-customer_id="{ row }">{{ customerName(row.customer_id) }}</template>
    <template #cell-sample_receive_date="{ row }">{{ formatDate(row.sample_receive_date) }}</template>
    <template #cell-issue_date="{ row }">{{ formatDate(row.issue_date) }}</template>
    <template #cell-completed_by="{ row }">{{ row.completed_by.join(', ') }}</template>
    <template #row-actions="{ row }">
      <button class="text-slate-400 hover:text-brand-600" title="Xem báo cáo" @click="openView(row)">
        <Eye class="w-4 h-4" />
      </button>
    </template>
  </DataTable>

  <Modal :show="showModal" :title="editingId ? 'Sửa báo cáo phân tích' : 'Thêm báo cáo phân tích'" @close="showModal = false">
    <form class="space-y-4" @submit.prevent="save">
      <div>
        <label class="field-label mb-1">Khách hàng</label>
        <select
          v-model="form.customer_id"
          class="w-full field-input"
        >
          <option value="" disabled>-- Chọn KH --</option>
          <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="field-label mb-1">Ngày nhận mẫu</label>
          <input v-model="form.sample_receive_date" type="date" class="w-full field-input" />
        </div>
        <div>
          <label class="field-label mb-1">Ngày phân tích</label>
          <input v-model="form.issue_date" type="date" class="w-full field-input" />
        </div>
      </div>

      <div>
        <label class="field-label mb-2">Mẫu phân tích & thành phần (TP / KQ)</label>
        <div v-for="(s, si) in form.samples" :key="si" class="mb-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-700/50">
          <div class="flex gap-2 mb-2">
            <input v-model="s.name" placeholder="Tên mẫu phân tích (VD: Bể SnI)" class="flex-1 field-input" />
            <button type="button" class="text-red-400" @click="removeSample(si)">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
          <div v-for="(c, ci) in s.components" :key="ci" class="flex flex-wrap gap-2 mb-2 pl-4 items-center">
            <input v-model="c.name" placeholder="TP (VD: SnO2, Ni, pH)" class="flex-1 min-w-[140px] field-input" />
            <input v-model="c.result" placeholder="KQ" class="w-20 field-input" />
            <input v-model="c.note" placeholder="Ghi chú" class="flex-1 min-w-[100px] field-input" />
            <button type="button" class="text-red-400 shrink-0" @click="removeComponent(si, ci)">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
          <button type="button" class="flex items-center gap-1 text-xs text-brand-600 pl-4" @click="addComponent(si)">
            <Plus class="w-3.5 h-3.5" /> Thêm TP
          </button>
        </div>
        <button type="button" class="flex items-center gap-1 text-sm text-brand-600" @click="addSample">
          <Plus class="w-4 h-4" /> Thêm mẫu phân tích
        </button>
      </div>

      <div>
        <label class="field-label mb-2">Nhân viên phân tích (có thể thêm nhiều)</label>
        <div v-for="(name, ni) in form.completed_by" :key="ni" class="flex gap-2 mb-2">
          <input v-model="form.completed_by[ni]" class="flex-1 field-input" />
          <button type="button" class="text-red-400" @click="removeCompletedBy(ni)">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
        <button type="button" class="flex items-center gap-1 text-sm text-brand-600" @click="addCompletedBy">
          <Plus class="w-4 h-4" /> Thêm nhân viên
        </button>
      </div>

      <div>
        <label class="field-label mb-1">Người duyệt</label>
        <input v-model="form.approved_by" class="w-full field-input" />
      </div>

      <div>
        <label class="field-label mb-1">Ghi chú</label>
        <textarea v-model="form.note" rows="2" class="w-full field-input" />
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <button type="button" class="px-4 py-2 rounded-xl text-slate-500 dark:text-slate-400" @click="showModal = false">Huỷ</button>
        <button type="submit" class="px-4 py-2 rounded-xl bg-brand-gradient text-white">Lưu</button>
      </div>
    </form>
  </Modal>

  <Modal :show="showViewModal" title="Báo cáo kết quả" @close="showViewModal = false">
    <ReportPrintPreview
      v-if="viewingReport"
      :report="viewingReport"
      :customer-name="customerName(viewingReport.customer_id)"
    />
  </Modal>
</template>
