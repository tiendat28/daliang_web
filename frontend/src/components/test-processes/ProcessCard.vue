<script setup>
import { computed } from 'vue'
import StatusPill from './StatusPill.vue'
import { formatProcessMeta, takeWithOverflow } from '../../utils/testProcessFormat'

// Một lưu trình trong danh sách. variant="row" cho cột danh sách trên máy tính,
// variant="card" cho thẻ rời trên điện thoại.
const props = defineProps({
  item: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  variant: { type: String, default: 'row' },
})

const MAX_CHIPS = 3

const chips = computed(() => takeWithOverflow(props.item.chemical_names, MAX_CHIPS).items)
// Đếm theo tổng số hóa chất của lưu trình, không phải theo số tên API trả về
const extraCount = computed(() => Math.max(0, (props.item.chemical_count || 0) - chips.value.length))

const meta = computed(() => formatProcessMeta({
  testMonth: props.item.test_month,
  sampleQuantity: props.item.sample_quantity,
  stepCount: props.item.step_count,
}))
</script>

<template>
  <button
    type="button"
    :aria-pressed="selected"
    class="w-full text-left flex flex-col gap-1.5 transition-colors"
    :class="variant === 'row'
      ? ['px-[18px] py-[13px] border-b border-lt-rule dark:border-slate-700',
         selected
           ? 'bg-lt-sel dark:bg-slate-700/60 shadow-[inset_3px_0_0_#0D8FA0]'
           : 'bg-white dark:bg-slate-800 hover:bg-lt-sel/60 dark:hover:bg-slate-700/40']
      : ['p-3.5 rounded-[18px] bg-white dark:bg-slate-800 shadow-lt-soft']"
  >
    <div class="flex items-center justify-between gap-2">
      <span class="text-[12.5px] font-semibold tracking-[0.2px] text-lt-muted dark:text-slate-400">{{ item.code }}</span>
      <StatusPill :value="item.status" />
    </div>

    <span class="text-[15px] font-semibold text-lt-ink dark:text-slate-100 truncate">{{ item.customer_name }}</span>

    <span v-if="item.requirement" class="text-[12.5px] text-lt-muted dark:text-slate-400 truncate">
      {{ item.requirement }}
    </span>

    <span class="text-[12px] text-lt-faint dark:text-slate-500">{{ meta }}</span>

    <div v-if="chips.length" class="flex items-center gap-1.5 mt-0.5 overflow-hidden">
      <span v-for="name in chips" :key="name" class="lt-chip truncate">{{ name }}</span>
      <span v-if="extraCount" class="text-[11.5px] text-lt-faint dark:text-slate-500">+{{ extraCount }}</span>
    </div>
  </button>
</template>
