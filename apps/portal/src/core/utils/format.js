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

/** Chữ cái đầu của tên để làm avatar: "Nguyễn Thị Thu" -> "NT" (họ + tên đệm đầu). */
export function initials(name) {
  const words = String(name || '').trim().split(/\s+/).filter(Boolean)
  if (!words.length) return '?'
  return (words[0][0] + (words[1]?.[0] || '')).toUpperCase()
}

/** Định dạng tiền tệ VND: 48600000 -> "48.600.000 ₫" */
export function formatCurrency(amount) {
  if (amount == null || amount === '') return '0 ₫'
  return new Intl.NumberFormat('vi-VN').format(amount) + ' ₫'
}

/** Định dạng số có dấu phân cách hàng nghìn (13600 -> "13.600") */
export function formatNumber(num) {
  if (num === null || num === undefined || num === '') return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

/** Định dạng ngày hết hạn sang dạng MM/YYYY (2027-09-30 -> "09/2027") */
export function formatExpiry(dateStr) {
  if (!dateStr) return '—'
  try {
    const parts = String(dateStr).split('-')
    if (parts.length >= 2) {
      return `${parts[1]}/${parts[0]}`
    }
    return dateStr
  } catch {
    return dateStr
  }
}

/** Định dạng phần trăm (65 -> "65%") */
export function formatPercent(val) {
  if (val === null || val === undefined || val === '') return '0%'
  return `${val}%`
}


