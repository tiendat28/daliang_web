<!-- /login (ban thiet ke Login.dc.html) - dang nhap bang ma nhan vien hoac email. -->
<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { Loader2, LockKeyhole, ShieldCheck, UserRound } from 'lucide-vue-next'
import AuthLayout from '@/core/layouts/AuthLayout.vue'
import { errorMessage } from '@/core/api/errors'
import { authApi } from '../api'
import { setUser } from '../store'

const route = useRoute()
const router = useRouter()
const identifier = ref('')
const password = ref('')
const remember = ref(false)
const error = ref('')
const busy = ref(false)

async function submit() {
  busy.value = true
  error.value = ''
  try {
    const result = await authApi.login(identifier.value, password.value, remember.value)
    const redirect = route.query.redirect || '/'
    if (result.step === 'done') {
      setUser(result.user)
      router.replace(redirect)
    } else {
      const mode = result.step === 'setup_2fa' ? 'setup' : undefined
      router.push({ name: 'verify-2fa', query: { redirect, mode } })
    }
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthLayout title="Đăng nhập" subtitle="Dùng mã nhân viên hoặc email công ty.">
    <form class="flex flex-col gap-5" @submit.prevent="submit">
      <div class="flex flex-col gap-2">
        <label for="identifier" class="dl-label">Mã nhân viên / Email</label>
        <label class="dl-field">
          <UserRound class="w-[18px] h-[18px] shrink-0" :stroke-width="1.8" />
          <input id="identifier" v-model="identifier" type="text" autocomplete="username" placeholder="DL0123 hoặc ten@daliang.com" required autofocus />
        </label>
      </div>
      <div class="flex flex-col gap-2">
        <div class="flex justify-between">
          <label for="password" class="dl-label">Mật khẩu</label>
          <RouterLink :to="{ name: 'forgot-password' }" class="text-[13px] font-semibold text-dl-teal hover:text-dl-tealdark no-underline">Quên mật khẩu?</RouterLink>
        </div>
        <label class="dl-field">
          <LockKeyhole class="w-[18px] h-[18px] shrink-0" :stroke-width="1.8" />
          <input id="password" v-model="password" type="password" autocomplete="current-password" placeholder="••••••••" required />
        </label>
      </div>
      <label class="flex items-center gap-2.5 text-sm text-dl-body dark:text-slate-300">
        <input v-model="remember" type="checkbox" class="w-[18px] h-[18px] accent-dl-teal" />
        Ghi nhớ thiết bị này trong 30 ngày
      </label>
      <p v-if="error" class="m-0 text-sm text-dl-badink">{{ error }}</p>
      <button type="submit" class="dl-btn dl-btn-lg" :disabled="busy">
        <Loader2 v-if="busy" class="w-4 h-4 animate-spin" /> Đăng nhập
      </button>
      <div class="flex gap-3 px-4 py-3.5 rounded-[14px] bg-dl-note text-dl-softink text-[13px] leading-[1.5] dark:bg-slate-800 dark:text-brand-300">
        <ShieldCheck class="w-[18px] h-[18px] shrink-0" :stroke-width="1.8" />
        <span>Tài khoản admin và kế toán sẽ được hỏi thêm mã xác thực 6 số (ứng dụng Authenticator) ở bước tiếp theo.</span>
      </div>
    </form>
  </AuthLayout>
</template>
