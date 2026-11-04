<script setup>
import { AlertTriangle, CheckCircle2, Info, ShieldAlert, X } from 'lucide-vue-next'
import { notify, notifyState } from '@/core/store/notify'

function getIcon(type) {
  if (type === 'error') return ShieldAlert
  if (type === 'warning') return AlertTriangle
  if (type === 'success') return CheckCircle2
  return Info
}

function getStyle(type) {
  if (type === 'error') {
    return {
      card: 'border-rose-200 dark:border-rose-800/80 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 shadow-[0_8px_30px_rgb(225,29,72,0.15)]',
      iconWrap: 'bg-rose-100 dark:bg-rose-950/80 text-rose-600 dark:text-rose-400',
      title: 'text-rose-700 dark:text-rose-400',
    }
  }
  if (type === 'warning') {
    return {
      card: 'border-amber-200 dark:border-amber-800/80 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 shadow-[0_8px_30px_rgb(217,119,6,0.15)]',
      iconWrap: 'bg-amber-100 dark:bg-amber-950/80 text-amber-600 dark:text-amber-400',
      title: 'text-amber-700 dark:text-amber-400',
    }
  }
  if (type === 'success') {
    return {
      card: 'border-emerald-200 dark:border-emerald-800/80 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 shadow-[0_8px_30px_rgb(16,185,129,0.15)]',
      iconWrap: 'bg-emerald-100 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400',
      title: 'text-emerald-700 dark:text-emerald-400',
    }
  }
  return {
    card: 'border-sky-200 dark:border-sky-800/80 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 shadow-[0_8px_30px_rgb(14,165,233,0.15)]',
    iconWrap: 'bg-sky-100 dark:bg-sky-950/80 text-sky-600 dark:text-sky-400',
    title: 'text-sky-700 dark:text-sky-400',
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed top-5 right-5 z-[99999] flex flex-col gap-3 max-w-sm sm:max-w-md w-full px-4 sm:px-0 pointer-events-none"
      aria-live="polite"
    >
      <TransitionGroup
        enter-active-class="transform transition ease-out duration-300"
        enter-from-class="translate-y-[-12px] opacity-0 scale-95"
        enter-to-class="translate-y-0 opacity-100 scale-100"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-for="toast in notifyState.toasts"
          :key="toast.id"
          class="pointer-events-auto flex items-start gap-3 p-3.5 rounded-2xl border shadow-lg backdrop-blur-sm"
          :class="getStyle(toast.type).card"
          role="alert"
        >
          <!-- Icon -->
          <div
            class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
            :class="getStyle(toast.type).iconWrap"
          >
            <component :is="getIcon(toast.type)" class="w-5 h-5" />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0 pr-1">
            <h4
              v-if="toast.title"
              class="text-sm font-bold m-0 leading-snug"
              :class="getStyle(toast.type).title"
            >
              {{ toast.title }}
            </h4>
            <p class="text-xs sm:text-sm mt-0.5 text-slate-600 dark:text-slate-300 leading-relaxed break-words m-0">
              {{ toast.message }}
            </p>
          </div>

          <!-- Close button -->
          <button
            type="button"
            class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors shrink-0"
            title="Đóng thông báo"
            @click="notify.remove(toast.id)"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
