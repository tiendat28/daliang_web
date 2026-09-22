<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Loader2 } from 'lucide-vue-next'
import { PAGE_WIDTH, PAGE_HEIGHT, DEFAULT_ZOOM } from '../../constants/testProcess'

// Khung xem trước tờ A4. HTML do backend dựng (cùng template với bản PDF) nên
// xem thế nào in ra thế ấy; ở đây chỉ lo việc thu nhỏ cho vừa chỗ trống.
// Tờ giấy luôn nền trắng, kể cả khi app đang ở chế độ tối.
const props = defineProps({
  html: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  // Số phần trăm (25…100) hoặc 'width' để co vừa bề ngang (dùng trên điện thoại)
  zoom: { type: [Number, String], default: DEFAULT_ZOOM },
  // false: khung cao theo tờ giấy và để trang cha cuộn (dùng trên điện thoại)
  fill: { type: Boolean, default: true },
  emptyText: { type: String, default: 'Chưa đủ dữ liệu để xem trước' },
})

const box = ref(null)
const boxWidth = ref(0)
let observer = null

onMounted(() => {
  // contentRect đã trừ sẵn phần đệm của khung nên đây là chỗ trống thật cho tờ giấy
  observer = new ResizeObserver(([entry]) => { boxWidth.value = entry.contentRect.width })
  observer.observe(box.value)
})

onBeforeUnmount(() => observer?.disconnect())

const scale = computed(() => {
  if (props.zoom !== 'width') return props.zoom / 100
  if (!boxWidth.value) return DEFAULT_ZOOM / 100
  return Math.min(boxWidth.value / PAGE_WIDTH, 1)
})
</script>

<template>
  <div
    ref="box"
    class="bg-lt-paper dark:bg-slate-900 flex items-start justify-center p-7"
    :class="fill ? 'flex-1 min-h-0 overflow-auto' : ''"
  >
    <div
      v-if="html"
      class="shrink-0 bg-white rounded-[4px] overflow-hidden shadow-lt-sheet"
      :style="{ width: `${PAGE_WIDTH * scale}px`, height: `${PAGE_HEIGHT * scale}px` }"
    >
      <iframe
        :srcdoc="html"
        title="Xem trước tờ in"
        class="border-0 bg-white"
        :style="{
          width: `${PAGE_WIDTH}px`,
          height: `${PAGE_HEIGHT}px`,
          transform: `scale(${scale})`,
          transformOrigin: 'top left',
        }"
      />
    </div>
    <div v-else class="flex items-center gap-2 pt-16 text-[12.5px] text-lt-faint dark:text-slate-400">
      <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
      <span>{{ loading ? 'Đang dựng tờ in…' : emptyText }}</span>
    </div>
  </div>
</template>
