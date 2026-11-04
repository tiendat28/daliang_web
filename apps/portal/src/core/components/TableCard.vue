<script setup>
import { computed } from 'vue'
import { Plus } from 'lucide-vue-next'
import { usePageCan } from '@/core/auth/store'

// Khung card dùng chung cho mọi bảng: tiêu đề + thanh nút ở trên, vùng nội dung
// tự co trong chiều cao còn lại (min-h-0) để chân bảng luôn nhìn thấy, phần chân
// (phân trang) nằm ở slot "footer".
// Nut "Them moi" tu an khi khong co quyen them (`<meta.permission>.create`);
// truyen :can-add de tu quyet dinh.
const props = defineProps({
  title: { type: String, default: '' },
  addLabel: { type: String, default: 'Thêm mới' },
  canAdd: { type: Boolean, default: null },
})
const emit = defineEmits(['add'])
const can = usePageCan()
const showAdd = computed(() => props.canAdd ?? can('create'))
</script>

<template>
  <div class="bg-white dark:bg-[#0e1728] rounded-2xl border border-slate-200/80 dark:border-slate-800/80 shadow-xs flex flex-col min-h-0">
    <div class="flex flex-wrap items-center justify-between gap-2.5 sm:gap-4 p-3.5 sm:p-5 pb-3 sm:pb-4 shrink-0">
      <h2 class="m-0 text-lg sm:text-2xl leading-tight font-bold text-slate-900 dark:text-slate-100">{{ title }}</h2>
      <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
        <slot name="toolbar" />
        <slot name="actions" />
        <button
          v-if="showAdd"
          class="flex items-center justify-center gap-1.5 text-sm bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-600 hover:to-emerald-700 text-white font-semibold px-3 sm:px-4 py-2 rounded-xl shadow-xs hover:shadow transition-all shrink-0 cursor-pointer"
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
