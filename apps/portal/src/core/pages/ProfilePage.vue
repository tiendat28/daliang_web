<!-- /profile - tai khoan cua toi: doi mat khau, bat/tat 2FA, ma du phong.
     Mat khau tam (admin cap) thi bi dua ve day cho toi khi doi xong. -->
<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { KeyRound, Loader2, ShieldCheck } from 'lucide-vue-next'
import { errorMessage } from '@/core/api/errors'
import { authApi } from '@/core/auth/api'
import { auth, setUser } from '@/core/auth/store'
import BackupCodes from '@/core/auth/components/BackupCodes.vue'
import TotpSetup from '@/core/auth/components/TotpSetup.vue'

const router = useRouter()
const TWO_FACTOR_ENABLED = false

const passwordForm = reactive({ current: '', next: '', confirm: '' })
const passwordMessage = ref('')
const passwordError = ref('')
const savingPassword = ref(false)

async function changePassword() {
  passwordMessage.value = ''
  passwordError.value = ''
  if (passwordForm.next !== passwordForm.confirm) {
    passwordError.value = 'Hai lần nhập mật khẩu mới không khớp'
    return
  }
  savingPassword.value = true
  const wasTemporary = auth.user.must_change_password
  try {
    setUser(await authApi.changePassword(passwordForm.current, passwordForm.next))
    Object.assign(passwordForm, { current: '', next: '', confirm: '' })
    passwordMessage.value = 'Đã đổi mật khẩu. Các thiết bị khác đã bị đăng xuất.'
    if (wasTemporary) router.replace('/')
  } catch (e) {
    passwordError.value = errorMessage(e)
  } finally {
    savingPassword.value = false
  }
}

// ---------- 2FA ----------
const settingUp = ref(false)
const backupCodes = ref(null)
const confirmPassword = ref('')
const twoFactorError = ref('')
const busy = ref(false)

async function onEnabled(result) {
  settingUp.value = false
  backupCodes.value = result.backup_codes
  setUser(await authApi.me())
}

async function withPassword(action) {
  busy.value = true
  twoFactorError.value = ''
  try {
    await action(confirmPassword.value)
    confirmPassword.value = ''
  } catch (e) {
    twoFactorError.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

const disable2fa = () => withPassword(async (password) => {
  setUser(await authApi.disable2fa(password))
  backupCodes.value = null
})
const newCodes = () => withPassword(async (password) => {
  backupCodes.value = (await authApi.newBackupCodes(password)).backup_codes
})
</script>

<template>
  <div class="flex flex-col gap-4 overflow-y-auto">
    <p v-if="auth.user?.must_change_password" class="px-4 py-3 rounded-2xl bg-amber-50 dark:bg-amber-900/30 text-sm text-amber-800 dark:text-amber-200">
      Bạn đang dùng mật khẩu tạm. Hãy đặt mật khẩu riêng để tiếp tục dùng hệ thống.
    </p>

    <section class="bg-white dark:bg-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm">
      <h2 class="font-semibold text-slate-800 dark:text-slate-100">{{ auth.user?.full_name }}</h2>
      <p class="text-sm text-slate-500 dark:text-slate-400">{{ auth.user?.email }}</p>
      <div class="flex flex-wrap gap-1.5 mt-3">
        <span v-for="role in auth.user?.roles" :key="role.code" class="px-2.5 py-0.5 rounded-full text-xs bg-brand-50 dark:bg-slate-700 text-brand-700 dark:text-brand-300">{{ role.name }}</span>
      </div>
    </section>

    <section class="bg-white dark:bg-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm">
      <h3 class="flex items-center gap-2 font-semibold text-slate-800 dark:text-slate-100 mb-4"><KeyRound class="w-4 h-4" /> Đổi mật khẩu</h3>
      <form class="grid gap-3 sm:grid-cols-3" @submit.prevent="changePassword">
        <div>
          <label class="field-label mb-1" for="current-password">Mật khẩu hiện tại</label>
          <input id="current-password" v-model="passwordForm.current" type="password" autocomplete="current-password" class="w-full field-input" required />
        </div>
        <div>
          <label class="field-label mb-1" for="new-password">Mật khẩu mới</label>
          <input id="new-password" v-model="passwordForm.next" type="password" autocomplete="new-password" class="w-full field-input" required />
        </div>
        <div>
          <label class="field-label mb-1" for="confirm-password">Nhập lại</label>
          <input id="confirm-password" v-model="passwordForm.confirm" type="password" autocomplete="new-password" class="w-full field-input" required />
        </div>
        <p class="sm:col-span-3 text-xs text-slate-400">Tối thiểu 10 ký tự, có cả chữ và số. Đổi xong, các thiết bị khác sẽ bị đăng xuất.</p>
        <p v-if="passwordError" class="sm:col-span-3 text-sm text-red-600">{{ passwordError }}</p>
        <p v-if="passwordMessage" class="sm:col-span-3 text-sm text-brand-700 dark:text-brand-300">{{ passwordMessage }}</p>
        <div class="sm:col-span-3">
          <button type="submit" class="h-10 px-5 rounded-xl bg-brand-gradient text-white text-sm font-semibold disabled:opacity-50 flex items-center gap-2" :disabled="savingPassword">
            <Loader2 v-if="savingPassword" class="w-4 h-4 animate-spin" /> Đổi mật khẩu
          </button>
        </div>
      </form>
    </section>

    <section v-if="TWO_FACTOR_ENABLED && !auth.user?.must_change_password" class="bg-white dark:bg-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm">
      <h3 class="flex items-center gap-2 font-semibold text-slate-800 dark:text-slate-100 mb-1"><ShieldCheck class="w-4 h-4" /> Xác thực 2 bước (2FA)</h3>
      <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">
        {{ auth.user?.totp_enabled ? 'Đang bật — mỗi lần đăng nhập cần thêm mã 6 số từ app Authenticator.' : 'Chưa bật.' }}
        <span v-if="auth.user?.require_2fa">Vai trò của bạn bắt buộc 2FA.</span>
      </p>

      <div class="max-w-md flex flex-col gap-4">
        <BackupCodes v-if="backupCodes" :codes="backupCodes" />

        <template v-if="!auth.user?.totp_enabled">
          <TotpSetup v-if="settingUp" @enabled="onEnabled" />
          <button v-else type="button" class="self-start h-10 px-5 rounded-xl bg-brand-gradient text-white text-sm font-semibold" @click="settingUp = true">Bật 2FA</button>
        </template>

        <form v-else class="flex flex-col gap-3" @submit.prevent>
          <div>
            <label class="field-label mb-1" for="confirm-2fa">Nhập mật khẩu để thao tác</label>
            <input id="confirm-2fa" v-model="confirmPassword" type="password" autocomplete="current-password" class="w-full field-input" />
          </div>
          <p v-if="twoFactorError" class="text-sm text-red-600">{{ twoFactorError }}</p>
          <div class="flex flex-wrap gap-2">
            <button type="button" class="h-10 px-4 rounded-xl border border-slate-200 dark:border-slate-600 text-sm text-slate-600 dark:text-slate-300 disabled:opacity-50" :disabled="busy || !confirmPassword" @click="newCodes">Tạo mã dự phòng mới</button>
            <button v-if="!auth.user?.require_2fa" type="button" class="h-10 px-4 rounded-xl border border-red-200 text-sm text-red-600 disabled:opacity-50" :disabled="busy || !confirmPassword" @click="disable2fa">Tắt 2FA</button>
          </div>
        </form>
      </div>
    </section>
  </div>
</template>
