<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: true,
  },
  title: String,
  size: {
    type: String,
    default: 'md',
  },
  fullscreen: Boolean,
})
const emit = defineEmits(['close'])

const sizeClass = computed(() => {
  if (props.fullscreen) return 'max-w-none h-full max-h-none rounded-none p-0'
  if (props.size === 'lg') return 'max-w-4xl'
  if (props.size === 'xl') return 'max-w-6xl'
  if (props.size === 'sm') return 'max-w-md'
  return 'max-w-2xl'
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[9999] p-2.5 sm:p-4 print:static print:bg-white print:backdrop-blur-none print:p-0 print:block"
      :class="fullscreen ? 'p-0' : ''"
      @click.self="emit('close')"
    >
      <div
        class="bg-white dark:bg-slate-800 rounded-2xl md:rounded-3xl shadow-2xl w-full max-h-[90vh] overflow-y-auto p-4 sm:p-5 md:p-6 print:max-w-none print:max-h-none print:overflow-visible print:static print:shadow-none print:rounded-none print:p-0 print:bg-white border border-slate-200 dark:border-slate-700"
        :class="sizeClass"
      >
        <div v-if="!fullscreen" class="flex items-center justify-between gap-2 mb-3.5 sm:mb-4 pb-3 border-b border-slate-100 dark:border-slate-700/60 print:hidden">
          <h3 class="font-bold text-base sm:text-lg text-slate-800 dark:text-slate-100 leading-snug">{{ title }}</h3>
          <button
            type="button"
            class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700/60 transition-colors text-base font-bold leading-none shrink-0"
            @click="emit('close')"
          >
            ✕
          </button>
        </div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>
