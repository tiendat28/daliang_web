<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import Modal from '../components/Modal.vue'
import { chemicalOrdersApi, labChemicalsApi, customersApi } from '../api/resources'
import { Plus, Trash2, Pencil } from 'lucide-vue-next'
import { productSearch } from '../store/productSearch'
import { formatDate } from '../utils/format'
import { groupChemicalOrders } from '../utils/orderGrouping'

const rows = ref([])
const labChemicals = ref([])
const customers = ref([])
const showModal = ref(false)
const editingId = ref(null)
const form = ref(emptyForm())

function labChemicalName(id) {
  return labChemicals.value.find(c => c.id === id)?.name || id
}
function customerName(id) {
  return customers.value.find(c => c.id === id)?.name || id
}

const displayRows = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter(r => [
    r.product_name, labChemicalName(r.lab_chemical_id), customerName(r.customer_id),
    r.concentration, r.amount, r.order_quantity, r.unit, r.note,
  ].some(v => String(v ?? '').toLowerCase().includes(q)))
})

// Gộp các dòng cùng lô (cùng KH + cùng ngày pha) để hiển thị chung 1 STT — xem utils/orderGrouping.js
const groupedRows = computed(() => groupChemicalOrders(displayRows.value))

// Với giao diện mobile, mỗi lô hiển thị dạng 1 thẻ gồm các hóa chất bên trong
const batches = computed(() => {
  const result = []
  groupedRows.value.forEach((row) => {
    if (row.spans.stt > 0) result.push({ stt: row.stt, lines: [row.order] })
    else result[result.length - 1].lines.push(row.order)
  })
  return result
})

function emptyLine() {
  return { lab_chemical_id: '', concentration: '', amount: '', used_amount: 0, unit: '' }
}

function emptyForm() {
  return {
    customer_id: '', order_quantity: '',
    product_name: '',
    mix_date: '', issue_date: '', note: '',
    lines: [emptyLine()],
  }
}

async function load() {
  const [orderList, chemicalList, customerList] = await Promise.all([
    chemicalOrdersApi.list(), labChemicalsApi.list(), customersApi.list(),
  ])
  rows.value = orderList
  labChemicals.value = chemicalList
  customers.value = customerList
}

function openAdd() {
  editingId.value = null
  form.value = emptyForm()
  showModal.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.value = {
    customer_id: row.customer_id,
    order_quantity: row.order_quantity || '',
    product_name: row.product_name || '',
    mix_date: row.mix_date || '',
    issue_date: row.issue_date || '',
    note: row.note || '',
    lines: [{
      lab_chemical_id: row.lab_chemical_id,
      concentration: row.concentration || '',
      amount: row.amount || '',
      used_amount: row.used_amount ?? 0,
      unit: row.unit || '',
    }],
  }
  showModal.value = true
}

function addLine() {
  form.value.lines.push(emptyLine())
}
function removeLine(i) {
  form.value.lines.splice(i, 1)
}

async function save() {
  const shared = {
    product_name: form.value.product_name || null,
    customer_id: form.value.customer_id,
    order_quantity: form.value.order_quantity,
    mix_date: form.value.mix_date || null,
    issue_date: form.value.issue_date || null,
    note: form.value.note,
  }
  if (editingId.value) {
    const line = form.value.lines[0]
    await chemicalOrdersApi.update(editingId.value, { ...shared, ...line })
  } else {
    for (const line of form.value.lines) {
      if (!line.lab_chemical_id) continue
      await chemicalOrdersApi.create({ ...shared, ...line })
    }
  }
  showModal.value = false
  await load()
}

async function remove(row) {
  if (confirm('Xoá đơn hàng này?')) {
    await chemicalOrdersApi.remove(row.id)
    await load()
  }
}

onMounted(load)
onUnmounted(() => { productSearch.query = '' })
</script>

<template>
  <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm flex flex-col">
    <div class="flex flex-wrap items-center justify-between gap-3 p-5 pb-4">
      <h2 class="font-semibold text-slate-700 dark:text-slate-200">Đơn hàng HCTN</h2>
      <button
        class="flex items-center gap-1 text-sm bg-brand-gradient text-white px-4 py-2 rounded-xl shadow"
        @click="openAdd"
      >
        <Plus class="w-4 h-4" /> Thêm mới
      </button>
    </div>

    <div v-if="groupedRows.length === 0" class="py-10 text-center text-slate-400 text-sm px-5">Chưa có đơn hàng nào</div>

    <!-- Desktop / tablet: bảng gộp theo lô, dùng rowspan cho STT/Tên sản phẩm/KH/Ngày -->
    <div v-else class="hidden sm:block overflow-auto px-5 pb-5 max-h-[65vh]">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-800 dark:text-slate-100 border-b-2 border-slate-300 dark:border-slate-600 sticky top-0 z-10 bg-white dark:bg-slate-800">
            <th class="py-2 pr-4 font-semibold w-12">STT</th>
            <th class="py-2 pr-4 font-semibold">Tên sản phẩm</th>
            <th class="py-2 pr-4 font-semibold">Hóa chất</th>
            <th class="py-2 pr-4 font-semibold">Nồng độ</th>
            <th class="py-2 pr-4 font-semibold">Sử dụng</th>
            <th class="py-2 pr-4 font-semibold">Đơn vị</th>
            <th class="py-2 pr-4 font-semibold">Khách hàng</th>
            <th class="py-2 pr-4 font-semibold">Ngày pha</th>
            <th class="py-2 pr-4 font-semibold">Ngày xuất</th>
            <th class="py-2 w-16"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in groupedRows"
            :key="row.order.id"
            class="border-b border-slate-200 dark:border-slate-700 hover:bg-brand-50/40 dark:hover:bg-slate-700/40"
          >
            <td v-if="row.spans.stt" :rowspan="row.spans.stt" class="py-3 pr-4 align-top text-slate-500 dark:text-slate-400">{{ row.stt }}</td>
            <td v-if="row.spans.product_name" :rowspan="row.spans.product_name" class="py-3 pr-4 align-top text-slate-700 dark:text-slate-200 font-medium">
              {{ row.order.product_name || labChemicalName(row.order.lab_chemical_id) }}
            </td>
            <td class="py-3 pr-4 align-top text-slate-700 dark:text-slate-200">{{ labChemicalName(row.order.lab_chemical_id) }}</td>
            <td class="py-3 pr-4 align-top text-slate-700 dark:text-slate-200">{{ row.order.concentration }}</td>
            <td class="py-3 pr-4 align-top text-slate-700 dark:text-slate-200">{{ row.order.used_amount }}</td>
            <td class="py-3 pr-4 align-top text-slate-700 dark:text-slate-200">{{ row.order.unit }}</td>
            <td v-if="row.spans.customer_id" :rowspan="row.spans.customer_id" class="py-3 pr-4 align-top text-slate-700 dark:text-slate-200">{{ customerName(row.order.customer_id) }}</td>
            <td v-if="row.spans.mix_date" :rowspan="row.spans.mix_date" class="py-3 pr-4 align-top text-slate-500 dark:text-slate-400 whitespace-nowrap">{{ formatDate(row.order.mix_date) }}</td>
            <td v-if="row.spans.issue_date" :rowspan="row.spans.issue_date" class="py-3 pr-4 align-top text-slate-500 dark:text-slate-400 whitespace-nowrap">{{ formatDate(row.order.issue_date) }}</td>
            <td class="py-3 align-top">
              <div class="flex items-center gap-2">
                <button class="text-slate-400 hover:text-brand-600" @click="openEdit(row.order)">
                  <Pencil class="w-4 h-4" />
                </button>
                <button class="text-slate-400 hover:text-red-500" @click="remove(row.order)">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile: mỗi lô 1 thẻ, các hóa chất trong lô liệt kê bên trong -->
    <div v-if="groupedRows.length > 0" class="sm:hidden flex flex-col gap-3 px-5 pb-5">
      <div v-for="batch in batches" :key="batch.stt" class="rounded-2xl bg-slate-50 dark:bg-slate-700/50 p-3">
        <p class="text-xs text-slate-400">#{{ batch.stt }} · {{ customerName(batch.lines[0].customer_id) }}</p>
        <p class="text-sm font-semibold text-slate-700 dark:text-slate-200 truncate">
          {{ batch.lines[0].product_name || labChemicalName(batch.lines[0].lab_chemical_id) }}
        </p>
        <p class="text-xs text-slate-400 mb-2">Pha: {{ formatDate(batch.lines[0].mix_date) }} · Xuất: {{ formatDate(batch.lines[0].issue_date) }}</p>

        <div
          v-for="line in batch.lines"
          :key="line.id"
          class="flex items-center justify-between gap-2 py-2 border-t border-slate-200 dark:border-slate-600"
        >
          <div class="min-w-0 text-sm text-slate-600 dark:text-slate-300">
            <p class="truncate">{{ labChemicalName(line.lab_chemical_id) }} · {{ line.concentration }}</p>
            <p class="text-xs text-slate-400">{{ line.used_amount }} {{ line.unit }}</p>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button class="text-slate-400 hover:text-brand-600" @click="openEdit(line)">
              <Pencil class="w-4 h-4" />
            </button>
            <button class="text-slate-400 hover:text-red-500" @click="remove(line)">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <Modal :show="showModal" :title="editingId ? 'Sửa đơn hàng' : 'Thêm đơn hàng'" @close="showModal = false">
    <form class="grid grid-cols-2 gap-x-4 gap-y-4" @submit.prevent="save">
      <div>
        <label class="field-label mb-1">Khách hàng</label>
        <select v-model="form.customer_id" class="w-full field-input">
          <option value="" disabled>-- Chọn --</option>
          <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div>
        <label class="field-label mb-1">Số lượng</label>
        <input v-model="form.order_quantity" class="w-full field-input" />
      </div>

      <div class="col-span-2 rounded-2xl border border-slate-200 dark:border-slate-600 p-4">
        <label class="field-label mb-1">Tên sản phẩm (để trống nếu đơn chỉ có 1 hóa chất)</label>
        <input v-model="form.product_name" placeholder="VD: pH 10" class="w-full field-input mb-3" />

        <label class="field-label mb-2">
          Hóa chất trong đơn{{ editingId ? '' : ' (có thể thêm nhiều nếu 1 đơn pha nhiều hóa chất, VD pH 10)' }}
        </label>
        <div v-for="(line, i) in form.lines" :key="i" class="grid grid-cols-5 gap-2 mb-2 items-start">
          <select v-model="line.lab_chemical_id" class="field-input">
            <option value="" disabled>-- Chọn hóa chất --</option>
            <option v-for="c in labChemicals" :key="c.id" :value="c.id">{{ c.code }} - {{ c.name }}</option>
          </select>
          <input v-model="line.concentration" placeholder="Nồng độ" class="field-input" />
          <input v-model="line.amount" placeholder="Lượng" class="field-input" />
          <input v-model.number="line.used_amount" type="number" placeholder="Sử dụng" class="field-input" />
          <div class="flex gap-1">
            <input v-model="line.unit" placeholder="Đ.vị" class="field-input flex-1 min-w-0" />
            <button
              v-if="!editingId && form.lines.length > 1"
              type="button" class="text-red-400 shrink-0" @click="removeLine(i)"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
        <button v-if="!editingId" type="button" class="flex items-center gap-1 text-sm text-brand-600" @click="addLine">
          <Plus class="w-4 h-4" /> Thêm hóa chất
        </button>
      </div>

      <div>
        <label class="field-label mb-1">Ngày pha</label>
        <input v-model="form.mix_date" type="date" class="w-full field-input" />
      </div>
      <div>
        <label class="field-label mb-1">Ngày xuất</label>
        <input v-model="form.issue_date" type="date" class="w-full field-input" />
      </div>

      <div class="col-span-2">
        <label class="field-label mb-1">Ghi chú</label>
        <textarea v-model="form.note" rows="2" class="w-full field-input" />
      </div>

      <div class="col-span-2 flex justify-end gap-2 pt-2">
        <button type="button" class="px-4 py-2 rounded-xl text-slate-500" @click="showModal = false">Huỷ</button>
        <button type="submit" class="px-4 py-2 rounded-xl bg-brand-gradient text-white">Lưu</button>
      </div>
    </form>
  </Modal>
</template>
