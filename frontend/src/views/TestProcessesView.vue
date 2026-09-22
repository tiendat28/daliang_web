<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Search, Loader2 } from 'lucide-vue-next'
import ProcessCard from '../components/test-processes/ProcessCard.vue'
import ProcessDetail from '../components/test-processes/ProcessDetail.vue'
import Modal from '../components/Modal.vue'
import MenuButton from '../components/layout/MenuButton.vue'
import { testProcessesApi, customersApi, companyProductsApi } from '../api/resources'
import { STATUSES } from '../constants/testProcess'
import { formatDateTime } from '../utils/format'
import { fromMonthInput } from '../utils/testProcessFormat'

// Màn hình chính của module: cột danh sách bên trái, tờ in bên phải.
// Trên điện thoại chỉ hiện một trong hai — có :id trên URL thì là trang chi tiết.
const route = useRoute()
const router = useRouter()

const PAGE_SIZE = 20

const items = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const loadingMore = ref(false)

const filters = ref({ q: '', status: '', customer_id: '', month: '', product_id: '' })
const sort = ref('-test_month')

const customers = ref([])
const products = ref([])

const selected = ref(null)
const detailLoading = ref(false)
const sheetHtml = ref('')
const sheetLoading = ref(false)
const busy = ref(false)

const templateName = ref('')
const templateDescription = ref('')
const showTemplateDialog = ref(false)
const savingTemplate = ref(false)
const templateError = ref('')

const SORTS = [
  { value: '-test_month', label: 'Tháng test mới nhất' },
  { value: 'test_month', label: 'Tháng test cũ nhất' },
  { value: '-updated_at', label: 'Vừa sửa gần đây' },
  { value: 'code', label: 'Mã lưu trình' },
]

const selectedId = computed(() => (route.params.id ? Number(route.params.id) : null))

const lastUpdated = computed(() => {
  const newest = items.value
    .map(item => item.updated_at)
    .filter(Boolean)
    .sort()
    .at(-1)
  return newest ? formatDateTime(newest) : ''
})

function queryParams(targetPage) {
  const { q, status, customer_id, month, product_id } = filters.value
  return {
    q: q.trim() || undefined,
    status: status || undefined,
    customer_id: customer_id || undefined,
    product_id: product_id || undefined,
    month_from: month ? fromMonthInput(month) : undefined,
    month_to: month ? fromMonthInput(month) : undefined,
    sort: sort.value,
    page: targetPage,
    page_size: PAGE_SIZE,
  }
}

async function load() {
  loading.value = true
  try {
    const data = await testProcessesApi.list(queryParams(1))
    items.value = data.items
    total.value = data.total
    page.value = 1
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (items.value.length >= total.value) return
  loadingMore.value = true
  try {
    const data = await testProcessesApi.list(queryParams(page.value + 1))
    items.value = [...items.value, ...data.items]
    total.value = data.total
    page.value += 1
  } finally {
    loadingMore.value = false
  }
}

async function loadDetail(id) {
  if (!id) {
    selected.value = null
    sheetHtml.value = ''
    return
  }
  detailLoading.value = true
  sheetLoading.value = true
  sheetHtml.value = ''
  // Hai lời gọi độc lập nhau: tờ in do backend tự dựng lại từ id
  const [detail, sheet] = await Promise.allSettled([
    testProcessesApi.get(id),
    testProcessesApi.sheet(id),
  ])
  if (detail.status === 'fulfilled') selected.value = detail.value
  sheetHtml.value = sheet.status === 'fulfilled' ? sheet.value : ''
  detailLoading.value = false
  sheetLoading.value = false
}

function select(item) {
  router.push({ name: 'test-process-detail', params: { id: item.id } })
}

watch(selectedId, id => loadDetail(id), { immediate: true })

let searchTimer = null
watch(() => filters.value.q, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => load(), 300)
})
watch([() => filters.value.status, () => filters.value.customer_id, () => filters.value.month, () => filters.value.product_id, sort], () => load())

onMounted(async () => {
  // Danh mục của bộ lọc không phụ thuộc danh sách nên tải song song
  const filters = Promise.all([
    customersApi.list().then(list => { customers.value = list }),
    companyProductsApi.list().then(list => { products.value = list }),
  ])
  await load()
  // Máy tính: chưa chọn gì thì mở sẵn lưu trình đầu danh sách cho đỡ trống
  if (!selectedId.value && items.value.length && window.innerWidth >= 768) {
    router.replace({ name: 'test-process-detail', params: { id: items.value[0].id } })
  }
  await filters
})

async function changeStatus(status) {
  const updated = await testProcessesApi.setStatus(selected.value.id, status)
  selected.value = updated
  const row = items.value.find(item => item.id === updated.id)
  if (row) row.status = updated.status
}

async function duplicate() {
  busy.value = true
  try {
    const copy = await testProcessesApi.duplicate(selected.value.id)
    await load()
    router.push({ name: 'test-process-detail', params: { id: copy.id } })
  } finally {
    busy.value = false
  }
}

async function remove() {
  if (!confirm(`Xóa lưu trình ${selected.value.code}? Bản ghi vẫn còn trong cơ sở dữ liệu, chỉ ẩn khỏi danh sách.`)) return
  await testProcessesApi.remove(selected.value.id)
  await load()
  router.replace({ name: 'test-processes' })
}

function openTemplateDialog() {
  templateName.value = ''
  templateDescription.value = ''
  templateError.value = ''
  showTemplateDialog.value = true
}

async function saveAsTemplate() {
  savingTemplate.value = true
  templateError.value = ''
  try {
    await testProcessesApi.saveAsTemplate(selected.value.id, {
      name: templateName.value,
      description: templateDescription.value || null,
    })
    showTemplateDialog.value = false
  } catch (error) {
    templateError.value = error.response?.data?.detail || 'Không lưu được quy trình chuẩn'
  } finally {
    savingTemplate.value = false
  }
}

function openPdf({ download }) {
  window.open(testProcessesApi.pdfUrl(selected.value.id, { download }), '_blank')
}
</script>

<template>
  <div class="font-lt flex flex-col flex-1 min-h-0 gap-3.5">
    <!-- Danh sách: ẩn trên điện thoại khi đang xem một lưu trình -->
    <div class="flex-col gap-3.5 flex-1 min-h-0" :class="selectedId ? 'hidden md:flex' : 'flex'">
      <div class="flex flex-wrap items-end gap-3">
        <MenuButton />
        <div class="flex flex-col gap-0.5">
          <h1 class="text-xl md:text-[22px] font-semibold tracking-[-0.2px] text-lt-ink dark:text-slate-100">Lưu trình test mẫu</h1>
          <span class="text-[12.5px] text-lt-muted dark:text-slate-400">
            {{ total }} lưu trình<template v-if="lastUpdated"> · cập nhật lần cuối {{ lastUpdated }}</template>
          </span>
        </div>

        <div class="flex-1" />

        <div class="flex items-center gap-2 w-full sm:w-72 h-10 px-3.5 bg-white dark:bg-slate-800 border border-lt-line dark:border-slate-600 rounded-xl">
          <Search class="w-[18px] h-[18px] text-lt-muted shrink-0" />
          <input
            v-model="filters.q"
            type="search"
            placeholder="Tìm mã, khách hàng, hóa chất…"
            aria-label="Tìm lưu trình"
            class="flex-1 min-w-0 bg-transparent border-none outline-none text-[13.5px] text-lt-ink dark:text-slate-100"
          />
        </div>

        <!-- Máy tính: nút nằm trên thanh công cụ; điện thoại: nút nổi ở đáy màn hình -->
        <button
          type="button"
          class="hidden md:flex items-center gap-2 h-10 px-4 rounded-xl bg-lt-gradient text-white text-[13.5px] font-semibold shadow-lt-accent"
          @click="router.push({ name: 'test-process-new' })"
        >
          <Plus class="w-[18px] h-[18px]" />Tạo lưu trình
        </button>
      </div>

      <div class="flex md:flex-wrap items-center gap-2 overflow-x-auto md:overflow-visible pb-0.5">
        <select v-model="filters.status" aria-label="Lọc theo trạng thái" class="h-[34px] shrink-0 px-3 rounded-[10px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-800 text-[13px] text-lt-body dark:text-slate-200">
          <option value="">Mọi trạng thái</option>
          <option v-for="status in STATUSES" :key="status.value" :value="status.value">{{ status.label }}</option>
        </select>
        <select v-model="filters.customer_id" aria-label="Lọc theo khách hàng" class="h-[34px] shrink-0 max-w-[190px] px-3 rounded-[10px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-800 text-[13px] text-lt-body dark:text-slate-200">
          <option value="">Mọi khách hàng</option>
          <option v-for="customer in customers" :key="customer.id" :value="customer.id">{{ customer.name }}</option>
        </select>
        <label class="flex items-center gap-2 h-[34px] shrink-0 px-3 rounded-[10px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-800 text-[13px] text-lt-body dark:text-slate-200">
          <span class="whitespace-nowrap">Tháng test</span>
          <input
            v-model="filters.month"
            type="month"
            aria-label="Lọc theo tháng test"
            class="w-[118px] bg-transparent border-none outline-none text-[13px] text-lt-body dark:text-slate-200"
          />
        </label>
        <select v-model="filters.product_id" aria-label="Lọc theo hóa chất" class="h-[34px] shrink-0 max-w-[170px] px-3 rounded-[10px] border border-lt-line dark:border-slate-600 bg-white dark:bg-slate-800 text-[13px] text-lt-body dark:text-slate-200">
          <option value="">Mọi hóa chất</option>
          <option v-for="product in products" :key="product.id" :value="product.id">{{ product.code }}</option>
        </select>
      </div>

      <div class="flex-1 min-h-0 flex gap-5">
        <!-- Cột danh sách -->
        <div class="flex flex-col w-full md:w-[372px] md:shrink-0 min-h-0 lt-surface overflow-hidden">
          <div class="flex items-center justify-between h-[46px] px-[18px] border-b border-lt-divider dark:border-slate-700 shrink-0">
            <span class="text-[12.5px] font-semibold text-lt-label dark:text-slate-300">{{ total }} lưu trình</span>
            <select v-model="sort" aria-label="Sắp xếp" class="bg-transparent border-none outline-none text-[12.5px] text-lt-muted dark:text-slate-400">
              <option v-for="option in SORTS" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </div>

          <div class="flex-1 min-h-0 overflow-y-auto">
            <div v-if="loading" class="flex items-center justify-center gap-2 py-12 text-[13px] text-lt-faint">
              <Loader2 class="w-4 h-4 animate-spin" />Đang tải…
            </div>

            <p v-else-if="!items.length" class="px-6 py-12 text-center text-[13px] text-lt-faint dark:text-slate-500">
              Chưa có lưu trình nào khớp bộ lọc.
            </p>

            <!-- Điện thoại: thẻ rời; máy tính: dòng liền nhau -->
            <div class="md:hidden flex flex-col gap-2.5 p-3 pb-24">
              <ProcessCard v-for="item in items" :key="item.id" :item="item" variant="card" @click="select(item)" />
            </div>
            <div class="hidden md:block">
              <ProcessCard
                v-for="item in items"
                :key="item.id"
                :item="item"
                :selected="item.id === selectedId"
                @click="select(item)"
              />
            </div>

            <div v-if="items.length < total" class="p-3">
              <button
                type="button"
                class="w-full h-9 rounded-[10px] border border-lt-line dark:border-slate-600 text-[12.5px] font-medium text-lt-body dark:text-slate-200 disabled:opacity-50"
                :disabled="loadingMore"
                @click="loadMore"
              >
                {{ loadingMore ? 'Đang tải…' : `Xem thêm (${total - items.length})` }}
              </button>
            </div>
          </div>
        </div>

        <!-- Chi tiết (máy tính) -->
        <ProcessDetail
          class="hidden md:flex"
          :process="selected"
          :sheet-html="sheetHtml"
          :sheet-loading="sheetLoading || detailLoading"
          :busy="busy"
          @edit="router.push({ name: 'test-process-edit', params: { id: selected.id } })"
          @duplicate="duplicate"
          @remove="remove"
          @status="changeStatus"
          @save-template="openTemplateDialog"
          @letterhead="router.push({ name: 'company-profile' })"
          @download="openPdf({ download: true })"
          @print="openPdf({ download: false })"
        />
      </div>
    </div>

    <button
      v-if="!selectedId"
      type="button"
      class="md:hidden fixed left-1/2 -translate-x-1/2 bottom-6 z-30 flex items-center gap-2 h-[50px] px-6 rounded-full bg-lt-gradient text-white text-[14.5px] font-semibold shadow-lt-fab"
      @click="router.push({ name: 'test-process-new' })"
    >
      <Plus class="w-[19px] h-[19px]" />Tạo lưu trình
    </button>

    <!-- Chi tiết (điện thoại) -->
    <ProcessDetail
      v-if="selectedId"
      class="md:hidden"
      :process="selected"
      :sheet-html="sheetHtml"
      :sheet-loading="sheetLoading || detailLoading"
      :busy="busy"
      @back="router.push({ name: 'test-processes' })"
      @edit="router.push({ name: 'test-process-edit', params: { id: selected.id } })"
      @duplicate="duplicate"
      @remove="remove"
      @status="changeStatus"
      @save-template="openTemplateDialog"
      @letterhead="router.push({ name: 'company-profile' })"
      @download="openPdf({ download: true })"
      @print="openPdf({ download: false })"
    />

    <Modal :show="showTemplateDialog" title="Lưu thành quy trình chuẩn" @close="showTemplateDialog = false">
      <div class="font-lt flex flex-col gap-4">
        <div class="flex flex-col gap-1.5">
          <label for="tpl-name" class="lt-label">Tên quy trình chuẩn</label>
          <input id="tpl-name" v-model="templateName" type="text" class="lt-field" placeholder="Mạ kẽm kiềm – thụ động – nhuộm màu" />
        </div>
        <div class="flex flex-col gap-1.5">
          <label for="tpl-desc" class="lt-label">Mô tả <span class="font-normal text-lt-faint">— không bắt buộc</span></label>
          <input id="tpl-desc" v-model="templateDescription" type="text" class="lt-field" placeholder="Dùng cho hàng cần màu xanh than." />
        </div>
        <p v-if="templateError" class="text-[12.5px] text-lt-voidink">{{ templateError }}</p>
        <div class="flex justify-end gap-2">
          <button type="button" class="lt-btn" @click="showTemplateDialog = false">Hủy</button>
          <button type="button" class="lt-btn-primary" :disabled="savingTemplate || !templateName.trim()" @click="saveAsTemplate">
            <Loader2 v-if="savingTemplate" class="w-[15px] h-[15px] animate-spin" />Lưu
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>
