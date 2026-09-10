<script setup>
import { computed } from 'vue'
import Modal from '../Modal.vue'
import { formatDateTime, formatFileSize } from '../../utils/format'
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
  <Modal :show="show" size="lg" :title="document?.name || 'Xem tài liệu'" @close="emit('close')">
    <div v-if="document" class="flex flex-col gap-4">
      <div class="text-xs text-slate-400 dark:text-slate-500">
        {{ document.uploaded_by }} · {{ formatDateTime(document.uploaded_at) }}
        <span v-if="document.file_size"> · {{ formatFileSize(document.file_size) }}</span>
      </div>

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

      <div class="flex justify-end gap-4 border-t border-slate-100 dark:border-slate-700 pt-3">
        <a :href="previewUrl" target="_blank" rel="noopener" class="inline-flex items-center gap-1 text-sm text-brand-600 hover:underline">
          <ExternalLink class="w-4 h-4" /> Mở tab mới
        </a>
        <a :href="downloadUrl" class="inline-flex items-center gap-1 text-sm text-brand-600 hover:underline">
          <Download class="w-4 h-4" /> Tải xuống
        </a>
      </div>
    </div>
  </Modal>
</template>
