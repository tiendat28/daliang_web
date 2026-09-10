<script setup>
import { computed } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import DynamicForm from '../components/DynamicForm.vue'
import { companyProductsApi } from '../api/resources'
import { productSearch } from '../store/productSearch'
import { useCrudResource } from '../composables/useCrudResource'

const processStageLabels = {
  pre_treatment: 'Tiền xử lý',
  plating: 'Mạ',
  post_plating: 'Sau mạ',
}

const columns = [
  { key: 'code', label: 'Mã', sortable: true },
  { key: 'name', label: 'Tên' },
  { key: 'field', label: 'Lĩnh vực', filterable: true },
  { key: 'process_stage', label: 'Công đoạn', filterable: true, format: v => processStageLabels[v] ?? v },
  { key: 'concentration', label: 'Nồng độ' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'price', label: 'Giá' },
]

const displayRows = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter(r =>
    [r.code, r.name, r.field, r.process_stage, r.concentration, r.unit].some(v =>
      String(v ?? '').toLowerCase().includes(q)
    )
  )
})

const fields = [
  { key: 'code', label: 'Mã sản phẩm' },
  { key: 'name', label: 'Tên sản phẩm' },
  { key: 'field', label: 'Lĩnh vực' },
  { key: 'usage_purpose', label: 'Công dụng' },
  { key: 'concentration', label: 'Nồng độ' },
  { key: 'unit', label: 'Đơn vị' },
  {
    key: 'process_stage', label: 'Công đoạn', type: 'select',
    options: [
      { value: 'pre_treatment', label: 'Tiền xử lý' },
      { value: 'plating', label: 'Mạ' },
      { value: 'post_plating', label: 'Sau mạ' },
    ],
  },
  { key: 'price', label: 'Giá', type: 'number' },
]

function emptyForm() {
  return { code: '', name: '', field: '', usage_purpose: '', concentration: '', unit: '', process_stage: '', price: null }
}

const { rows, showModal, editingId, form, openAdd, openEdit, save, remove } = useCrudResource(
  companyProductsApi, emptyForm,
  { confirmRemove: row => `Xoá sản phẩm "${row.name}"?` },
)
</script>

<template>
  <DataTable :columns="columns" :rows="displayRows" title="Sản phẩm công ty" @add="openAdd" @edit="openEdit" @delete="remove" />

  <Modal :show="showModal" :title="editingId ? 'Sửa sản phẩm' : 'Thêm sản phẩm'" @close="showModal = false">
    <DynamicForm v-model="form" :fields="fields" @submit="save">
      <template #actions>
        <button type="button" class="px-4 py-2 rounded-xl text-slate-500" @click="showModal = false">Huỷ</button>
        <button type="submit" class="px-4 py-2 rounded-xl bg-brand-gradient text-white">Lưu</button>
      </template>
    </DynamicForm>
  </Modal>
</template>
