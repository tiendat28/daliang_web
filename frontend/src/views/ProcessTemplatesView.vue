<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Pencil, Copy, Trash2, MoreHorizontal, Loader2 } from 'lucide-vue-next'
import Modal from '../components/Modal.vue'
import StepListEditor from '../components/test-processes/StepListEditor.vue'
import DropdownMenu from '../components/test-processes/DropdownMenu.vue'
import MenuButton from '../components/layout/MenuButton.vue'
import { processTemplatesApi } from '../api/resources'
import { useStepEditorLookups } from '../composables/useStepEditorLookups'
import { normalizeStep } from '../constants/testProcess'
import { stepPayload } from '../utils/testProcessPayload'
import { takeWithOverflow } from '../utils/testProcessFormat'

// Quy trình chuẩn = bộ bước dùng lại khi tạo lưu trình mới. Sửa ở đây không
// đụng tới các lưu trình đã lưu, vì lúc chèn là chép bước sang lưu trình.
const router = useRouter()

const MAX_CHIPS = 6

const templates = ref([])
const loading = ref(true)

const { products, labChemicals, operationOptions, load: loadLookups } = useStepEditorLookups()

const showEditor = ref(false)
const editingId = ref(null)
const saving = ref(false)
const errorMessage = ref('')
const draft = reactive({ name: '', description: '' })
const draftSteps = reactive([])

const editorTitle = computed(() => (editingId.value ? 'Sửa quy trình chuẩn' : 'Tạo quy trình chuẩn'))

const canSave = computed(() =>
  Boolean(draft.name.trim()) && draftSteps.length > 0 && draftSteps.every(step => (step.operation || '').trim()))

async function load() {
  loading.value = true
  try {
    templates.value = await processTemplatesApi.list()
  } finally {
    loading.value = false
  }
}

// Danh sách và các danh mục không phụ thuộc nhau nên tải song song
onMounted(() => { load(); loadLookups() })

// Kèm sẵn dãy chip cho mỗi dòng, khỏi tính lại mỗi lần vẽ lại
const rows = computed(() => templates.value.map(template => ({
  ...template,
  chips: takeWithOverflow(template.operations, MAX_CHIPS),
})))

function openEditor(template = null) {
  editingId.value = template?.id ?? null
  draft.name = template?.name || ''
  draft.description = template?.description || ''
  draftSteps.splice(0, draftSteps.length, ...((template?.steps || []).map(normalizeStep)))
  errorMessage.value = ''
  showEditor.value = true
}

async function saveTemplate() {
  if (!canSave.value) return
  saving.value = true
  errorMessage.value = ''
  const payload = {
    name: draft.name.trim(),
    description: draft.description.trim() || null,
    steps: draftSteps.map(stepPayload),
  }
  try {
    if (editingId.value) await processTemplatesApi.update(editingId.value, payload)
    else await processTemplatesApi.create(payload)
    showEditor.value = false
    await load()
  } catch (error) {
    const detail = error.response?.data?.detail
    errorMessage.value = typeof detail === 'string'
      ? detail
      : 'Không lưu được quy trình chuẩn, kiểm tra lại các bước'
  } finally {
    saving.value = false
  }
}

async function duplicate(template) {
  await processTemplatesApi.create({
    name: `${template.name} (bản sao)`,
    description: template.description,
    steps: (template.steps || []).map(normalizeStep),
  })
  await load()
}

async function remove(template) {
  if (!confirm(`Xóa quy trình chuẩn "${template.name}"? Các lưu trình đã dùng nó không bị ảnh hưởng.`)) return
  await processTemplatesApi.remove(template.id)
  await load()
}
</script>

<template>
  <div class="font-lt flex flex-col flex-1 min-h-0 gap-3.5">
    <div class="flex flex-wrap items-end gap-4">
      <MenuButton />
      <div class="flex flex-col gap-0.5">
        <h1 class="text-[22px] font-semibold tracking-[-0.2px] text-lt-ink dark:text-slate-100">Quy trình chuẩn</h1>
        <span class="text-[12.5px] text-lt-muted dark:text-slate-400">
          Bộ bước dùng lại khi tạo lưu trình mới — sửa ở đây không ảnh hưởng lưu trình đã lưu
        </span>
      </div>
      <div class="flex-1" />
      <button
        type="button"
        class="flex items-center gap-2 h-10 px-4 rounded-xl bg-lt-gradient text-white text-[13.5px] font-semibold shadow-lt-teal"
        @click="openEditor()"
      >
        <Plus class="w-[18px] h-[18px]" />Tạo quy trình chuẩn
      </button>
    </div>

    <div class="flex-1 min-h-0 flex flex-col lt-surface overflow-hidden">
      <div class="flex items-center h-[46px] px-[22px] border-b border-lt-divider dark:border-slate-700 shrink-0">
        <span class="text-[12.5px] font-semibold text-lt-label dark:text-slate-300">{{ templates.length }} quy trình chuẩn</span>
      </div>

      <div class="flex-1 min-h-0 overflow-y-auto">
        <div v-if="loading" class="flex items-center justify-center gap-2 py-12 text-[13px] text-lt-faint">
          <Loader2 class="w-4 h-4 animate-spin" />Đang tải…
        </div>

        <p v-else-if="!templates.length" class="px-6 py-12 text-center text-[13px] text-lt-faint dark:text-slate-500">
          Chưa có quy trình chuẩn nào. Tạo mới ở đây, hoặc mở một lưu trình đã nhập rồi
          chọn “Lưu thành quy trình chuẩn”.
        </p>

        <div
          v-for="template in rows"
          :key="template.id"
          class="flex flex-col md:flex-row md:items-start gap-4 px-[22px] py-[18px] border-b border-lt-rule dark:border-slate-700"
        >
          <div class="flex flex-col gap-2 flex-1 min-w-0">
            <div class="flex items-center gap-2.5 flex-wrap">
              <span class="text-[15px] font-semibold text-lt-ink dark:text-slate-100">{{ template.name }}</span>
              <span class="lt-chip rounded-full font-semibold">{{ template.step_count }} bước</span>
            </div>
            <span v-if="template.description" class="text-[13px] text-lt-muted dark:text-slate-400">{{ template.description }}</span>
            <div class="flex flex-wrap items-center gap-1.5 mt-0.5">
              <span
                v-for="(operation, index) in template.chips.items"
                :key="index"
                class="px-2.5 py-[3px] rounded-[7px] bg-lt-tint dark:bg-slate-700 border border-lt-divider dark:border-slate-600 text-[11.5px] text-lt-label dark:text-slate-300"
              >
                {{ operation }}
              </span>
              <span v-if="template.chips.extra" class="text-[11.5px] text-lt-faint dark:text-slate-500">
                +{{ template.chips.extra }} bước
              </span>
            </div>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <button
              type="button"
              class="flex items-center h-[34px] px-3.5 rounded-[10px] bg-lt-wash dark:bg-slate-700 text-[12.5px] font-semibold text-lt-tealink dark:text-brand-300"
              @click="router.push({ name: 'test-process-new', query: { template: template.id } })"
            >
              Dùng cho lưu trình mới
            </button>
            <button type="button" class="lt-btn" @click="openEditor(template)">
              <Pencil class="w-[15px] h-[15px]" />Sửa
            </button>
            <DropdownMenu width="w-48">
              <template #trigger="{ toggle }">
                <button type="button" class="lt-btn-ghost" aria-label="Thao tác khác" @click="toggle">
                  <MoreHorizontal class="w-4 h-4" />
                </button>
              </template>
              <template #default="{ close }">
                <button type="button" class="lt-menu-item" @click="close(); duplicate(template)">
                  <Copy class="w-4 h-4" />Nhân bản
                </button>
                <button type="button" class="lt-menu-item-danger" @click="close(); remove(template)">
                  <Trash2 class="w-4 h-4" />Xóa
                </button>
              </template>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </div>

    <Modal :show="showEditor" :title="editorTitle" size="lg" @close="showEditor = false">
      <div class="font-lt flex flex-col gap-4">
        <div class="flex flex-wrap gap-3.5">
          <div class="flex flex-col gap-1.5 flex-1 min-w-[220px]">
            <label for="tpl-edit-name" class="lt-label">Tên quy trình chuẩn</label>
            <input id="tpl-edit-name" v-model="draft.name" type="text" class="lt-field" placeholder="Mạ kẽm kiềm – thụ động – nhuộm màu" />
          </div>
          <div class="flex flex-col gap-1.5 flex-1 min-w-[220px]">
            <label for="tpl-edit-desc" class="lt-label">Mô tả</label>
            <input id="tpl-edit-desc" v-model="draft.description" type="text" class="lt-field" placeholder="Dùng cho hàng cần màu xanh than." />
          </div>
        </div>

        <div class="h-px bg-lt-divider dark:bg-slate-700" />

        <StepListEditor
          :steps="draftSteps"
          :products="products"
          :lab-chemicals="labChemicals"
          :operation-options="operationOptions"
          :show-template-button="false"
        />

        <p v-if="errorMessage" class="px-4 py-2.5 rounded-xl bg-lt-void text-[12.5px] text-lt-voidink">{{ errorMessage }}</p>

        <div class="flex justify-end gap-2">
          <button type="button" class="lt-btn" @click="showEditor = false">Hủy</button>
          <button type="button" class="lt-btn-primary" :disabled="!canSave || saving" @click="saveTemplate">
            <Loader2 v-if="saving" class="w-[15px] h-[15px] animate-spin" />Lưu
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>
