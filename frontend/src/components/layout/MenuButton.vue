<script setup>
import { Menu } from 'lucide-vue-next'
import { sidebarOpen } from '../../store/sidebar'

// Nút mở thanh bên, cho các trang tự dựng đầu trang riêng (không dùng Topbar).
</script>

<template>
  <button
    type="button"
    class="md:hidden w-10 h-10 shrink-0 rounded-full bg-white dark:bg-slate-700 flex items-center justify-center shadow-sm"
    aria-label="Mở thanh điều hướng"
    @click="sidebarOpen = true"
  >
    <Menu class="w-4 h-4 text-slate-500 dark:text-slate-300" />
  </button>
</template>
