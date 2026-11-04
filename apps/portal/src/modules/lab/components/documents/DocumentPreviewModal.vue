<script setup>
import { computed } from 'vue'
import Modal from '@/core/components/Modal.vue'
import { formatDateTime, formatFileSize } from '@/core/utils/format'
import { Download, ExternalLink, FileText } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  document: Object,
  previewUrl: String,
  downloadUrl: String,
})
const emit = defineEmits(['close'])

const OFFICE_MIME_TYPES = [
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

const isImage = computed(() => !!props.document?.mime_type?.startsWith('image/'))
// File Word (.doc/.docx) duoc backend convert sang PDF khi xem truoc (inline=true) nen dung chung khung iframe voi PDF
const isOfficeDoc = computed(() => {
  const ext = props.document?.original_filename?.split('.').pop()?.toLowerCase()
  return OFFICE_MIME_TYPES.includes(props.document?.mime_type) || ext === 'doc' || ext === 'docx'
})
const showPdfViewer = computed(() => props.document?.mime_type === 'application/pdf' || isOfficeDoc.value)
// toolbar=1&navpanes=0: an cui thu muc/thumbnail cua trinh xem PDF de danh khong gian cho trang chinh
const pdfViewerUrl = computed(() => props.previewUrl ? `${props.previewUrl}#toolbar=1&navpanes=0` : '')
</script>

<template>
  <Modal :show="show" fullscreen :title="document?.name || 'Xem tài liệu'" @close="emit('close')">
    <div v-if="document" class="document-viewer">
      <header class="document-viewer-header">
        <div class="flex items-center gap-3 min-w-0">
          <FileText class="w-5 h-5 text-lt-tealink shrink-0" />
          <div class="min-w-0"><h2 class="document-title">{{ document.name }}</h2><p class="document-meta">{{ document.uploaded_by }} · {{ formatDateTime(document.uploaded_at) }}<span v-if="document.file_size"> · {{ formatFileSize(document.file_size) }}</span></p></div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <a :href="previewUrl" target="_blank" rel="noopener" class="lt-btn"><ExternalLink class="w-4 h-4" />Mở tab mới</a>
          <a :href="downloadUrl" class="lt-btn-primary"><Download class="w-4 h-4" />Tải xuống</a>
          <button type="button" class="lt-btn-ghost" aria-label="Đóng" @click="emit('close')">×</button>
        </div>
      </header>

      <div class="document-viewer-body">
        <div class="document-canvas">

      <div v-if="isImage" class="rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-900 flex justify-center">
        <img :src="previewUrl" :alt="document.name" class="max-h-[65vh] object-contain" />
      </div>

      <template v-else-if="showPdfViewer">
        <!-- Iframe PDF viewer chỉ ổn định trên desktop; trên di động dễ hiện trắng nên ưu tiên mở tab mới -->
        <iframe
          :src="pdfViewerUrl"
          class="hidden sm:block w-full h-[65vh] rounded-xl border border-slate-200 dark:border-slate-600 bg-white"
        />
        <div class="sm:hidden flex flex-col items-center justify-center gap-3 py-14 text-slate-400 text-sm text-center">
          <FileText class="w-10 h-10 text-slate-300" />
          <p>Trình duyệt di động có thể không xem trước được PDF trong khung nhỏ.</p>
          <a
            :href="previewUrl"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-gradient text-white text-sm"
          >
            <ExternalLink class="w-4 h-4" /> Mở tài liệu
          </a>
        </div>
      </template>

      <div v-else class="flex flex-col items-center justify-center gap-3 py-16 text-slate-400 text-sm text-center">
        <p>Không thể xem trước định dạng tệp này ({{ document.original_filename }}).</p>
        <a
          :href="downloadUrl"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-gradient text-white text-sm"
        >
          <Download class="w-4 h-4" /> Tải xuống để xem
        </a>
      </div>
        </div>

        <aside class="document-viewer-side">
          <h3>Thông tin tài liệu</h3>
          <div class="document-side-section"><span>Người tải lên</span><strong>{{ document.uploaded_by || '—' }}</strong></div>
          <div class="document-side-section"><span>Thời gian</span><strong>{{ formatDateTime(document.uploaded_at) }}</strong></div>
          <div class="document-side-section"><span>Tên tệp gốc</span><strong>{{ document.original_filename || '—' }}</strong></div>
          <div class="document-side-section"><span>Kích thước</span><strong>{{ document.file_size ? formatFileSize(document.file_size) : '—' }}</strong></div>
          <a :href="downloadUrl" class="lt-btn-primary justify-center mt-2"><Download class="w-4 h-4" />Tải bản gốc</a>
        </aside>
      </div>
    </div>
  </Modal>
</template>

<style scoped>
.document-viewer { @apply flex flex-col h-full min-h-0 bg-lt-paper dark:bg-slate-900; }
.document-viewer-header { @apply flex items-center justify-between gap-4 min-h-[68px] px-5 border-b border-lt-divider dark:border-slate-700 bg-white dark:bg-slate-800; }
.document-title { @apply m-0 text-[15px] font-bold text-lt-ink dark:text-slate-100 truncate; }
.document-meta { @apply m-0 mt-0.5 text-xs text-lt-muted dark:text-slate-400; }
.document-viewer-body { @apply flex flex-1 min-h-0; }
.document-canvas { @apply flex-1 min-w-0 overflow-auto p-6 bg-lt-paper dark:bg-slate-900; }
.document-viewer-side { @apply w-[260px] shrink-0 overflow-y-auto p-5 border-l border-lt-divider dark:border-slate-700 bg-white dark:bg-slate-800; }
.document-viewer-side h3 { @apply m-0 mb-4 text-[15px] font-bold text-lt-ink dark:text-slate-100; }
.document-side-section { @apply flex flex-col gap-1 p-3 mb-2.5 rounded-xl bg-lt-tint dark:bg-slate-700/60; }
.document-side-section span { @apply text-[11px] text-lt-faint dark:text-slate-400; }
.document-side-section strong { @apply text-[12.5px] text-lt-ink dark:text-slate-100 break-words; }
</style>
