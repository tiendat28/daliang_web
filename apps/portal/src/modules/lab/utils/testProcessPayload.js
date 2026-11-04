/**
 * Dọn dữ liệu form trước khi gửi lên API của module "Lưu trình test mẫu".
 *
 * Ô số để trống trả về chuỗi rỗng chứ không phải null, còn schema bên backend
 * chỉ nhận số hoặc null — nên mọi payload đều đi qua đây.
 */

/** "" / null / không phải số -> null. */
export function numOrNull(value) {
  if (value === '' || value === null || value === undefined) return null
  const number = Number(value)
  return Number.isNaN(number) ? null : number
}

/** Chuỗi rỗng (kể cả toàn dấu cách) -> null. */
export function textOrNull(value) {
  const text = (value ?? '').toString().trim()
  return text || null
}

/** Một bước đúng hình dạng TestProcessStepIn. */
export function stepPayload(step) {
  return {
    operation: (step.operation || '').trim(),
    time_min: numOrNull(step.time_min),
    time_max: numOrNull(step.time_max),
    time_unit: step.time_unit || null,
    temp_mode: step.temp_mode || 'none',
    temp_min: numOrNull(step.temp_min),
    temp_max: numOrNull(step.temp_max),
    ph_min: numOrNull(step.ph_min),
    ph_max: numOrNull(step.ph_max),
    time_text: textOrNull(step.time_text),
    temp_text: textOrNull(step.temp_text),
    ph_text: textOrNull(step.ph_text),
    note: textOrNull(step.note),
    concentrations: (step.concentrations || [])
      // Dòng trống hoàn toàn thì bỏ, khỏi in ra một dòng rỗng trên phiếu
      .filter(row => row.component || row.value_min !== null && row.value_min !== ''
        || row.value_max !== null && row.value_max !== '' || row.text_override)
      .map(row => ({
        component: textOrNull(row.component),
        value_min: numOrNull(row.value_min),
        value_max: numOrNull(row.value_max),
        unit: textOrNull(row.unit),
        text_override: textOrNull(row.text_override),
      })),
    chemicals: (step.chemicals || [])
      .filter(row => (row.display_name || '').trim())
      .map(row => ({
        product_id: row.product_id ?? null,
        lab_chemical_id: row.lab_chemical_id ?? null,
        display_name: row.display_name.trim(),
      })),
  }
}
