<script setup>
import { Menu } from 'lucide-vue-next'
import { sidebarOpen } from '@/core/store/sidebar'

// Nút mở thanh bên, cho các trang tự dựng đầu trang riêng (không dùng Topbar).
</script>

<template>
  <button
    type="button"
    class="w-10 h-10 shrink-0 rounded-xl border border-dl-line dark:border-slate-600 bg-white dark:bg-slate-800 flex items-center justify-center text-dl-body dark:text-slate-300 hover:text-dl-teal hover:border-dl-teal transition-colors"
    aria-label="Mở thanh điều hướng"
    @click="sidebarOpen = !sidebarOpen"
  >
    <Menu class="w-[18px] h-[18px]" :stroke-width="1.8" />
  </button>
</template>
