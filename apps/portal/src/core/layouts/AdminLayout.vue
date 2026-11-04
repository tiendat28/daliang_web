<script setup>
import { useRoute } from 'vue-router'
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'
import HorizontalTabs from './HorizontalTabs.vue'

// Khung cong noi bo (ban thiet ke Admin): thanh ben co dinh ben trai, noi dung
// ben phai. Topbar va HorizontalTabs luon hien thi o dau vung noi dung.
const route = useRoute()
</script>

<template>
  <div class="relative flex h-screen supports-[height:100dvh]:h-[100dvh] overflow-hidden bg-slate-100/70 dark:bg-[#070c16]">
    <Sidebar />
    <main class="flex-1 min-w-0 flex flex-col overflow-hidden">
      <div class="shrink-0">
        <Topbar v-if="!route.meta.hideTopbar || route.meta.documentTopbar" />
      </div>
      <HorizontalTabs />
      <div
        class="flex-1 min-h-0 flex flex-col"
        :class="route.meta.documentFull ? 'p-0 overflow-hidden' : 'p-3 sm:p-6 lg:p-7 overflow-y-auto'"
      >
        <slot />
      </div>
    </main>
  </div>
</template>
