<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  Users, Package, FlaskConical, Wrench, ClipboardList, TestTubes, Boxes, Settings, FileBarChart2, NotebookPen, FileText,
} from 'lucide-vue-next'
import SettingsPanel from './SettingsPanel.vue'
import { sidebarOpen } from '../../store/sidebar'

const route = useRoute()
const showSettings = ref(false)

const navItems = [
  { name: 'customers', label: 'Khách hàng', icon: Users },
  { name: 'company-products', label: 'Sản phẩm công ty', icon: Package },
  { name: 'lab-chemicals', label: 'Hóa chất', icon: FlaskConical },
  { name: 'equipment', label: 'Thiết bị', icon: Wrench },
  { name: 'chemical-orders', label: 'Đơn hàng HCTN', icon: ClipboardList },
  { name: 'chemical-sampling', label: 'Lấy mẫu HC', icon: TestTubes },
  { name: 'analysis-reports', label: 'Báo cáo phân tích', icon: FileBarChart2 },
  { name: 'work-log', label: 'Nhật ký công tác', icon: NotebookPen },
  { name: 'documents', label: 'Tài liệu', icon: FileText },
]
</script>

<template>
  <div
    v-if="sidebarOpen"
    class="fixed inset-0 bg-black/40 z-40 md:hidden"
    @click="sidebarOpen = false"
  />

  <aside
    class="w-64 shrink-0 bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-3xl p-5 flex flex-col gap-1 shadow-sm transition-transform duration-300 fixed inset-y-4 left-4 z-50 md:static md:inset-auto md:m-4 md:mr-0 md:h-[calc(100vh-2rem)] md:translate-x-0"
    :class="sidebarOpen ? 'translate-x-0' : '-translate-x-[150%]'"
  >
    <div class="flex items-center gap-2 px-2 pb-6">
      <div class="w-9 h-9 rounded-xl bg-brand-gradient flex items-center justify-center">
        <Boxes class="w-5 h-5 text-white" />
      </div>
      <span class="font-bold text-lg text-slate-800 dark:text-slate-100">Daliang VN</span>
    </div>

    <RouterLink
      v-for="item in navItems"
      :key="item.name"
      :to="{ name: item.name }"
      class="flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-colors"
      :class="route.name === item.name
        ? 'bg-brand-gradient text-white shadow'
        : 'text-slate-500 dark:text-slate-300 hover:bg-brand-50 dark:hover:bg-slate-700 hover:text-brand-700 dark:hover:text-brand-300'"
      @click="sidebarOpen = false"
    >
      <component :is="item.icon" class="w-4 h-4" />
      {{ item.label }}
    </RouterLink>

    <div class="mt-auto pt-2 border-t border-slate-200 dark:border-slate-700">
      <button
        class="w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-colors text-slate-500 dark:text-slate-300 hover:bg-brand-50 dark:hover:bg-slate-700 hover:text-brand-700 dark:hover:text-brand-300"
        @click="showSettings = true"
      >
        <Settings class="w-4 h-4" />
        Cài đặt
      </button>
    </div>

    <SettingsPanel :show="showSettings" @close="showSettings = false" />
  </aside>
</template>
