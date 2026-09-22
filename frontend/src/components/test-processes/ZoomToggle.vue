<script setup>
import { computed } from 'vue'
import { Minus, Plus } from 'lucide-vue-next'
import { ZOOM_LEVELS, DEFAULT_ZOOM, stepZoom } from '../../constants/testProcess'

// Nút - / + chỉnh mức hiển thị tờ in ở chân khung xem trước.
const props = defineProps({ modelValue: { type: Number, default: DEFAULT_ZOOM } })
const emit = defineEmits(['update:modelValue'])

const atMin = computed(() => props.modelValue <= ZOOM_LEVELS[0])
const atMax = computed(() => props.modelValue >= ZOOM_LEVELS[ZOOM_LEVELS.length - 1])

function step(direction) {
  const next = stepZoom(props.modelValue, direction)
  if (next !== props.modelValue) emit('update:modelValue', next)
}
</script>

<template>
  <div class="flex items-center gap-0.5 p-0.5 rounded-[9px] bg-lt-paper dark:bg-slate-700">
    <button
      type="button"
      class="flex items-center justify-center w-[22px] h-[22px] rounded-[7px] text-lt-body dark:text-slate-200
             enabled:hover:bg-white dark:enabled:hover:bg-slate-800 disabled:opacity-40"
      aria-label="Thu nhỏ"
      :disabled="atMin"
      @click="step(-1)"
    >
      <Minus class="w-3.5 h-3.5" />
    </button>

    <span class="w-[42px] text-center text-[11.5px] font-semibold tabular-nums text-lt-tealink dark:text-slate-100">
      {{ modelValue }}%
    </span>

    <button
      type="button"
      class="flex items-center justify-center w-[22px] h-[22px] rounded-[7px] text-lt-body dark:text-slate-200
             enabled:hover:bg-white dark:enabled:hover:bg-slate-800 disabled:opacity-40"
      aria-label="Phóng to"
      :disabled="atMax"
      @click="step(1)"
    >
      <Plus class="w-3.5 h-3.5" />
    </button>
  </div>
</template>
