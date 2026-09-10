<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import { analysisReportsApi, customersApi } from '../api/resources'
import { Plus, Trash2, Eye, Printer } from 'lucide-vue-next'
import { formatFormula } from '../utils/chemFormula'
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

function printReport() {
  window.print()
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
          <div v-for="(c, ci) in s.components" :key="ci" class="flex gap-2 mb-2 pl-4">
            <input v-model="c.name" placeholder="TP (VD: SnO2, Ni, pH)" class="flex-1 field-input" />
            <input v-model="c.result" placeholder="KQ" class="w-24 field-input" />
            <input v-model="c.note" placeholder="Ghi chú" class="w-28 field-input" />
            <button type="button" class="text-red-400" @click="removeComponent(si, ci)">
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
    <div v-if="viewingReport">
      <div id="print-report" class="bg-white text-black p-6" style="font-family: 'Times New Roman', Georgia, serif;">
        <table class="w-full border-collapse border-2 border-black text-sm" style="table-layout: fixed;">
          <colgroup>
            <col style="width: 20%" />
            <col style="width: 18%" />
            <col style="width: 27%" />
            <col style="width: 35%" />
          </colgroup>
          <tbody>
            <tr>
              <td class="border border-black text-center align-middle p-2" rowspan="2">
                <img src="/images/logo-dlvc.png" alt="DLVC" class="w-24 h-auto mx-auto" />
              </td>
              <td class="border border-black text-center p-2" colspan="3">
                <p>越南大亮化工有限公司</p>
                <p class="font-bold">DALIANG CHEMICAL VIETNAM CO.,LTD</p>
              </td>
            </tr>
            <tr>
              <td class="border border-black text-center p-3 text-xl font-bold tracking-wide" colspan="3">BÁO CÁO KẾT QUẢ PHÂN TÍCH</td>
            </tr>

            <tr>
              <td class="border border-black p-2 whitespace-nowrap">Tên khách hàng:</td>
              <td class="border border-black p-2 text-center font-bold" colspan="3">{{ customerName(viewingReport.customer_id) }}</td>
            </tr>
            <tr>
              <td class="border border-black p-2 whitespace-nowrap">Ngày nhận mẫu:</td>
              <td class="border border-black p-2 text-center" colspan="3">{{ formatDate(viewingReport.sample_receive_date) }}</td>
            </tr>
            <tr>
              <td class="border border-black p-2 whitespace-nowrap">Ngày phân tích:</td>
              <td class="border border-black p-2 text-center" colspan="3">{{ formatDate(viewingReport.issue_date) }}</td>
            </tr>

            <tr class="font-bold text-center">
              <td class="border border-black p-2">Mẫu phân tích</td>
              <td class="border border-black p-2">Thành phần</td>
              <td class="border border-black p-2">Kết quả phân tích</td>
              <td class="border border-black p-2">Ghi chú</td>
            </tr>

            <template v-for="s in viewingReport.samples" :key="s.id">
              <tr v-for="(c, ci) in (s.components.length ? s.components : [{ id: `${s.id}-empty`, name: '', result: '', note: '' }])" :key="c.id">
                <td v-if="ci === 0" class="border border-black p-2 text-center font-bold align-middle" :rowspan="s.components.length || 1">{{ s.name }}</td>
                <td class="border border-black p-2 text-center">{{ formatFormula(c.name) }}</td>
                <td class="border border-black p-2 text-center">{{ c.result }}</td>
                <td class="border border-black p-2 text-center">{{ c.note }}</td>
              </tr>
            </template>
          </tbody>
        </table>

        <p v-if="viewingReport.note" class="mt-4 text-sm">Ghi chú: {{ viewingReport.note }}</p>

        <div class="flex justify-between text-center mt-10 px-10">
          <div>
            <p class="italic">Nhân viên hóa nghiệm</p>
            <p v-for="(name, i) in viewingReport.completed_by" :key="i" class="font-bold" :class="i === 0 ? 'mt-8' : 'mt-1'">{{ name }}</p>
          </div>
          <div>
            <p class="italic">Người duyệt</p>
            <p class="font-bold mt-8">{{ viewingReport.approved_by || '' }}</p>
          </div>
        </div>
      </div>

      <div class="flex justify-end mt-4 print:hidden">
        <button type="button" class="flex items-center gap-1 px-4 py-2 rounded-xl bg-brand-gradient text-white text-sm" @click="printReport">
          <Printer class="w-4 h-4" /> In báo cáo
        </button>
      </div>
    </div>
  </Modal>
</template>
