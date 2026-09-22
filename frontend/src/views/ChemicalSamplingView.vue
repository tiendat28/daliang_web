<script setup>
import { ref, onMounted, computed } from 'vue'
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import FormActions from '../components/FormActions.vue'
import DynamicForm from '../components/DynamicForm.vue'
import { chemicalSamplingApi, companyProductsApi } from '../api/resources'
import { useCrudResource } from '../composables/useCrudResource'
import { useSearchedRows } from '../composables/useSearchedRows'

const products = ref([])

const columns = [
  { key: 'company_product_id', label: 'Sản phẩm' },
  { key: 'name', label: 'Tên mẫu' },
  { key: 'quantity', label: 'SL' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'sample_date', label: 'Ngày' },
  { key: 'note', label: 'Ghi chú' },
]

function productCode(id) {
  return products.value.find(p => p.id === id)?.code || id
}

const fields = computed(() => [
  { key: 'company_product_id', label: 'Sản phẩm công ty', type: 'select', options: products.value.map(p => ({ value: p.id, label: p.code })) },
  { key: 'name', label: 'Tên mẫu' },
  { key: 'quantity', label: 'Số lượng', type: 'number' },
  { key: 'unit', label: 'Đơn vị' },
  { key: 'sample_date', label: 'Ngày lấy mẫu', type: 'date' },
  { key: 'note', label: 'Ghi chú', type: 'textarea' },
])

function emptyForm() {
  return { company_product_id: '', name: '', quantity: 0, unit: '', sample_date: '', note: '' }
}

const { rows, showModal, editingId, form, openAdd, openEdit, save, remove } = useCrudResource(
  chemicalSamplingApi, emptyForm,
  { confirmRemove: () => 'Xoá bản ghi lấy mẫu này?' },
)

const displayRows = useSearchedRows(rows, r => [productCode(r.company_product_id), r.name, r.unit, r.note])

onMounted(async () => { products.value = await companyProductsApi.list() })
</script>

<template>
  <DataTable :columns="columns" :rows="displayRows" title="Lấy mẫu hóa chất" @add="openAdd" @edit="openEdit" @delete="remove">
    <template #cell-company_product_id="{ row }">{{ productCode(row.company_product_id) }}</template>
  </DataTable>

  <Modal :show="showModal" :title="editingId ? 'Sửa bản ghi' : 'Thêm bản ghi'" @close="showModal = false">
    <DynamicForm v-model="form" :fields="fields" @submit="save">
      <template #actions>
        <FormActions @cancel="showModal = false" />
      </template>
    </DynamicForm>
  </Modal>
</template>
