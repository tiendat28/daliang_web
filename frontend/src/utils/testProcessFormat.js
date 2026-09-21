/**
 * Bản sao phía trình duyệt của app/services/test_process_format.py.
 *
 * Dùng cho những chỗ chưa gửi dữ liệu lên server: dòng tóm tắt của bước đang
 * thu gọn trong form và gợi ý "in ra: …" cạnh ô nồng độ. Tờ A4 xem trước vẫn
 * do backend dựng, nên nếu hai bên lệch nhau thì bản Python là bản đúng.
 *
 * Mọi hàm trả về CHUỖI HTML ĐÃ ESCAPE (có thể chứa <sub>/<sup>) — hiện bằng
 * v-html. Cần chuỗi trơn thì dùng stripHtml().
 */

const TIME_UNIT_LABELS = { sec: 'giây', min: 'phút', hour: 'giờ' }
const AMBIENT_LABEL = 'Thường'

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
}

/** Bỏ số 0 thừa: 50.00 -> "50", 1.30 -> "1.3". */
export function formatNumber(value) {
  if (value === null || value === undefined || value === '') return ''
  const number = Number(value)
  if (Number.isNaN(number)) return String(value)
  return String(Number(number.toFixed(3)))
}

/** Có cả hai -> "min-max"; chỉ một -> giá trị đó. */
export function formatRange(valueMin, valueMax) {
  const low = formatNumber(valueMin)
  const high = formatNumber(valueMax)
  if (low && high) return low === high ? low : `${low}-${high}`
  return low || high
}

/** Tự đổi chữ số trong công thức sang cú pháp đánh dấu: HNO3 -> HNO_3, Zn2+ -> Zn^2+. */
export function applyFormulaMarkers(text) {
  if (!text) return ''
  return String(text).replace(/([A-Za-z)])(\d+)([+-]?)/g, (_m, before, digits, sign) =>
    `${before}${sign ? '^' : '_'}${digits}${sign}`)
}

/** Escape HTML rồi đổi "_" thành <sub>, "^" thành <sup>. */
export function renderMarkers(text) {
  if (!text) return ''
  return escapeHtml(text).replace(/([_^])(\d+[+-]?|[+-])/g, (_m, marker, body) => {
    const tag = marker === '_' ? 'sub' : 'sup'
    return `<${tag}>${body}</${tag}>`
  })
}

/** Bỏ ký hiệu _ ^ để lấy chuỗi trơn: "HNO_3" -> "HNO3". */
export function stripMarkers(text) {
  return text ? String(text).replace(/[_^]/g, '') : ''
}

/** Bỏ thẻ HTML để nhét chuỗi vào title / aria-label. */
export function stripHtml(html) {
  return html ? String(html).replace(/<[^>]*>/g, '') : ''
}

export function formatTime(step) {
  if (step.time_text) return renderMarkers(step.time_text)
  const span = formatRange(step.time_min, step.time_max)
  if (!span) return ''
  const unit = TIME_UNIT_LABELS[step.time_unit] || ''
  return escapeHtml(`${span} ${unit}`.trim())
}

export function formatTemperature(step) {
  if (step.temp_text) return renderMarkers(step.temp_text)
  const mode = step.temp_mode || 'none'
  if (mode === 'ambient') return escapeHtml(AMBIENT_LABEL)
  if (mode !== 'range') return ''
  const span = formatRange(step.temp_min, step.temp_max)
  return span ? escapeHtml(`${span}°C`) : ''
}

export function formatPh(step) {
  if (step.ph_text) return renderMarkers(step.ph_text)
  return escapeHtml(formatRange(step.ph_min, step.ph_max))
}

export function formatConcentration(row) {
  if (row.text_override) return renderMarkers(row.text_override)
  const span = formatRange(row.value_min, row.value_max)
  const value = escapeHtml(`${span}${row.unit || ''}`)
  if (!row.component) return value
  if (!value) return renderMarkers(row.component)
  return `${renderMarkers(row.component)}: ${value}`
}

export function formatChemical(row) {
  return renderMarkers(row.display_name || '')
}

/** Toàn bộ phần chữ in được của 1 bước — cùng cấu trúc với step.display của API. */
export function stepDisplay(step) {
  return {
    operation: renderMarkers(step.operation || ''),
    time: formatTime(step),
    temperature: formatTemperature(step),
    ph: formatPh(step),
    concentrations: (step.concentrations || []).map(formatConcentration),
    chemicals: (step.chemicals || []).map(formatChemical),
  }
}

/** Dòng tóm tắt của bước đang thu gọn: "2-3 phút · Thường · 0.5% · HNO₃". */
export function stepSummary(step) {
  const display = step.display || stepDisplay(step)
  const parts = [
    display.time,
    display.temperature,
    display.ph ? `pH ${display.ph}` : '',
    ...display.concentrations,
    ...display.chemicals,
  ].filter(Boolean)
  return parts.join(' · ')
}

/** Bỏ dấu tiếng Việt để tìm kiếm không phân biệt dấu: "Rua nuoc" khớp "Rửa nước". */
export function foldAccents(text) {
  if (!text) return ''
  return String(text)
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
}

/** In 2 chữ số: 2 -> "02". */
export function formatSampleQuantity(quantity) {
  const number = Number(quantity)
  return Number.isFinite(number) ? String(Math.trunc(number)).padStart(2, '0') : ''
}

/** "2026-08-01" -> "08/2026". */
export function formatTestMonth(value) {
  if (!value) return ''
  const [year, month] = String(value).split('-')
  return month ? `${month}/${year}` : String(value)
}

/** Dòng meta dưới tên khách: "08/2026 · 02 mẫu · 10 bước". */
export function formatProcessMeta({ testMonth, sampleQuantity, stepCount }) {
  return [
    formatTestMonth(testMonth),
    `${formatSampleQuantity(sampleQuantity)} mẫu`,
    `${stepCount || 0} bước`,
  ].join(' · ')
}

/** Lấy tối đa `max` phần tử đầu và đếm phần còn lại, cho dãy chip "+3". */
export function takeWithOverflow(list, max) {
  const items = (list || []).filter(Boolean)
  return { items: items.slice(0, max), extra: Math.max(0, items.length - max) }
}

/** "2026-08-01" -> "2026-08" cho ô <input type="month">. */
export function toMonthInput(value) {
  return value ? String(value).slice(0, 7) : ''
}

/** "2026-08" -> "2026-08-01" như API mong đợi. */
export function fromMonthInput(value) {
  return value ? `${value}-01` : null
}
