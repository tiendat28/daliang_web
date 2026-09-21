<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Check, Clock, Download, Loader2 } from 'lucide-vue-next'
import SuggestInput from '../components/test-processes/SuggestInput.vue'
import StepListEditor from '../components/test-processes/StepListEditor.vue'
import SheetFrame from '../components/test-processes/SheetFrame.vue'
import ZoomToggle from '../components/test-processes/ZoomToggle.vue'
import MenuButton from '../components/layout/MenuButton.vue'
import { testProcessesApi, processTemplatesApi, customersApi } from '../api/resources'
import { useStepEditorLookups } from '../composables/useStepEditorLookups'
import { STATUSES, emptyStep, normalizeStep } from '../constants/testProcess'
import { currentPeriod } from '../utils/format'
import { fromMonthInput, toMonthInput } from '../utils/testProcessFormat'
import { numOrNull, stepPayload, textOrNull } from '../utils/testProcessPayload'

// Form nhập/sửa lưu trình, có khung xem trước tờ in cập nhật khi ngừng gõ.
// Tờ xem trước do backend dựng nên đúng bằng bản PDF sẽ tải về.
const route = useRoute()
const router = useRouter()

const processId = computed(() => (route.params.id ? Number(route.params.id) : null))
const isEdit = computed(() => processId.value !== null)

const form = reactive({
  customer_id: null,
  customer_name: '',
  requirement: '',
  sample_quantity: 1,
  test_month: currentPeriod(),
  prepared_by: '',
  status: 'draft',
  internal_note: '',
})

const steps = reactive([emptyStep()])

const code = ref('')
const customers = ref([])
const { products, labChemicals, operationOptions, load: loadLookups } = useStepEditorLookups()

const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')
const savedSnapshot = ref('')

const sheetHtml = ref('')
const sheetLoading = ref(false)
const zoom = ref('fit')

function buildPayload() {
  return {
    customer_id: form.customer_id || null,
    customer_name: form.customer_name.trim(),
    requirement: textOrNull(form.requirement),
    sample_quantity: numOrNull(form.sample_quantity) || 1,
    test_month: fromMonthInput(form.test_month),
    prepared_by: textOrNull(form.prepared_by),
    status: form.status,
    internal_note: textOrNull(form.internal_note),
    steps: steps.map(stepPayload),
  }
}

const payload = computed(() => buildPayload())

const canSave = computed(() =>
  Boolean(payload.value.customer_name)
  && payload.value.steps.length > 0
  && payload.value.steps.every(step => step.operation))

const dirty = computed(() => JSON.stringify(payload.value) !== savedSnapshot.value)

// Lưu trình mới thì luôn là "chưa lưu" cho tới khi bấm Lưu
const unsaved = computed(() => !isEdit.value || dirty.value)

function fillFrom(process) {
  form.customer_id = process.customer_id ?? null
  form.customer_name = process.customer_name || ''
  form.requirement = process.requirement || ''
  form.sample_quantity = process.sample_quantity ?? 1
  form.test_month = toMonthInput(process.test_month) || currentPeriod()
  form.prepared_by = process.prepared_by || ''
  form.status = process.status || 'draft'
  form.internal_note = process.internal_note || ''
  steps.splice(0, steps.length, ...(process.steps || []).map(normalizeStep))
  code.value = process.code || ''
}

/** Lưu trình đang sửa, hoặc bộ bước của quy trình chuẩn được chọn khi tạo mới. */
async function loadInitialData() {
  if (isEdit.value) {
    fillFrom(await testProcessesApi.get(processId.value))
    return
  }
  if (!route.query.template) return
  const templates = await processTemplatesApi.list()
  const template = templates.find(item => item.id === Number(route.query.template))
  if (template) steps.splice(0, steps.length, ...(template.steps || []).map(normalizeStep))
}

onMounted(async () => {
  // Các danh mục không phụ thuộc lưu trình nên chạy song song, khỏi chờ hai nhịp
  const lookups = Promise.all([customersApi.list().then(list => { customers.value = list }), loadLookups()])
  try {
    await loadInitialData()
    savedSnapshot.value = JSON.stringify(buildPayload())
  } finally {
    loading.value = false
  }
  await lookups
})

const customerOptions = computed(() => customers.value.map(customer => ({ value: customer.name, id: customer.id })))

function pickCustomer(option) {
  form.customer_id = option.id ?? null
}

// Gõ tên khác tên khách trong danh mục thì bỏ liên kết, chỉ giữ chữ
watch(() => form.customer_name, (name) => {
  if (!form.customer_id) return
  const linked = customers.value.find(customer => customer.id === form.customer_id)
  if (linked && linked.name !== name) form.customer_id = null
})

// ---- Xem trước: dựng lại khi ngừng gõ ----
let previewTimer = null
let previewToken = 0

async function refreshPreview() {
  if (!canSave.value) {
    sheetHtml.value = ''
    return
  }
  const token = ++previewToken
  sheetLoading.value = true
  try {
    const html = await testProcessesApi.previewSheet(payload.value)
    if (token === previewToken) sheetHtml.value = html
  } catch {
    if (token === previewToken) sheetHtml.value = ''
  } finally {
    if (token === previewToken) sheetLoading.value = false
  }
}

// payload là computed dựng lại object mới mỗi lần form đổi nên watch thường là
// đủ; thêm deep chỉ khiến Vue duyệt lại cả cây bước sau từng phím gõ.
watch(payload, () => {
  clearTimeout(previewTimer)
  previewTimer = setTimeout(refreshPreview, 500)
}, { immediate: true })

onBeforeUnmount(() => clearTimeout(previewTimer))

function readError(error) {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map(item => item.msg?.replace(/^Value error, /, '')).join('. ')
  return 'Không lưu được lưu trình, thử lại giúp mình'
}

async function save({ thenPdf = false } = {}) {
  if (!canSave.value || saving.value) return
  saving.value = true
  errorMessage.value = ''
  try {
    const saved = isEdit.value
      ? await testProcessesApi.update(processId.value, payload.value)
      : await testProcessesApi.create(payload.value)
    savedSnapshot.value = JSON.stringify(payload.value)
    if (thenPdf) window.open(testProcessesApi.pdfUrl(saved.id, { download: true }), '_blank')
    router.push({ name: 'test-process-detail', params: { id: saved.id } })
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    saving.value = false
  }
}

function cancel() {
  if (dirty.value && !confirm('Bỏ các thay đổi chưa lưu?')) return
  if (isEdit.value) router.push({ name: 'test-process-detail', params: { id: processId.value } })
  else router.push({ name: 'test-processes' })
}
</script>

<template>
  <div class="font-lt flex flex-col flex-1 min-h-0 gap-3.5">
    <!-- Đầu trang -->
    <div class="flex flex-wrap items-end gap-3">
      <MenuButton />
      <div class="flex flex-col gap-0.5">
        <span class="text-[12.5px] text-lt-muted dark:text-slate-400">
          <RouterLink :to="{ name: 'test-processes' }" class="text-lt-muted hover:text-lt-tealink">Lưu trình test mẫu</RouterLink>
          / {{ isEdit ? code || 'Sửa' : 'Tạo mới' }}
        </span>
        <h1 class="text-[22px] font-semibold tracking-[-0.2px] text-lt-ink dark:text-slate-100">
          {{ isEdit ? 'Sửa lưu trình' : 'Tạo lưu trình' }}
        </h1>
      </div>

      <div class="flex-1" />

      <span class="flex items-center gap-1.5 text-[12.5px] text-lt-muted dark:text-slate-400">
        <template v-if="unsaved"><Clock class="w-[15px] h-[15px]" />Chưa lưu</template>
        <template v-else><Check class="w-[15px] h-[15px] text-lt-tealink" />Đã lưu</template>
      </span>

      <button type="button" class="h-[38px] px-4 rounded-[11px] text-[13.5px] font-medium text-lt-label dark:text-slate-300" @click="cancel">
        Hủy
      </button>
      <button
        type="button"
        class="flex items-center gap-1.5 h-[38px] px-4 rounded-[11px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-800 text-[13.5px] font-medium text-lt-body dark:text-slate-200 disabled:opacity-50"
        :disabled="!canSave || saving"
        @click="save({ thenPdf: true })"
      >
        <Download class="w-4 h-4" />Lưu và tải PDF
      </button>
      <button
        type="button"
        class="flex items-center gap-1.5 h-[38px] px-5 rounded-[11px] bg-lt-gradient text-white text-[13.5px] font-semibold shadow-lt-teal disabled:opacity-50"
        :disabled="!canSave || saving"
        @click="save()"
      >
        <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />Lưu
      </button>
    </div>

    <p v-if="errorMessage" class="px-4 py-2.5 rounded-xl bg-lt-void text-[12.5px] text-lt-voidink">{{ errorMessage }}</p>

    <div class="flex-1 min-h-0 flex gap-5">
      <!-- Form -->
      <div class="flex flex-col gap-5 w-full lg:w-[672px] lg:shrink-0 min-h-0 overflow-y-auto lt-surface p-5">
        <div v-if="loading" class="flex items-center gap-2 py-10 text-[13px] text-lt-faint">
          <Loader2 class="w-4 h-4 animate-spin" />Đang tải…
        </div>

        <template v-else>
          <div class="flex flex-col gap-3.5">
            <h2 class="text-[15px] font-semibold text-lt-ink dark:text-slate-100">Thông tin chung</h2>

            <div class="flex flex-wrap gap-3.5">
              <div class="flex flex-col gap-1.5 flex-1 min-w-[220px]">
                <label for="f-customer" class="lt-label">Khách hàng</label>
                <SuggestInput
                  v-model="form.customer_name"
                  :options="customerOptions"
                  input-id="f-customer"
                  placeholder="Tên khách hàng in lên phiếu"
                  @select="pickCustomer"
                />
              </div>
              <div class="flex flex-col gap-1.5 w-[132px]">
                <label for="f-quantity" class="lt-label">Số lượng mẫu</label>
                <input id="f-quantity" v-model.number="form.sample_quantity" type="number" min="1" class="lt-field" />
              </div>
            </div>

            <div class="flex flex-col gap-1.5">
              <label for="f-requirement" class="lt-label">Yêu cầu của khách</label>
              <textarea
                id="f-requirement"
                v-model="form.requirement"
                rows="2"
                placeholder="sản phẩm sau xử lý có màu xanh than-xanh xám"
                class="lt-field h-auto py-2.5 resize-none leading-[1.45]"
              />
            </div>

            <div class="flex flex-wrap gap-3.5">
              <div class="flex flex-col gap-1.5 w-[168px]">
                <label for="f-month" class="lt-label">Tháng test</label>
                <input id="f-month" v-model="form.test_month" type="month" class="lt-field" />
              </div>
              <div class="flex flex-col gap-1.5 flex-1 min-w-[180px]">
                <label for="f-prepared" class="lt-label">Người lập</label>
                <input id="f-prepared" v-model="form.prepared_by" type="text" placeholder="Vũ Thị Oanh" class="lt-field" />
              </div>
              <div class="flex flex-col gap-1.5 w-[160px]">
                <label for="f-status" class="lt-label">Trạng thái</label>
                <select id="f-status" v-model="form.status" class="lt-field">
                  <option v-for="status in STATUSES" :key="status.value" :value="status.value">{{ status.label }}</option>
                </select>
              </div>
            </div>

            <div class="flex flex-col gap-1.5">
              <label for="f-note" class="lt-label">
                Ghi chú nội bộ <span class="font-normal text-lt-faint">— không in lên phiếu</span>
              </label>
              <input
                id="f-note"
                v-model="form.internal_note"
                type="text"
                placeholder="Ví dụ: chờ khách duyệt màu trước khi chạy loạt đầu"
                class="lt-field"
              />
            </div>
          </div>

          <div class="h-px bg-lt-divider dark:bg-slate-700" />

          <StepListEditor
            :steps="steps"
            :products="products"
            :lab-chemicals="labChemicals"
            :operation-options="operationOptions"
          />
        </template>
      </div>

      <!-- Xem trước -->
      <div class="hidden lg:flex flex-col flex-1 min-w-0 min-h-0 lt-surface overflow-hidden">
        <div class="flex items-center justify-between h-[46px] px-[18px] border-b border-lt-divider dark:border-slate-700 shrink-0">
          <span class="text-[13px] font-semibold text-lt-ink dark:text-slate-100">Xem trước tờ in</span>
          <span class="flex items-center gap-1.5 text-[11.5px] text-lt-faint dark:text-slate-500">
            <span class="w-1.5 h-1.5 rounded-full" :class="sheetLoading ? 'bg-lt-teal animate-pulse' : 'bg-lt-teal'" />
            Cập nhật khi bạn ngừng gõ
          </span>
        </div>

        <SheetFrame
          :html="sheetHtml"
          :loading="sheetLoading"
          :zoom="zoom"
          empty-text="Nhập tên khách hàng và ít nhất một bước để xem trước"
        />

        <div class="flex items-center justify-between h-11 px-[18px] border-t border-lt-divider dark:border-slate-700 shrink-0">
          <span class="text-[12px] text-lt-muted dark:text-slate-400">A4 · 1 trang</span>
          <ZoomToggle v-model="zoom" />
        </div>
      </div>
    </div>
  </div>
</template>
