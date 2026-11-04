<!-- /forgot-password -->
<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ArrowLeft, CircleCheck, Loader2, Mail } from 'lucide-vue-next'
import AuthLayout from '@/core/layouts/AuthLayout.vue'
import { errorMessage } from '@/core/api/errors'
import { authApi } from '../api'

const email = ref('')
const sent = ref(false)
const error = ref('')
const busy = ref(false)

async function submit() {
  busy.value = true
  error.value = ''
  try {
    await authApi.forgotPassword(email.value)
    sent.value = true
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthLayout title="Quên mật khẩu" subtitle="Nhập email tài khoản, chúng tôi gửi link đặt lại mật khẩu.">
    <div v-if="sent" class="flex flex-col gap-4">
      <div class="flex items-start gap-3 rounded-[14px] bg-dl-note px-4 py-3.5 text-sm leading-[1.5] text-dl-softink dark:bg-slate-800 dark:text-brand-300">
        <CircleCheck class="mt-0.5 h-[18px] w-[18px] shrink-0" :stroke-width="1.8" />
        <p class="m-0">
        Nếu <b>{{ email }}</b> có tài khoản, link đặt lại mật khẩu đã được gửi (hết hạn sau 30 phút).
        Không thấy email thì kiểm tra thư rác, hoặc nhờ quản trị viên cấp mật khẩu tạm.
        </p>
      </div>
      <RouterLink :to="{ name: 'login' }" class="inline-flex items-center gap-2 text-sm font-semibold text-dl-teal hover:text-dl-tealdark no-underline">
        <ArrowLeft class="h-4 w-4" /> Về trang đăng nhập
      </RouterLink>
    </div>
    <form v-else class="flex flex-col gap-4" @submit.prevent="submit">
      <div class="flex flex-col gap-2">
        <label class="dl-label" for="email">Email công ty</label>
        <label class="dl-field">
          <Mail class="h-[18px] w-[18px] shrink-0" :stroke-width="1.8" />
          <input id="email" v-model="email" type="email" autocomplete="username" placeholder="ten@daliang.com" required autofocus />
        </label>
      </div>
      <p v-if="error" class="m-0 text-sm text-dl-badink">{{ error }}</p>
      <button type="submit" class="dl-btn dl-btn-lg" :disabled="busy">
        <Loader2 v-if="busy" class="w-4 h-4 animate-spin" /> Gửi link
      </button>
      <RouterLink :to="{ name: 'login' }" class="inline-flex items-center justify-center gap-2 text-sm font-semibold text-dl-muted hover:text-dl-teal no-underline">
        <ArrowLeft class="h-4 w-4" /> Về trang đăng nhập
      </RouterLink>
    </form>
  </AuthLayout>
</template>
