<script setup>
import { ref, watch } from 'vue'
import Modal from '../Modal.vue'
import { UploadCloud } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  categoryLabel: String,
  saving: Boolean,
})
const emit = defineEmits(['close', 'submit'])

const name = ref('')
const uploadedBy = ref('')
const file = ref(null)

watch(() => props.show, (visible) => {
  if (visible) {
    name.value = ''
    uploadedBy.value = ''
    file.value = null
  }
})

function onFileChange(e) {
  const picked = e.target.files?.[0] || null
  file.value = picked
  if (picked && !name.value) name.value = picked.name
}

function submit() {
  if (!file.value || !uploadedBy.value.trim()) return
  emit('submit', { file: file.value, name: name.value.trim() || file.value.name, uploadedBy: uploadedBy.value.trim() })
}
</script>

<template>
  <Modal :show="show" :title="`Thêm tài liệu — ${categoryLabel}`" @close="emit('close')">
    <form class="flex flex-col gap-4" @submit.prevent="submit">
      <div>
        <label class="field-label mb-1">Tệp tài liệu</label>
        <label
          class="flex flex-col items-center justify-center gap-2 border-2 border-dashed border-slate-200 dark:border-slate-600 rounded-2xl py-8 px-4 text-center cursor-pointer hover:border-brand-400 transition-colors"
        >
          <UploadCloud class="w-6 h-6 text-slate-400" />
          <span class="text-sm text-slate-500 dark:text-slate-300 break-all">
            {{ file ? file.name : 'Chọn tệp để tải lên (PDF, ảnh, Word, Excel...)' }}
          </span>
          <input type="file" class="hidden" @change="onFileChange" />
        </label>
      </div>

      <div>
        <label class="field-label mb-1">Tên tài liệu</label>
        <input v-model="name" placeholder="VD: MSDS - NaOH 50%" class="w-full field-input" />
      </div>

      <div>
        <label class="field-label mb-1">Người tải lên</label>
        <input v-model="uploadedBy" placeholder="VD: Gibel" class="w-full field-input" />
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <button type="button" class="px-4 py-2 rounded-xl text-slate-500" @click="emit('close')">Huỷ</button>
        <button
          type="submit"
          class="px-4 py-2 rounded-xl bg-brand-gradient text-white disabled:opacity-50"
          :disabled="saving || !file || !uploadedBy.trim()"
        >
          {{ saving ? 'Đang tải lên...' : 'Tải lên' }}
        </button>
      </div>
    </form>
  </Modal>
</template>
