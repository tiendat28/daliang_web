<!-- /system/users - tao tai khoan, gan vai tro, khoa/mo, cap lai mat khau, go 2FA.
     Mat khau tam chi hien MOT lan de admin chuyen cho nhan vien. -->
<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { AlertTriangle, Check, KeyRound, Loader2, Lock, LockOpen, Pencil, Shield, ShieldAlert, Trash2, UserRound, UsersRound } from 'lucide-vue-next'
import Modal from '@/core/components/Modal.vue'
import { errorMessage } from '@/core/api/errors'
import { formatDateTime } from '@/core/utils/format'
import { auth, can } from '@/core/auth/store'
import { notify } from '@/core/store/notify'
import { auditLogApi, rolesApi, usersApi } from '../api'

const users = ref([])
const roles = ref([])
const permissions = ref([])
const recentLogs = ref([])
const selectedRoleId = ref(null)
const loading = ref(true)
const error = ref('')

const editing = ref(null)          // null = dong; {} = tao moi; user = sua
const form = ref({ email: '', full_name: '', role_ids: [], is_active: true })
const saving = ref(false)
const formError = ref('')
const temporary = ref(null)        // { email, password } vua cap

async function load() {
  loading.value = true
  try {
    const [loadedUsers, loadedRoles, loadedPermissions, audit] = await Promise.all([
      usersApi.list(), rolesApi.list(), rolesApi.permissions(), auditLogApi.list({ page: 1, page_size: 4 }),
    ])
    users.value = loadedUsers
    roles.value = loadedRoles
    permissions.value = loadedPermissions
    recentLogs.value = audit.items || []
    selectedRoleId.value ||= loadedRoles[0]?.id || null

    // Khoi tao tap quyen cho tung vai tro
    loadedRoles.forEach(r => {
      rolePerms.value[r.id] = new Set(r.permission_codes || [])
    })
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}
onMounted(load)

const isNew = computed(() => editing.value && !editing.value.id)

function open(user = {}) {
  editing.value = user
  formError.value = ''
  form.value = {
    email: user.email || '',
    full_name: user.full_name || '',
    role_ids: [...(user.role_ids || [])],
    is_active: user.is_active ?? true,
  }
}

async function save() {
  saving.value = true
  formError.value = ''
  try {
    if (isNew.value) {
      const result = await usersApi.create({ email: form.value.email, full_name: form.value.full_name, role_ids: form.value.role_ids })
      temporary.value = { email: result.user.email, password: result.temporary_password }
    } else {
      await usersApi.update(editing.value.id, {
        full_name: form.value.full_name, role_ids: form.value.role_ids, is_active: form.value.is_active,
      })
    }
    editing.value = null
    await load()
  } catch (e) {
    formError.value = errorMessage(e)
  } finally {
    saving.value = false
  }
}

async function act(user, action) {
  const questions = {
    password: `Cấp mật khẩu tạm mới cho ${user.full_name}? Mật khẩu cũ và mọi phiên đăng nhập sẽ mất hiệu lực.`,
    twofa: `Gỡ 2FA của ${user.full_name}? (Dùng khi nhân viên mất điện thoại và hết mã dự phòng.)`,
    toggleActive: user.is_active ? `Khoá tài khoản ${user.full_name}?` : `Mở khoá tài khoản ${user.full_name}?`,
    remove: `Xoá tài khoản ${user.full_name}? Tài khoản sẽ không thể đăng nhập.`,
  }
  if (questions[action] && !confirm(questions[action])) return
  try {
    if (action === 'password') {
      const result = await usersApi.resetPassword(user.id)
      temporary.value = { email: user.email, password: result.temporary_password }
    } else if (action === 'twofa') {
      await usersApi.reset2fa(user.id)
    } else if (action === 'unlock') {
      await usersApi.unlock(user.id)
    } else if (action === 'toggleActive') {
      await usersApi.setActive(user.id, !user.is_active)
    } else if (action === 'remove') {
      await usersApi.remove(user.id)
    }
    await load()
  } catch (e) {
    alert(errorMessage(e))
  }
}

const isLocked = user => user.locked_until && new Date(user.locked_until) > new Date()
const activeCount = computed(() => users.value.filter(user => user.is_active && !isLocked(user)).length)
const require2faCount = computed(() => users.value.filter(user => !user.totp_enabled).length)
const lockedCount = computed(() => users.value.filter(user => !user.is_active || isLocked(user)).length)
const selectedRole = computed(() => roles.value.find(role => role.id === selectedRoleId.value) || roles.value[0])

// --- Phân quyền theo vai trò ---
const rolePerms = ref({})
const savingRole = ref(false)
const roleMessage = ref({ type: '', text: '' })
const permSearchQuery = ref('')
const activeModuleFilter = ref('all')

const moduleTabs = [
  { key: 'all', label: 'Tất cả' },
  { key: 'lab', label: 'Kỹ thuật' },
  { key: 'warehouse', label: 'Kho' },
  { key: 'dispatch', label: 'Điều phối' },
  { key: 'accounting', label: 'Kế toán' },
  { key: 'hr', label: 'Nhân sự' },
  { key: 'common', label: 'Chung' },
  { key: 'system', label: 'Hệ thống' },
]

const actionsList = ['view', 'create', 'update', 'delete', 'approve', 'export']
const actionLabels = {
  view: 'Xem',
  create: 'Thêm',
  update: 'Sửa',
  delete: 'Xoá',
  approve: 'Duyệt',
  export: 'Xuất file',
}

const RESOURCE_LABELS = {
  'accounting.invoices': 'Hoá đơn',
  'accounting.vouchers': 'Phiếu thu chi',
  'accounting.receivables': 'Công nợ phải thu',
  'accounting.payables': 'Công nợ phải trả',
  'accounting.cashbook': 'Sổ quỹ',
  'accounting.reports': 'Báo cáo tài chính kế toán',
  'common.company_profile': 'Thông tin công ty',
  'common.customers': 'Khách hàng',
  'common.products': 'Sản phẩm công ty',
  'common.documents': 'Tài liệu kỹ thuật',
  'dispatch.trips': 'Chuyến giao hàng',
  'dispatch.vehicles': 'Xe giao hàng',
  'dispatch.drivers': 'Tài xế giao hàng',
  'hr.employees': 'Hồ sơ nhân viên',
  'hr.attendance': 'Chấm công',
  'hr.leave_requests': 'Đơn nghỉ phép',
  'hr.contracts': 'Hợp đồng lao động',
  'hr.certificates': 'Chứng chỉ đào tạo',
  'hr.departments': 'Phòng ban',
  'lab.chemicals': 'Hóa chất thí nghiệm',
  'lab.indicators': 'Chất chỉ thị',
  'lab.equipment': 'Thiết bị thí nghiệm',
  'lab.formulations': 'Đơn hàng pha chế (HCTN)',
  'lab.samples': 'Lấy mẫu hoá chất',
  'lab.analysis_reports': 'Báo cáo phân tích',
  'lab.work_logs': 'Nhật ký công việc',
  'lab.test_processes': 'Lưu trình test mẫu',
  'lab.process_templates': 'Quy trình chuẩn',
  'system.users': 'Tài khoản người dùng',
  'system.roles': 'Vai trò & phân quyền',
  'system.audit_log': 'Nhật ký thao tác',
  'website.contact_leads': 'Đơn liên hệ website',
  '*': 'Toàn quyền hệ thống',
}

function formatResourceLabel(key, rawDesc) {
  if (RESOURCE_LABELS[key]) return RESOURCE_LABELS[key]
  if (!rawDesc) return key
  return rawDesc.replace(/^(Xem|Thêm|Sửa|Xoá|Duyệt|Xuất file|Quản lý|Cấp lại|Gỡ|Đánh dấu)\s+/i, '').trim()
}

function getRolePermsSet(roleId) {
  if (!roleId) return new Set()
  if (!rolePerms.value[roleId]) {
    const role = roles.value.find(r => r.id === roleId)
    rolePerms.value[roleId] = new Set(role?.permission_codes || [])
  }
  return rolePerms.value[roleId]
}

function selectRole(role) {
  selectedRoleId.value = role.id
  roleMessage.value = { type: '', text: '' }
  if (role.code === 'lab') activeModuleFilter.value = 'lab'
  else if (role.code === 'warehouse') activeModuleFilter.value = 'warehouse'
  else if (role.code === 'dispatch' || role.code === 'driver') activeModuleFilter.value = 'dispatch'
  else if (role.code === 'accounting') activeModuleFilter.value = 'accounting'
  else if (role.code === 'hr') activeModuleFilter.value = 'hr'
  else activeModuleFilter.value = 'all'
}

const permissionRows = computed(() => {
  const groups = new Map()

  for (const permission of permissions.value) {
    if (permission.code === '*') {
      if (!groups.has('*')) {
        groups.set('*', {
          key: '*',
          module: 'all',
          moduleLabel: 'Toàn quyền',
          label: 'Toàn quyền hệ thống (*)',
          actions: { view: '*' },
        })
      }
      continue
    }

    const parts = permission.code.split('.')
    let action = parts.pop()
    const module = parts[0]
    const key = parts.join('.')

    if (action === 'manage') {
      action = 'update'
    }

    if (!groups.has(key)) {
      const moduleLabels = {
        lab: 'Kỹ thuật',
        warehouse: 'Kho',
        dispatch: 'Điều phối',
        accounting: 'Kế toán',
        hr: 'Nhân sự',
        common: 'Chung',
        system: 'Hệ thống',
        website: 'Website',
        all: 'Toàn quyền',
      }
      groups.set(key, {
        key,
        module,
        moduleLabel: moduleLabels[module] || module,
        label: formatResourceLabel(key, permission.description || key),
        actions: {},
      })
    }
    groups.get(key).actions[action] = permission.code
  }

  let list = [...groups.values()]

  if (activeModuleFilter.value !== 'all') {
    list = list.filter(r => r.module === activeModuleFilter.value || (r.key === '*' && activeModuleFilter.value === 'all'))
  }

  if (permSearchQuery.value.trim()) {
    const q = permSearchQuery.value.trim().toLowerCase()
    list = list.filter(r => r.label.toLowerCase().includes(q) || r.key.toLowerCase().includes(q))
  }

  return list
})

function roleHasPermission(code) {
  if (!code || !selectedRole.value) return false
  const perms = getRolePermsSet(selectedRole.value.id)
  if (perms.has('*')) return true
  return perms.has(code)
}

function togglePermission(code) {
  if (!code || !selectedRole.value) return
  const perms = getRolePermsSet(selectedRole.value.id)
  roleMessage.value = { type: '', text: '' }

  if (code === '*') {
    if (perms.has('*')) {
      perms.delete('*')
    } else {
      perms.clear()
      perms.add('*')
    }
    return
  }

  if (perms.has('*')) {
    perms.clear()
    for (const p of permissions.value) {
      if (p.code !== '*' && p.code !== code) {
        perms.add(p.code)
      }
    }
  } else {
    if (perms.has(code)) {
      perms.delete(code)
    } else {
      perms.add(code)
    }
  }
}

function toggleRow(row) {
  if (!selectedRole.value) return
  const perms = getRolePermsSet(selectedRole.value.id)
  const actionCodes = Object.values(row.actions).filter(Boolean)
  if (!actionCodes.length) return
  roleMessage.value = { type: '', text: '' }

  const allChecked = actionCodes.every(code => roleHasPermission(code))
  if (allChecked) {
    actionCodes.forEach(code => {
      if (perms.has('*')) {
        togglePermission(code)
      } else {
        perms.delete(code)
      }
    })
  } else {
    actionCodes.forEach(code => perms.add(code))
  }
}

function selectAllCurrentView() {
  if (!selectedRole.value) return
  const perms = getRolePermsSet(selectedRole.value.id)
  permissionRows.value.forEach(row => {
    Object.values(row.actions).forEach(code => {
      if (code) perms.add(code)
    })
  })
}

function clearAllCurrentView() {
  if (!selectedRole.value) return
  const perms = getRolePermsSet(selectedRole.value.id)
  if (perms.has('*')) {
    perms.clear()
  } else {
    permissionRows.value.forEach(row => {
      Object.values(row.actions).forEach(code => {
        if (code) perms.delete(code)
      })
    })
  }
}

async function saveRolePermissions() {
  if (!selectedRole.value) return
  if (!can('system.roles.manage')) {
    const msg = 'Bạn không có quyền chỉnh sửa phân quyền vai trò'
    roleMessage.value = { type: 'error', text: msg }
    notify.permissionDenied(msg)
    return
  }

  savingRole.value = true
  roleMessage.value = { type: '', text: '' }
  try {
    const roleId = selectedRole.value.id
    const perms = getRolePermsSet(roleId)
    const payload = {
      code: selectedRole.value.code,
      name: selectedRole.value.name,
      description: selectedRole.value.description,
      require_2fa: selectedRole.value.require_2fa,
      permission_codes: Array.from(perms),
    }
    const updated = await rolesApi.update(roleId, payload)
    const idx = roles.value.findIndex(r => r.id === roleId)
    if (idx > -1) {
      roles.value[idx] = updated
    }
    rolePerms.value[roleId] = new Set(updated.permission_codes || [])
    roleMessage.value = {
      type: 'success',
      text: `Đã lưu phân quyền cho vai trò "${selectedRole.value.name}" thành công!`,
    }
    notify.success(`Đã lưu phân quyền cho vai trò "${selectedRole.value.name}"!`)
    setTimeout(() => {
      if (roleMessage.value.type === 'success') roleMessage.value = { type: '', text: '' }
    }, 4000)
  } catch (err) {
    const msg = errorMessage(err) || 'Không thể lưu phân quyền'
    roleMessage.value = {
      type: 'error',
      text: msg,
    }
    notify.error(msg, 'Không thể lưu phân quyền')
  } finally {
    savingRole.value = false
  }
}

const currentRolePermCount = computed(() => {
  if (!selectedRole.value) return 0
  const perms = getRolePermsSet(selectedRole.value.id)
  if (perms.has('*')) return permissions.value.length
  return perms.size
})

const logActionLabel = item => ({ POST: 'Thêm', PUT: 'Sửa', PATCH: 'Sửa', DELETE: 'Xoá', 'login.success': 'Đăng nhập', 'login.fail': 'Đăng nhập sai', '2fa.enable': 'Bật 2FA', 'password.reset': 'Đặt lại mật khẩu' }[item.action] || item.action)
const logTypeClass = item => /fail|lock|delete/.test(item.action) ? 'bg-dl-bad text-dl-badink' : /login|enable/.test(item.action) ? 'bg-dl-soft text-dl-teal' : 'bg-dl-info text-dl-infoink'
</script>

<template>
  <div class="flex flex-col gap-5">
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <article class="dl-stat-card"><span class="dl-stat-icon bg-dl-soft text-dl-teal"><UsersRound class="w-5 h-5" /></span><span class="dl-stat-label">Tài khoản</span><strong>{{ activeCount }}</strong><small>đang hoạt động</small></article>
      <article class="dl-stat-card"><span class="dl-stat-icon bg-dl-violet text-dl-violetink"><Shield class="w-5 h-5" /></span><span class="dl-stat-label">Vai trò</span><strong>{{ roles.length }}</strong><small>nhóm phân quyền</small></article>
      <article class="dl-stat-card"><span class="dl-stat-icon bg-dl-warn text-dl-warnink"><AlertTriangle class="w-5 h-5" /></span><span class="dl-stat-label">Chưa bật 2FA</span><strong>{{ require2faCount }}</strong><small>cần nhắc</small></article>
      <article class="dl-stat-card"><span class="dl-stat-icon bg-dl-bad text-dl-badink"><Lock class="w-5 h-5" /></span><span class="dl-stat-label">Đăng nhập lỗi</span><strong>{{ lockedCount }}</strong><small>đang bị hạn chế</small></article>
    </div>

    <section class="dl-card !p-0 overflow-hidden">
      <div class="flex flex-wrap items-center justify-between gap-3 px-5 pt-5 pb-3">
        <h2 class="m-0 text-base font-bold text-dl-ink dark:text-slate-100">Tài khoản nhân viên</h2>
        <button type="button" class="dl-btn" @click="open()"><UserRound class="w-4 h-4" /> Thêm tài khoản</button>
      </div>
      <p v-if="error" class="px-5 pb-4 text-sm text-dl-badink">{{ error }}</p>
      <div v-if="loading" class="py-10 flex justify-center"><Loader2 class="w-5 h-5 animate-spin text-dl-muted" /></div>
      <div v-else class="overflow-auto px-5 pb-5">
        <table class="w-full min-w-[760px] text-sm">
          <thead><tr><th class="dl-th">Nhân viên</th><th class="dl-th">Bộ phận</th><th class="dl-th">Vai trò</th><th class="dl-th">Trạng thái</th><th class="dl-th">Đăng nhập</th><th class="dl-th" /></tr></thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td class="dl-td"><div class="font-semibold text-dl-ink dark:text-slate-100">{{ user.full_name }}</div><div class="text-xs text-dl-muted">{{ user.email }}</div></td>
              <td class="dl-td">{{ user.department || '—' }}</td>
              <td class="dl-td"><span v-for="role in user.roles" :key="role.code" class="block">{{ role.name }}</span><span v-if="!user.roles.length" class="text-dl-muted">Chưa có</span></td>
              <td class="dl-td"><span class="dl-badge" :class="!user.is_active || isLocked(user) ? 'bg-dl-bad text-dl-badink' : 'bg-dl-ok text-dl-okink'">{{ !user.is_active || isLocked(user) ? 'Đã khoá' : 'Hoạt động' }}</span></td>
              <td class="dl-td whitespace-nowrap">{{ user.last_login_at ? formatDateTime(user.last_login_at) : '—' }}</td>
              <td class="dl-td">
                <div class="flex justify-end gap-1">
                  <button class="dl-icon-btn" title="Sửa" @click="open(user)"><Pencil class="w-4 h-4" /></button>
                  <button class="dl-icon-btn" title="Cấp mật khẩu tạm" @click="act(user, 'password')"><KeyRound class="w-4 h-4" /></button>
                  <button v-if="isLocked(user)" class="dl-icon-btn" title="Mở khoá tạm" @click="act(user, 'unlock')"><LockOpen class="w-4 h-4" /></button>
                  <button v-else-if="user.id !== auth.user?.id" class="dl-icon-btn" :title="user.is_active ? 'Khoá tài khoản' : 'Mở khoá tài khoản'" @click="act(user, 'toggleActive')">
                    <Lock v-if="user.is_active" class="w-4 h-4 text-amber-600 dark:text-amber-400" />
                    <LockOpen v-else class="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                  </button>
                  <button v-if="user.id !== auth.user?.id" class="dl-icon-btn text-rose-500 hover:text-rose-600" title="Xoá tài khoản" @click="act(user, 'remove')">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div class="grid grid-cols-1 xl:grid-cols-[1.15fr_1fr] gap-5">
      <section class="dl-card !p-0 overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex flex-wrap items-center justify-between gap-2 sm:gap-3 px-4 sm:px-5 pt-4 sm:pt-5 pb-3">
          <div class="flex items-center gap-2">
            <h2 class="m-0 text-base font-bold text-dl-ink dark:text-slate-100">Phân quyền theo vai trò</h2>
            <span class="text-xs text-slate-500 dark:text-slate-400">({{ currentRolePermCount }} quyền)</span>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="!can('system.roles.manage')" class="dl-badge bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 font-medium text-xs">
              Chỉ xem (Không có quyền sửa)
            </span>
            <span v-if="selectedRole" class="dl-badge bg-dl-warn text-dl-warnink font-semibold">
              Đang xem: {{ selectedRole.name }}
            </span>
          </div>
        </div>

        <!-- Role Tabs -->
        <div class="flex flex-wrap gap-2 px-5 pb-3">
          <button
            v-for="role in roles"
            :key="role.id"
            type="button"
            class="role-tab transition-all cursor-pointer"
            :class="selectedRole?.id === role.id ? 'role-tab-active shadow-sm' : 'hover:bg-slate-200 dark:hover:bg-slate-700'"
            @click="selectRole(role)"
          >
            {{ role.name }}
          </button>
        </div>

        <!-- Module Filter Tabs & Action tools -->
        <div class="flex flex-wrap items-center justify-between gap-2 px-5 py-2.5 bg-slate-50/70 dark:bg-slate-900/60 border-y border-slate-200/70 dark:border-slate-800">
          <div class="flex flex-wrap items-center gap-1">
            <button
              v-for="tab in moduleTabs"
              :key="tab.key"
              type="button"
              class="h-7 px-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer"
              :class="activeModuleFilter === tab.key ? 'bg-teal-600 text-white shadow-xs' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/80 dark:hover:bg-slate-800'"
              @click="activeModuleFilter = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="flex items-center gap-2">
            <button
              type="button"
              class="text-xs text-teal-600 dark:text-teal-400 font-semibold hover:underline cursor-pointer"
              @click="selectAllCurrentView"
            >
              Chọn tất cả
            </button>
            <span class="text-slate-300 dark:text-slate-600">|</span>
            <button
              type="button"
              class="text-xs text-slate-500 dark:text-slate-400 hover:text-rose-500 cursor-pointer"
              @click="clearAllCurrentView"
            >
              Bỏ chọn
            </button>
          </div>
        </div>

        <!-- Table with Checkable Boxes -->
        <div class="overflow-auto px-5 max-h-[460px]">
          <table class="w-full min-w-[620px] text-sm">
            <thead class="sticky top-0 bg-white dark:bg-slate-800 z-10 shadow-[0_1px_0_rgba(0,0,0,0.06)]">
              <tr>
                <th class="dl-th pl-0">Chức năng</th>
                <th
                  v-for="action in actionsList"
                  :key="action"
                  class="dl-th text-center w-14"
                >
                  {{ actionLabels[action] }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in permissionRows"
                :key="row.key"
                class="hover:bg-slate-50/70 dark:hover:bg-slate-800/60 transition-colors"
              >
                <td
                  class="dl-td pl-0 font-semibold cursor-pointer select-none group"
                  title="Nhấn để chọn/bỏ tất cả quyền của chức năng này"
                  @click="toggleRow(row)"
                >
                  <div class="flex items-center gap-1.5">
                    <span class="group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors">{{ row.label }}</span>
                    <span class="text-[11px] font-normal text-slate-400 dark:text-slate-500">({{ row.moduleLabel }})</span>
                  </div>
                </td>
                <td
                  v-for="action in actionsList"
                  :key="action"
                  class="dl-td text-center p-1"
                >
                  <button
                    v-if="row.actions[action]"
                    type="button"
                    class="permission-box cursor-pointer hover:scale-110 active:scale-95 transition-all focus:outline-none focus:ring-2 focus:ring-teal-500/40"
                    :class="[
                      roleHasPermission(row.actions[action])
                        ? 'permission-box-on'
                        : 'border-slate-300 dark:border-slate-600 hover:border-teal-500 bg-white dark:bg-slate-800'
                    ]"
                    :title="`${roleHasPermission(row.actions[action]) ? 'Bỏ quyền' : 'Cấp quyền'}: ${actionLabels[action]} ${row.label}`"
                    @click="togglePermission(row.actions[action])"
                  >
                    <Check v-if="roleHasPermission(row.actions[action])" class="w-3.5 h-3.5" />
                  </button>
                  <span v-else class="text-xs text-slate-300 dark:text-slate-600 select-none">—</span>
                </td>
              </tr>
              <tr v-if="permissionRows.length === 0">
                <td colspan="7" class="py-8 text-center text-sm text-slate-400">
                  Không tìm thấy chức năng phù hợp.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Footer with Save Button and Feedback -->
        <div class="flex flex-wrap items-center justify-between gap-2.5 sm:gap-3 px-4 sm:px-5 py-3.5 sm:py-4 border-t border-slate-100 dark:border-slate-800 mt-auto bg-slate-50/40 dark:bg-slate-900/30">
          <div class="flex items-center gap-2">
            <span v-if="!roleMessage.text" class="text-xs text-slate-500 dark:text-slate-400">
              Nhấn trực tiếp vào ô để cấp/bỏ quyền, sau đó bấm Lưu thay đổi.
            </span>
            <div
              v-else
              :class="roleMessage.type === 'success' ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800' : 'bg-rose-50 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border-rose-200 dark:border-rose-800'"
              class="px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-2 shadow-xs"
            >
              <Check v-if="roleMessage.type === 'success'" class="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <ShieldAlert v-else class="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
              <span>{{ roleMessage.text }}</span>
            </div>
          </div>

          <button
            type="button"
            class="dl-btn cursor-pointer inline-flex items-center gap-2"
            :disabled="savingRole"
            @click="saveRolePermissions"
          >
            <Loader2 v-if="savingRole" class="w-4 h-4 animate-spin" />
            <Check v-else class="w-4 h-4" />
            <span>{{ savingRole ? 'Đang lưu...' : 'Lưu thay đổi' }}</span>
          </button>
        </div>
      </section>

      <section class="dl-card !p-0 overflow-hidden self-start">
        <div class="flex flex-wrap items-center justify-between gap-2 sm:gap-3 px-4 sm:px-5 pt-4 sm:pt-5 pb-3"><h2 class="m-0 text-base font-bold text-dl-ink dark:text-slate-100">Nhật ký thao tác gần đây</h2><RouterLink to="/system/audit-log" class="text-sm font-semibold text-dl-teal no-underline">Xem tất cả</RouterLink></div>
        <div class="overflow-auto px-5 pb-2"><table class="w-full min-w-[520px] text-sm"><thead><tr><th class="dl-th pl-0">Thời gian</th><th class="dl-th">Người thực hiện</th><th class="dl-th">Hành động</th><th class="dl-th">Loại</th></tr></thead><tbody><tr v-for="item in recentLogs" :key="item.id"><td class="dl-td pl-0 whitespace-nowrap">{{ formatDateTime(item.created_at) }}</td><td class="dl-td font-semibold">{{ item.user_name || item.user_email || 'Hệ thống' }}</td><td class="dl-td">{{ item.summary || logActionLabel(item) }}</td><td class="dl-td"><span class="dl-badge" :class="logTypeClass(item)">{{ logActionLabel(item) }}</span></td></tr><tr v-if="!recentLogs.length"><td colspan="4" class="py-8 text-center text-sm text-dl-muted">Chưa có nhật ký thao tác</td></tr></tbody></table></div>
      </section>
    </div>
  </div>

  <Modal :show="!!editing" :title="isNew ? 'Thêm tài khoản' : 'Sửa tài khoản'" @close="editing = null">
    <form class="flex flex-col gap-4" @submit.prevent="save">
      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="field-label mb-1" for="u-email">Email</label>
          <input id="u-email" v-model="form.email" type="email" class="w-full field-input" :disabled="!isNew" required />
        </div>
        <div>
          <label class="field-label mb-1" for="u-name">Họ tên</label>
          <input id="u-name" v-model="form.full_name" class="w-full field-input" required />
        </div>
      </div>
      <div>
        <span class="field-label mb-1">Vai trò</span>
        <div class="grid gap-1.5 sm:grid-cols-2">
          <label v-for="role in roles" :key="role.id" class="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-300">
            <input v-model="form.role_ids" type="checkbox" :value="role.id" class="rounded mt-0.5" />
            <span>{{ role.name }}<span v-if="role.require_2fa" class="text-xs text-slate-400"> · bắt buộc 2FA</span></span>
          </label>
        </div>
      </div>
      <label v-if="!isNew" class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
        <input v-model="form.is_active" type="checkbox" class="rounded" :disabled="editing.id === auth.user?.id" />
        <Lock v-if="!form.is_active" class="w-4 h-4 text-red-500" /> Cho phép đăng nhập
      </label>
      <p v-if="isNew" class="text-xs text-slate-400">Hệ thống tạo mật khẩu tạm và hiện một lần sau khi lưu; nhân viên phải đổi ở lần đăng nhập đầu.</p>
      <p v-if="formError" class="text-sm text-red-600">{{ formError }}</p>
      <div class="flex justify-end gap-2">
        <button type="button" class="h-10 px-4 rounded-xl text-sm text-slate-500" @click="editing = null">Huỷ</button>
        <button type="submit" class="h-10 px-5 rounded-xl bg-brand-gradient text-white text-sm font-semibold disabled:opacity-50 flex items-center gap-2" :disabled="saving">
          <Loader2 v-if="saving" class="w-4 h-4 animate-spin" /> Lưu
        </button>
      </div>
    </form>
  </Modal>

  <Modal :show="!!temporary" title="Mật khẩu tạm" @close="temporary = null">
    <div class="flex flex-col gap-3">
      <p class="text-sm text-slate-600 dark:text-slate-300">
        Gửi cho <b>{{ temporary?.email }}</b>. Mật khẩu chỉ hiện <b>lần này</b>; nhân viên phải đổi ngay khi đăng nhập.
      </p>
      <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 font-mono text-center text-lg select-all text-slate-800 dark:text-slate-100">{{ temporary?.password }}</div>
      <button type="button" class="h-10 rounded-xl bg-brand-gradient text-white text-sm font-semibold" @click="temporary = null">Đã ghi lại</button>
    </div>
  </Modal>
</template>
