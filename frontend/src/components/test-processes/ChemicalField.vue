<script setup>
import { ref, computed } from 'vue'
import { X } from 'lucide-vue-next'
import { applyFormulaMarkers, foldAccents, renderMarkers } from '../../utils/testProcessFormat'

// Ô "Hóa chất" của một bước: các chip đã chọn + ô tìm sản phẩm công ty / hóa
// chất PTN. Gõ tên lạ rồi Enter thì lưu nguyên văn, vì phiếu test hay có hóa
// chất chưa nhập vào danh mục.
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  products: { type: Array, default: () => [] },
  labChemicals: { type: Array, default: () => [] },
  inputId: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const query = ref('')
const open = ref(false)

const options = computed(() => [
  ...props.products.map(product => ({
    key: `p-${product.id}`,
    label: product.code,
    hint: product.name && product.name !== product.code ? product.name : 'SP công ty',
    chemical: { product_id: product.id, lab_chemical_id: null, display_name: product.code },
  })),
  ...props.labChemicals.map(chemical => ({
    key: `l-${chemical.id}`,
    label: chemical.code,
    hint: chemical.name || 'HC PTN',
    // Mã hóa chất PTN thường là công thức nên tự đánh dấu chỉ số: HNO3 -> HNO_3
    chemical: { product_id: null, lab_chemical_id: chemical.id, display_name: applyFormulaMarkers(chemical.code) },
  })),
])

const matches = computed(() => {
  const needle = foldAccents(query.value).trim().toLowerCase()
  const taken = new Set(props.modelValue.map(row => (row.display_name || '').toLowerCase()))
  const pool = options.value.filter(option => !taken.has(option.chemical.display_name.toLowerCase()))
  if (!needle) return pool.slice(0, 8)
  return pool
    .filter(option => foldAccents(`${option.label} ${option.hint}`).toLowerCase().includes(needle))
    .slice(0, 8)
})

function add(chemical) {
  emit('update:modelValue', [...props.modelValue, chemical])
  query.value = ''
}

function addTyped() {
  const name = query.value.trim()
  if (!name) return
  const chosen = matches.value[0]
  if (chosen && chosen.label.toLowerCase() === name.toLowerCase()) add({ ...chosen.chemical })
  else add({ product_id: null, lab_chemical_id: null, display_name: name })
}

function removeAt(index) {
  emit('update:modelValue', props.modelValue.filter((_, i) => i !== index))
}

function removeLast() {
  if (!query.value && props.modelValue.length) removeAt(props.modelValue.length - 1)
}

function onBlur() {
  setTimeout(() => { open.value = false }, 120)
}
</script>

<template>
  <div class="relative">
    <div class="flex flex-wrap items-center gap-1.5 min-h-[38px] px-2.5 py-[5px] rounded-[10px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-700">
      <span
        v-for="(row, index) in modelValue"
        :key="index"
        class="flex items-center gap-1.5 pl-2.5 pr-1.5 py-1 rounded-lg bg-lt-chip dark:bg-slate-600 border border-lt-chipline dark:border-slate-500 text-[12.5px] font-medium text-lt-chipink dark:text-slate-100"
      >
        <span v-html="renderMarkers(row.display_name)" />
        <button
          type="button"
          class="text-[#6E8C86] dark:text-slate-300 hover:text-lt-voidink"
          :aria-label="`Bỏ ${row.display_name}`"
          @click="removeAt(index)"
        >
          <X class="w-3 h-3" />
        </button>
      </span>

      <input
        :id="inputId"
        v-model="query"
        type="text"
        placeholder="Tìm sản phẩm công ty hoặc hóa chất PTN…"
        autocomplete="off"
        title="Gõ tên lạ rồi Enter để thêm. Dùng _ cho chỉ số dưới (HNO_3) và ^ cho chỉ số trên (Zn^2+)."
        class="flex-1 min-w-[180px] h-[26px] bg-transparent border-none outline-none text-[13px] text-lt-ink dark:text-slate-100"
        @focus="open = true"
        @blur="onBlur"
        @keydown.enter.prevent="addTyped"
        @keydown.backspace="removeLast"
      />
    </div>

    <ul
      v-if="open && matches.length"
      class="absolute left-0 right-0 top-[44px] z-30 max-h-64 overflow-y-auto p-1.5 rounded-xl bg-white dark:bg-slate-800 border border-lt-line dark:border-slate-600 shadow-lt-card"
    >
      <li v-for="option in matches" :key="option.key">
        <button
          type="button"
          class="w-full flex items-center justify-between gap-3 px-2 py-1.5 rounded-lg text-left text-[13px] text-lt-ink dark:text-slate-100 hover:bg-lt-wash dark:hover:bg-slate-700"
          @mousedown.prevent="add({ ...option.chemical })"
        >
          <span class="font-medium truncate" v-html="renderMarkers(option.chemical.display_name)" />
          <span class="text-[11.5px] text-lt-faint dark:text-slate-500 truncate max-w-[55%]">{{ option.hint }}</span>
        </button>
      </li>
    </ul>
  </div>
</template>
