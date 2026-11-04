<!-- /verify-2fa - buoc 2 cua dang nhap. ?mode=setup: vai tro bat buoc 2FA ma chua
     cai (quet QR); khong co mode: nhap ma 6 so hoac mot ma du phong. -->
<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, KeyRound, Loader2 } from 'lucide-vue-next'
import AuthLayout from '@/core/layouts/AuthLayout.vue'
import { errorMessage } from '@/core/api/errors'
import BackupCodes from '../components/BackupCodes.vue'
import TotpSetup from '../components/TotpSetup.vue'
import { authApi } from '../api'
import { setUser } from '../store'

const route = useRoute()
const router = useRouter()
const setupMode = computed(() => route.query.mode === 'setup')
const redirect = computed(() => route.query.redirect || '/')

const code = ref('')
const error = ref('')
const busy = ref(false)
const backupCodes = ref(null)   // co sau khi cai xong - hien cho nguoi dung luu truoc khi vao
const pendingUser = ref(null)

function backToLogin() {
  router.replace({ name: 'login', query: { redirect: redirect.value } })
}

async function verify() {
  busy.value = true
  error.value = ''
  try {
    const result = await authApi.verify2fa(code.value.trim())
    setUser(result.user)
    router.replace(redirect.value)
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

function enabled(result) {
  backupCodes.value = result.backup_codes
  pendingUser.value = result.user
}

function finish() {
  setUser(pendingUser.value)
  router.replace(redirect.value)
}
</script>

<template>
  <AuthLayout
    :title="setupMode ? 'Cài xác thực 2 bước' : 'Xác thực 2 bước'"
    :subtitle="setupMode ? 'Vai trò của bạn bắt buộc bật 2FA trước khi vào.' : 'Nhập mã 6 số trong app Authenticator.'"
  >
    <template v-if="backupCodes">
      <BackupCodes :codes="backupCodes" />
      <button type="button" class="mt-4 w-full h-11 rounded-xl bg-brand-gradient text-white font-semibold" @click="finish">
        Tôi đã lưu mã — vào hệ thống
      </button>
    </template>

    <TotpSetup v-else-if="setupMode" @enabled="enabled" @expired="backToLogin" />

    <form v-else class="flex flex-col gap-4" @submit.prevent="verify">
      <div class="flex flex-col gap-2">
        <label class="dl-label" for="code">Mã xác thực</label>
        <label class="dl-field">
          <KeyRound class="h-[18px] w-[18px] shrink-0" :stroke-width="1.8" />
          <input id="code" v-model="code" autocomplete="one-time-code" maxlength="9" inputmode="numeric" placeholder="123456 hoặc XXXX-XXXX" class="text-center tracking-[0.3em] text-lg" required autofocus />
        </label>
        <p class="m-0 text-xs text-dl-muted">Mất điện thoại? Nhập một mã dự phòng dạng XXXX-XXXX.</p>
      </div>
      <p v-if="error" class="m-0 text-sm text-dl-badink">{{ error }}</p>
      <button type="submit" class="dl-btn dl-btn-lg" :disabled="busy">
        <Loader2 v-if="busy" class="w-4 h-4 animate-spin" /> Xác nhận
      </button>
      <button type="button" class="inline-flex items-center justify-center gap-2 text-sm font-semibold text-dl-muted hover:text-dl-teal" @click="backToLogin">
        <ArrowLeft class="h-4 w-4" /> Đăng nhập lại
      </button>
    </form>
  </AuthLayout>
</template>
