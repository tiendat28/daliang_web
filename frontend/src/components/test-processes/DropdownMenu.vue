<script setup>
import { ref } from 'vue'

// Menu thả xuống: nút bấm ở slot "trigger", các dòng ở slot mặc định.
// Lớp phủ trong suốt phía sau để bấm ra ngoài là đóng.
defineProps({
  align: { type: String, default: 'right' },   // 'right' | 'left'
  width: { type: String, default: 'w-56' },
})

const open = ref(false)

function toggle() {
  open.value = !open.value
}

function close() {
  open.value = false
}

defineExpose({ close })
</script>

<template>
  <div class="relative">
    <slot name="trigger" :toggle="toggle" :open="open" />

    <div v-if="open" class="fixed inset-0 z-10" @click="close" />
    <div
      v-if="open"
      class="absolute top-[38px] z-20 p-1.5 rounded-xl bg-white dark:bg-slate-800 border border-lt-line dark:border-slate-600 shadow-lt-card"
      :class="[align === 'right' ? 'right-0' : 'left-0', width]"
    >
      <slot :close="close" />
    </div>
  </div>
</template>
