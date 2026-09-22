<script setup>
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import FormActions from '../components/FormActions.vue'
import { Plus, Trash2 } from 'lucide-vue-next'
import { companyProductsApi } from '../api/resources'
import { useCrudResource } from '../composables/useCrudResource'
import { useSearchedRows } from '../composables/useSearchedRows'
import { PROCESS_STAGES, processStageLabel } from '../constants/processStages'

// Một mã có thể gồm nhiều thành phần (810 → 810A, 810B, 810C), và pH / nhiệt độ /
// thời gian cũng là một dòng trong bảng thông số — đúng như bảng giấy đang dùng.
// Ba cột thông số vì thế xếp chồng theo dòng con, giống bảng Thiết bị.
const columns = [
  { key: 'code', label: 'Mã', sortable: true },
  { key: 'name', label: 'Tên sản phẩm' },
  { key: 'component', label: 'Thành phần' },
  { key: 'standard', label: 'Tiêu chuẩn' },
  { key: 'spec_range', label: 'Phạm vi' },
  { key: 'field', label: 'Lĩnh vực', filterable: true },
  { key: 'process_stage', label: 'Công đoạn', filterable: true, format: processStageLabel },
  { key: 'usage_purpose', label: 'Công dụng' },
  { key: 'price', label: 'Giá' },
]

function emptyComponent() {
  return { component: '', standard: '', spec_range: '' }
}

function emptyForm() {
  return {
    code: '', name: '', field: '', usage_purpose: '', process_stage: '', price: null,
    components: [emptyComponent()],
  }
}

const { rows, showModal, editingId, form, openAdd, openEdit, save, remove } = useCrudResource(
  companyProductsApi, emptyForm,
  {
    mapRowToForm: row => ({
      code: row.code,
      name: row.name,
      field: row.field || '',
      usage_purpose: row.usage_purpose || '',
      process_stage: row.process_stage || '',
      price: row.price,
      components: row.components.length
        ? row.components.map(c => ({
            component: c.component || '', standard: c.standard || '', spec_range: c.spec_range || '',
          }))
        : [emptyComponent()],
    }),
    buildPayload: form => ({
      ...form,
      // Ô chọn chưa đụng tới gửi lên "" — công đoạn là tuỳ chọn nên đổi thành null.
      process_stage: form.process_stage || null,
      components: form.components.filter(c => c.component || c.standard || c.spec_range),
    }),
    confirmRemove: row => `Xoá sản phẩm "${row.name || row.code}"?`,
  },
)

const displayRows = useSearchedRows(rows, r => [
  r.code, r.name, r.field, r.usage_purpose, r.process_stage,
  ...r.components.flatMap(c => [c.component, c.standard, c.spec_range]),
])

function addComponent() {
  form.value.components.push(emptyComponent())
}

function removeComponent(index) {
  form.value.components.splice(index, 1)
}
</script>

<template>
  <DataTable
    :columns="columns"
    :rows="displayRows"
    title="Sản phẩm công ty"
    mobile-primary-key="code"
    mobile-secondary-key="name"
    @add="openAdd"
    @edit="openEdit"
    @delete="remove"
  >
    <template #cell-component="{ row }">
      <div v-for="c in row.components" :key="c.id" class="text-slate-700 dark:text-slate-200 mb-1 last:mb-0">{{ c.component }}</div>
    </template>
    <template #cell-standard="{ row }">
      <div v-for="c in row.components" :key="c.id" class="text-slate-700 dark:text-slate-200 mb-1 last:mb-0">{{ c.standard || '—' }}</div>
    </template>
    <template #cell-spec_range="{ row }">
      <div v-for="c in row.components" :key="c.id" class="text-slate-700 dark:text-slate-200 mb-1 last:mb-0">{{ c.spec_range || '—' }}</div>
    </template>

    <!-- Điện thoại: mã + tên nằm ở đầu thẻ, bảng thông số xếp thẳng hàng bên dưới -->
    <template #mobile-details="{ row }">
      <div class="rounded-xl bg-slate-50 dark:bg-slate-700/40 px-3 py-2">
        <template v-if="row.components.length">
          <div class="grid grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)_minmax(0,1fr)] gap-x-2 pb-1 text-[11px] uppercase tracking-wide text-slate-400 dark:text-slate-500 border-b border-slate-200 dark:border-slate-600">
            <span>Thành phần</span>
            <span class="text-right">Tiêu chuẩn</span>
            <span class="text-right">Phạm vi</span>
          </div>
          <div
            v-for="c in row.components"
            :key="c.id"
            class="grid grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)_minmax(0,1fr)] gap-x-2 py-1 text-sm text-slate-700 dark:text-slate-200 border-b border-slate-100 dark:border-slate-700/60 last:border-0"
          >
            <span class="truncate">{{ c.component || '—' }}</span>
            <span class="text-right">{{ c.standard || '—' }}</span>
            <span class="text-right">{{ c.spec_range || '—' }}</span>
          </div>
        </template>
        <p v-if="row.usage_purpose" class="pt-1.5 text-xs text-slate-500 dark:text-slate-400">
          Công dụng: {{ row.usage_purpose }}
        </p>
        <p v-if="row.field || row.process_stage" class="pt-1 text-xs italic text-slate-400 dark:text-slate-500">
          {{ [row.field, processStageLabel(row.process_stage)].filter(Boolean).join(' · ') }}
        </p>
      </div>
    </template>
  </DataTable>

  <Modal :show="showModal" :title="editingId ? 'Sửa sản phẩm' : 'Thêm sản phẩm'" @close="showModal = false">
    <form class="space-y-4" @submit.prevent="save">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-4">
        <div class="min-w-0">
          <label class="field-label mb-1">Mã sản phẩm</label>
          <input v-model="form.code" class="w-full field-input" />
        </div>
        <div class="min-w-0">
          <label class="field-label mb-1">Tên sản phẩm</label>
          <input v-model="form.name" class="w-full field-input" />
        </div>
        <div class="min-w-0">
          <label class="field-label mb-1">Lĩnh vực</label>
          <input v-model="form.field" class="w-full field-input" />
        </div>
        <div class="min-w-0">
          <label class="field-label mb-1">Công đoạn</label>
          <select v-model="form.process_stage" class="w-full field-input">
            <option value="">-- Không chọn --</option>
            <option v-for="opt in PROCESS_STAGES" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div class="sm:col-span-2 min-w-0">
          <label class="field-label mb-1">Công dụng</label>
          <input v-model="form.usage_purpose" class="w-full field-input" />
        </div>
        <div class="min-w-0">
          <label class="field-label mb-1">Giá</label>
          <input v-model.number="form.price" type="number" class="w-full field-input" />
        </div>
      </div>

      <div>
        <label class="field-label mb-2">Bảng thông số</label>
        <!-- Ba ô xếp dọc trên điện thoại, thành một hàng từ khổ sm; nút xoá luôn
             nằm ngoài lưới để không chiếm mất một cột của hàng nhập. -->
        <div class="hidden sm:flex gap-2 mb-1 text-[11px] uppercase tracking-wide text-slate-400 dark:text-slate-500">
          <div class="grid grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)_minmax(0,1fr)] gap-2 flex-1 min-w-0">
            <span>Thành phần</span>
            <span>Tiêu chuẩn</span>
            <span>Phạm vi</span>
          </div>
          <span class="w-4 shrink-0" />
        </div>
        <div v-for="(c, i) in form.components" :key="i" class="flex items-center gap-2 mb-2">
          <div class="grid grid-cols-1 sm:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)_minmax(0,1fr)] gap-2 flex-1 min-w-0">
            <input v-model="c.component" placeholder="CHB-89A, pH, Nhiệt độ…" class="field-input" />
            <input v-model="c.standard" placeholder="100 ml/L" class="field-input" />
            <input v-model="c.spec_range" placeholder="80-120 ml/L" class="field-input" />
          </div>
          <button type="button" class="text-red-400 shrink-0" @click="removeComponent(i)">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
        <button type="button" class="flex items-center gap-1 text-sm text-brand-600" @click="addComponent">
          <Plus class="w-4 h-4" /> Thêm thành phần
        </button>
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <FormActions @cancel="showModal = false" />
      </div>
    </form>
  </Modal>
</template>
