import { reactive, watch } from 'vue'

const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('theme') : null
const prefersDark = typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches

export const themeStore = reactive({
  mode: stored === 'dark' || stored === 'light' ? stored : (prefersDark ? 'dark' : 'light'),
})

function apply(mode) {
  if (typeof document !== 'undefined') {
    document.documentElement.classList.toggle('dark', mode === 'dark')
  }
}
apply(themeStore.mode)

watch(() => themeStore.mode, (mode) => {
  apply(mode)
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('theme', mode)
  }
})

export function setTheme(mode) {
  themeStore.mode = mode
}

export function toggleTheme() {
  themeStore.mode = themeStore.mode === 'dark' ? 'light' : 'dark'
}
