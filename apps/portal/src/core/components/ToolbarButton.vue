<script setup>
import { Loader2 } from 'lucide-vue-next'

// Nút phụ trên thanh công cụ của bảng (Xuất Excel, Xuất PDF...): mobile chỉ còn icon.
defineProps({
  icon: { type: [Object, Function], required: true },
  label: { type: String, required: true },
  loading: { type: Boolean, default: false },
  title: { type: String, default: '' },
})
</script>

<template>
  <button
    class="flex items-center justify-center gap-1 text-sm border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 w-9 h-9 sm:w-auto sm:h-auto sm:px-4 sm:py-2 rounded-full sm:rounded-xl hover:bg-brand-50 dark:hover:bg-slate-700 disabled:opacity-50 shrink-0"
    :disabled="loading"
    :title="title || label"
  >
    <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
    <component :is="icon" v-else class="w-4 h-4" />
    <span class="hidden sm:inline">{{ label }}</span>
  </button>
</template>
