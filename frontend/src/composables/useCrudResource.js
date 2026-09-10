import { ref, onMounted, onUnmounted } from 'vue'
import { productSearch } from '../store/productSearch'

// Chuẩn hoá pattern CRUD lặp lại ở các view: rows + modal + form + load/save/remove.
export function useCrudResource(api, emptyForm, options = {}) {
  const {
    mapRowToForm = row => ({ ...row }),
    buildPayload = form => form,
    confirmRemove = () => 'Xoá bản ghi này?',
    resetSearchOnUnmount = true,
  } = options

  const rows = ref([])
  const showModal = ref(false)
  const editingId = ref(null)
  const form = ref(emptyForm())

  async function load() {
    rows.value = await api.list()
  }

  function openAdd() {
    editingId.value = null
    form.value = emptyForm()
    showModal.value = true
  }

  function openEdit(row) {
    editingId.value = row.id
    form.value = mapRowToForm(row)
    showModal.value = true
  }

  async function save() {
    const payload = buildPayload(form.value)
    if (editingId.value) {
      await api.update(editingId.value, payload)
    } else {
      await api.create(payload)
    }
    showModal.value = false
    await load()
  }

  async function remove(row) {
    if (confirm(confirmRemove(row))) {
      await api.remove(row.id)
      await load()
    }
  }

  onMounted(load)
  if (resetSearchOnUnmount) {
    onUnmounted(() => { productSearch.query = '' })
  }

  return { rows, showModal, editingId, form, load, openAdd, openEdit, save, remove }
}
