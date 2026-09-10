<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import { customersApi } from '../api/resources'
import { Plus, Trash2 } from 'lucide-vue-next'
import { productSearch } from '../store/productSearch'

const rows = ref([])
const showModal = ref(false)
const editingId = ref(null)
const form = ref(emptyForm())

const columns = [
  { key: 'name', label: 'Tên KH', sortable: true },
  { key: 'address', label: 'Địa chỉ' },
  { key: 'field_names', label: 'Lĩnh vực' },
  { key: 'field_products', label: 'SP dùng' },
]

const displayRows = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter(r => {
    const fieldNames = r.fields.map(f => f.field_name)
    const productCodes = r.fields.flatMap(f => f.products.map(p => p.product_code_text))
    return [r.name, r.address, r.note, ...fieldNames, ...productCodes].some(v =>
      String(v ?? '').toLowerCase().includes(q)
    )
  })
})

function emptyForm() {
  return { name: '', address: '', note: '', fields: [{ field_name: '', product_codes: [''] }] }
}

async function load() {
  rows.value = await customersApi.list()
}

function openAdd() {
  editingId.value = null
  form.value = emptyForm()
  showModal.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name,
    address: row.address,
    note: row.note,
    fields: row.fields.length
      ? row.fields.map(f => ({ field_name: f.field_name, product_codes: f.products.map(p => p.product_code_text) }))
      : [{ field_name: '', product_codes: [''] }],
  }
  showModal.value = true
}

function addField() {
  form.value.fields.push({ field_name: '', product_codes: [''] })
}

function removeField(i) {
  form.value.fields.splice(i, 1)
}

async function save() {
  const payload = {
    ...form.value,
    fields: form.value.fields
      .filter(f => f.field_name)
      .map(f => ({
        field_name: f.field_name,
        product_codes: f.product_codes.join(',').split(',').map(c => c.trim()).filter(Boolean),
      })),
  }
  if (editingId.value) {
    await customersApi.update(editingId.value, payload)
  } else {
    await customersApi.create(payload)
  }
  showModal.value = false
  await load()
}

async function remove(row) {
  if (confirm(`Xoá khách hàng "${row.name}"?`)) {
    await customersApi.remove(row.id)
    await load()
  }
}

onMounted(load)
onUnmounted(() => { productSearch.query = '' })
</script>

<template>
  <DataTable :columns="columns" :rows="displayRows" title="Khách hàng" @add="openAdd" @edit="openEdit" @delete="remove">
    <template #cell-field_names="{ row }">
      <div v-for="f in row.fields" :key="f.id" class="text-xs text-slate-500 mb-1">{{ f.field_name }}</div>
    </template>
    <template #cell-field_products="{ row }">
      <div v-for="f in row.fields" :key="f.id" class="text-xs text-slate-500 mb-1">
        {{ f.products.map(p => p.product_code_text).join(', ') }}
      </div>
    </template>
  </DataTable>

  <Modal :show="showModal" :title="editingId ? 'Sửa khách hàng' : 'Thêm khách hàng'" @close="showModal = false">
    <form class="space-y-4" @submit.prevent="save">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="field-label mb-1">Tên khách hàng</label>
          <input v-model="form.name" class="w-full field-input" />
        </div>
        <div>
          <label class="field-label mb-1">Địa chỉ</label>
          <input v-model="form.address" class="w-full field-input" />
        </div>
      </div>

      <div>
        <label class="field-label mb-2">Lĩnh vực & sản phẩm dùng</label>
        <div v-for="(f, i) in form.fields" :key="i" class="mb-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-700/50">
          <div class="flex gap-2 mb-2">
            <input v-model="f.field_name" placeholder="Lĩnh vực (VD: Kẽm axit)" class="flex-1 field-input" />
            <button type="button" class="text-red-400" @click="removeField(i)">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
          <input
            :value="f.product_codes.join(', ')"
            @input="f.product_codes = $event.target.value.split(',')"
            placeholder="Mã SP dùng, cách nhau bởi dấu phẩy (VD: ZK835, ZK838)"
            class="w-full field-input"
          />
        </div>
        <button type="button" class="flex items-center gap-1 text-sm text-brand-600" @click="addField">
          <Plus class="w-4 h-4" /> Thêm lĩnh vực
        </button>
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
</template>
