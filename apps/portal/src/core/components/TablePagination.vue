<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

// Chân bảng: chọn số dòng/trang + chuyển trang. Luôn nằm trong vùng nhìn thấy
// vì card bảng co theo chiều cao còn lại (xem TableCard).
defineProps({
  page: { type: Number, required: true },
  pageSize: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  totalRows: { type: Number, required: true },
  pageSizeOptions: { type: Array, default: () => [20, 50, 100, 200] },
})
const emit = defineEmits(['update:page', 'update:pageSize'])
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-2 sm:gap-3 p-3.5 sm:p-5 pt-3 sm:pt-4 border-t border-slate-100 dark:border-slate-800 text-xs sm:text-sm text-slate-500 dark:text-slate-400 shrink-0">
    <div class="flex items-center gap-1.5 sm:gap-2">
      <span>Hiển thị</span>
      <select
        :value="pageSize"
        class="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/80 dark:text-slate-100 px-1.5 sm:px-2 py-1 text-xs sm:text-sm"
        @change="emit('update:pageSize', Number($event.target.value))"
      >
        <option v-for="opt in pageSizeOptions" :key="opt" :value="opt">{{ opt }}</option>
      </select>
      <span>/ trang · {{ totalRows }} dòng</span>
    </div>
    <div class="flex items-center gap-1">
      <button
        class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center disabled:opacity-30 hover:bg-brand-50 dark:hover:bg-slate-700"
        :disabled="page <= 1"
        @click="emit('update:page', page - 1)"
      >
        <ChevronLeft class="w-4 h-4" />
      </button>
      <span class="px-1.5 sm:px-2 whitespace-nowrap">Trang {{ page }} / {{ totalPages }}</span>
      <button
        class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center disabled:opacity-30 hover:bg-brand-50 dark:hover:bg-slate-700"
        :disabled="page >= totalPages"
        @click="emit('update:page', page + 1)"
      >
        <ChevronRight class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
