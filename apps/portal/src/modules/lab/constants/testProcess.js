// Danh mục dùng chung của module "Lưu trình test mẫu".
// Nhãn tiếng Việt nằm ở đây, mã lưu trong DB vẫn là tiếng Anh (xem app/models.py).

export const STATUSES = [
  { value: 'draft', label: 'Nháp', chip: 'bg-lt-draft text-lt-draftink' },
  { value: 'in_progress', label: 'Đang test', chip: 'bg-lt-run text-lt-runink' },
  { value: 'completed', label: 'Hoàn thành', chip: 'bg-lt-done text-lt-doneink' },
  { value: 'cancelled', label: 'Đã hủy', chip: 'bg-lt-void text-lt-voidink' },
]

export function statusMeta(value) {
  return STATUSES.find(s => s.value === value) || STATUSES[0]
}

export const TIME_UNITS = [
  { value: 'sec', label: 'giây' },
  { value: 'min', label: 'phút' },
  { value: 'hour', label: 'giờ' },
]

export const TEMP_MODES = [
  { value: 'none', label: 'Trống' },
  { value: 'ambient', label: 'Thường' },
  { value: 'range', label: 'Khoảng' },
]

// Đơn vị nồng độ hay dùng; ô vẫn cho gõ tay đơn vị khác.
export const CONCENTRATION_UNITS = ['g/l', 'ml/l', '%', 'mg/l', 'A/dm²']

// Hạng mục thêm nhanh bằng một cú bấm trên thanh công cụ của form
export const QUICK_OPERATIONS = ['Rửa nước', 'Rửa nước x2']

// Tờ A4 ở 96 dpi — mọi khung xem trước đều quy về hai số này
export const PAGE_WIDTH = 794
export const PAGE_HEIGHT = 1123
// Phần đầu trang (lề trên + khối letterhead) dùng cho khung xem trước letterhead
export const LETTERHEAD_HEIGHT = 132

// Các mức thu phóng của khung xem trước, theo thứ tự tăng dần (nút - và +)
export const ZOOM_LEVELS = [25, 50, 75, 80, 90, 100]
// 50% là mức gần vừa khung xem trước trên máy tính nhất trong danh sách trên
export const DEFAULT_ZOOM = 50

/** Mức kế tiếp theo hướng `step` (-1 hoặc 1); đụng đầu/cuối thì giữ nguyên. */
export function stepZoom(zoom, step) {
  const index = ZOOM_LEVELS.indexOf(zoom)
  const next = (index === -1 ? ZOOM_LEVELS.indexOf(DEFAULT_ZOOM) : index) + step
  return ZOOM_LEVELS[next] ?? zoom
}

/** Một bước trống, dùng cho nút "Thêm bước". */
export function emptyStep(operation = '') {
  return {
    operation,
    time_min: null, time_max: null, time_unit: 'min',
    temp_mode: 'none', temp_min: null, temp_max: null,
    ph_min: null, ph_max: null,
    time_text: null, temp_text: null, ph_text: null,
    note: null,
    concentrations: [],
    chemicals: [],
  }
}

/**
 * Đưa một bước lấy từ API (lưu trình đã lưu, quy trình chuẩn, "lần gần nhất")
 * về đúng hình dạng mà form dùng — thiếu ô nào thì điền mặc định.
 */
export function normalizeStep(raw = {}) {
  return {
    ...emptyStep(),
    ...raw,
    time_unit: raw.time_unit ?? null,
    temp_mode: raw.temp_mode || 'none',
    concentrations: (raw.concentrations || []).map(row => ({
      component: row.component ?? '',
      value_min: row.value_min ?? null,
      value_max: row.value_max ?? null,
      unit: row.unit ?? '',
      text_override: row.text_override ?? null,
    })),
    chemicals: (raw.chemicals || []).map(row => ({
      product_id: row.product_id ?? null,
      lab_chemical_id: row.lab_chemical_id ?? null,
      display_name: row.display_name ?? '',
    })),
  }
}
