<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Plus, Trash2 } from 'lucide-vue-next'
import { documentsApi } from '../api/resources'
import { fileKind } from '../utils/fileIcon'
import { formatDateTime } from '../utils/format'
import { productSearch } from '../store/productSearch'
import DocumentUploadModal from '../components/documents/DocumentUploadModal.vue'
import DocumentPreviewModal from '../components/documents/DocumentPreviewModal.vue'

const categories = [
  { key: 'msds', label: 'MSDS' },
  { key: 'coa', label: 'COA' },
  { key: 'technical', label: 'Kỹ thuật' },
  { key: 'method_analysis', label: 'Phương pháp phân tích' },
]

const activeCategory = ref(categories[0].key)
const documents = ref([])
const loading = ref(false)

const showUpload = ref(false)
const uploading = ref(false)
const previewDoc = ref(null)

const activeCategoryLabel = computed(() => categories.find(c => c.key === activeCategory.value)?.label || '')

const displayDocuments = computed(() => {
  const q = productSearch.query.trim().toLowerCase()
  if (!q) return documents.value
  return documents.value.filter(d =>
    [d.name, d.uploaded_by, d.original_filename].some(v => String(v ?? '').toLowerCase().includes(q))
  )
})

async function load() {
  loading.value = true
  try {
    documents.value = await documentsApi.list(activeCategory.value)
  } finally {
    loading.value = false
  }
}

watch(activeCategory, load)
onMounted(load)
onUnmounted(() => { productSearch.query = '' })

async function handleUpload({ file, name, uploadedBy }) {
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('category', activeCategory.value)
    formData.append('name', name)
    formData.append('uploaded_by', uploadedBy)
    await documentsApi.upload(formData)
    showUpload.value = false
    await load()
  } finally {
    uploading.value = false
  }
}

function openPreview(doc) {
  previewDoc.value = doc
}

async function remove(doc) {
  if (confirm(`Xoá tài liệu "${doc.name}"?`)) {
    await documentsApi.remove(doc.id)
    if (previewDoc.value?.id === doc.id) previewDoc.value = null
    await load()
  }
}

const previewUrl = computed(() => previewDoc.value ? documentsApi.fileUrl(previewDoc.value.id, { inline: true }) : '')
const downloadUrl = computed(() => previewDoc.value ? documentsApi.fileUrl(previewDoc.value.id) : '')
</script>

<template>
  <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm flex flex-col">
    <div class="flex flex-wrap items-center justify-between gap-3 p-5 pb-4">
      <h2 class="font-semibold text-slate-700 dark:text-slate-200">Tài liệu</h2>
      <button
        class="flex items-center gap-1 text-sm bg-brand-gradient text-white px-4 py-2 rounded-xl shadow"
        @click="showUpload = true"
      >
        <Plus class="w-4 h-4" /> Thêm
      </button>
    </div>

    <div class="flex gap-2 px-5 pb-4 overflow-x-auto">
      <button
        v-for="cat in categories"
        :key="cat.key"
        class="shrink-0 px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-colors"
        :class="activeCategory === cat.key
          ? 'bg-brand-gradient text-white shadow'
          : 'bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-300 hover:text-brand-600'"
        @click="activeCategory = cat.key"
      >
        {{ cat.label }}
      </button>
    </div>

    <div v-if="loading" class="py-10 text-center text-slate-400 text-sm">Đang tải...</div>

    <template v-else>
      <div v-if="displayDocuments.length === 0" class="py-10 text-center text-slate-400 text-sm px-5">
        Chưa có tài liệu nào trong mục {{ activeCategoryLabel }}
      </div>

      <!-- Desktop / tablet table -->
      <div v-else class="hidden sm:block overflow-auto px-5 pb-5 max-h-[65vh]">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-slate-800 dark:text-slate-100 border-b-2 border-slate-300 dark:border-slate-600 sticky top-0 z-10 bg-white dark:bg-slate-800">
              <th class="py-2 pr-4 font-semibold">Tên tài liệu</th>
              <th class="py-2 pr-4 font-semibold">Người tải</th>
              <th class="py-2 pr-4 font-semibold">Thời gian</th>
              <th class="py-2 w-16"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="doc in displayDocuments"
              :key="doc.id"
              class="border-b border-slate-200 dark:border-slate-700 hover:bg-brand-50/40 dark:hover:bg-slate-700/40 cursor-pointer"
              @click="openPreview(doc)"
            >
              <td class="py-3 pr-4 text-slate-700 dark:text-slate-200">
                <div class="flex items-center gap-3">
                  <span class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" :class="fileKind(doc.original_filename).className">
                    <component :is="fileKind(doc.original_filename).icon" class="w-4 h-4" />
                  </span>
                  <span class="truncate">{{ doc.name }}</span>
                </div>
              </td>
              <td class="py-3 pr-4 text-slate-500 dark:text-slate-400">{{ doc.uploaded_by }}</td>
              <td class="py-3 pr-4 text-slate-500 dark:text-slate-400 whitespace-nowrap">{{ formatDateTime(doc.uploaded_at) }}</td>
              <td class="py-3">
                <button class="text-slate-400 hover:text-red-500" @click.stop="remove(doc)">
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile card list -->
      <div v-if="displayDocuments.length > 0" class="sm:hidden flex flex-col gap-2 px-5 pb-5">
        <div
          v-for="doc in displayDocuments"
          :key="doc.id"
          class="flex items-center gap-3 p-3 rounded-2xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 shadow-sm cursor-pointer"
          @click="openPreview(doc)"
        >
          <span class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" :class="fileKind(doc.original_filename).className">
            <component :is="fileKind(doc.original_filename).icon" class="w-5 h-5" />
          </span>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{{ doc.name }}</p>
            <p class="text-xs text-slate-400 truncate">{{ doc.uploaded_by }} · {{ formatDateTime(doc.uploaded_at) }}</p>
          </div>
          <button class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-slate-700 shrink-0" @click.stop="remove(doc)">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </template>
  </div>

  <DocumentUploadModal
    :show="showUpload"
    :category-label="activeCategoryLabel"
    :saving="uploading"
    @close="showUpload = false"
    @submit="handleUpload"
  />

  <DocumentPreviewModal
    :show="!!previewDoc"
    :document="previewDoc"
    :preview-url="previewUrl"
    :download-url="downloadUrl"
    @close="previewDoc = null"
  />
</template>
