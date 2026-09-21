<script setup>
import { ref, computed, watch } from 'vue'
import { X, Search, Check, Loader2 } from 'lucide-vue-next'
import { processTemplatesApi } from '../../api/resources'
import { foldAccents } from '../../utils/testProcessFormat'

// Hộp thoại "Chèn từ quy trình chuẩn". Trả về các bước của quy trình được chọn,
// việc chèn hay thay do view cha làm.
const props = defineProps({
  show: { type: Boolean, default: false },
  currentStepCount: { type: Number, default: 0 },
})

const emit = defineEmits(['close', 'insert', 'replace'])

const templates = ref([])
const loading = ref(false)
const query = ref('')
const selectedId = ref(null)

watch(() => props.show, async (open) => {
  if (!open) return
  query.value = ''
  selectedId.value = null
  loading.value = true
  try {
    templates.value = await processTemplatesApi.list()
    selectedId.value = templates.value[0]?.id ?? null
  } finally {
    loading.value = false
  }
})

const matches = computed(() => {
  const needle = foldAccents(query.value).trim().toLowerCase()
  if (!needle) return templates.value
  return templates.value.filter(template =>
    foldAccents(`${template.name} ${template.description || ''} ${(template.operations || []).join(' ')}`)
      .toLowerCase().includes(needle))
})

const selected = computed(() => templates.value.find(template => template.id === selectedId.value) || null)

function summary(template) {
  const names = (template.operations || []).filter(Boolean)
  const shown = names.slice(0, 6).join(', ')
  return `${template.step_count} bước · ${shown}${names.length > 6 ? '…' : ''}`
}

function send(event) {
  if (!selected.value) return
  emit(event, selected.value.steps || [])
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="font-lt fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/30 backdrop-blur-sm" @click.self="emit('close')">
      <div class="flex flex-col w-full max-w-[620px] max-h-[85vh] rounded-[20px] bg-white dark:bg-slate-800 shadow-lt-dialog overflow-hidden">
        <div class="flex items-start justify-between px-5 pt-[18px] pb-3.5">
          <div class="flex flex-col gap-0.5">
            <h2 class="text-base font-semibold text-lt-ink dark:text-slate-100">Chèn từ quy trình chuẩn</h2>
            <span class="text-[12.5px] text-lt-muted dark:text-slate-400">
              Lưu trình đang có {{ currentStepCount }} bước.
            </span>
          </div>
          <button
            type="button"
            class="w-8 h-8 flex items-center justify-center rounded-[10px] bg-lt-paper dark:bg-slate-700 text-lt-label dark:text-slate-300"
            aria-label="Đóng"
            @click="emit('close')"
          >
            <X class="w-4 h-4" />
          </button>
        </div>

        <div class="px-5 pb-3">
          <div class="flex items-center gap-2 h-10 px-3 rounded-[11px] border border-lt-line dark:border-slate-600">
            <Search class="w-4 h-4 text-lt-muted shrink-0" />
            <input
              v-model="query"
              type="search"
              placeholder="Tìm quy trình chuẩn…"
              aria-label="Tìm quy trình chuẩn"
              class="flex-1 min-w-0 bg-transparent border-none outline-none text-[13.5px] text-lt-ink dark:text-slate-100"
            />
          </div>
        </div>

        <div class="flex-1 min-h-0 overflow-y-auto px-5 flex flex-col gap-2">
          <div v-if="loading" class="flex items-center justify-center gap-2 py-10 text-[13px] text-lt-faint">
            <Loader2 class="w-4 h-4 animate-spin" />Đang tải…
          </div>

          <p v-else-if="!matches.length" class="py-10 text-center text-[13px] text-lt-faint dark:text-slate-500">
            Chưa có quy trình chuẩn nào khớp. Tạo ở trang “Quy trình chuẩn”, hoặc lưu từ
            một lưu trình đã nhập.
          </p>

          <button
            v-for="template in matches"
            :key="template.id"
            type="button"
            :aria-pressed="template.id === selectedId"
            class="flex items-start gap-3 w-full p-3.5 rounded-[13px] border text-left"
            :class="template.id === selectedId
              ? 'border-lt-selline bg-lt-sel dark:bg-slate-700 dark:border-slate-500'
              : 'border-lt-edge dark:border-slate-600 bg-white dark:bg-slate-800'"
            @click="selectedId = template.id"
          >
            <span
              class="flex items-center justify-center w-5 h-5 mt-0.5 rounded-full shrink-0"
              :class="template.id === selectedId ? 'bg-lt-gradient' : 'border-[1.5px] border-[#D3E0DD] dark:border-slate-500'"
            >
              <Check v-if="template.id === selectedId" class="w-3 h-3 text-white" />
            </span>
            <span class="flex flex-col gap-1 min-w-0">
              <span class="text-sm font-semibold text-lt-ink dark:text-slate-100">{{ template.name }}</span>
              <span class="text-[12.5px] text-lt-muted dark:text-slate-400">{{ summary(template) }}</span>
            </span>
          </button>
        </div>

        <div class="flex flex-wrap items-center gap-2.5 px-5 pt-3.5 pb-[18px] mt-3 border-t border-lt-divider dark:border-slate-700">
          <span class="flex-1 min-w-[160px] text-[12px] leading-[1.4] text-lt-muted dark:text-slate-400">
            <template v-if="currentStepCount">Thay toàn bộ sẽ xóa {{ currentStepCount }} bước bạn đã nhập.</template>
          </span>
          <button
            type="button"
            class="h-[38px] px-4 rounded-[11px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-700 text-[13.5px] font-medium text-lt-body dark:text-slate-200 disabled:opacity-50"
            :disabled="!selected"
            @click="send('replace')"
          >
            Thay toàn bộ các bước
          </button>
          <button
            type="button"
            class="h-[38px] px-[18px] rounded-[11px] bg-lt-gradient text-white text-[13.5px] font-semibold shadow-lt-teal disabled:opacity-50"
            :disabled="!selected"
            @click="send('insert')"
          >
            Chèn vào cuối
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
