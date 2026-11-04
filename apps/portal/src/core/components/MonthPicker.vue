<script setup>
import { CalendarDays } from 'lucide-vue-next'

// Mobile: ô chọn tháng co thành nút icon lịch cho thanh công cụ gọn 1 dòng.
// Ô tháng thật nằm chồng lên, trong suốt, nên bấm vào icon là mở đúng bộ chọn của máy.
defineProps({ modelValue: { type: String, default: '' } })
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <label
    class="sm:hidden relative flex items-center justify-center w-9 h-9 rounded-full border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 shrink-0"
    title="Chọn tháng"
  >
    <CalendarDays class="w-4 h-4" />
    <input
      :value="modelValue"
      type="month"
      class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      @input="emit('update:modelValue', $event.target.value)"
    />
  </label>
  <input
    :value="modelValue"
    type="month"
    class="hidden sm:block field-input w-auto text-sm px-3 py-2"
    @input="emit('update:modelValue', $event.target.value)"
  />
</template>
