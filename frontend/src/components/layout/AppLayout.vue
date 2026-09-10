<script setup>
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'
import MobileBottomNav from './MobileBottomNav.vue'
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <Sidebar />
    <main class="flex-1 p-4 flex flex-col overflow-hidden">
      <div class="bg-white/40 dark:bg-slate-800/40 rounded-3xl p-6 flex flex-col flex-1 overflow-hidden">
        <Topbar />
        <div class="flex-1 overflow-y-auto pb-24 sm:pb-6">
          <slot />
        </div>
      </div>
    </main>
    <MobileBottomNav />
  </div>
</template>
