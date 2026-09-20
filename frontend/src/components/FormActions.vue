<script setup>
// Cặp nút Huỷ / Lưu dùng chung cho mọi form trong modal.
defineProps({
  submitLabel: { type: String, default: 'Lưu' },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['cancel'])
</script>

<template>
  <button type="button" class="px-4 py-2 rounded-xl text-slate-500 dark:text-slate-400" @click="emit('cancel')">Huỷ</button>
  <button type="submit" class="px-4 py-2 rounded-xl bg-brand-gradient text-white disabled:opacity-50" :disabled="disabled">
    {{ submitLabel }}
  </button>
</template>
