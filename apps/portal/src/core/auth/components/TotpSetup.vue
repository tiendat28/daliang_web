<!-- Cai 2FA: quet QR bang app Authenticator, nhap ma 6 so de xac nhan.
     Dung luc dang nhap (vai tro bat buoc 2FA) va o trang Tai khoan.
     Xong thi phat 'enabled' kem { backup_codes, user? }. -->
<script setup>
import { onMounted, ref } from 'vue'
import { KeyRound, Loader2, QrCode } from 'lucide-vue-next'
import { authApi } from '../api'
import { errorMessage } from '@/core/api/errors'

const emit = defineEmits(['enabled', 'expired'])

const qr = ref('')
const secret = ref('')
const code = ref('')
const error = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    const data = await authApi.setup2fa()
    qr.value = data.qr
    secret.value = data.secret
  } catch (e) {
    if (e.response?.status === 401) emit('expired')
    else error.value = errorMessage(e)
  }
})

async function confirm() {
  busy.value = true
  error.value = ''
  try {
    emit('enabled', await authApi.enable2fa(code.value.trim()))
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <form class="flex flex-col gap-4" @submit.prevent="confirm">
    <ol class="text-sm leading-[1.55] text-dl-body dark:text-slate-300 list-decimal pl-5 space-y-1">
      <li>Cài <b>Google Authenticator</b> hoặc <b>Microsoft Authenticator</b> trên điện thoại.</li>
      <li>Trong app, chọn thêm tài khoản rồi quét mã dưới đây.</li>
      <li>Nhập mã 6 số app hiện ra.</li>
    </ol>
    <div class="flex justify-center rounded-[14px] bg-dl-panel p-4 dark:bg-slate-800">
      <img v-if="qr" :src="qr" alt="Mã QR cài 2FA" class="h-48 w-48 rounded-xl bg-white p-2" />
      <div v-else class="flex h-48 w-48 items-center justify-center"><Loader2 class="h-6 w-6 animate-spin text-dl-muted" /></div>
    </div>
    <p v-if="secret" class="m-0 text-center text-xs text-dl-muted break-all">
      Không quét được? Nhập tay: <span class="font-mono text-dl-body dark:text-slate-300">{{ secret }}</span>
    </p>
    <div class="flex flex-col gap-2">
      <label class="dl-label" for="totp-code">Mã 6 số</label>
      <label class="dl-field">
        <KeyRound class="h-[18px] w-[18px] shrink-0" :stroke-width="1.8" />
        <input id="totp-code" v-model="code" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="123456" class="text-center tracking-[0.4em] text-lg" required />
      </label>
    </div>
    <p v-if="error" class="m-0 text-sm text-dl-badink">{{ error }}</p>
    <button type="submit" class="dl-btn dl-btn-lg" :disabled="busy || !qr">
      <Loader2 v-if="busy" class="w-4 h-4 animate-spin" /> Xác nhận
    </button>
  </form>
</template>
