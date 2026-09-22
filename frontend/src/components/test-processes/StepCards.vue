<script setup>
// Chế độ "Từng bước" — dễ đọc trên điện thoại hơn tờ A4 thu nhỏ.
// Chữ lấy từ step.display do backend dựng sẵn nên khớp với tờ in.
import { renderMarkers } from '../../utils/testProcessFormat'

defineProps({ steps: { type: Array, default: () => [] } })

function rows(step) {
  const display = step.display || {}
  return [
    { label: 'Thời gian', values: display.time ? [display.time] : [] },
    { label: 'Nhiệt độ', values: display.temperature ? [display.temperature] : [] },
    { label: 'pH', values: display.ph ? [display.ph] : [] },
    { label: 'Nồng độ', values: display.concentrations || [] },
  ].filter(row => row.values.length)
}

function chemicals(step) {
  return step.display?.chemicals || []
}
</script>

<template>
  <div class="flex flex-col gap-2.5">
    <div
      v-for="(step, index) in steps"
      :key="step.id ?? index"
      class="flex flex-col gap-2.5 p-3.5 rounded-[18px] bg-white dark:bg-slate-800 shadow-lt-raise"
    >
      <div class="flex items-center gap-2.5">
        <span class="flex items-center justify-center w-6 h-6 rounded-lg bg-lt-step dark:bg-slate-700 text-[12px] font-semibold text-lt-label dark:text-slate-300">
          {{ index + 1 }}
        </span>
        <span class="text-[15px] font-semibold text-lt-ink dark:text-slate-100" v-html="step.display?.operation || renderMarkers(step.operation)" />
      </div>

      <template v-if="rows(step).length || chemicals(step).length">
        <div class="h-px bg-lt-divider dark:bg-slate-700" />

        <div v-for="row in rows(step)" :key="row.label" class="flex gap-3">
          <span class="w-[74px] shrink-0 text-[12.5px] text-lt-muted dark:text-slate-400">{{ row.label }}</span>
          <div class="flex flex-col gap-0.5 min-w-0">
            <span
              v-for="(value, i) in row.values"
              :key="i"
              class="text-[13.5px] font-medium text-lt-ink dark:text-slate-100"
              v-html="value"
            />
          </div>
        </div>

        <div v-if="chemicals(step).length" class="flex gap-3">
          <span class="w-[74px] shrink-0 pt-0.5 text-[12.5px] text-lt-muted dark:text-slate-400">Hóa chất</span>
          <div class="flex flex-wrap gap-1.5 min-w-0">
            <span v-for="(name, i) in chemicals(step)" :key="i" class="lt-chip" v-html="name" />
          </div>
        </div>
      </template>

      <span v-else class="pl-[34px] text-[12.5px] text-lt-faint dark:text-slate-500">Chưa có thông số</span>
    </div>
  </div>
</template>
