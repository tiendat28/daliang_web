<script setup>
import { Plus } from 'lucide-vue-next'

// Khung card dùng chung cho mọi bảng: tiêu đề + thanh nút ở trên, vùng nội dung
// tự co trong chiều cao còn lại (min-h-0) để chân bảng luôn nhìn thấy, phần chân
// (phân trang) nằm ở slot "footer".
defineProps({
  title: { type: String, default: '' },
  addLabel: { type: String, default: 'Thêm mới' },
})
const emit = defineEmits(['add'])
</script>

<template>
  <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm flex flex-col min-h-0">
    <div class="flex flex-wrap items-center justify-between gap-3 p-5 pb-4 shrink-0">
      <h2 class="font-semibold text-slate-700 dark:text-slate-200">{{ title }}</h2>
      <div class="flex flex-wrap items-center gap-2">
        <slot name="actions" />
        <button
          class="flex items-center justify-center gap-1 text-sm bg-brand-gradient text-white w-9 h-9 sm:w-auto sm:h-auto sm:px-4 sm:py-2 rounded-full sm:rounded-xl shadow shrink-0"
          :title="addLabel"
          @click="emit('add')"
        >
          <Plus class="w-4 h-4" />
          <span class="hidden sm:inline">{{ addLabel }}</span>
        </button>
      </div>
    </div>

    <slot />

    <slot name="footer" />
  </div>
</template>
