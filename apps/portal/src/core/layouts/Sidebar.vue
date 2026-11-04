<!-- Thanh ben cua cong noi bo (ban thiet ke nang cap UI/UX):
     Mau nen #111827, accent #14b8a6, text #2dd4bf.
     Hien thi co dinh ben canh tren Desktop (lg:static, khong an),
     Dang ngan keo truot tren Mobile (< lg). -->
<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  House, Settings, X, ChevronDown,
} from 'lucide-vue-next'
import SettingsPanel from './SettingsPanel.vue'
import { sidebarOpen } from '@/core/store/sidebar'
import { getItemRoute, isItemActive, visibleMenus } from '@/modules'

const route = useRoute()
const showSettings = ref(false)

// Luu trang thai mo/dong thu cong cua cac bo phan (Accordion)
const moduleExpanded = ref({})

const menus = computed(() => visibleMenus())

// Hien thi ca Bo phan va Quan tri he thong truc tiep tren Sidebar
const SECTIONS = [
  { key: 'departments', label: 'Bộ phận' },
  { key: 'system', label: 'Hệ thống' },
]

const sections = computed(() => SECTIONS
  .map(section => ({
    ...section,
    menus: menus.value
      .filter(m => m.section === section.key)
      .map(menu => ({
        ...menu,
        items: menu.items.filter(item => !['lab-customers', 'lab-products'].includes(item.name)),
      }))
      .filter(menu => menu.items.length),
  }))
  .filter(section => section.menus.length || section.key === 'system'))

const overviewItems = computed(() => menus.value
  .flatMap(menu => menu.items)
  .filter(item => ['lab-customers', 'lab-products'].includes(item.name)))

const hasActiveChild = menu => menu.items.some(item => isItemActive(item, route))

function isModuleOpen(menu) {
  if (moduleExpanded.value[menu.label] !== undefined) {
    return moduleExpanded.value[menu.label]
  }
  return hasActiveChild(menu)
}

function toggleModule(menu, e) {
  if (e) {
    e.preventDefault()
    e.stopPropagation()
  }
  moduleExpanded.value[menu.label] = !isModuleOpen(menu)
}

// Dong sidebar chi tren thiet bi di dong (< lg)
const close = () => {
  sidebarOpen.value = false
}

function onNavClick() {
  if (typeof window !== 'undefined' && window.innerWidth < 1024) {
    close()
  }
}

function onKeyDown(e) {
  if (e.key === 'Escape' && sidebarOpen.value && window.innerWidth < 1024) {
    close()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})
</script>

<template>
  <!-- Lop phu mo (Backdrop) chi hien tren Mobile (< lg) khi sidebar mo -->
  <Transition
    enter-active-class="transition-opacity duration-300 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-200 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-40 lg:hidden"
      @click="close"
    />
  </Transition>

  <!-- Sidebar: Co dinh ben trai tren Desktop (lg:static, lg:translate-x-0), truot ra tren Mobile (fixed, z-50) -->
  <nav
    aria-label="Menu chính"
    class="fixed inset-y-0 left-0 z-50 w-[275px] h-screen bg-white dark:bg-[#0c1424] text-slate-700 dark:text-slate-300 px-4 py-5 flex flex-col justify-between gap-3
           border-r border-slate-200/90 dark:border-slate-800/80 transition-transform duration-300 ease-in-out overflow-hidden shrink-0
           lg:static lg:translate-x-0 lg:z-30 lg:shadow-none"
    :class="sidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'"
  >
    <!-- Vung cuon noi dung Menu -->
    <div class="flex flex-col gap-0.5 min-h-0 overflow-y-auto no-scrollbar pr-0.5">
      <!-- Header / Logo -->
      <div class="flex items-center justify-between pb-3.5 mb-2 border-b border-slate-200/80 dark:border-slate-800/80 shrink-0">
        <RouterLink :to="{ name: 'home' }" class="flex items-center gap-2.5 px-0.5 group" @click="onNavClick">
          <span class="w-11 h-11 rounded-xl bg-white inline-flex items-center justify-center shrink-0 overflow-hidden shadow-xs border border-slate-200 dark:border-slate-700/60 group-hover:scale-105 transition-transform">
            <img src="/images/logo-dlvc.png" alt="DALIANG" class="w-full h-full object-contain" />
          </span>
          <span class="flex flex-col leading-[1.15]">
            <span class="text-[14px] font-bold tracking-[0.05em] text-slate-900 dark:text-white">DALIANG</span>
            <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400">Hoá chất xi mạ</span>
          </span>
        </RouterLink>
        <!-- Nut dong chi hien tren Mobile (< lg) -->
        <button
          type="button"
          class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors lg:hidden"
          title="Đóng thanh điều hướng"
          aria-label="Đóng thanh điều hướng"
          @click="close"
        >
          <X class="w-5 h-5" :stroke-width="1.8" />
        </button>
      </div>

      <!-- Tong quan -->
      <div class="nav-section">Tổng quan</div>
      <RouterLink
        :to="{ name: 'home' }"
        class="nav-item group"
        :class="route.name === 'home' ? 'nav-item-active' : ''"
        @click="onNavClick"
      >
        <House
          class="w-[18px] h-[18px] shrink-0"
          :class="route.name === 'home' ? 'text-teal-600 dark:text-[#2dd4bf]' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200'"
          :stroke-width="1.8"
        />
        <span class="truncate">Trang chủ</span>
      </RouterLink>

      <RouterLink
        v-for="item in overviewItems"
        :key="item.name"
        :to="getItemRoute(item)"
        class="nav-item group"
        :class="isItemActive(item, route) ? 'nav-item-active' : ''"
        @click="onNavClick"
      >
        <component
          :is="item.icon"
          class="w-[18px] h-[18px] shrink-0"
          :class="isItemActive(item, route) ? 'text-teal-600 dark:text-[#2dd4bf]' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200'"
          :stroke-width="1.8"
        />
        <span class="truncate">{{ item.label }}</span>
      </RouterLink>

      <!-- Cac bo phan & He thong -->
      <template v-for="section in sections" :key="section.key">
        <div class="nav-section">{{ section.label }}</div>
        <template v-for="menu in section.menus" :key="menu.label">
          <!-- Parent item: Khi co muc con active, chi sang chu/icon #2dd4bf, khong to nen xanh -->
          <div class="relative flex items-center">
            <RouterLink
              :to="getItemRoute(menu.items[0])"
              class="nav-item group flex-1 pr-9"
              :class="hasActiveChild(menu) ? 'nav-item-parent-active' : ''"
              @click="onNavClick"
            >
              <component
                :is="menu.icon"
                class="w-[18px] h-[18px] shrink-0"
                :class="hasActiveChild(menu) ? 'text-teal-600 dark:text-[#2dd4bf]' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200'"
                :stroke-width="1.8"
              />
              <span class="flex-1 truncate">{{ menu.label }}</span>
            </RouterLink>

            <!-- Nut chevron click de dong/mo rieng bo phan -->
            <button
              type="button"
              class="absolute right-1.5 w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
              :title="isModuleOpen(menu) ? 'Thu gọn' : 'Mở rộng'"
              @click="toggleModule(menu, $event)"
            >
              <ChevronDown
                class="w-4 h-4 transition-transform duration-200 shrink-0"
                :class="isModuleOpen(menu) ? 'rotate-180 text-teal-600 dark:text-[#2dd4bf]' : 'text-slate-400 dark:text-slate-500'"
              />
            </button>
          </div>

          <!-- Tree line phan cap cac muc con -->
          <template v-if="isModuleOpen(menu)">
            <div class="nav-tree">
              <RouterLink
                v-for="item in menu.items"
                :key="item.name"
                :to="getItemRoute(item)"
                class="nav-child"
                :class="isItemActive(item, route) ? 'nav-child-active' : ''"
                @click="onNavClick"
              >
                <component
                  :is="item.icon"
                  class="w-4 h-4 shrink-0"
                  :class="isItemActive(item, route) ? 'text-teal-600 dark:text-[#2dd4bf]' : 'text-slate-400 dark:text-slate-500'"
                />
                <span class="truncate">{{ item.label }}</span>
              </RouterLink>
            </div>
          </template>
        </template>

        <!-- Muc Cai dat (Xuat du lieu & Sao luu) trong nhom He thong -->
        <button
          v-if="section.key === 'system'"
          type="button"
          class="nav-item group w-full text-left"
          :class="showSettings ? 'nav-item-active' : ''"
          @click="showSettings = true; onNavClick();"
        >
          <Settings
            class="w-[18px] h-[18px] shrink-0"
            :class="showSettings ? 'text-teal-600 dark:text-[#2dd4bf]' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200'"
            :stroke-width="1.8"
          />
          <span class="truncate">Cài đặt</span>
        </button>
      </template>
    </div>

    <SettingsPanel :show="showSettings" @close="showSettings = false" />
  </nav>
</template>

<style scoped>
.nav-section {
  @apply text-[11px] font-bold tracking-[0.08em] uppercase text-slate-400 dark:text-slate-500 px-3.5 pt-3.5 pb-1.5;
}

.nav-item {
  @apply flex items-center gap-3 h-10 px-3.5 rounded-[12px] text-sm font-medium text-slate-600 dark:text-slate-300
         hover:bg-slate-100 dark:hover:bg-white/[0.05] hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer border-l-2 border-transparent;
}

/* Parent khi co muc con active: Chi sang chu/icon teal, khong to nen xanh */
.nav-item-parent-active {
  color: #0d9488 !important;
  background-color: transparent !important;
  font-weight: 600;
}
:root.dark .nav-item-parent-active,
.dark .nav-item-parent-active {
  color: #2dd4bf !important;
}

/* Item doc lap o Tong quan khi active */
.nav-item-active {
  background-color: rgba(20, 184, 166, 0.12) !important;
  color: #0d9488 !important;
  font-weight: 600;
  border-left-color: #0d9488 !important;
}
:root.dark .nav-item-active,
.dark .nav-item-active {
  background-color: rgba(20, 184, 166, 0.16) !important;
  color: #2dd4bf !important;
  border-left-color: #14b8a6 !important;
}

/* Duong ke doc phan cap (Tree line) */
.nav-tree {
  margin-left: 22px;
  padding-left: 14px;
  border-left: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 3px;
  margin-bottom: 5px;
}
:root.dark .nav-tree,
.dark .nav-tree {
  border-left-color: #1e293b;
}

.nav-child {
  @apply flex items-center gap-2.5 h-[34px] px-2.5 rounded-[8px] text-[13px] font-medium text-slate-500 dark:text-slate-400
         hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-white/[0.05] transition-colors border-l-2 border-transparent;
}

/* Chi muc con dang chon moi co nen teal nhat, chu teal va vach chi bao */
.nav-child-active {
  background-color: rgba(20, 184, 166, 0.12) !important;
  color: #0d9488 !important;
  font-weight: 600;
  border-left-color: #0d9488 !important;
}
:root.dark .nav-child-active,
.dark .nav-child-active {
  background-color: rgba(20, 184, 166, 0.16) !important;
  color: #2dd4bf !important;
  border-left-color: #14b8a6 !important;
}

.nav-icon-btn {
  @apply w-8 h-8 shrink-0 inline-flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400
         hover:text-teal-600 dark:hover:text-[#2dd4bf] hover:bg-slate-200/60 dark:hover:bg-white/10 transition-colors;
}

/* An scrollbar cho phan danh sach menu */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
