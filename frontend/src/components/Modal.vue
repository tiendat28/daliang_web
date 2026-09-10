<script setup>
const props = defineProps({ show: Boolean, title: String, size: { type: String, default: 'md' } })
const emit = defineEmits(['close'])

const sizeClass = props.size === 'lg' ? 'max-w-4xl' : 'max-w-2xl'
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 bg-slate-900/30 backdrop-blur-sm flex items-center justify-center z-50 p-4 print:static print:bg-white print:backdrop-blur-none print:p-0 print:block">
      <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-xl w-full max-h-[85vh] overflow-y-auto p-6 print:max-w-none print:max-h-none print:overflow-visible print:static print:shadow-none print:rounded-none print:p-0 print:bg-white" :class="sizeClass">
        <div class="flex items-center justify-between mb-4 print:hidden">
          <h3 class="font-semibold text-lg text-slate-800 dark:text-slate-100">{{ title }}</h3>
          <button class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200" @click="emit('close')">✕</button>
        </div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>
