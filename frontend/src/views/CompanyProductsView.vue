<script setup>
import DataTable from '../components/DataTable.vue'
import Modal from '../components/Modal.vue'
import FormActions from '../components/FormActions.vue'
import DynamicForm from '../components/DynamicForm.vue'
import { companyProductsApi } from '../api/resources'
import { useCrudResource } from '../composables/useCrudResource'
import { useSearchedRows } from '../composables/useSearchedRows'
import { PROCESS_STAGES, processStageLabel } from '../constants/processStages'

// Các thông số kỹ thuật là chữ tự do, đơn vị viết luôn trong ô nên không còn
// cột "Đơn vị" riêng — xem thêm ghi chú ở models.py.
const columns = [
  { key: 'code', label: 'Mã', sortable: true },
  { key: 'name', label: 'Tên' },
  { key: 'field', label: 'Lĩnh vực', filterable: true },
  { key: 'usage_purpose', label: 'Công dụng' },
  { key: 'process_stage', label: 'Công đoạn', filterable: true, format: processStageLabel },
  { key: 'concentration', label: 'Nồng độ' },
  { key: 'temperature', label: 'Nhiệt độ' },
  { key: 'duration', label: 'Thời gian' },
  { key: 'ph', label: 'pH' },
  { key: 'price', label: 'Giá' },
]

const fields = [
  { key: 'code', label: 'Mã sản phẩm' },
  { key: 'name', label: 'Tên sản phẩm' },
  { key: 'field', label: 'Lĩnh vực' },
  { key: 'usage_purpose', label: 'Công dụng', full: true },
  { key: 'process_stage', label: 'Công đoạn', type: 'select', options: PROCESS_STAGES },
  { key: 'concentration', label: 'Nồng độ', placeholder: 'VD: 5 ml/L' },
  { key: 'temperature', label: 'Nhiệt độ', placeholder: 'VD: 50°C' },
  { key: 'duration', label: 'Thời gian', placeholder: 'VD: 10 giây, 10 phút' },
  { key: 'ph', label: 'pH', placeholder: 'VD: 1.8' },
  { key: 'price', label: 'Giá', type: 'number' },
]

function emptyForm() {
  return {
    code: '', name: '', field: '', usage_purpose: '', process_stage: '',
    concentration: '', temperature: '', duration: '', ph: '', price: null,
  }
}

const { rows, showModal, editingId, form, openAdd, openEdit, save, remove } = useCrudResource(
  companyProductsApi, emptyForm,
  { confirmRemove: row => `Xoá sản phẩm "${row.name}"?` },
)

const displayRows = useSearchedRows(rows, r => [
  r.code, r.name, r.field, r.usage_purpose, r.process_stage,
  r.concentration, r.temperature, r.duration, r.ph,
])
</script>

<template>
  <DataTable :columns="columns" :rows="displayRows" title="Sản phẩm công ty" @add="openAdd" @edit="openEdit" @delete="remove" />

  <Modal :show="showModal" :title="editingId ? 'Sửa sản phẩm' : 'Thêm sản phẩm'" @close="showModal = false">
    <DynamicForm v-model="form" :fields="fields" @submit="save">
      <template #actions>
        <FormActions @cancel="showModal = false" />
      </template>
    </DynamicForm>
  </Modal>
</template>
