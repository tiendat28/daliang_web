<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Search, Bell, Menu } from 'lucide-vue-next'
import { productSearch } from '../../store/productSearch'
import { sidebarOpen } from '../../store/sidebar'

const route = useRoute()
const searchOpen = ref(false)
const searchable = ['customers', 'company-products', 'lab-chemicals', 'equipment', 'chemical-orders', 'chemical-sampling', 'analysis-reports', 'work-log', 'documents']

function toggleSearch() {
  if (!searchable.includes(route.name)) return
  searchOpen.value = !searchOpen.value
  if (!searchOpen.value) productSearch.query = ''
}

watch(() => route.name, () => {
  searchOpen.value = false
  productSearch.query = ''
})
</script>

<template>
  <div class="flex items-center justify-between mb-6 shrink-0 gap-3">
    <div class="flex items-center gap-3 min-w-0">
      <button
        class="w-10 h-10 shrink-0 rounded-full bg-white dark:bg-slate-700 flex items-center justify-center shadow-sm md:hidden"
        @click="sidebarOpen = true"
      >
        <Menu class="w-4 h-4 text-slate-500 dark:text-slate-300" />
      </button>
      <div class="min-w-0">
        <p class="text-brand-600 dark:text-brand-400 font-medium text-sm mb-1 hidden sm:block">Chào mừng trở lại 👋</p>
        <h1 class="text-xl sm:text-3xl font-bold text-slate-800 dark:text-slate-100 truncate">{{ route.meta.title || 'Dashboard' }}</h1>
      </div>
    </div>
    <div class="flex items-center gap-2 sm:gap-4 shrink-0">
      <input
        v-if="searchOpen"
        v-model="productSearch.query"
        type="text"
        placeholder="Tìm theo mã, tên, lĩnh vực..."
        class="w-32 sm:w-64 rounded-full border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-4 py-2 text-sm text-slate-700 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-400"
        autofocus
      />
      <button
        class="w-10 h-10 rounded-full bg-white dark:bg-slate-700 flex items-center justify-center shadow-sm"
        :class="searchable.includes(route.name) ? 'text-brand-600' : ''"
        @click="toggleSearch"
      >
        <Search class="w-4 h-4" :class="searchOpen ? 'text-brand-600' : 'text-slate-500 dark:text-slate-300'" />
      </button>
      <button class="w-10 h-10 rounded-full bg-white dark:bg-slate-700 flex items-center justify-center shadow-sm">
        <Bell class="w-4 h-4 text-slate-500 dark:text-slate-300" />
      </button>
      <div class="w-10 h-10 rounded-full bg-brand-gradient flex items-center justify-center text-white font-semibold text-sm">
        DL
      </div>
    </div>
  </div>
</template>
