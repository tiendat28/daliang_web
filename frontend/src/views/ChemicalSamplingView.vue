<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import DynamicForm from '../components/DynamicForm.vue'
import { chemicalSamplingApi, companyProductsApi } from '../api/resources'
import { productSearch } from '../store/productSearch'

const rows = ref([])
const products = ref([])
const showModal = ref(false)
const editingId = ref(null)
const form = ref(emptyForm())

const columns = [
  { key: 'company_product_id', label: 'Sản phẩm' },
  { key: 'name', label: 'Tên mẫu' },
  { key: 'quantity', label: 'SL' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'sample_date', label: 'Ngày' },
  { key: 'note', label: 'Ghi chú' },
]

function productName(id) {
  return products.value.find(p => p.id === id)?.name || id
}

const displayRows = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter(r => [
    productName(r.company_product_id), r.name, r.unit, r.note,
  ].some(v => String(v ?? '').toLowerCase().includes(q)))
})

const fields = computed(() => [
  { key: 'company_product_id', label: 'Sản phẩm công ty', type: 'select', options: products.value.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` })) },
  { key: 'name', label: 'Tên mẫu' },
  { key: 'quantity', label: 'Số lượng', type: 'number' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'sample_date', label: 'Ngày lấy mẫu', type: 'date' },
  { key: 'note', label: 'Ghi chú', type: 'textarea' },
])

function emptyForm() {
  return { company_product_id: '', name: '', quantity: 0, unit: '', sample_date: '', note: '' }
}

async function load() {
  const [samplingList, productList] = await Promise.all([chemicalSamplingApi.list(), companyProductsApi.list()])
  rows.value = samplingList
  products.value = productList
}

function openAdd() { editingId.value = null; form.value = emptyForm(); showModal.value = true }
function openEdit(row) { editingId.value = row.id; form.value = { ...row }; showModal.value = true }
async function save() {
  if (editingId.value) {
    await chemicalSamplingApi.update(editingId.value, form.value)
  } else {
    await chemicalSamplingApi.create(form.value)
  }
  showModal.value = false
  await load()
}
async function remove(row) {
  if (confirm('Xoá bản ghi lấy mẫu này?')) {
    await chemicalSamplingApi.remove(row.id)
    await load()
  }
}

onMounted(load)
onUnmounted(() => { productSearch.query = '' })
</script>

<template>
  <DataTable :columns="columns" :rows="displayRows" title="Lấy mẫu hóa chất" @add="openAdd" @edit="openEdit" @delete="remove">
    <template #cell-company_product_id="{ row }">{{ productName(row.company_product_id) }}</template>
  </DataTable>

  <Modal :show="showModal" :title="editingId ? 'Sửa bản ghi' : 'Thêm bản ghi'" @close="showModal = false">
    <DynamicForm v-model="form" :fields="fields" @submit="save">
      <template #actions>
        <button type="button" class="px-4 py-2 rounded-xl text-slate-500" @click="showModal = false">Huỷ</button>
        <button type="submit" class="px-4 py-2 rounded-xl bg-brand-gradient text-white">Lưu</button>
      </template>
    </DynamicForm>
  </Modal>
</template>
