<script setup>
import { ref, computed } from 'vue'
import {
  Plus, GripVertical, Pencil, Copy, X, LayoutTemplate, ChevronUp, ChevronDown, Loader2,
} from 'lucide-vue-next'
import StepEditor from './StepEditor.vue'
import TemplatePickerDialog from './TemplatePickerDialog.vue'
import { testProcessesApi } from '../../api/resources'
import { emptyStep, normalizeStep, QUICK_OPERATIONS } from '../../constants/testProcess'
import { renderMarkers, stepSummary, stripHtml } from '../../utils/testProcessFormat'

// Danh sách các bước: mỗi lúc chỉ mở một bước để sửa, các bước còn lại thu gọn
// thành một dòng. Mảng `steps` do view cha giữ và được sửa thẳng tại chỗ.
const props = defineProps({
  steps: { type: Array, required: true },
  products: { type: Array, default: () => [] },
  labChemicals: { type: Array, default: () => [] },
  operationOptions: { type: Array, default: () => [] },
  showTemplateButton: { type: Boolean, default: true },
})

const openIndex = ref(props.steps.length ? 0 : null)
const dragIndex = ref(null)
const fillingIndex = ref(null)
const showTemplates = ref(false)

const summaries = computed(() => props.steps.map(step => stepSummary(step)))

function addStep(operation = '') {
  props.steps.push(emptyStep(operation))
  openIndex.value = props.steps.length - 1
}

function duplicateStep(index) {
  props.steps.splice(index + 1, 0, normalizeStep(JSON.parse(JSON.stringify(props.steps[index]))))
  openIndex.value = index + 1
}

function removeStep(index) {
  props.steps.splice(index, 1)
  if (openIndex.value === index) openIndex.value = null
  else if (openIndex.value > index) openIndex.value -= 1
}

function move(from, to) {
  if (to < 0 || to >= props.steps.length || from === to) return
  const open = openIndex.value
  const [step] = props.steps.splice(from, 1)
  props.steps.splice(to, 0, step)

  // Giữ đúng bước đang mở sau khi các bước ở giữa dịch một chỗ
  if (open === null) return
  if (open === from) {
    openIndex.value = to
    return
  }
  let next = open
  if (from < open) next -= 1
  if (to <= next) next += 1
  openIndex.value = next
}

function onDrop(index) {
  if (dragIndex.value === null) return
  move(dragIndex.value, index)
  dragIndex.value = null
}

/** Nút "Điền theo lần gần nhất": lấy thông số của lần gần nhất dùng hạng mục này. */
async function fillFromLast(index) {
  const step = props.steps[index]
  if (!step.operation) return
  fillingIndex.value = index
  try {
    const result = await testProcessesApi.lastStep(step.operation)
    if (result.found && result.step) {
      props.steps.splice(index, 1, normalizeStep({ ...result.step, operation: step.operation }))
    }
  } finally {
    fillingIndex.value = null
  }
}

function insertTemplate(templateSteps) {
  templateSteps.forEach(step => props.steps.push(normalizeStep(step)))
  showTemplates.value = false
  openIndex.value = null
}

function replaceWithTemplate(templateSteps) {
  props.steps.splice(0, props.steps.length, ...templateSteps.map(normalizeStep))
  showTemplates.value = false
  openIndex.value = null
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex items-center justify-between">
      <h2 class="text-[15px] font-semibold text-lt-ink dark:text-slate-100">Chi tiết quy trình</h2>
      <span class="text-[12.5px] text-lt-muted dark:text-slate-400">{{ steps.length }} bước</span>
    </div>

    <div class="flex flex-wrap items-center gap-2">
      <button
        type="button"
        class="flex items-center gap-1.5 h-8 px-3 rounded-[9px] bg-lt-wash dark:bg-slate-700 text-[12.5px] font-semibold text-lt-tealink dark:text-brand-300"
        @click="addStep()"
      >
        <Plus class="w-[15px] h-[15px]" />Thêm bước
      </button>
      <button
        v-for="operation in QUICK_OPERATIONS"
        :key="operation"
        type="button"
        class="h-8 px-3 rounded-[9px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-700 text-[12.5px] text-lt-body dark:text-slate-200"
        @click="addStep(operation)"
      >
        + {{ operation }}
      </button>
      <div class="flex-1" />
      <button
        v-if="showTemplateButton"
        type="button"
        class="flex items-center gap-1.5 h-8 px-3 rounded-[9px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-700 text-[12.5px] text-lt-body dark:text-slate-200"
        @click="showTemplates = true"
      >
        <LayoutTemplate class="w-[15px] h-[15px]" />Chèn từ quy trình chuẩn
      </button>
    </div>

    <p v-if="!steps.length" class="px-3 py-8 text-center text-[13px] text-lt-faint dark:text-slate-500 border border-dashed border-lt-line dark:border-slate-600 rounded-[14px]">
      Chưa có bước nào. Bấm “Thêm bước” hoặc chèn từ một quy trình chuẩn.
    </p>

    <template v-for="(step, index) in steps" :key="index">
      <StepEditor
        v-if="openIndex === index"
        :step="step"
        :index="index"
        :products="products"
        :lab-chemicals="labChemicals"
        :operation-options="operationOptions"
        :filling-last="fillingIndex === index"
        @remove="removeStep(index)"
        @duplicate="duplicateStep(index)"
        @fill-last="fillFromLast(index)"
      />

      <div
        v-else
        draggable="true"
        class="flex items-center gap-2.5 h-12 px-3 rounded-[14px] border border-lt-soft dark:border-slate-700 bg-lt-card dark:bg-slate-800/60"
        :class="dragIndex === index ? 'opacity-50' : ''"
        @dragstart="dragIndex = index"
        @dragover.prevent
        @drop="onDrop(index)"
        @dragend="dragIndex = null"
      >
        <GripVertical class="w-3.5 h-3.5 text-[#B9C9C7] shrink-0 cursor-grab" />
        <span class="flex items-center justify-center w-[22px] h-[22px] shrink-0 rounded-[7px] bg-lt-step dark:bg-slate-700 text-[12px] font-semibold text-lt-label dark:text-slate-300">
          {{ index + 1 }}
        </span>
        <span class="text-[13.5px] font-medium text-lt-ink dark:text-slate-100 shrink-0 max-w-[40%] truncate" v-html="step.operation ? renderMarkers(step.operation) : '(chưa đặt tên)'" />
        <span
          class="text-[12.5px] text-lt-faint dark:text-slate-500 truncate"
          :title="stripHtml(summaries[index])"
          v-html="summaries[index] || 'chưa có thông số'"
        />
        <div class="flex-1" />
        <button
          type="button"
          class="w-7 h-7 flex items-center justify-center rounded-lg text-lt-muted hover:bg-lt-wash dark:hover:bg-slate-700 shrink-0 disabled:opacity-30"
          :aria-label="`Đưa bước ${index + 1} lên trên`"
          :disabled="index === 0"
          @click="move(index, index - 1)"
        >
          <ChevronUp class="w-[15px] h-[15px]" />
        </button>
        <button
          type="button"
          class="w-7 h-7 flex items-center justify-center rounded-lg text-lt-muted hover:bg-lt-wash dark:hover:bg-slate-700 shrink-0 disabled:opacity-30"
          :aria-label="`Đưa bước ${index + 1} xuống dưới`"
          :disabled="index === steps.length - 1"
          @click="move(index, index + 1)"
        >
          <ChevronDown class="w-[15px] h-[15px]" />
        </button>
        <button
          type="button"
          class="w-7 h-7 flex items-center justify-center rounded-lg text-lt-muted hover:bg-lt-wash dark:hover:bg-slate-700 shrink-0"
          :aria-label="`Sửa bước ${index + 1}`"
          @click="openIndex = index"
        >
          <Pencil class="w-[15px] h-[15px]" />
        </button>
        <button
          type="button"
          class="w-7 h-7 flex items-center justify-center rounded-lg text-lt-muted hover:bg-lt-wash dark:hover:bg-slate-700 shrink-0"
          :aria-label="`Nhân bản bước ${index + 1}`"
          @click="duplicateStep(index)"
        >
          <Copy class="w-[15px] h-[15px]" />
        </button>
        <button
          type="button"
          class="w-7 h-7 flex items-center justify-center rounded-lg text-lt-voidink hover:bg-lt-void/60 shrink-0"
          :aria-label="`Xóa bước ${index + 1}`"
          @click="removeStep(index)"
        >
          <X class="w-[15px] h-[15px]" />
        </button>
      </div>
    </template>

    <div v-if="fillingIndex !== null" class="flex items-center gap-2 text-[12px] text-lt-faint">
      <Loader2 class="w-3.5 h-3.5 animate-spin" />Đang lấy thông số lần gần nhất…
    </div>

    <TemplatePickerDialog
      :show="showTemplates"
      :current-step-count="steps.length"
      @close="showTemplates = false"
      @insert="insertTemplate"
      @replace="replaceWithTemplate"
    />
  </div>
</template>
