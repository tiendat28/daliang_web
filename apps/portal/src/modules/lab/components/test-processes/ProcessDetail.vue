<script setup>
import { ref, computed, watch } from 'vue'
import {
  ArrowLeft, ChevronDown, Pencil, Copy, Download, Printer, MoreHorizontal,
  LayoutTemplate, Building2, Trash2, Loader2, FileText,
} from 'lucide-vue-next'
import StatusPill from '@/modules/lab/components/test-processes/StatusPill.vue'
import SheetFrame from '@/modules/lab/components/test-processes/SheetFrame.vue'
import StepCards from '@/modules/lab/components/test-processes/StepCards.vue'
import DropdownMenu from '@/modules/lab/components/test-processes/DropdownMenu.vue'
import ZoomToggle from '@/modules/lab/components/test-processes/ZoomToggle.vue'
import { STATUSES, statusMeta, DEFAULT_ZOOM } from '@/modules/lab/constants/testProcess'
import { formatProcessMeta } from '@/modules/lab/utils/testProcessFormat'
import { toMonthInput } from '@/modules/lab/utils/testProcessFormat'
import { stepPayload } from '@/modules/lab/utils/testProcessPayload'
import { formatDateTime } from '@/core/utils/format'
import { usePageCan } from '@/core/auth/store'

// An nut them/sua/xoa khi khong co quyen sua (meta.permission cua trang)
const can = usePageCan()

// Khung chi tiết một lưu trình. Trên máy tính là cột bên phải của màn hình danh
// sách; trên điện thoại là cả một trang (có nút quay lại và thanh nút dưới).
const props = defineProps({
  process: { type: Object, default: null },
  sheetHtml: { type: String, default: '' },
  sheetLoading: { type: Boolean, default: false },
  busy: { type: Boolean, default: false },
  infoSaving: { type: Boolean, default: false },
  infoError: { type: String, default: '' },
})

const emit = defineEmits([
  'back', 'edit', 'duplicate', 'remove', 'status', 'save-template', 'letterhead', 'download', 'print', 'save-info',
])

const zoom = ref(DEFAULT_ZOOM)
const mobileTab = ref('sheet')   // 'sheet' | 'steps'
const infoForm = ref({ customer_name: '', requirement: '', sample_quantity: 1, test_month: '', prepared_by: '' })

watch(() => props.process?.id, () => {
  mobileTab.value = 'sheet'
  if (props.process) {
    infoForm.value = {
      customer_name: props.process.customer_name || '',
      requirement: props.process.requirement || '',
      sample_quantity: props.process.sample_quantity || 1,
      test_month: toMonthInput(props.process.test_month) || '',
      prepared_by: props.process.prepared_by || '',
    }
  }
}, { immediate: true })

const meta = computed(() => (props.process ? formatProcessMeta({
  testMonth: props.process.test_month,
  sampleQuantity: props.process.sample_quantity,
  stepCount: props.process.steps?.length,
}) : ''))

function pickStatus(value, close) {
  close()
  if (value !== props.process.status) emit('status', value)
}

function saveInfo() {
  emit('save-info', {
    customer_id: props.process.customer_id ?? null,
    customer_name: infoForm.value.customer_name,
    requirement: infoForm.value.requirement || null,
    sample_quantity: Number(infoForm.value.sample_quantity) || 1,
    test_month: `${infoForm.value.test_month}-01`,
    prepared_by: infoForm.value.prepared_by || null,
    status: props.process.status,
    internal_note: props.process.internal_note || null,
    steps: (props.process.steps || []).map(stepPayload),
  })
}
</script>

<template>
  <div class="relative flex flex-col flex-1 min-h-0 lt-surface overflow-hidden">
    <template v-if="process">
      <!-- Thanh công cụ (máy tính) -->
      <div class="hidden md:flex items-center gap-3 px-5 py-4 border-b border-lt-divider dark:border-slate-700 shrink-0">
        <div class="flex flex-col min-w-0">
          <span class="text-[12px] font-semibold tracking-[0.2px] text-lt-muted dark:text-slate-400">{{ process.code }}</span>
          <span class="text-[18px] font-semibold text-lt-ink dark:text-slate-100 truncate">{{ process.customer_name }}</span>
        </div>

        <div class="flex-1" />

        <span
          v-if="!can('update')"
          class="flex items-center h-[34px] px-3 rounded-[10px] text-[12.5px] font-semibold whitespace-nowrap shrink-0"
          :class="statusMeta(process.status).chip"
        >{{ statusMeta(process.status).label }}</span>
        <DropdownMenu v-else width="w-44">
          <template #trigger="{ toggle }">
            <button
              type="button"
              aria-label="Đổi trạng thái"
              aria-haspopup="menu"
              class="flex items-center gap-1.5 h-[34px] px-3 rounded-[10px] text-[12.5px] font-semibold whitespace-nowrap shrink-0"
              :class="statusMeta(process.status).chip"
              @click="toggle"
            >
              {{ statusMeta(process.status).label }}
              <ChevronDown class="w-3.5 h-3.5" />
            </button>
          </template>
          <template #default="{ close }">
            <button
              v-for="option in STATUSES"
              :key="option.value"
              type="button"
              class="lt-menu-item"
              @click="pickStatus(option.value, close)"
            >
              <span class="w-2 h-2 rounded-full" :class="option.chip" />
              {{ option.label }}
            </button>
          </template>
        </DropdownMenu>

        <div class="w-px h-6 bg-lt-edge dark:bg-slate-700" />

        <button v-if="can('update')" type="button" class="lt-btn" @click="emit('edit')">
          <Pencil class="w-[15px] h-[15px]" />Sửa
        </button>
        <button v-if="can('create')" type="button" class="lt-btn" :disabled="busy" @click="emit('duplicate')">
          <Loader2 v-if="busy" class="w-[15px] h-[15px] animate-spin" />
          <Copy v-else class="w-[15px] h-[15px]" />Nhân bản
        </button>
        <button type="button" class="lt-btn-primary" @click="emit('download')">
          <Download class="w-[15px] h-[15px]" />Tải PDF
        </button>
        <button type="button" class="lt-btn-ghost" aria-label="In lưu trình" @click="emit('print')">
          <Printer class="w-4 h-4" />
        </button>

        <DropdownMenu width="w-60">
          <template #trigger="{ toggle }">
            <button type="button" class="lt-btn-ghost" aria-label="Thao tác khác" @click="toggle">
              <MoreHorizontal class="w-4 h-4" />
            </button>
          </template>
          <template #default="{ close }">
            <button v-if="can('create')" type="button" class="lt-menu-item" @click="close(); emit('save-template')">
              <LayoutTemplate class="w-4 h-4" />Lưu thành quy trình chuẩn
            </button>
            <button type="button" class="lt-menu-item" @click="close(); emit('letterhead')">
              <Building2 class="w-4 h-4" />Thông tin công ty
            </button>
            <button v-if="can('delete')" type="button" class="lt-menu-item-danger" @click="close(); emit('remove')">
              <Trash2 class="w-4 h-4" />Xóa lưu trình
            </button>
          </template>
        </DropdownMenu>
      </div>

      <!-- Đầu trang (điện thoại) -->
      <div class="md:hidden flex flex-col shrink-0">
        <div class="flex items-center justify-between h-14 px-3">
          <button
            type="button"
            class="w-11 h-11 flex items-center justify-center rounded-[14px] text-lt-ink dark:text-slate-100"
            aria-label="Quay lại danh sách"
            @click="emit('back')"
          >
            <ArrowLeft class="w-5 h-5" />
          </button>
          <span class="text-[13px] font-semibold tracking-[0.2px] text-lt-muted dark:text-slate-400">{{ process.code }}</span>

          <!-- Màn hẹp gộp trạng thái và các thao tác vào chung một menu -->
          <DropdownMenu v-if="can('update')" width="w-60">
            <template #trigger="{ toggle }">
              <button
                type="button"
                class="w-11 h-11 flex items-center justify-center rounded-[14px] text-lt-body dark:text-slate-300"
                aria-label="Thao tác khác"
                @click="toggle"
              >
                <MoreHorizontal class="w-[18px] h-[18px]" />
              </button>
            </template>
            <template #default="{ close }">
              <button
                v-for="option in STATUSES"
                :key="option.value"
                type="button"
                class="lt-menu-item"
                @click="pickStatus(option.value, close)"
              >
                <span class="w-2 h-2 rounded-full" :class="option.chip" />{{ option.label }}
              </button>
              <div class="h-px my-1 bg-lt-divider dark:bg-slate-700" />
              <button v-if="can('create')" type="button" class="lt-menu-item" @click="close(); emit('save-template')">
                <LayoutTemplate class="w-4 h-4" />Lưu thành quy trình chuẩn
              </button>
              <button v-if="can('delete')" type="button" class="lt-menu-item-danger" @click="close(); emit('remove')">
                <Trash2 class="w-4 h-4" />Xóa lưu trình
              </button>
            </template>
          </DropdownMenu>
        </div>

        <div class="flex flex-col gap-[7px] px-4 pb-3.5">
          <h1 class="text-[19px] font-semibold text-lt-ink dark:text-slate-100">{{ process.customer_name }}</h1>
          <div class="flex items-center gap-2">
            <StatusPill :value="process.status" />
            <span class="text-[12.5px] text-lt-muted dark:text-slate-400">{{ meta }}</span>
          </div>
          <span v-if="process.requirement" class="text-[13px] leading-[1.45] text-lt-label dark:text-slate-300">
            Yêu cầu: {{ process.requirement }}
          </span>
        </div>

        <div class="px-4 pb-3">
          <div class="flex p-[3px] rounded-xl bg-lt-step dark:bg-slate-700">
            <button
              v-for="tab in [{ key: 'sheet', label: 'Tờ A4' }, { key: 'steps', label: 'Từng bước' }]"
              :key="tab.key"
              type="button"
              class="flex-1 h-9 rounded-[9px] text-[13.5px]"
              :class="mobileTab === tab.key
                ? 'bg-white dark:bg-slate-800 font-semibold text-lt-tealink shadow-sm'
                : 'font-medium text-lt-muted dark:text-slate-300'"
              @click="mobileTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Nội dung: máy tính luôn là tờ A4, điện thoại theo tab đang chọn -->
      <div class="hidden md:flex flex-1 min-h-0">
        <SheetFrame :html="sheetHtml" :loading="sheetLoading" :zoom="zoom" class="flex-1 min-w-0" />
        <aside class="w-[282px] shrink-0 border-l border-lt-divider dark:border-slate-700 bg-white dark:bg-slate-800 overflow-y-auto p-4">
          <div class="flex items-center justify-between gap-2 mb-4">
            <h2 class="m-0 text-[15px] font-bold text-lt-ink dark:text-slate-100">Chỉnh sửa dữ liệu</h2>
            <span class="inline-flex w-7 h-7 items-center justify-center rounded-lg bg-lt-wash text-lt-tealink"><FileText class="w-4 h-4" /></span>
          </div>
          <form v-if="can('update')" class="flex flex-col gap-3" @submit.prevent="saveInfo">
            <label class="document-field"><span>Mã lưu trình</span><input :value="process.code" disabled /></label>
            <label class="document-field"><span>Khách hàng</span><input v-model="infoForm.customer_name" required /></label>
            <label class="document-field"><span>Yêu cầu</span><textarea v-model="infoForm.requirement" rows="3" /></label>
            <label class="document-field"><span>Ngày test</span><input v-model="infoForm.test_month" type="month" required /></label>
            <label class="document-field"><span>Số lượng mẫu</span><input v-model.number="infoForm.sample_quantity" type="number" min="1" required /></label>
            <label class="document-field"><span>Người lập văn bản</span><input v-model="infoForm.prepared_by" /></label>
            <p v-if="infoError" class="text-xs text-lt-voidink">{{ infoError }}</p>
            <button type="submit" class="lt-btn-primary w-full justify-center" :disabled="infoSaving">
              <Loader2 v-if="infoSaving" class="w-4 h-4 animate-spin" />
              <span v-else>Lưu thay đổi</span>
            </button>
          </form>
          <div v-else class="flex flex-col gap-3">
            <div class="document-info-block"><span>Mã lưu trình</span><strong>{{ process.code }}</strong></div>
            <div class="document-info-block"><span>Khách hàng</span><strong>{{ process.customer_name }}</strong></div>
            <div class="document-info-block"><span>Tháng test</span><strong>{{ process.test_month || '—' }}</strong></div>
            <div class="document-info-block"><span>Số lượng mẫu</span><strong>{{ process.sample_quantity ?? '—' }}</strong></div>
            <div class="document-info-block"><span>Người lập</span><strong>{{ process.prepared_by || '—' }}</strong></div>
          </div>
        </aside>
      </div>

      <div class="md:hidden flex-1 min-h-0 overflow-y-auto px-4 pb-28">
        <SheetFrame
          v-if="mobileTab === 'sheet'"
          :html="sheetHtml"
          :loading="sheetLoading"
          :fill="false"
          zoom="width"
          class="rounded-2xl"
        />
        <StepCards v-else :steps="process.steps" />
      </div>

      <!-- Chân khung (máy tính) -->
      <div class="hidden md:flex items-center gap-3 h-11 px-5 border-t border-lt-divider dark:border-slate-700 shrink-0">
        <span class="text-[12px] text-lt-muted dark:text-slate-400 truncate">
          <template v-if="process.internal_note">Ghi chú nội bộ: {{ process.internal_note }}</template>
          <template v-else-if="process.source_process_code">Nhân bản từ {{ process.source_process_code }}</template>
        </span>
        <div class="flex-1" />
        <span class="text-[12px] text-lt-faint dark:text-slate-500">Thu phóng</span>
        <ZoomToggle v-model="zoom" />
      </div>

      <!-- Thanh nút dưới (điện thoại) -->
      <div class="md:hidden absolute left-0 right-0 bottom-0 flex items-center gap-2.5 px-4 pt-6 pb-5 bg-gradient-to-t from-white via-white/95 to-transparent dark:from-slate-800 dark:via-slate-800/95">
        <button v-if="can('update')"
          type="button"
          class="flex items-center justify-center gap-1.5 h-12 px-4 rounded-[14px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-800 text-sm font-medium text-lt-body dark:text-slate-200"
          @click="emit('edit')"
        >
          <Pencil class="w-4 h-4" />Sửa
        </button>
        <button
          type="button"
          class="flex-1 flex items-center justify-center gap-2 h-12 rounded-[14px] bg-lt-gradient text-white text-[14.5px] font-semibold shadow-lt-fab"
          @click="emit('download')"
        >
          <Download class="w-[17px] h-[17px]" />Tải PDF
        </button>
        <button v-if="can('create')"
          type="button"
          class="w-12 h-12 flex items-center justify-center rounded-[14px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-800 text-lt-body dark:text-slate-200"
          aria-label="Nhân bản lưu trình"
          :disabled="busy"
          @click="emit('duplicate')"
        >
          <Copy class="w-[17px] h-[17px]" />
        </button>
      </div>
    </template>

    <div v-else class="flex-1 flex items-center justify-center px-6 text-center text-[13px] text-lt-faint dark:text-slate-500">
      Chọn một lưu trình ở danh sách bên trái để xem tờ in.
    </div>
  </div>
</template>

<style scoped>
.document-info-block {
  @apply flex flex-col gap-1 px-3 py-2.5 rounded-xl bg-lt-tint dark:bg-slate-700/60;
}
.document-info-block span {
  @apply text-[11px] font-medium text-lt-faint dark:text-slate-400;
}
.document-info-block strong {
  @apply text-[12.5px] font-semibold text-lt-ink dark:text-slate-100 break-words;
}
.document-field { @apply flex flex-col gap-1.5; }
.document-field span { @apply text-[11px] font-semibold text-lt-label dark:text-slate-300; }
.document-field input, .document-field textarea {
  @apply w-full box-border rounded-[10px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-[12.5px] text-lt-ink dark:text-slate-100 outline-none focus:border-lt-teal focus:ring-2 focus:ring-lt-teal/10;
}
.document-field input:disabled { @apply bg-lt-tint text-lt-muted dark:bg-slate-700/60 dark:text-slate-400; }
</style>
