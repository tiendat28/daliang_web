<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  Users, Package, FlaskConical, Wrench, ClipboardList, TestTubes, Boxes, Settings,
  FileBarChart2, NotebookPen, FileText, ListChecks,
} from 'lucide-vue-next'
import SettingsPanel from './SettingsPanel.vue'
import { sidebarOpen } from '../../store/sidebar'

const route = useRoute()
const showSettings = ref(false)

// Chia 2 nhóm: "Dữ liệu" là các danh mục tra cứu, "Nghiệp vụ" là việc làm hằng ngày
const navGroups = [
  {
    label: 'Dữ liệu',
    items: [
      { name: 'customers', label: 'Khách hàng', icon: Users },
      { name: 'company-products', label: 'Sản phẩm công ty', icon: Package },
      { name: 'lab-chemicals', label: 'Hóa chất', icon: FlaskConical },
      { name: 'equipment', label: 'Thiết bị', icon: Wrench },
      { name: 'documents', label: 'Tài liệu', icon: FileText },
      { name: 'work-log', label: 'Nhật ký công tác', icon: NotebookPen },
    ],
  },
  {
    label: 'Nghiệp vụ',
    items: [
      { name: 'chemical-orders', label: 'Đơn hàng HCTN', icon: ClipboardList },
      { name: 'chemical-sampling', label: 'Lấy mẫu HC', icon: TestTubes },
      {
        name: 'test-processes',
        label: 'Lưu trình test mẫu',
        icon: ListChecks,
        // Cả module dùng chung một mục; mở mục con khi đang ở trong module.
        // Route nào thuộc mục nào do meta.nav/meta.navChild bên router quyết định.
        nav: 'test-processes',
        children: [
          { key: 'list', name: 'test-processes', label: 'Danh sách' },
          { key: 'templates', name: 'process-templates', label: 'Quy trình chuẩn' },
        ],
      },
      { name: 'analysis-reports', label: 'Báo cáo phân tích', icon: FileBarChart2 },
    ],
  },
]

// Mục gộp nhiều trang (Lưu trình test mẫu) sáng theo meta.nav của route đang mở,
// mục thường thì so tên route — khỏi phải giữ thêm một danh sách tên route ở đây.
function isActive(item) {
  return item.nav ? route.meta.nav === item.nav : route.name === item.name
}

function isChildActive(child) {
  return route.meta.navChild === child.key
}
</script>

<template>
  <div
    v-if="sidebarOpen"
    class="fixed inset-0 bg-black/40 z-40 md:hidden"
    @click="sidebarOpen = false"
  />

  <aside
    class="w-64 shrink-0 bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-3xl p-5 flex flex-col gap-1 shadow-sm transition-transform duration-300 fixed inset-y-4 left-4 z-50 md:static md:inset-auto md:m-4 md:mr-0 md:h-[calc(100vh-2rem)] md:translate-x-0 overflow-y-auto"
    :class="sidebarOpen ? 'translate-x-0' : '-translate-x-[150%]'"
  >
    <RouterLink to="/" class="flex items-center gap-2 px-2 pb-6">
      <div class="w-9 h-9 rounded-xl bg-brand-gradient flex items-center justify-center">
        <Boxes class="w-5 h-5 text-white" />
      </div>
      <span class="font-bold text-lg text-slate-800 dark:text-slate-100">Daliang VN</span>
    </RouterLink>

    <div v-for="group in navGroups" :key="group.label" class="flex flex-col gap-1">
      <span class="px-4 pt-2 pb-1 text-[11.5px] font-semibold text-slate-400 dark:text-slate-500">
        {{ group.label }}
      </span>

      <template v-for="item in group.items" :key="item.name">
        <RouterLink
          :to="{ name: item.name }"
          class="flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-colors"
          :class="isActive(item)
            ? 'bg-brand-gradient text-white shadow'
            : 'text-slate-500 dark:text-slate-300 hover:bg-brand-50 dark:hover:bg-slate-700 hover:text-brand-700 dark:hover:text-brand-300'"
          @click="sidebarOpen = false"
        >
          <component :is="item.icon" class="w-4 h-4" />
          {{ item.label }}
        </RouterLink>

        <div v-if="item.children && isActive(item)" class="flex flex-col gap-0.5 pl-7 py-1">
          <RouterLink
            v-for="child in item.children"
            :key="child.key"
            :to="{ name: child.name }"
            class="px-3 py-1.5 rounded-xl text-[13px] transition-colors"
            :class="isChildActive(child)
              ? 'font-semibold text-brand-700 dark:text-brand-300 bg-brand-50 dark:bg-slate-700'
              : 'font-medium text-slate-500 dark:text-slate-400 hover:text-brand-700 dark:hover:text-brand-300'"
            @click="sidebarOpen = false"
          >
            {{ child.label }}
          </RouterLink>
        </div>
      </template>
    </div>

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
