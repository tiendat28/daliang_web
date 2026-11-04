<!-- /reset-password?token=... - mo tu link trong email -->
<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ArrowLeft, CircleCheck, LockKeyhole, Loader2 } from 'lucide-vue-next'
import AuthLayout from '@/core/layouts/AuthLayout.vue'
import { errorMessage } from '@/core/api/errors'
import { authApi } from '../api'

const route = useRoute()
const password = ref('')
const confirm = ref('')
const done = ref(false)
const error = ref('')
const busy = ref(false)

async function submit() {
  if (password.value !== confirm.value) {
    error.value = 'Hai lần nhập không khớp'
    return
  }
  busy.value = true
  error.value = ''
  try {
    await authApi.resetPassword(String(route.query.token || ''), password.value)
    done.value = true
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthLayout title="Đặt mật khẩu mới" subtitle="Tối thiểu 10 ký tự, có cả chữ và số.">
    <div v-if="done" class="flex flex-col gap-4">
      <div class="flex items-start gap-3 rounded-[14px] bg-dl-note px-4 py-3.5 text-sm leading-[1.5] text-dl-softink dark:bg-slate-800 dark:text-brand-300">
        <CircleCheck class="mt-0.5 h-[18px] w-[18px] shrink-0" :stroke-width="1.8" />
        <p class="m-0">Đã đổi mật khẩu. Mọi phiên đăng nhập cũ đã bị đăng xuất.</p>
      </div>
      <RouterLink :to="{ name: 'login' }" class="dl-btn dl-btn-lg no-underline">Đăng nhập</RouterLink>
    </div>
    <form v-else class="flex flex-col gap-4" @submit.prevent="submit">
      <div class="flex flex-col gap-2">
        <label class="dl-label" for="new-password">Mật khẩu mới</label>
        <label class="dl-field">
          <LockKeyhole class="h-[18px] w-[18px] shrink-0" :stroke-width="1.8" />
          <input id="new-password" v-model="password" type="password" autocomplete="new-password" placeholder="Tối thiểu 10 ký tự" required autofocus />
        </label>
      </div>
      <div class="flex flex-col gap-2">
        <label class="dl-label" for="confirm-password">Nhập lại mật khẩu</label>
        <label class="dl-field">
          <LockKeyhole class="h-[18px] w-[18px] shrink-0" :stroke-width="1.8" />
          <input id="confirm-password" v-model="confirm" type="password" autocomplete="new-password" placeholder="Nhập lại mật khẩu mới" required />
        </label>
      </div>
      <p v-if="error" class="m-0 text-sm text-dl-badink">{{ error }}</p>
      <button type="submit" class="dl-btn dl-btn-lg" :disabled="busy">
        <Loader2 v-if="busy" class="w-4 h-4 animate-spin" /> Đổi mật khẩu
      </button>
    </form>
  </AuthLayout>
</template>
