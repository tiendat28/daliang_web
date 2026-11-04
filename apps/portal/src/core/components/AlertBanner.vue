<script setup>
import { Check, X } from 'lucide-vue-next'

defineProps({
  successMsg: {
    type: String,
    default: '',
  },
  error: {
    type: String,
    default: '',
  },
  dismissible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])
</script>

<template>
  <div v-if="successMsg" class="alert-banner alert-success">
    <Check class="w-5 h-5 flex-shrink-0" />
    <span class="flex-1">{{ successMsg }}</span>
    <button
      v-if="dismissible"
      type="button"
      class="text-emerald-700 dark:text-emerald-300 hover:opacity-80 p-0.5"
      @click="emit('close')"
    >
      <X class="w-4 h-4" />
    </button>
  </div>
</template>
