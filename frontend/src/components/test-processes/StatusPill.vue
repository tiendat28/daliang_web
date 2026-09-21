<script setup>
import { computed } from 'vue'
import { statusMeta } from '../../constants/testProcess'

// Chip trạng thái. Màu nền và màu chữ đi thành cặp nên đọc được ở cả nền sáng lẫn tối.
const props = defineProps({ value: { type: String, default: 'draft' } })
const meta = computed(() => statusMeta(props.value))
</script>

<template>
  <span class="px-[9px] py-0.5 rounded-full text-[11.5px] font-semibold whitespace-nowrap" :class="meta.chip">
    {{ meta.label }}
  </span>
</template>
