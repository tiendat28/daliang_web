<!-- Bang "Cai dat" o chan sidebar: phan giao dien dung chung, roi den phan
     rieng cua tung module (settingsSections trong index.js cua module:
     { component, visible() } - visible de an theo quyen). -->
<script setup>
import { computed } from 'vue'
import { Sun, Moon } from 'lucide-vue-next'
import Modal from '@/core/components/Modal.vue'
import { themeStore, setTheme } from '@/core/store/theme'
import { modules } from '@/modules'

defineProps({ show: Boolean })
const emit = defineEmits(['close'])

const sections = computed(() => modules
  .flatMap(module => module.settingsSections || [])
  .filter(section => !section.visible || section.visible())
  .map(section => section.component))

const THEMES = [
  { mode: 'light', label: 'Sáng', icon: Sun },
  { mode: 'dark', label: 'Tối', icon: Moon },
]
</script>

<template>
  <Modal :show="show" title="Cài đặt" @close="emit('close')">
    <div class="space-y-6">
      <section>
        <h4 class="text-sm font-semibold text-slate-600 dark:text-slate-300 mb-2">Giao diện</h4>
        <div class="flex gap-2">
          <button
            v-for="theme in THEMES" :key="theme.mode"
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-colors"
            :class="themeStore.mode === theme.mode
              ? 'bg-brand-gradient text-white border-transparent shadow'
              : 'text-slate-500 dark:text-slate-300 border-slate-200 dark:border-slate-600'"
            @click="setTheme(theme.mode)"
          >
            <component :is="theme.icon" class="w-4 h-4" /> {{ theme.label }}
          </button>
        </div>
      </section>

      <component :is="section" v-for="(section, index) in sections" :key="index" />
    </div>
  </Modal>
</template>
