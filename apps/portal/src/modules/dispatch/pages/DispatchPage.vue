<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  AlertTriangle,
  Car,
  Check,
  CheckCircle2,
  Clock,
  FileImage,
  Info,
  MapPin,
  Navigation,
  Plus,
  Search,
  ShieldAlert,
  Truck,
  UserCheck,
  UserPlus,
  Users,
  X,
} from 'lucide-vue-next'
import Modal from '@/core/components/Modal.vue'
import FormActions from '@/core/components/FormActions.vue'
import AlertBanner from '@/core/components/AlertBanner.vue'
import { errorMessage } from '@/core/api/errors'
import { initials as getInitials } from '@/core/utils/format'
import {
  assignTrip,
  createTrip,
  createVehicle,
  getDispatchDashboard,
  getDrivers,
  getVehicles,
  updateTripStatus,
} from '../api'

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const successMsg = ref('')

const dashboard = ref(null)
const drivers = ref([])
const vehicles = ref([])
const trips = ref({
  unassigned: [],
  delivering: [],
  delivered: [],
  issue: [],
})

const searchQuery = ref('')

// Modals
const showCreateTripModal = ref(false)
const showAssignModal = ref(false)
const showTripDetailModal = ref(false)
const showVehiclesModal = ref(false)

const selectedTripForAssign = ref(null)
const selectedTripDetail = ref(null)

// Forms
const createTripForm = ref({
  dispatch_code: '',
  customer_name: '',
  customer_address: '',
  items_summary: '',
  is_hazardous: true,
  driver_id: null,
  vehicle_id: null,
  estimated_time: '',
  trip_date: new Date().toISOString().slice(0, 10),
})

const assignForm = ref({
  driver_id: null,
  vehicle_id: null,
  estimated_time: 'Dự kiến 11:30',
})

const statusForm = ref({
  status: 'delivered',
  issue_note: '',
  proof_image_url: '',
  estimated_time: '',
})

const newVehicleForm = ref({
  plate_number: '',
  vehicle_type: 'Xe tải 1.5 tấn',
  max_payload_kg: 1500,
  hazard_permit_expiry: '2027-12-31',
  status: 'active',
  notes: '',
})

// Metrics
const metrics = computed(() => {
  if (dashboard.value?.metrics) {
    return dashboard.value.metrics
  }
  return {
    trips_today: 6,
    delivering_count: 2,
    delivered_count: 1,
    issues_count: 1,
  }
})

// Filtered lists for Kanban
function filterList(list) {
  if (!list) return []
  if (!searchQuery.value.trim()) return list
  const q = searchQuery.value.trim().toLowerCase()
  return list.filter(
    t =>
      t.dispatch_code?.toLowerCase().includes(q) ||
      t.customer_name?.toLowerCase().includes(q) ||
      t.items_summary?.toLowerCase().includes(q) ||
      t.driver_name?.toLowerCase().includes(q) ||
      t.customer_address?.toLowerCase().includes(q)
  )
}

const filteredUnassigned = computed(() => filterList(trips.value.unassigned))
const filteredDelivering = computed(() => filterList(trips.value.delivering))
const filteredDelivered = computed(() => filterList(trips.value.delivered))
const filteredIssue = computed(() => filterList(trips.value.issue))

// Load data
async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [dashRes, vehRes, drvRes] = await Promise.all([
      getDispatchDashboard(),
      getVehicles().catch(() => ({ data: [] })),
      getDrivers().catch(() => ({ data: [] })),
    ])
    dashboard.value = dashRes.data
    drivers.value = dashRes.data.drivers || []
    trips.value = dashRes.data.trips || {
      unassigned: [],
      delivering: [],
      delivered: [],
      issue: [],
    }
    vehicles.value = vehRes.data || []
    if (drvRes.data?.length) {
      drivers.value = drvRes.data
    }
  } catch (err) {
    error.value = errorMessage(err) || 'Không thể tải dữ liệu điều phối'
  } finally {
    loading.value = false
  }
}

// Open Assign Modal
function openAssignModal(trip) {
  selectedTripForAssign.value = trip
  const readyDriver = drivers.value.find(d => d.status === 'ready') || drivers.value[0]
  assignForm.value.driver_id = readyDriver?.id || null
  assignForm.value.vehicle_id = readyDriver?.default_vehicle_id || null
  assignForm.value.estimated_time = 'Dự kiến 11:30'
  showAssignModal.value = true
}

// Submit Assign
async function handleAssignTrip() {
  if (!selectedTripForAssign.value || !assignForm.value.driver_id) return
  saving.value = true
  error.value = ''
  try {
    await assignTrip(selectedTripForAssign.value.id, assignForm.value)
    showAssignModal.value = false
    successMsg.value = `Đã phân công tài xế cho chuyến ${selectedTripForAssign.value.dispatch_code}!`
    setTimeout(() => (successMsg.value = ''), 4000)
    await loadData()
  } catch (err) {
    error.value = errorMessage(err) || 'Lỗi khi phân công chuyến giao'
  } finally {
    saving.value = false
  }
}

// Open Trip Detail
function openTripDetail(trip) {
  selectedTripDetail.value = trip
  statusForm.value.status = trip.status
  statusForm.value.issue_note = trip.issue_note || ''
  statusForm.value.proof_image_url = trip.proof_image_url || ''
  statusForm.value.estimated_time = trip.estimated_time || ''
  showTripDetailModal.value = true
}

// Submit Trip Status Update
async function handleUpdateTripStatus() {
  if (!selectedTripDetail.value) return
  saving.value = true
  error.value = ''
  try {
    await updateTripStatus(selectedTripDetail.value.id, statusForm.value)
    showTripDetailModal.value = false
    successMsg.value = `Đã cập nhật trạng thái chuyến ${selectedTripDetail.value.dispatch_code}!`
    setTimeout(() => (successMsg.value = ''), 4000)
    await loadData()
  } catch (err) {
    error.value = errorMessage(err) || 'Lỗi khi cập nhật trạng thái'
  } finally {
    saving.value = false
  }
}

// Submit Create Trip
async function handleCreateTrip() {
  saving.value = true
  error.value = ''
  try {
    await createTrip(createTripForm.value)
    showCreateTripModal.value = false
    successMsg.value = 'Đã tạo chuyến giao hàng mới!'
    setTimeout(() => (successMsg.value = ''), 4000)
    createTripForm.value = {
      dispatch_code: '',
      customer_name: '',
      customer_address: '',
      items_summary: '',
      is_hazardous: true,
      driver_id: null,
      vehicle_id: null,
      estimated_time: '',
      trip_date: new Date().toISOString().slice(0, 10),
    }
    await loadData()
  } catch (err) {
    error.value = errorMessage(err) || 'Lỗi khi tạo chuyến giao'
  } finally {
    saving.value = false
  }
}

// Add Vehicle
async function handleAddVehicle() {
  saving.value = true
  error.value = ''
  try {
    await createVehicle(newVehicleForm.value)
    successMsg.value = `Đã thêm xe ${newVehicleForm.value.plate_number} vào đội xe!`
    setTimeout(() => (successMsg.value = ''), 4000)
    newVehicleForm.value = {
      plate_number: '',
      vehicle_type: 'Xe tải 1.5 tấn',
      max_payload_kg: 1500,
      hazard_permit_expiry: '2027-12-31',
      status: 'active',
      notes: '',
    }
    const vehRes = await getVehicles()
    vehicles.value = vehRes.data || []
  } catch (err) {
    error.value = errorMessage(err) || 'Lỗi khi thêm xe'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="dispatch-container">
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
        <h1 class="page-title">Bảng điều phối giao hàng</h1>
      </div>

      <div class="header-right">
        <!-- Live Search -->
        <label class="search-box">
          <Search class="w-4 h-4 text-slate-400" />
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Tìm kiếm phiếu, khách, tài xế…"
          />
        </label>

        <!-- Notification button -->
        <button
          type="button"
          class="icon-btn"
          title="Thông báo"
        >
          <Info class="w-4 h-4" />
        </button>

        <!-- Action Button: Tạo chuyến -->
        <button
          type="button"
          class="btn-primary"
          @click="showCreateTripModal = true"
        >
          <Plus class="w-4 h-4" />
          <span>Tạo chuyến</span>
        </button>
      </div>
    </header>

    <!-- 4 KPI Stat Cards -->
    <div class="kpi-grid">
      <!-- Card 1: Chuyến hôm nay -->
      <div class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-text">
            <span class="kpi-label">Chuyến hôm nay</span>
            <span class="kpi-value text-slate-900">[{{ metrics.trips_today }}]</span>
            <span class="kpi-subtext">từ {{ metrics.trips_today }} phiếu xuất</span>
          </div>
          <div class="kpi-icon-wrap bg-mint-light text-mint-dark">
            <Truck class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Card 2: Đang giao -->
      <div class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-text">
            <span class="kpi-label">Đang giao</span>
            <span class="kpi-value text-sky-800">[{{ metrics.delivering_count }}]</span>
            <span class="kpi-subtext">{{ metrics.delivering_count }} xe trên đường</span>
          </div>
          <div class="kpi-icon-wrap bg-sky-100 text-sky-800">
            <Navigation class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Card 3: Đã giao -->
      <div class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-text">
            <span class="kpi-label">Đã giao</span>
            <span class="kpi-value text-emerald-800">[{{ metrics.delivered_count }}]</span>
            <span class="kpi-subtext">có ảnh biên nhận</span>
          </div>
          <div class="kpi-icon-wrap bg-emerald-100 text-emerald-800">
            <Check class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Card 4: Sự cố -->
      <div class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-text">
            <span class="kpi-label">Sự cố</span>
            <span class="kpi-value text-rose-800">[{{ metrics.issues_count }}]</span>
            <span class="kpi-subtext">cần gọi khách</span>
          </div>
          <div class="kpi-icon-wrap bg-rose-100 text-rose-800">
            <AlertTriangle class="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>

    <!-- Middle Section: Tài xế & xe -->
    <div class="driver-section-card">
      <div class="section-header">
        <h2 class="section-title">Tài xế &amp; xe</h2>
        <button
          type="button"
          class="link-btn"
          @click="showVehiclesModal = true"
        >
          Quản lý xe
        </button>
      </div>

      <div class="drivers-grid">
        <div
          v-for="drv in drivers"
          :key="drv.id"
          class="driver-card"
        >
          <!-- Initials Circle -->
          <span class="avatar-badge">
            {{ getInitials(drv.full_name) }}
          </span>

          <div class="driver-info">
            <span class="driver-name">{{ drv.full_name }}</span>
            <span class="driver-vehicle">
              {{ drv.default_vehicle_plate ? `Xe ${drv.default_vehicle_plate.slice(0, 3)}[...]` : 'Xe —' }}
            </span>
            <span class="driver-permit">
              {{ drv.hazard_training_expiry ? `GP hàng NH: ${drv.hazard_training_expiry}` : '—' }}
            </span>
            <div class="mt-1">
              <span
                v-if="drv.status === 'running'"
                class="status-pill bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300"
              >
                Đang chạy
              </span>
              <span
                v-else-if="drv.status === 'ready'"
                class="status-pill bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300"
              >
                Sẵn sàng
              </span>
              <span
                v-else-if="drv.status === 'issue'"
                class="status-pill bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300"
              >
                Sự cố
              </span>
              <span
                v-else
                class="status-pill bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
              >
                Nghỉ
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 4 Kanban Columns -->
    <div class="kanban-board">
      <!-- Column 1: Chờ phân công -->
      <div class="kanban-column">
        <div class="column-header">
          <span class="column-title">Chờ phân công</span>
          <span class="badge-count bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">{{ filteredUnassigned.length }}</span>
        </div>

        <div class="column-cards">
          <div
            v-for="t in filteredUnassigned"
            :key="t.id"
            class="trip-card"
          >
            <div class="trip-card-header">
              <span class="trip-code">{{ t.dispatch_code }}</span>
            </div>
            <span class="trip-customer">{{ t.customer_name }}</span>
            <span class="trip-address">
              <MapPin class="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-slate-400" />
              <span>{{ t.customer_address || '[Địa chỉ khách]' }}</span>
            </span>
            <span class="trip-items">{{ t.items_summary }}</span>

            <div v-if="t.is_hazardous" class="flex gap-1.5 my-1">
              <span class="status-pill bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300">
                Hàng nguy hiểm
              </span>
            </div>

            <div class="trip-card-footer">
              <button
                type="button"
                class="btn-assign"
                @click="openAssignModal(t)"
              >
                <UserPlus class="w-4 h-4" />
                <span>Phân công tài xế</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Column 2: Đang giao -->
      <div class="kanban-column">
        <div class="column-header">
          <span class="column-title">Đang giao</span>
          <span class="badge-count bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300">{{ filteredDelivering.length }}</span>
        </div>

        <div class="column-cards">
          <div
            v-for="t in filteredDelivering"
            :key="t.id"
            class="trip-card cursor-pointer hover:border-sky-400 dark:hover:border-sky-500 transition-colors"
            @click="openTripDetail(t)"
          >
            <div class="trip-card-header">
              <span class="trip-code">{{ t.dispatch_code }}</span>
              <span class="status-pill bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300">Đang chạy</span>
            </div>
            <span class="trip-customer">{{ t.customer_name }}</span>
            <span class="trip-address">
              <MapPin class="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-slate-400" />
              <span>{{ t.customer_address || '[Địa chỉ khách]' }}</span>
            </span>
            <span class="trip-items">{{ t.items_summary }}</span>

            <div v-if="t.is_hazardous" class="flex gap-1.5 my-1">
              <span class="status-pill bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300">
                Hàng nguy hiểm
              </span>
            </div>

            <div class="driver-footer">
              <span class="driver-mini-avatar">{{ t.driver_initials || getInitials(t.driver_name) }}</span>
              <span class="driver-footer-name">{{ t.driver_name }}</span>
              <span class="ml-auto text-xs text-slate-500 dark:text-slate-400">{{ t.estimated_time || 'Dự kiến 10:40' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Column 3: Đã giao -->
      <div class="kanban-column">
        <div class="column-header">
          <span class="column-title">Đã giao</span>
          <span class="badge-count bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">{{ filteredDelivered.length }}</span>
        </div>

        <div class="column-cards">
          <div
            v-for="t in filteredDelivered"
            :key="t.id"
            class="trip-card cursor-pointer hover:border-emerald-400 dark:hover:border-emerald-500 transition-colors"
            @click="openTripDetail(t)"
          >
            <div class="trip-card-header">
              <span class="trip-code">{{ t.dispatch_code }}</span>
              <span class="status-pill bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">Hoàn tất</span>
            </div>
            <span class="trip-customer">{{ t.customer_name }}</span>
            <span class="trip-address">
              <MapPin class="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-slate-400" />
              <span>{{ t.customer_address || '[Địa chỉ khách]' }}</span>
            </span>
            <span class="trip-items">{{ t.items_summary }}</span>

            <div v-if="t.is_hazardous" class="flex gap-1.5 my-1">
              <span class="status-pill bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300">
                Hàng nguy hiểm
              </span>
            </div>

            <div class="driver-footer">
              <span class="driver-mini-avatar">{{ t.driver_initials || getInitials(t.driver_name) }}</span>
              <span class="driver-footer-name">{{ t.driver_name }}</span>
              <span class="ml-auto text-xs text-slate-500 dark:text-slate-400">{{ t.issue_note || 'Giao 08:52 · có ảnh' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Column 4: Sự cố -->
      <div class="kanban-column">
        <div class="column-header">
          <span class="column-title">Sự cố</span>
          <span class="badge-count bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300">{{ filteredIssue.length }}</span>
        </div>

        <div class="column-cards">
          <div
            v-for="t in filteredIssue"
            :key="t.id"
            class="trip-card cursor-pointer hover:border-rose-400 dark:hover:border-rose-500 transition-colors"
            @click="openTripDetail(t)"
          >
            <div class="trip-card-header">
              <span class="trip-code">{{ t.dispatch_code }}</span>
              <span class="status-pill bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300">Cần xử lý</span>
            </div>
            <span class="trip-customer">{{ t.customer_name }}</span>
            <span class="trip-address">
              <MapPin class="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-slate-400" />
              <span>{{ t.customer_address || '[Địa chỉ khách]' }}</span>
            </span>
            <span class="trip-items">{{ t.items_summary }}</span>

            <div v-if="t.is_hazardous" class="flex gap-1.5 my-1">
              <span class="status-pill bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300">
                Hàng nguy hiểm
              </span>
            </div>

            <div class="driver-footer">
              <span class="driver-mini-avatar">{{ t.driver_initials || getInitials(t.driver_name) }}</span>
              <span class="driver-footer-name">{{ t.driver_name }}</span>
              <span class="ml-auto text-xs text-slate-500 dark:text-slate-400 font-medium text-rose-700 dark:text-rose-400">
                {{ t.issue_note || 'Khách vắng — hẹn lại' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL 1: Phân công tài xế -->
    <Modal
      v-if="showAssignModal"
      :show="showAssignModal"
      title="Phân công tài xế & Xe giao hàng"
      size="md"
      @close="showAssignModal = false"
    >
      <form class="space-y-4" @submit.prevent="handleAssignTrip">
        <div v-if="selectedTripForAssign" class="p-3 bg-slate-50 dark:bg-slate-800/70 rounded-xl border border-slate-200 dark:border-slate-700">
          <span class="font-mono font-bold text-slate-900 dark:text-slate-100 block text-xs">
            {{ selectedTripForAssign.dispatch_code }}
          </span>
          <span class="font-semibold text-slate-900 dark:text-slate-100 text-sm block mt-0.5">
            {{ selectedTripForAssign.customer_name }}
          </span>
          <span class="text-xs text-slate-500 dark:text-slate-400 block">
            {{ selectedTripForAssign.items_summary }}
          </span>
        </div>

        <div>
          <label class="form-label">Chọn tài xế phụ trách</label>
          <select v-model="assignForm.driver_id" class="form-input" required>
            <option
              v-for="d in drivers"
              :key="d.id"
              :value="d.id"
            >
              {{ d.full_name }} — {{ d.status === 'ready' ? 'Sẵn sàng' : d.status === 'running' ? 'Đang chạy' : d.status }} ({{ d.default_vehicle_plate || 'Chưa gán xe' }})
            </option>
          </select>
        </div>

        <div>
          <label class="form-label">Chọn xe giao hàng</label>
          <select v-model="assignForm.vehicle_id" class="form-input">
            <option :value="null">-- Mặc định theo tài xế --</option>
            <option
              v-for="v in vehicles"
              :key="v.id"
              :value="v.id"
            >
              {{ v.plate_number }} ({{ v.vehicle_type }}) — Tối đa {{ v.max_payload_kg }} kg
            </option>
          </select>
        </div>

        <div>
          <label class="form-label">Giờ giao hàng dự kiến</label>
          <input
            v-model="assignForm.estimated_time"
            type="text"
            class="form-input"
            placeholder="VD: Dự kiến 11:30"
          />
        </div>

        <FormActions
          :loading="saving"
          submit-text="Xác nhận phân công"
          @cancel="showAssignModal = false"
        />
      </form>
    </Modal>

    <!-- MODAL 2: Tạo chuyến giao hàng -->
    <Modal
      v-if="showCreateTripModal"
      :show="showCreateTripModal"
      title="Tạo chuyến giao hàng mới"
      size="md"
      @close="showCreateTripModal = false"
    >
      <form class="space-y-4" @submit.prevent="handleCreateTrip">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="form-label">Mã phiếu xuất kho</label>
            <input
              v-model="createTripForm.dispatch_code"
              type="text"
              class="form-input"
              placeholder="VD: PX-2609-16"
              required
            />
          </div>
          <div>
            <label class="form-label">Ngày giao hàng</label>
            <input
              v-model="createTripForm.trip_date"
              type="date"
              class="form-input"
              required
            />
          </div>
        </div>

        <div>
          <label class="form-label">Khách hàng nhận hàng</label>
          <input
            v-model="createTripForm.customer_name"
            type="text"
            class="form-input"
            placeholder="VD: Công ty TNHH Cơ khí Đại Phát"
            required
          />
        </div>

        <div>
          <label class="form-label">Địa chỉ giao hàng</label>
          <input
            v-model="createTripForm.customer_address"
            type="text"
            class="form-input"
            placeholder="VD: Lô 12, KCN Tân Bình, TP.HCM"
          />
        </div>

        <div>
          <label class="form-label">Tóm tắt hàng hoá</label>
          <input
            v-model="createTripForm.items_summary"
            type="text"
            class="form-input"
            placeholder="VD: 5 can NI-534C · 2 can CU-4"
          />
        </div>

        <div class="flex items-center gap-2">
          <input
            id="haz_check"
            v-model="createTripForm.is_hazardous"
            type="checkbox"
            class="rounded border-slate-300 text-teal-600 focus:ring-teal-500 w-4 h-4"
          />
          <label for="haz_check" class="text-sm font-medium text-slate-700 cursor-pointer">
            Có hóa chất nguy hiểm (Cần tài xế có chứng chỉ tập huấn)
          </label>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="form-label">Tài xế (không bắt buộc)</label>
            <select v-model="createTripForm.driver_id" class="form-input">
              <option :value="null">-- Chờ phân công --</option>
              <option
                v-for="d in drivers"
                :key="d.id"
                :value="d.id"
              >
                {{ d.full_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="form-label">Dự kiến giao lúc</label>
            <input
              v-model="createTripForm.estimated_time"
              type="text"
              class="form-input"
              placeholder="VD: Dự kiến 14:00"
            />
          </div>
        </div>

        <FormActions
          :loading="saving"
          submit-text="Lưu chuyến giao"
          @cancel="showCreateTripModal = false"
        />
      </form>
    </Modal>

    <!-- MODAL 3: Chi tiết & Cập nhật trạng thái chuyến -->
    <Modal
      v-if="showTripDetailModal"
      :show="showTripDetailModal"
      title="Chi tiết & Cập nhật chuyến giao hàng"
      size="md"
      @close="showTripDetailModal = false"
    >
      <form class="space-y-4" @submit.prevent="handleUpdateTripStatus">
        <div v-if="selectedTripDetail" class="p-3 bg-slate-50 dark:bg-slate-800/70 rounded-xl border border-slate-200 dark:border-slate-700">
          <div class="flex justify-between items-center mb-1">
            <span class="font-mono font-bold text-slate-900 dark:text-slate-100 text-sm">
              {{ selectedTripDetail.dispatch_code }}
            </span>
            <span
              v-if="selectedTripDetail.status === 'delivering'"
              class="status-pill bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300"
            >
              Đang chạy
            </span>
            <span
              v-else-if="selectedTripDetail.status === 'delivered'"
              class="status-pill bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300"
            >
              Hoàn tất
            </span>
            <span
              v-else
              class="status-pill bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300"
            >
              Sự cố
            </span>
          </div>
          <span class="font-semibold text-slate-900 dark:text-slate-100 text-base block">
            {{ selectedTripDetail.customer_name }}
          </span>
          <span class="text-xs text-slate-500 dark:text-slate-400 block mt-0.5">
            {{ selectedTripDetail.customer_address }}
          </span>
          <span class="text-xs text-slate-700 dark:text-slate-300 block mt-1">
            Hàng: {{ selectedTripDetail.items_summary }}
          </span>
          <span class="text-xs text-slate-600 dark:text-slate-400 block mt-1">
            Tài xế: <b class="text-slate-900 dark:text-slate-100">{{ selectedTripDetail.driver_name || 'Chưa gán' }}</b> ({{ selectedTripDetail.vehicle_plate || 'Xe —' }})
          </span>
        </div>

        <div>
          <label class="form-label">Cập nhật trạng thái</label>
          <select v-model="statusForm.status" class="form-input">
            <option value="delivering">Đang chạy trên đường</option>
            <option value="delivered">Đã giao thành công (Hoàn tất)</option>
            <option value="issue">Báo sự cố giao hàng</option>
          </select>
        </div>

        <div v-if="statusForm.status === 'delivering'">
          <label class="form-label">Giờ dự kiến đến</label>
          <input
            v-model="statusForm.estimated_time"
            type="text"
            class="form-input"
            placeholder="Dự kiến 11:30"
          />
        </div>

        <div v-if="statusForm.status === 'delivered'">
          <label class="form-label">Ghi chú giao nhận / Biên lai có ảnh</label>
          <input
            v-model="statusForm.issue_note"
            type="text"
            class="form-input"
            placeholder="Giao 08:52 · có ảnh biên nhận"
          />
        </div>

        <div v-if="statusForm.status === 'issue'">
          <label class="form-label">Mô tả sự cố &amp; Phương án xử lý</label>
          <textarea
            v-model="statusForm.issue_note"
            rows="2"
            class="form-input"
            placeholder="Khách vắng — hẹn lại vào buổi chiều..."
            required
          ></textarea>
        </div>

        <FormActions
          :loading="saving"
          submit-text="Cập nhật trạng thái"
          @cancel="showTripDetailModal = false"
        />
      </form>
    </Modal>

    <!-- MODAL 4: Quản lý Đội xe -->
    <Modal
      v-if="showVehiclesModal"
      :show="showVehiclesModal"
      title="Quản lý Đội xe vận chuyển hóa chất"
      size="lg"
      @close="showVehiclesModal = false"
    >
      <div class="space-y-4">
        <div>
          <h4 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2">Danh sách xe công ty</h4>
          <div class="space-y-2 max-h-56 overflow-y-auto pr-1">
            <div
              v-for="v in vehicles"
              :key="v.id"
              class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 flex items-center justify-between"
            >
              <div>
                <span class="font-mono font-bold text-slate-900 dark:text-slate-100 text-sm">{{ v.plate_number }}</span>
                <span class="text-xs text-slate-500 dark:text-slate-400 block">{{ v.vehicle_type }} · Tối đa {{ v.max_payload_kg }} kg</span>
              </div>
              <div class="text-right">
                <span class="text-xs text-teal-700 dark:text-teal-300 bg-teal-50 dark:bg-teal-950/60 px-2 py-0.5 rounded font-medium">
                  GP NH: {{ v.hazard_permit_expiry || 'Đạt chuẩn' }}
                </span>
                <span class="text-xs text-slate-500 dark:text-slate-400 block mt-0.5">
                  {{ v.status === 'active' ? 'Đang hoạt động' : 'Bảo dưỡng' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="border-t border-slate-200 dark:border-slate-700 pt-3">
          <h4 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2">Thêm xe mới</h4>
          <form class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5" @submit.prevent="handleAddVehicle">
            <div>
              <input
                v-model="newVehicleForm.plate_number"
                type="text"
                class="form-input text-xs"
                placeholder="Biển số (51C-123.45)"
                required
              />
            </div>
            <div>
              <input
                v-model="newVehicleForm.vehicle_type"
                type="text"
                class="form-input text-xs"
                placeholder="Loại xe (Xe tải 1.5T)"
                required
              />
            </div>
            <div>
              <input
                v-model="newVehicleForm.hazard_permit_expiry"
                type="date"
                class="form-input text-xs"
                required
              />
            </div>
            <div>
              <button
                type="submit"
                class="btn-primary w-full h-[38px] justify-center text-xs"
                :disabled="saving"
              >
                <Plus class="w-3.5 h-3.5" /> Thêm xe
              </button>
            </div>
          </form>
        </div>

        <div class="flex justify-end pt-2">
          <button
            type="button"
            class="btn-secondary"
            @click="showVehiclesModal = false"
          >
            Đóng
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped>
.dispatch-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.link-btn {
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  background: transparent;
  border: 0;
  cursor: pointer;
  @apply text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300;
}

.bg-mint-light {
  @apply bg-emerald-50 dark:bg-emerald-950/60;
}
.text-mint-dark {
  @apply text-emerald-700 dark:text-emerald-300;
}

/* Driver & Vehicles Section */
.driver-section-card {
  border-radius: 20px;
  padding: 20px;
  box-sizing: border-box;
  @apply bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/60 shadow-[0_1px_2px_rgba(15,23,42,0.04),0_8px_24px_rgba(15,23,42,0.05)];
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  @apply text-slate-900 dark:text-slate-100;
}
.drivers-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 1100px) {
  .drivers-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 640px) {
  .drivers-grid {
    grid-template-columns: 1fr;
  }
}
.driver-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 14px;
  min-width: 0;
  @apply bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-700/50;
}
.avatar-badge {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  @apply bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300;
}
.driver-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex-grow: 1;
  min-width: 0;
}
.driver-name {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  @apply text-slate-900 dark:text-slate-100;
}
.driver-vehicle {
  font-size: 12px;
  @apply text-slate-500 dark:text-slate-400;
}
.driver-permit {
  font-size: 11px;
  @apply text-slate-500 dark:text-slate-400;
}

/* Kanban Board */
.kanban-board {
  display: flex;
  gap: 14px;
  flex-grow: 1;
  min-width: 0;
  align-items: flex-start;
}
@media (max-width: 1100px) {
  .kanban-board {
    flex-direction: column;
  }
}
.kanban-column {
  flex: 1 1 0;
  min-width: 0;
  border-radius: 20px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  @apply bg-slate-100/70 dark:bg-slate-900/50 border border-slate-200/60 dark:border-slate-800/80;
}
@media (max-width: 1100px) {
  .kanban-column {
    width: 100%;
  }
}
.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
}
.column-title {
  font-weight: 700;
  font-size: 14px;
  @apply text-slate-900 dark:text-slate-100;
}
.badge-count {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}
.column-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.trip-card {
  border-radius: 16px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  @apply bg-white dark:bg-slate-800 border border-slate-200/70 dark:border-slate-700/60 shadow-[0_1px_2px_rgba(15,23,42,0.04)];
}
.trip-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.trip-code {
  font-family: ui-monospace, Menlo, monospace;
  font-weight: 700;
  font-size: 13px;
  @apply text-slate-900 dark:text-slate-100;
}
.trip-customer {
  font-size: 14px;
  font-weight: 700;
  @apply text-slate-900 dark:text-slate-100;
}
.trip-address {
  display: flex;
  gap: 6px;
  font-size: 12px;
  line-height: 1.45;
  @apply text-slate-500 dark:text-slate-400;
}
.trip-items {
  font-size: 12px;
  @apply text-slate-700 dark:text-slate-300;
}
.trip-card-footer {
  padding-top: 10px;
  @apply border-t border-slate-100 dark:border-slate-700/60;
}
.driver-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 10px;
  @apply border-t border-slate-100 dark:border-slate-700/60;
}
.driver-mini-avatar {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  flex-shrink: 0;
  @apply bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300;
}
.driver-footer-name {
  font-size: 13px;
  font-weight: 600;
  @apply text-slate-900 dark:text-slate-100;
}
</style>
