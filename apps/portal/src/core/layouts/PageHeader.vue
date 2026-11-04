<!-- Dau trang chung (ban thiet ke Admin): duong dan dang mono + tieu de ben
     trai; o tim kiem, nut thong bao va nut hanh dong cua trang (slot "actions") ben
     phai. O tim kiem ghi vao pageSearch - cac trang loc bang useSearchedRows. -->
<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell, LogOut, Search, X, Sun, Moon } from 'lucide-vue-next'
import MenuButton from './MenuButton.vue'
import { auth, logout } from '@/core/auth/store'
import { initials } from '@/core/utils/format'
import { pageSearch } from '@/core/store/pageSearch'
import { themeStore, toggleTheme } from '@/core/store/theme'

defineProps({
  title: { type: String, default: '' },
  searchable: { type: Boolean, default: true },
})
const route = useRoute()
const router = useRouter()
const roleName = computed(() => auth.user?.roles?.[0]?.name || '')
const searchExpanded = ref(false)

const departmentLabel = computed(() => {
  if (['home', 'lab-customers', 'lab-products'].includes(route.name)) return 'Tổng quan'
  const path = route.path || ''
  if (path.startsWith('/lab')) return 'Kỹ thuật'
  if (path.startsWith('/hr')) return 'Nhân sự'
  if (path.startsWith('/accounting')) return 'Kế toán'
  if (path.startsWith('/warehouse')) return 'Kho'
  if (path.startsWith('/dispatch')) return 'Điều phối xe'
  if (path.startsWith('/system')) return 'Hệ thống'
  return 'Tổng quan'
})

function onSearchBlur() {
  if (!pageSearch.query) searchExpanded.value = false
}

async function signOut() {
  await logout()
  router.replace({ name: 'login' })
}
</script>

<template>
  <header
    class="flex items-center justify-between gap-3 h-14 sm:h-[58px] px-4 sm:px-6 shrink-0 bg-white/80 dark:bg-[#0c1424]/85 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800/80 sticky top-0 z-20 transition-colors duration-200"
  >
    <div class="flex items-center gap-2.5 min-w-0">
      <MenuButton class="lg:hidden" />
      <RouterLink :to="{ name: 'home' }" class="hidden sm:flex lg:hidden items-center gap-2 pr-3 border-r border-slate-200 dark:border-slate-800 shrink-0">
        <img src="/images/logo-dlvc.png" alt="DALIANG" class="w-12 h-8 object-contain" />
        <span class="text-xs font-bold tracking-[0.05em] text-slate-900 dark:text-white">DALIANG</span>
      </RouterLink>
      
      <!-- Breadcrumb gon nhe, tinh te -->
      <div class="flex items-center gap-1.5 min-w-0 text-xs sm:text-sm">
        <span class="text-slate-400 dark:text-slate-500 font-medium shrink-0 hidden sm:inline">{{ departmentLabel }}</span>
        <span class="text-slate-300 dark:text-slate-700 text-xs hidden sm:inline">/</span>
        <h1 class="m-0 text-sm sm:text-base font-bold text-slate-800 dark:text-slate-100 truncate">
          {{ title || route.meta.title }}
        </h1>
      </div>
    </div>

    <div class="flex items-center gap-1.5 sm:gap-2 min-w-0">
      <!-- O tim kiem trong trang -->
      <div v-if="searchable" class="relative flex items-center">
        <div
          class="flex items-center h-9 rounded-xl border border-slate-200/90 dark:border-slate-700/80 bg-slate-100/70 dark:bg-slate-800/60 transition-all duration-200 focus-within:border-teal-500 focus-within:ring-2 focus-within:ring-teal-500/20"
          :class="searchExpanded || pageSearch.query ? 'w-48 sm:w-64 px-2.5 bg-white dark:bg-[#121c2e]' : 'w-9 justify-center'"
        >
          <button
            type="button"
            class="w-5 h-5 flex items-center justify-center text-slate-400 dark:text-slate-400 hover:text-teal-600 shrink-0"
            title="Tìm kiếm trong trang"
            @click="searchExpanded = !searchExpanded"
          >
            <Search class="w-4 h-4" :stroke-width="1.8" />
          </button>
          <input
            v-if="searchExpanded || pageSearch.query"
            v-model="pageSearch.query"
            type="text"
            placeholder="Tìm kiếm..."
            class="w-full h-8 ml-1.5 bg-transparent text-xs sm:text-sm text-slate-800 dark:text-slate-100 placeholder:text-slate-400 outline-none border-0"
            @focus="searchExpanded = true"
            @blur="onSearchBlur"
          />
          <button
            v-if="pageSearch.query"
            type="button"
            class="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 p-0.5"
            @click="pageSearch.query = ''"
          >
            <X class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <!-- Nut doi nhanh Sang / Toi (1-click) -->
      <button
        type="button"
        aria-label="Chuyển chế độ sáng tối"
        :title="themeStore.mode === 'dark' ? 'Chuyển sang chế độ Sáng' : 'Chuyển sang chế độ Tối'"
        class="w-9 h-9 rounded-xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-[#121c2e] text-slate-600 dark:text-slate-300 hover:text-teal-600 dark:hover:text-[#2dd4bf] hover:border-teal-500/50 transition-all inline-flex items-center justify-center shadow-2xs"
        @click="toggleTheme"
      >
        <Sun v-if="themeStore.mode === 'dark'" class="w-[17px] h-[17px] text-amber-400 hover:rotate-45 transition-transform" :stroke-width="1.8" />
        <Moon v-else class="w-[17px] h-[17px] text-slate-600 hover:-rotate-12 transition-transform" :stroke-width="1.8" />
      </button>

      <!-- Nut thong bao -->
      <button
        type="button"
        aria-label="Thông báo"
        class="w-9 h-9 rounded-xl border border-slate-200/90 dark:border-slate-700/80 bg-white dark:bg-[#121c2e] text-slate-600 dark:text-slate-300 hover:text-teal-600 dark:hover:text-[#2dd4bf] hover:border-teal-500/50 transition-all inline-flex items-center justify-center relative shadow-2xs"
      >
        <Bell class="w-[17px] h-[17px]" :stroke-width="1.8" />
        <span class="absolute top-2 right-2 w-1.5 h-1.5 bg-teal-500 rounded-full"></span>
      </button>

      <!-- The tai khoan nguoi dung -->
      <RouterLink
        :to="{ name: 'profile' }"
        class="hidden md:flex items-center gap-2 pl-1.5 pr-2 py-1 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800/60 transition-colors group"
        title="Tài khoản của tôi"
      >
        <span class="w-7 h-7 rounded-full bg-teal-500/15 text-teal-700 dark:text-[#2dd4bf] ring-1 ring-teal-500/30 inline-flex items-center justify-center text-xs font-bold shrink-0">
          {{ initials(auth.user?.full_name) }}
        </span>
        <span class="flex flex-col leading-tight min-w-0">
          <span class="text-xs font-semibold text-slate-800 dark:text-slate-100 group-hover:text-teal-600 transition-colors truncate max-w-[130px]">
            {{ auth.user?.full_name || auth.user?.email }}
          </span>
          <span class="text-[10px] text-slate-400 truncate">{{ roleName }}</span>
        </span>
      </RouterLink>

      <!-- Nut dang xuat tren Topbar -->
      <button
        type="button"
        aria-label="Đăng xuất"
        title="Đăng xuất"
        class="w-9 h-9 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-slate-800/80 transition-colors inline-flex items-center justify-center"
        @click="signOut"
      >
        <LogOut class="w-[17px] h-[17px]" :stroke-width="1.8" />
      </button>

      <slot name="actions" />
    </div>
  </header>
</template>
