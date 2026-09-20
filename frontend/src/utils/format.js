export function formatDate(dateStr) {
  if (!dateStr) return ''
  const [y, m, d] = dateStr.split('-')
  return `${d}.${m}.${y}`
}

export function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return ''
  if (bytes < 1024) return `${bytes} B`
  const units = ['KB', 'MB', 'GB']
  let value = bytes / 1024
  let i = 0
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024
    i++
  }
  return `${value.toFixed(1)} ${units[i]}`
}

// So gio tang ca: bo .0 thua (2 -> "2 giờ", 1.5 -> "1,5 giờ"), trong neu khong OT
export function formatOtHours(hours) {
  if (hours === null || hours === undefined || hours === '') return ''
  const value = Number(hours)
  if (Number.isNaN(value)) return ''
  return `${String(value).replace('.', ',')} giờ`
}

/** "2026-09" — tháng hiện tại, dùng cho ô chọn tháng (input type="month"). */
export function currentPeriod() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

/** "20260920" — hậu tố ngày cho tên file xuất ra. */
export function todayStamp() {
  const d = new Date()
  return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`
}

/** Tách "2026-09" thành { year: '2026', month: '9' } để ghép vào tiêu đề báo cáo. */
export function periodParts(period) {
  const [year, month] = (period || '').split('-')
  return { year, month: month ? String(Number(month)) : '' }
}
