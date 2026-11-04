import { reactive } from 'vue'

export const notifyState = reactive({
  toasts: [],
})

let nextId = 1

export const notify = {
  add({ type = 'info', title = '', message = '', duration = 4000 }) {
    const id = nextId++
    const toast = { id, type, title, message, duration }
    notifyState.toasts.push(toast)
    if (duration > 0) {
      setTimeout(() => {
        notify.remove(id)
      }, duration)
    }
    return id
  },
  success(message, title = 'Thành công') {
    return notify.add({ type: 'success', title, message })
  },
  error(message, title = 'Lỗi') {
    return notify.add({ type: 'error', title, message, duration: 5000 })
  },
  warning(message, title = 'Cảnh báo') {
    return notify.add({ type: 'warning', title, message, duration: 5000 })
  },
  permissionDenied(message = 'Bạn không có quyền thực hiện thao tác này') {
    return notify.add({
      type: 'error',
      title: 'Không có quyền thực hiện',
      message,
      duration: 6000,
    })
  },
  remove(id) {
    const idx = notifyState.toasts.findIndex(t => t.id === id)
    if (idx > -1) {
      notifyState.toasts.splice(idx, 1)
    }
  },
  clear() {
    notifyState.toasts = []
  },
}
