<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

// Chân bảng: chọn số dòng/trang + chuyển trang. Luôn nằm trong vùng nhìn thấy
// vì card bảng co theo chiều cao còn lại (xem TableCard).
defineProps({
  page: { type: Number, required: true },
  pageSize: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  totalRows: { type: Number, required: true },
  pageSizeOptions: { type: Array, default: () => [10, 20, 50, 100] },
})
const emit = defineEmits(['update:page', 'update:pageSize'])
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3 p-5 pt-4 border-t border-slate-100 dark:border-slate-700 text-sm text-slate-500 dark:text-slate-400 shrink-0">
    <div class="flex items-center gap-2">
      <span>Hiển thị</span>
      <select
        :value="pageSize"
        class="rounded-lg border border-slate-200 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 px-2 py-1 text-sm"
        @change="emit('update:pageSize', Number($event.target.value))"
      >
        <option v-for="opt in pageSizeOptions" :key="opt" :value="opt">{{ opt }}</option>
      </select>
      <span>/ trang · {{ totalRows }} dòng</span>
    </div>
    <div class="flex items-center gap-1">
      <button
        class="w-8 h-8 rounded-lg flex items-center justify-center disabled:opacity-30 hover:bg-brand-50 dark:hover:bg-slate-700"
        :disabled="page <= 1"
        @click="emit('update:page', page - 1)"
      >
        <ChevronLeft class="w-4 h-4" />
      </button>
      <span class="px-2">Trang {{ page }} / {{ totalPages }}</span>
      <button
        class="w-8 h-8 rounded-lg flex items-center justify-center disabled:opacity-30 hover:bg-brand-50 dark:hover:bg-slate-700"
        :disabled="page >= totalPages"
        @click="emit('update:page', page + 1)"
      >
        <ChevronRight class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
