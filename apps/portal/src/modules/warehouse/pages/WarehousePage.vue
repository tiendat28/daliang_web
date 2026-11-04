<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  AlertTriangle,
  ArrowDownToLine,
  ArrowUpFromLine,
  Boxes,
  Calendar,
  Check,
  Download,
  FileSpreadsheet,
  Info,
  MapPin,
  Package,
  Plus,
  Search,
  ShieldAlert,
  Trash2,
  Truck,
  X,
} from 'lucide-vue-next'
import Modal from '@/core/components/Modal.vue'
import FormActions from '@/core/components/FormActions.vue'
import AlertBanner from '@/core/components/AlertBanner.vue'
import { formatDate, formatNumber, formatExpiry } from '@/core/utils/format'
import { exportToCsv } from '@/core/utils/export'
import { getHazardBadges, QUICK_CHEMICAL_CATALOG } from '@/core/utils/chemical'
import { errorMessage } from '@/core/api/errors'
import client from '@/core/api/client'
import {
  createDispatch,
  createReceipt,
  getWarehouseDashboard,
  loadDispatch,
  pickDispatch,
} from '../api'

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const successMsg = ref('')

const dashboard = ref(null)
const stockLots = ref([])
const pendingDispatches = ref([])
const alerts = ref([])
const locations = ref([])
const customers = ref([])

const searchQuery = ref('')
const activeTab = ref('all') // all | finished | material | packaging

// Modals
const showReceiptModal = ref(false)
const showDispatchModal = ref(false)
const showPickModal = ref(false)
const showLoadModal = ref(false)
const showAlertModal = ref(false)
const activeAlert = ref(null)

// Forms
const receiptForm = ref({
  receipt_code: '',
  receipt_type: 'purchase',
  supplier_name: 'Công ty Hoá chất Á Châu',
  receipt_date: new Date().toISOString().slice(0, 10),
  note: '',
  items: [
    {
      product_code: 'NI-534C',
      product_name: 'Phụ gia mạ niken',
      category: 'finished',
      lot_number: 'L2609-06',
      expiration_date: '2027-09-30',
      location_code: 'A-02-3',
      quantity: 100,
      unit: 'kg',
      hazard_types: 'toxic',
    },
  ],
})

const dispatchForm = ref({
  dispatch_code: '',
  customer_name: '',
  customer_id: null,
  dispatch_date: new Date().toISOString().slice(0, 10),
  items_summary: '',
  receiver_name: '',
  note: '',
  items: [
    {
      product_code: 'NI-534C',
      product_name: 'Phụ gia mạ niken',
      lot_number: 'L2609-02',
      quantity: 50,
      unit: 'kg',
    },
  ],
})

const selectedDispatchForPick = ref(null)
const selectedDispatchForLoad = ref(null)
const loadForm = ref({
  driver_name: 'Nguyễn Văn Hùng',
  vehicle_plate: '59C-123.45',
  note: '',
})

// Metrics
const metrics = computed(() => {
  if (dashboard.value?.metrics) {
    return dashboard.value.metrics
  }
  return {
    total_items: 136,
    warehouses_count: 3,
    locations_count: 48,
    low_stock_count: 4,
    expiring_count: 6,
    today_dispatches_count: 9,
    pending_dispatches_count: 3,
  }
})

// Filtered stock items
const filteredStock = computed(() => {
  let list = stockLots.value || []
  if (activeTab.value !== 'all') {
    list = list.filter(item => item.category === activeTab.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter(
      item =>
        item.product_code?.toLowerCase().includes(q) ||
        item.product_name?.toLowerCase().includes(q) ||
        item.lot_number?.toLowerCase().includes(q) ||
        item.location_code?.toLowerCase().includes(q)
    )
  }
  return list
})

// Filtered pending dispatches
const filteredDispatches = computed(() => {
  let list = pendingDispatches.value || []
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter(
      d =>
        d.dispatch_code?.toLowerCase().includes(q) ||
        d.customer_name?.toLowerCase().includes(q) ||
        d.items_summary?.toLowerCase().includes(q)
    )
  }
  return list
})

// Progress bar color
function getProgressBarColor(percent) {
  if (percent >= 40) return '#0b7d72'
  if (percent >= 20) return '#d97706'
  return '#b42318'
}

// Load data
async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [dashRes, locRes, custRes] = await Promise.all([
      getWarehouseDashboard(),
      client.get('/warehouse/locations').catch(() => ({ data: [] })),
      client.get('/common/customers').catch(() => ({ data: [] })),
    ])
    dashboard.value = dashRes.data
    stockLots.value = dashRes.data.stock_lots || []
    pendingDispatches.value = dashRes.data.pending_dispatches || []
    alerts.value = dashRes.data.alerts || []
    locations.value = locRes.data || []
    customers.value = custRes.data || []
  } catch (err) {
    error.value = errorMessage(err) || 'Không thể tải dữ liệu kho'
  } finally {
    loading.value = false
  }
}

// Export to CSV/Excel
function exportExcel() {
  const headers = ['Mã hàng', 'Tên hàng', 'Phân loại', 'Số lô', 'Hạn dùng', 'Vị trí', 'Tồn kho', 'Đơn vị', 'Nguy hiểm', 'Mức tồn (%)']
  const rows = filteredStock.value.map(item => [
    item.product_code,
    item.product_name,
    item.category === 'finished' ? 'Thành phẩm' : item.category === 'material' ? 'Nguyên liệu' : 'Bao bì',
    item.lot_number,
    formatExpiry(item.expiration_date),
    item.location_code,
    item.quantity,
    item.unit,
    item.hazard_types || '—',
    `${item.stock_percent}%`,
  ])
  exportToCsv(`ton_kho_theo_lo_${new Date().toISOString().slice(0, 10)}.csv`, headers, rows)
}

// Receipt actions
function addReceiptItem() {
  receiptForm.value.items.push({
    product_code: '',
    product_name: '',
    category: 'finished',
    lot_number: '',
    expiration_date: '',
    location_code: 'A-01-1',
    quantity: 1,
    unit: 'kg',
    hazard_types: '',
  })
}

function removeReceiptItem(index) {
  if (receiptForm.value.items.length > 1) {
    receiptForm.value.items.splice(index, 1)
  }
}

async function handleSaveReceipt() {
  saving.value = true
  error.value = ''
  try {
    await createReceipt(receiptForm.value)
    showReceiptModal.value = false
    successMsg.value = 'Đã lập phiếu nhập kho thành công!'
    setTimeout(() => (successMsg.value = ''), 4000)
    await loadData()
  } catch (err) {
    error.value = errorMessage(err) || 'Lỗi khi lập phiếu nhập kho'
  } finally {
    saving.value = false
  }
}

// Dispatch actions
function addDispatchItem() {
  dispatchForm.value.items.push({
    product_code: '',
    product_name: '',
    lot_number: '',
    quantity: 1,
    unit: 'kg',
  })
}

function removeDispatchItem(index) {
  if (dispatchForm.value.items.length > 1) {
    dispatchForm.value.items.splice(index, 1)
  }
}

async function handleSaveDispatch() {
  saving.value = true
  error.value = ''
  try {
    await createDispatch(dispatchForm.value)
    showDispatchModal.value = false
    successMsg.value = 'Đã tạo phiếu xuất kho thành công!'
    setTimeout(() => (successMsg.value = ''), 4000)
    await loadData()
  } catch (err) {
    error.value = errorMessage(err) || 'Lỗi khi tạo phiếu xuất kho'
  } finally {
    saving.value = false
  }
}

// Pick action
function openPickModal() {
  const pending = pendingDispatches.value.find(d => d.status === 'pending')
  selectedDispatchForPick.value = pending || pendingDispatches.value[0] || null
  showPickModal.value = true
}

async function handleConfirmPick() {
  if (!selectedDispatchForPick.value) return
  saving.value = true
  error.value = ''
  try {
    await pickDispatch(selectedDispatchForPick.value.id)
    showPickModal.value = false
    successMsg.value = `Đã soạn xong hàng cho phiếu ${selectedDispatchForPick.value.dispatch_code}!`
    setTimeout(() => (successMsg.value = ''), 4000)
    await loadData()
  } catch (err) {
    error.value = errorMessage(err) || 'Lỗi khi cập nhật soạn hàng'
  } finally {
    saving.value = false
  }
}

// Load action
function openLoadModal() {
  const picked = pendingDispatches.value.find(d => d.status === 'picked')
  selectedDispatchForLoad.value = picked || pendingDispatches.value[0] || null
  showLoadModal.value = true
}

async function handleConfirmLoad() {
  if (!selectedDispatchForLoad.value) return
  saving.value = true
  error.value = ''
  try {
    await loadDispatch(selectedDispatchForLoad.value.id, loadForm.value)
    showLoadModal.value = false
    successMsg.value = `Đã bàn giao xe cho phiếu ${selectedDispatchForLoad.value.dispatch_code}!`
    setTimeout(() => (successMsg.value = ''), 4000)
    await loadData()
  } catch (err) {
    error.value = errorMessage(err) || 'Lỗi khi bàn giao xe'
  } finally {
    saving.value = false
  }
}

// Alert action
function handleAlertClick(alert) {
  activeAlert.value = alert
  showAlertModal.value = true
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="warehouse-container">
    <!-- Success / Error notification -->
    <AlertBanner
      :success-msg="successMsg"
      :error="error"
      @close-success="successMsg = ''"
      @close-error="error = ''"
    />

    <!-- Top Header -->
    <header class="top-header">
      <div class="header-left">
        <h1 class="page-title">Kho</h1>
      </div>

      <div class="header-right">
        <!-- Live Search -->
        <label class="search-box">
          <Search class="w-4 h-4 text-slate-400" />
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Tìm kiếm mã, tên, vị trí…"
          />
        </label>

        <!-- Notification Bell -->
        <button
          type="button"
          class="icon-btn relative"
          title="Cảnh báo an toàn và tồn kho"
          @click="showAlertModal = true"
        >
          <Info class="w-4 h-4" />
          <span
            v-if="alerts.length > 0"
            class="absolute top-2 right-2 w-2 h-2 rounded-full bg-rose-500"
          ></span>
        </button>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <button
            type="button"
            class="btn-secondary"
            @click="showReceiptModal = true"
          >
            <Plus class="w-4 h-4" />
            <span>Phiếu nhập</span>
          </button>

          <button
            type="button"
            class="btn-primary"
            @click="showDispatchModal = true"
          >
            <Plus class="w-4 h-4" />
            <span>Phiếu xuất</span>
          </button>
        </div>
      </div>
    </header>

    <!-- 4 KPI Stat Cards -->
    <div class="kpi-grid">
      <!-- Card 1: Mã hàng đang lưu -->
      <div class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-text">
            <span class="kpi-label">Mã hàng đang lưu</span>
            <span class="kpi-value text-slate-900 dark:text-slate-100">[{{ metrics.total_items }}]</span>
            <span class="kpi-subtext">{{ metrics.warehouses_count }} kho · {{ metrics.locations_count }} vị trí</span>
          </div>
          <div class="kpi-icon-wrap bg-[#d3f4ee] dark:bg-teal-900/40 text-[#0f5f56] dark:text-teal-300">
            <Boxes class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Card 2: Dưới mức tối thiểu -->
      <div class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-text">
            <span class="kpi-label">Dưới mức tối thiểu</span>
            <span class="kpi-value text-rose-600 dark:text-rose-400">[{{ metrics.low_stock_count }}]</span>
            <span class="kpi-subtext text-rose-600 dark:text-rose-400 font-medium">cần đặt thêm</span>
          </div>
          <div class="kpi-icon-wrap bg-[#fde4e4] dark:bg-rose-900/40 text-[#9b1c1c] dark:text-rose-300">
            <AlertTriangle class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Card 3: Sắp hết hạn dùng -->
      <div class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-text">
            <span class="kpi-label">Sắp hết hạn dùng</span>
            <span class="kpi-value text-amber-600 dark:text-amber-400">[{{ metrics.expiring_count }}]</span>
            <span class="kpi-subtext">trong 60 ngày</span>
          </div>
          <div class="kpi-icon-wrap bg-[#fdf0cf] dark:bg-amber-900/40 text-[#8a4b08] dark:text-amber-300">
            <Calendar class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Card 4: Phiếu xuất hôm nay -->
      <div class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-text">
            <span class="kpi-label">Phiếu xuất hôm nay</span>
            <span class="kpi-value text-sky-700 dark:text-sky-300">[{{ metrics.today_dispatches_count }}]</span>
            <span class="kpi-subtext">{{ metrics.pending_dispatches_count }} chờ soạn</span>
          </div>
          <div class="kpi-icon-wrap bg-[#e0f0fb] dark:bg-sky-900/40 text-[#0b5a85] dark:text-sky-300">
            <Truck class="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Area: Left Table & Right Widget Column -->
    <div class="main-layout">
      <!-- Left Column: Tồn kho theo lô -->
      <div class="main-card left-column">
        <div class="card-header">
          <h2 class="card-title">Tồn kho theo lô</h2>

          <div class="filter-actions">
            <!-- Tabs -->
            <div class="tab-pill-group">
              <button
                type="button"
                :class="['tab-pill', { active: activeTab === 'all' }]"
                @click="activeTab = 'all'"
              >
                Tất cả
              </button>
              <button
                type="button"
                :class="['tab-pill', { active: activeTab === 'finished' }]"
                @click="activeTab = 'finished'"
              >
                Thành phẩm
              </button>
              <button
                type="button"
                :class="['tab-pill', { active: activeTab === 'material' }]"
                @click="activeTab = 'material'"
              >
                Nguyên liệu
              </button>
              <button
                type="button"
                :class="['tab-pill', { active: activeTab === 'packaging' }]"
                @click="activeTab = 'packaging'"
              >
                Bao bì
              </button>
            </div>

            <!-- Xuất Excel -->
            <button
              type="button"
              class="btn-secondary"
              @click="exportExcel"
            >
              <Download class="w-4 h-4" />
              <span>Xuất Excel</span>
            </button>
          </div>
        </div>

        <!-- Table -->
        <div class="table-wrap">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Mã hàng</th>
                <th>Tên hàng</th>
                <th>Hạn dùng</th>
                <th>Vị trí</th>
                <th>Tồn</th>
                <th>Nguy hiểm</th>
                <th>Mức tồn</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center py-8 text-slate-500">
                  Đang tải dữ liệu tồn kho...
                </td>
              </tr>
              <tr v-else-if="filteredStock.length === 0">
                <td colspan="7" class="text-center py-8 text-slate-500">
                  Không tìm thấy mặt hàng nào phù hợp.
                </td>
              </tr>
              <tr v-for="item in filteredStock" :key="item.id">
                <!-- Mã hàng -->
                <td class="font-mono font-semibold text-slate-900 dark:text-slate-100">
                  {{ item.product_code }}
                </td>

                <!-- Tên hàng -->
                <td>
                  <div class="flex flex-col gap-0.5">
                    <span class="font-semibold text-slate-900 dark:text-slate-100">{{ item.product_name }}</span>
                    <span class="text-xs text-slate-500 dark:text-slate-400">
                      {{ item.category === 'finished' ? 'Thành phẩm' : item.category === 'material' ? 'Nguyên liệu' : 'Bao bì' }}
                      · lô {{ item.lot_number }}
                    </span>
                  </div>
                </td>

                <!-- Hạn dùng -->
                <td class="text-slate-600 dark:text-slate-300">
                  {{ formatExpiry(item.expiration_date) }}
                </td>

                <!-- Vị trí -->
                <td class="font-mono text-slate-700 dark:text-slate-300">
                  {{ item.location_code }}
                </td>

                <!-- Tồn -->
                <td>
                  <b class="text-slate-900 dark:text-slate-100 font-semibold">{{ formatNumber(item.quantity) }}</b>
                  <span class="text-slate-500 dark:text-slate-400 text-xs ml-1">{{ item.unit }}</span>
                </td>

                <!-- Nguy hiểm -->
                <td>
                  <div class="flex flex-wrap gap-1">
                    <template v-if="getHazardBadges(item.hazard_types).length">
                      <span
                        v-for="(badge, bIdx) in getHazardBadges(item.hazard_types)"
                        :key="bIdx"
                        class="hazard-pill"
                        :class="badge.cls"
                      >
                        {{ badge.label }}
                      </span>
                    </template>
                    <span v-else class="text-slate-400 dark:text-slate-500">—</span>
                  </div>
                </td>

                <!-- Mức tồn -->
                <td>
                  <div class="flex items-center gap-2">
                    <div class="progress-bar-wrap">
                      <div
                        class="progress-bar-fill"
                        :style="{
                          width: `${item.stock_percent}%`,
                          backgroundColor: getProgressBarColor(item.stock_percent),
                        }"
                      ></div>
                    </div>
                    <span class="text-xs text-slate-500 dark:text-slate-400 font-mono">{{ item.stock_percent }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Right Column (340px) -->
      <div class="right-column">
        <!-- Card 1: Phiếu xuất chờ xử lý -->
        <div class="main-card">
          <div class="card-header mb-3">
            <h2 class="card-title">Phiếu xuất chờ xử lý</h2>
            <button
              type="button"
              class="text-xs font-semibold text-teal-700 hover:text-teal-800"
              @click="showDispatchModal = true"
            >
              Tất cả
            </button>
          </div>

          <div class="divide-y divide-slate-100 dark:divide-slate-700/60">
            <div
              v-for="disp in filteredDispatches"
              :key="disp.id"
              class="py-3 flex flex-col gap-1.5"
            >
              <div class="flex items-center justify-between">
                <span class="font-mono font-bold text-slate-900 dark:text-slate-100 text-xs">
                  {{ disp.dispatch_code }}
                </span>
                <span
                  v-if="disp.status === 'pending'"
                  class="status-badge bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300"
                >
                  Chờ soạn
                </span>
                <span
                  v-else-if="disp.status === 'picked'"
                  class="status-badge bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300"
                >
                  Đã soạn
                </span>
                <span
                  v-else-if="disp.status === 'loaded'"
                  class="status-badge bg-teal-50 dark:bg-teal-950/60 text-teal-700 dark:text-teal-300"
                >
                  Đã giao xe
                </span>
                <span
                  v-else
                  class="status-badge bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300"
                >
                  Hoàn thành
                </span>
              </div>
              <span class="text-sm font-semibold text-slate-900 dark:text-slate-100">{{ disp.customer_name }}</span>
              <span class="text-xs text-slate-500 dark:text-slate-400">{{ disp.items_summary }}</span>
            </div>
          </div>

          <!-- Bottom Action Buttons in Card 1 -->
          <div class="flex gap-2 mt-4 pt-2">
            <button
              type="button"
              class="btn-pick"
              @click="openPickModal"
            >
              <Package class="w-4 h-4" />
              <span>Soạn hàng</span>
            </button>
            <button
              type="button"
              class="btn-primary flex-1 justify-center"
              @click="openLoadModal"
            >
              <Truck class="w-4 h-4" />
              <span>Giao cho xe</span>
            </button>
          </div>
        </div>

        <!-- Card 2: Cảnh báo -->
        <div class="main-card">
          <div class="card-header mb-3">
            <h2 class="card-title">Cảnh báo</h2>
          </div>

          <div class="divide-y divide-slate-100 dark:divide-slate-700/60">
            <div
              v-for="alt in alerts"
              :key="alt.id || alt.title"
              class="py-3 flex items-center justify-between gap-2.5 cursor-pointer hover:bg-slate-50/50 dark:hover:bg-slate-700/40 rounded-lg px-1 transition-colors"
              @click="handleAlertClick(alt)"
            >
              <div class="flex flex-col gap-0.5 min-w-0">
                <span class="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                  {{ alt.title }}
                </span>
                <span class="text-xs text-slate-500 dark:text-slate-400">
                  {{ alt.description }}
                </span>
              </div>

              <span
                v-if="alt.badge_type === 'red'"
                class="status-badge bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 flex-shrink-0"
              >
                {{ alt.badge }}
              </span>
              <span
                v-else-if="alt.badge_type === 'purple'"
                class="status-badge bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 flex-shrink-0"
              >
                {{ alt.badge }}
              </span>
              <span
                v-else
                class="status-badge bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300 flex-shrink-0"
              >
                {{ alt.badge }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL 1: Lập phiếu nhập kho -->
    <Modal
      v-if="showReceiptModal"
      title="Lập phiếu nhập kho"
      size="lg"
      @close="showReceiptModal = false"
    >
      <form class="space-y-4" @submit.prevent="handleSaveReceipt">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label class="form-label">Loại nhập</label>
            <select v-model="receiptForm.receipt_type" class="form-input">
              <option value="purchase">Mua hàng từ NCC</option>
              <option value="production">Nhập thành phẩm pha chế</option>
              <option value="return">Khách hàng trả lại</option>
            </select>
          </div>
          <div>
            <label class="form-label">Nhà cung cấp / Nguồn hàng</label>
            <input
              v-model="receiptForm.supplier_name"
              type="text"
              class="form-input"
              placeholder="VD: Công ty Hoá chất Á Châu"
              required
            />
          </div>
          <div>
            <label class="form-label">Ngày nhập kho</label>
            <input
              v-model="receiptForm.receipt_date"
              type="date"
              class="form-input"
              required
            />
          </div>
        </div>

        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="font-semibold text-sm text-slate-800 dark:text-slate-200">Danh mục hàng hoá chất nhập</span>
            <button
              type="button"
              class="text-xs text-teal-700 dark:text-teal-400 font-semibold hover:underline flex items-center gap-1"
              @click="addReceiptItem"
            >
              <Plus class="w-3.5 h-3.5" /> Thêm dòng
            </button>
          </div>

          <div class="space-y-2 max-h-64 overflow-y-auto pr-1">
            <div
              v-for="(it, idx) in receiptForm.items"
              :key="idx"
              class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-700/40 grid grid-cols-1 md:grid-cols-6 gap-2 items-center"
            >
              <div class="md:col-span-1">
                <input
                  v-model="it.product_code"
                  type="text"
                  placeholder="Mã SP"
                  class="form-input text-xs"
                  required
                />
              </div>
              <div class="md:col-span-2">
                <input
                  v-model="it.product_name"
                  type="text"
                  placeholder="Tên sản phẩm"
                  class="form-input text-xs"
                  required
                />
              </div>
              <div>
                <input
                  v-model="it.lot_number"
                  type="text"
                  placeholder="Số lô (VD: L2609-02)"
                  class="form-input text-xs"
                  required
                />
              </div>
              <div>
                <input
                  v-model="it.location_code"
                  type="text"
                  placeholder="Vị trí (A-02-3)"
                  class="form-input text-xs"
                  required
                />
              </div>
              <div class="flex items-center gap-1">
                <input
                  v-model.number="it.quantity"
                  type="number"
                  placeholder="SL"
                  min="0.1"
                  step="any"
                  class="form-input text-xs flex-1 min-w-[70px] md:w-20"
                  required
                />
                <select v-model="it.unit" class="form-input text-xs w-16">
                  <option value="kg">kg</option>
                  <option value="can">can</option>
                  <option value="cái">cái</option>
                  <option value="lít">lít</option>
                </select>
                <button
                  type="button"
                  class="text-slate-400 hover:text-red-500 p-1"
                  @click="removeReceiptItem(idx)"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="form-label">Ghi chú phiếu nhập</label>
          <textarea
            v-model="receiptForm.note"
            rows="2"
            class="form-input"
            placeholder="Kiểm tra bao bì niêm phong đạt chuẩn..."
          ></textarea>
        </div>

        <FormActions
          :loading="saving"
          submit-text="Lưu phiếu nhập"
          @cancel="showReceiptModal = false"
        />
      </form>
    </Modal>

    <!-- MODAL 2: Lập phiếu xuất kho -->
    <Modal
      v-if="showDispatchModal"
      title="Lập phiếu xuất kho"
      size="lg"
      @close="showDispatchModal = false"
    >
      <form class="space-y-4" @submit.prevent="handleSaveDispatch">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="form-label">Khách hàng nhận hàng</label>
            <input
              v-model="dispatchForm.customer_name"
              type="text"
              class="form-input"
              placeholder="VD: Xi mạ Tân Phú"
              required
            />
          </div>
          <div>
            <label class="form-label">Ngày xuất kho</label>
            <input
              v-model="dispatchForm.dispatch_date"
              type="date"
              class="form-input"
              required
            />
          </div>
        </div>

        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="font-semibold text-sm text-slate-800 dark:text-slate-200">
              Danh mục hoá chất xuất (Ưu tiên FEFO - Lô cận date)
            </span>
            <button
              type="button"
              class="text-xs text-teal-700 dark:text-teal-400 font-semibold hover:underline flex items-center gap-1"
              @click="addDispatchItem"
            >
              <Plus class="w-3.5 h-3.5" /> Thêm dòng
            </button>
          </div>

          <div class="space-y-2 max-h-64 overflow-y-auto pr-1">
            <div
              v-for="(it, idx) in dispatchForm.items"
              :key="idx"
              class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-700/40 grid grid-cols-1 md:grid-cols-5 gap-2 items-center"
            >
              <div>
                <input
                  v-model="it.product_code"
                  type="text"
                  placeholder="Mã SP (NI-534C)"
                  class="form-input text-xs"
                  required
                />
              </div>
              <div class="md:col-span-2">
                <input
                  v-model="it.product_name"
                  type="text"
                  placeholder="Tên sản phẩm"
                  class="form-input text-xs"
                  required
                />
              </div>
              <div>
                <input
                  v-model="it.lot_number"
                  type="text"
                  placeholder="Lô xuất (FEFO)"
                  class="form-input text-xs"
                  required
                />
              </div>
              <div class="flex items-center gap-1">
                <input
                  v-model.number="it.quantity"
                  type="number"
                  min="0.1"
                  step="any"
                  placeholder="SL"
                  class="form-input text-xs flex-1 min-w-[70px] md:w-20"
                  required
                />
                <select v-model="it.unit" class="form-input text-xs w-16">
                  <option value="kg">kg</option>
                  <option value="can">can</option>
                  <option value="lít">lít</option>
                </select>
                <button
                  type="button"
                  class="text-slate-400 hover:text-red-500 p-1"
                  @click="removeDispatchItem(idx)"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="form-label">Ghi chú giao hàng</label>
          <textarea
            v-model="dispatchForm.note"
            rows="2"
            class="form-input"
            placeholder="Ghi chú đóng gói, xe giao..."
          ></textarea>
        </div>

        <FormActions
          :loading="saving"
          submit-text="Lưu phiếu xuất"
          @cancel="showDispatchModal = false"
        />
      </form>
    </Modal>

    <!-- MODAL 3: Soạn hàng -->
    <Modal
      v-if="showPickModal"
      title="Soạn hàng cho phiếu xuất"
      size="md"
      @close="showPickModal = false"
    >
      <div v-if="selectedDispatchForPick" class="space-y-4">
        <div class="p-3 bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800/60 rounded-xl">
          <div class="flex justify-between items-center mb-1">
            <span class="font-mono font-bold text-amber-900 dark:text-amber-300">
              {{ selectedDispatchForPick.dispatch_code }}
            </span>
            <span class="status-badge bg-amber-200 dark:bg-amber-900/60 text-amber-900 dark:text-amber-200">Chờ soạn</span>
          </div>
          <div class="text-sm font-semibold text-slate-900 dark:text-slate-100">
            Khách: {{ selectedDispatchForPick.customer_name }}
          </div>
          <div class="text-xs text-slate-600 dark:text-slate-400 mt-1">
            {{ selectedDispatchForPick.items_summary }}
          </div>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400 mb-2">Vị trí lấy hàng gợi ý</h4>
          <div class="space-y-2">
            <div
              v-for="it in selectedDispatchForPick.items"
              :key="it.id"
              class="flex items-center justify-between p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
            >
              <div>
                <span class="font-mono font-bold text-sm text-slate-900 dark:text-slate-100">{{ it.product_code }}</span>
                <span class="text-xs text-slate-500 dark:text-slate-400 block">{{ it.product_name }}</span>
              </div>
              <div class="text-right">
                <span class="font-mono font-semibold text-teal-700 dark:text-teal-300 bg-teal-50 dark:bg-teal-950/60 px-2 py-0.5 rounded">
                  Kệ A-02-3
                </span>
                <span class="text-xs text-slate-600 dark:text-slate-400 block mt-0.5">
                  {{ it.quantity }} {{ it.unit }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            class="btn-secondary"
            @click="showPickModal = false"
          >
            Đóng
          </button>
          <button
            type="button"
            class="btn-primary"
            :disabled="saving"
            @click="handleConfirmPick"
          >
            <Check class="w-4 h-4" />
            <span>Xác nhận đã soạn xong</span>
          </button>
        </div>
      </div>
      <div v-else class="text-center py-6 text-slate-500">
        Hiện không có phiếu xuất nào ở trạng thái chờ soạn.
      </div>
    </Modal>

    <!-- MODAL 4: Giao xe -->
    <Modal
      v-if="showLoadModal"
      title="Bàn giao hàng cho xe tải"
      size="md"
      @close="showLoadModal = false"
    >
      <div v-if="selectedDispatchForLoad" class="space-y-4">
        <div class="p-3 bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800/60 rounded-xl">
          <div class="flex justify-between items-center mb-1">
            <span class="font-mono font-bold text-sky-900 dark:text-sky-300">
              {{ selectedDispatchForLoad.dispatch_code }}
            </span>
            <span class="status-badge bg-sky-200 dark:bg-sky-900/60 text-sky-900 dark:text-sky-200">Đã soạn</span>
          </div>
          <div class="text-sm font-semibold text-slate-900 dark:text-slate-100">
            Khách: {{ selectedDispatchForLoad.customer_name }}
          </div>
          <div class="text-xs text-slate-600 dark:text-slate-400 mt-1">
            {{ selectedDispatchForLoad.items_summary }}
          </div>
        </div>

        <div class="space-y-3">
          <div>
            <label class="form-label">Tên tài xế phụ trách</label>
            <input
              v-model="loadForm.driver_name"
              type="text"
              class="form-input"
              placeholder="Nguyễn Văn Hùng"
              required
            />
          </div>
          <div>
            <label class="form-label">Biển số xe giao hàng</label>
            <input
              v-model="loadForm.vehicle_plate"
              type="text"
              class="form-input"
              placeholder="59C-123.45"
              required
            />
          </div>
          <div>
            <label class="form-label">Ghi chú bàn giao</label>
            <textarea
              v-model="loadForm.note"
              rows="2"
              class="form-input"
              placeholder="Đã kiểm tra tem nhãn và biên bản giao nhận..."
            ></textarea>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            class="btn-secondary"
            @click="showLoadModal = false"
          >
            Hủy
          </button>
          <button
            type="button"
            class="btn-primary"
            :disabled="saving"
            @click="handleConfirmLoad"
          >
            <Truck class="w-4 h-4" />
            <span>Xác nhận giao cho xe</span>
          </button>
        </div>
      </div>
    </Modal>

    <!-- MODAL 5: Chi tiết cảnh báo & Đặt thêm -->
    <Modal
      v-if="showAlertModal"
      title="Chi tiết Cảnh báo Kho & An toàn Hoá chất"
      size="md"
      @close="showAlertModal = false"
    >
      <div v-if="activeAlert" class="space-y-4">
        <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/70 flex items-start gap-3">
          <ShieldAlert class="w-6 h-6 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 class="font-bold text-slate-900 dark:text-slate-100 text-base">{{ activeAlert.title }}</h3>
            <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">{{ activeAlert.description }}</p>
          </div>
        </div>

        <div class="p-3 bg-blue-50 dark:bg-blue-950/60 border border-blue-100 dark:border-blue-900/60 rounded-xl text-xs text-blue-800 dark:text-blue-300 leading-relaxed">
          <b>Quy định an toàn Daliang:</b> Hóa chất nhóm Oxy hoá mạnh (như CrO3) phải bảo quản cách ly hoàn toàn khỏi khu vực chứa dung môi và hóa chất hữu cơ. Tuân thủ nghiêm ngặt nguyên tắc FEFO (hạn dùng gần nhất xuất trước).
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            class="btn-secondary"
            @click="showAlertModal = false"
          >
            Đóng
          </button>
          <button
            type="button"
            class="btn-primary"
            @click="
              showReceiptModal = true;
              showAlertModal = false;
            "
          >
            <Plus class="w-4 h-4" />
            <span>Lên phiếu đặt thêm</span>
          </button>
        </div>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="alt in alerts"
          :key="alt.title"
          class="p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
        >
          <div class="flex justify-between items-center">
            <span class="font-semibold text-slate-900 dark:text-slate-100 text-sm">{{ alt.title }}</span>
            <span class="status-badge bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300">{{ alt.badge }}</span>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ alt.description }}</p>
        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped>
.warehouse-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.bg-mint-light {
  @apply bg-emerald-50 dark:bg-emerald-950/60;
}
.text-mint-dark {
  @apply text-emerald-700 dark:text-emerald-300;
}

/* Layout */
.main-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}
@media (max-width: 1100px) {
  .main-layout {
    flex-direction: column;
  }
}
.left-column {
  flex: 1 1 0;
  min-width: 0;
}
.right-column {
  width: 340px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
@media (max-width: 1100px) {
  .right-column {
    width: 100%;
  }
}

.hazard-pill {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}
</style>
