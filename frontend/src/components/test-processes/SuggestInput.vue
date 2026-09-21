<script setup>
import { ref, computed } from 'vue'
import { ChevronDown } from 'lucide-vue-next'
import { foldAccents } from '../../utils/testProcessFormat'

// Ô gõ tự do có gợi ý: khách hàng, hạng mục, đơn vị… Gõ gì cũng lưu được,
// danh sách chỉ để bấm cho nhanh. Tìm không phân biệt dấu.
const props = defineProps({
  modelValue: { type: String, default: '' },
  // Mỗi gợi ý là chuỗi hoặc { value, hint }
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: '' },
  inputId: { type: String, default: '' },
  inputClass: { type: String, default: '' },
  maxItems: { type: Number, default: 8 },
})

const emit = defineEmits(['update:modelValue', 'select'])

const open = ref(false)
const input = ref(null)

const normalized = computed(() => props.options.map(option => (
  typeof option === 'string' ? { value: option, hint: '' } : option
)))

const matches = computed(() => {
  const needle = foldAccents(props.modelValue || '').trim().toLowerCase()
  const pool = needle
    ? normalized.value.filter(option => foldAccents(option.value).toLowerCase().includes(needle))
    : normalized.value
  return pool.slice(0, props.maxItems)
})

function pick(option) {
  emit('update:modelValue', option.value)
  emit('select', option)
  open.value = false
  input.value?.blur()
}

// Đóng trễ một nhịp, nếu không thì bấm vào gợi ý sẽ bị blur nuốt mất
function onBlur() {
  setTimeout(() => { open.value = false }, 120)
}

function toggle() {
  open.value = !open.value
  input.value?.focus()
}
</script>

<template>
  <div class="relative">
    <div
      class="flex items-center gap-2 lt-field"
      :class="inputClass"
    >
      <input
        :id="inputId"
        ref="input"
        :value="modelValue"
        type="text"
        :placeholder="placeholder"
        autocomplete="off"
        class="flex-1 min-w-0 bg-transparent border-none outline-none text-[13.5px] text-lt-ink dark:text-slate-100"
        @input="emit('update:modelValue', $event.target.value)"
        @focus="open = true"
        @blur="onBlur"
      />
      <button
        type="button"
        class="text-lt-muted dark:text-slate-400 shrink-0"
        tabindex="-1"
        aria-label="Xem gợi ý"
        @mousedown.prevent="toggle"
      >
        <ChevronDown class="w-[15px] h-[15px]" />
      </button>
    </div>

    <ul
      v-if="open && matches.length"
      class="absolute left-0 right-0 top-[42px] z-30 max-h-64 overflow-y-auto p-1.5 rounded-xl bg-white dark:bg-slate-800 border border-lt-line dark:border-slate-600 shadow-lt-card"
    >
      <li v-for="option in matches" :key="option.value">
        <button
          type="button"
          class="w-full flex items-center justify-between gap-3 px-2 py-1.5 rounded-lg text-left text-[13px] text-lt-ink dark:text-slate-100 hover:bg-lt-wash dark:hover:bg-slate-700"
          @mousedown.prevent="pick(option)"
        >
          <span class="truncate">{{ option.value }}</span>
          <span v-if="option.hint" class="text-[11.5px] text-lt-faint dark:text-slate-500 shrink-0">{{ option.hint }}</span>
        </button>
      </li>
    </ul>
  </div>
</template>
