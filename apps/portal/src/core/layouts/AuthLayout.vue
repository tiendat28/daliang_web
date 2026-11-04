<!-- Khung cac trang dang nhap / 2FA / quen mat khau (ban thiet ke Login.dc.html):
     khoi xanh dam gioi thieu cong ben trai, form ben phai. Man hep chi con form. -->
<script setup>
import { Calculator, Droplet, FlaskConical, Package, Truck, Users } from 'lucide-vue-next'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})

const DEPARTMENTS = [
  { label: 'Kỹ thuật', icon: FlaskConical },
  { label: 'Nhân sự', icon: Users },
  { label: 'Kế toán', icon: Calculator },
  { label: 'Kho', icon: Package },
  { label: 'Điều phối xe', icon: Truck },
]
</script>

<template>
  <div class="h-screen overflow-y-auto flex gap-5 p-3 sm:p-5 bg-dl-page dark:bg-none dark:bg-slate-900">
    <section class="auth-intro hidden lg:flex flex-1 rounded-[28px] bg-dl-dark p-12 flex-col justify-between min-h-full">
      <div class="flex items-center gap-2.5">
        <span class="w-11 h-11 rounded-xl bg-dl-grad text-white inline-flex items-center justify-center">
          <Droplet class="w-[22px] h-[22px]" :stroke-width="2" />
        </span>
        <span class="flex flex-col leading-[1.1]">
          <span class="text-[17px] font-bold tracking-[0.06em] text-white">DALIANG</span>
          <span class="text-[11px] font-medium text-[#a7d8d1]">Hoá chất xi mạ</span>
        </span>
      </div>
      <div class="flex flex-col gap-[18px]">
        <h1 class="m-0 text-[42px] leading-[1.15] font-bold tracking-[-0.02em] text-white">Cổng làm việc nội bộ</h1>
        <p class="m-0 text-base leading-[1.6] text-[#c7e3df] max-w-[460px]">
          Một tài khoản cho mọi bộ phận. Sau khi đăng nhập, bạn chỉ thấy những mục mình được cấp quyền.
        </p>
        <div class="flex flex-wrap gap-2.5 mt-2">
          <span v-for="dept in DEPARTMENTS" :key="dept.label" class="inline-flex items-center gap-2 h-10 px-3.5 rounded-xl bg-white/[0.08] text-[#e4f3f1] text-sm font-medium">
            <component :is="dept.icon" class="w-4 h-4 text-dl-mint" :stroke-width="1.8" />{{ dept.label }}
          </span>
        </div>
      </div>
      <span class="text-[13px] text-[#86b3ad]">Chỉ dành cho nhân viên Daliang VN. Mọi truy cập đều được ghi nhật ký.</span>
    </section>

    <section class="w-full lg:w-[560px] shrink-0 flex items-center justify-center py-8">
      <div class="w-full max-w-[420px] flex flex-col gap-5">
        <div class="flex lg:hidden items-center gap-2.5 mb-2">
          <span class="w-10 h-10 rounded-xl bg-dl-grad text-white inline-flex items-center justify-center">
            <Droplet class="w-5 h-5" :stroke-width="2" />
          </span>
          <span class="text-[17px] font-bold tracking-[0.06em] text-dl-ink dark:text-slate-100">DALIANG</span>
        </div>
        <div class="flex flex-col gap-2">
          <h2 class="m-0 text-[30px] font-bold text-dl-ink dark:text-slate-100">{{ title }}</h2>
          <p v-if="subtitle" class="m-0 text-[15px] text-dl-muted dark:text-slate-400">{{ subtitle }}</p>
        </div>
        <slot />
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Luoi o vuong mo tren nen xanh dam, 40px moi o */
.auth-intro {
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 40px 40px;
}
</style>
