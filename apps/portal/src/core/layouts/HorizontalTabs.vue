<script setup>
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { LAB_GROUPS } from '@/modules/lab/routes'
import { canVisit, routeByName } from '@/modules'

const route = useRoute()

const currentGroup = computed(() => {
  return LAB_GROUPS.find(group => {
    return group.tabs.some(tab => {
      return route.name === tab.name || (tab.activeFor || []).includes(route.name)
    })
  })
})

const visibleTabs = computed(() => {
  if (!currentGroup.value) return []
  return currentGroup.value.tabs.filter(tab => {
    return canVisit(routeByName[tab.name]?.meta)
  })
})

function isTabActive(tab) {
  return route.name === tab.name || (tab.activeFor || []).includes(route.name)
}
</script>

<template>
  <div
    v-if="currentGroup && visibleTabs.length > 1"
    class="bg-white/80 dark:bg-[#0c1424]/75 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800/80 px-4 sm:px-6 py-1.5 flex items-center justify-between gap-3 shrink-0 z-10 transition-colors"
  >
    <div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 w-full">
      <span class="text-[11px] font-semibold text-slate-400 dark:text-slate-400 mr-1.5 shrink-0 hidden sm:inline-flex items-center px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800/60">
        {{ currentGroup.label }}
      </span>
      <RouterLink
        v-for="tab in visibleTabs"
        :key="tab.name"
        :to="{ name: tab.name }"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-[13px] font-medium transition-all shrink-0"
        :class="isTabActive(tab)
          ? 'bg-teal-500/15 text-teal-700 dark:text-[#2dd4bf] font-semibold ring-1 ring-teal-500/30 shadow-2xs'
          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/[0.05]'"
      >
        <component
          :is="tab.icon"
          class="w-3.5 h-3.5 shrink-0"
          :class="isTabActive(tab) ? 'text-teal-600 dark:text-[#2dd4bf]' : 'text-slate-400 dark:text-slate-500'"
        />
        <span>{{ tab.label }}</span>
      </RouterLink>
    </div>
  </div>
</template>

