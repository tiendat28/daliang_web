<script setup>
import { RouterLink, useRoute } from 'vue-router'
import { Users, Package, FlaskConical, ClipboardList, MoreHorizontal } from 'lucide-vue-next'
import { sidebarOpen } from '../../store/sidebar'

const route = useRoute()

const navItems = [
  { name: 'customers', label: 'Khách hàng', icon: Users },
  { name: 'company-products', label: 'Sản phẩm', icon: Package },
  { name: 'lab-chemicals', label: 'Hóa chất', icon: FlaskConical },
  { name: 'chemical-orders', label: 'Đơn hàng', icon: ClipboardList },
]
</script>

<template>
  <nav class="sm:hidden fixed left-1/2 -translate-x-1/2 bottom-3 w-[calc(100%-24px)] max-w-md bg-white/90 dark:bg-slate-800/90 backdrop-blur-xl border border-slate-100 dark:border-slate-700 rounded-[22px] shadow-xl flex items-stretch justify-between px-2 py-2 z-40">
    <RouterLink
      v-for="item in navItems"
      :key="item.name"
      :to="{ name: item.name }"
      class="flex-1 flex flex-col items-center gap-1 py-1 px-1 rounded-2xl min-w-0"
      :class="route.name === item.name ? 'text-slate-800 dark:text-slate-100' : 'text-slate-400 dark:text-slate-500'"
    >
      <span
        class="w-8 h-[26px] rounded-[10px] flex items-center justify-center"
        :class="route.name === item.name ? 'bg-brand-gradient text-white' : ''"
      >
        <component :is="item.icon" class="w-4 h-4" />
      </span>
      <span class="text-[10px] font-semibold truncate max-w-full">{{ item.label }}</span>
    </RouterLink>

    <button
      class="flex-1 flex flex-col items-center gap-1 py-1 px-1 rounded-2xl min-w-0 text-slate-400 dark:text-slate-500"
      @click="sidebarOpen = true"
    >
      <span class="w-8 h-[26px] rounded-[10px] flex items-center justify-center">
        <MoreHorizontal class="w-4 h-4" />
      </span>
      <span class="text-[10px] font-semibold">Thêm</span>
    </button>
  </nav>
</template>
