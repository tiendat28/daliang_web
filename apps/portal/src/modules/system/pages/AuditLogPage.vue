<!-- /system/audit-log - ai lam gi, luc nao: moi thao tac them/sua/xoa + su kien dang nhap. -->
<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { Loader2 } from 'lucide-vue-next'
import TableCard from '@/core/components/TableCard.vue'
import TablePagination from '@/core/components/TablePagination.vue'
import { errorMessage } from '@/core/api/errors'
import { formatDateTime } from '@/core/utils/format'
import { auditLogApi } from '../api'

const ACTIONS = {
  POST: 'Thêm / thao tác', PUT: 'Sửa', PATCH: 'Sửa', DELETE: 'Xoá',
  'login.success': 'Đăng nhập', 'login.fail': 'Đăng nhập sai', 'login.2fa_fail': 'Sai mã 2FA',
  logout: 'Đăng xuất', '2fa.enable': 'Bật 2FA', '2fa.disable': 'Tắt 2FA', '2fa.backup_codes': 'Tạo mã dự phòng',
  'password.change': 'Đổi mật khẩu', 'password.reset_requested': 'Xin đặt lại MK', 'password.reset': 'Đặt lại MK',
  'session.reuse_detected': 'Phiên bị dùng lại (nghi lộ)',
}
const MODULES = { common: 'Dữ liệu chung', lab: 'Kỹ thuật', hr: 'Nhân sự', system: 'Hệ thống', website: 'Website', auth: 'Đăng nhập' }

const filters = reactive({ module: '', action: '' })
const page = ref(1)
const pageSize = ref(50)
const result = ref({ items: [], total: 0 })
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    result.value = await auditLogApi.list({
      page: page.value, page_size: pageSize.value,
      module: filters.module || undefined, action: filters.action || undefined,
    })
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}
onMounted(load)
watch(filters, () => { page.value = 1; load() })
watch([page, pageSize], load)

const bad = item => item.status >= 400 || /fail|reuse/.test(item.action)
</script>

<template>
  <TableCard title="Nhật ký thao tác" :can-add="false">
    <template #actions>
      <select v-model="filters.module" class="field-input flex-1 sm:flex-initial text-xs sm:text-sm">
        <option value="">Mọi phân hệ</option>
        <option v-for="(label, key) in MODULES" :key="key" :value="key">{{ label }}</option>
      </select>
      <select v-model="filters.action" class="field-input flex-1 sm:flex-initial text-xs sm:text-sm">
        <option value="">Mọi thao tác</option>
        <option value="login">Đăng nhập</option>
        <option value="password">Mật khẩu</option>
        <option value="2fa">2FA</option>
        <option value="POST">Thêm</option>
        <option value="PUT">Sửa</option>
        <option value="DELETE">Xoá</option>
      </select>
    </template>

    <p v-if="error" class="px-5 pb-4 text-sm text-red-600">{{ error }}</p>
    <div class="flex-1 min-h-0 overflow-auto px-5">
      <div v-if="loading && !result.items.length" class="py-10 flex justify-center"><Loader2 class="w-5 h-5 animate-spin text-slate-400" /></div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
            <th class="py-2 pr-4 font-medium whitespace-nowrap">Thời gian</th>
            <th class="py-2 pr-4 font-medium">Người</th>
            <th class="py-2 pr-4 font-medium">Thao tác</th>
            <th class="py-2 pr-4 font-medium hidden md:table-cell">Đường dẫn</th>
            <th class="py-2 font-medium hidden lg:table-cell">IP</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in result.items" :key="item.id" class="border-b border-slate-100 dark:border-slate-700/60">
            <td class="py-2 pr-4 whitespace-nowrap text-slate-500">{{ formatDateTime(item.created_at) }}</td>
            <td class="py-2 pr-4 text-slate-700 dark:text-slate-200">{{ item.user_email || '—' }}</td>
            <td class="py-2 pr-4" :class="bad(item) ? 'text-red-600' : 'text-slate-700 dark:text-slate-200'">
              {{ ACTIONS[item.action] || item.action }}
              <span v-if="item.module" class="text-xs text-slate-400"> · {{ MODULES[item.module] || item.module }}</span>
            </td>
            <td class="py-2 pr-4 hidden md:table-cell font-mono text-xs text-slate-400">{{ item.path }}<span v-if="item.status"> → {{ item.status }}</span></td>
            <td class="py-2 hidden lg:table-cell text-xs text-slate-400">{{ item.ip }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <template #footer>
      <TablePagination
        v-model:page="page" v-model:page-size="pageSize"
        :total-rows="result.total" :total-pages="Math.max(1, Math.ceil(result.total / pageSize))"
        :page-size-options="[20, 50, 100, 200]"
      />
    </template>
  </TableCard>
</template>
