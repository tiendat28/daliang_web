<script setup>
import { ZOOM_OPTIONS } from '../../constants/testProcess'

// Cặp nút "Vừa khung / 100%" ở chân khung xem trước tờ in.
defineProps({ modelValue: { type: String, default: 'fit' } })
defineEmits(['update:modelValue'])
</script>

<template>
  <div class="flex p-0.5 rounded-[9px] bg-lt-paper dark:bg-slate-700">
    <button
      v-for="option in ZOOM_OPTIONS"
      :key="option.value"
      type="button"
      class="px-2.5 py-1 rounded-[7px] text-[11.5px]"
      :class="modelValue === option.value
        ? 'bg-white dark:bg-slate-800 font-semibold text-lt-tealink shadow-sm'
        : 'font-medium text-lt-muted dark:text-slate-300'"
      @click="$emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>
