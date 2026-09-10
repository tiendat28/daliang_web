import { reactive, watch } from 'vue'

const stored = localStorage.getItem('theme')
const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches

export const themeStore = reactive({ mode: stored === 'dark' || stored === 'light' ? stored : (prefersDark ? 'dark' : 'light') })

function apply(mode) {
  document.documentElement.classList.toggle('dark', mode === 'dark')
}
apply(themeStore.mode)

watch(() => themeStore.mode, (mode) => {
  apply(mode)
  localStorage.setItem('theme', mode)
})

export function setTheme(mode) {
  themeStore.mode = mode
}
