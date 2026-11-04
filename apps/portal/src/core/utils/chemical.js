/**
 * Shared Chemical Domain Constants & Helpers
 * Dùng chung cho Kho, Điều phối giao hàng, Phòng thí nghiệm, v.v.
 */

export const HAZARD_MAP = {
  toxic: { label: 'Độc', cls: 'bg-[#fde4e4] dark:bg-rose-950/60 text-[#9b1c1c] dark:text-rose-300' },
  corrosive: { label: 'Ăn mòn', cls: 'bg-[#fdf0cf] dark:bg-amber-950/60 text-[#8a4b08] dark:text-amber-300' },
  oxidizing: { label: 'Oxy hoá', cls: 'bg-[#ece8fb] dark:bg-purple-950/60 text-[#5b3fb0] dark:text-purple-300' },
  flammable: { label: 'Dễ cháy', cls: 'bg-[#fee2e2] dark:bg-rose-950/60 text-[#dc2626] dark:text-rose-300' },
}

/**
 * Phân tách chuỗi nguy hại (VD: "toxic, corrosive") thành mảng badge hiển thị
 * @param {string} hazardStr
 * @returns {Array<{ label: string, cls: string }>}
 */
export function getHazardBadges(hazardStr) {
  if (!hazardStr) return []
  const parts = String(hazardStr)
    .split(',')
    .map(s => s.trim().toLowerCase())
    .filter(Boolean)

  return parts.map(p => HAZARD_MAP[p] || {
    label: p,
    cls: 'bg-[#eef2f6] dark:bg-slate-700 text-[#334155] dark:text-slate-300',
  })
}

/** Danh mục hóa chất tiêu chuẩn cho autocomplete */
export const QUICK_CHEMICAL_CATALOG = [
  { code: 'NI-534C', name: 'Phụ gia mạ niken bóng', category: 'finished', unit: 'kg', location: 'A-02-3', hazard: 'toxic' },
  { code: 'CRT-650', name: 'Phụ gia crom CRT-650', category: 'finished', unit: 'kg', location: 'A-04-1', hazard: 'corrosive' },
  { code: 'CU-4', name: 'Phụ gia mạ đồng axit', category: 'finished', unit: 'kg', location: 'A-01-2', hazard: 'corrosive' },
  { code: 'CRO3-99', name: 'Axit cromic CrO3 99.8%', category: 'material', unit: 'kg', location: 'D-02-1', hazard: 'oxidizing' },
  { code: 'SP-20', name: 'Hoá chất tẩy dầu kiềm', category: 'finished', unit: 'kg', location: 'B-01-2', hazard: 'corrosive' },
  { code: 'AC-100', name: 'Axit hoạt hoá bề mặt AC-100', category: 'material', unit: 'lít', location: 'C-03-1', hazard: 'corrosive' },
  { code: 'ZN-80', name: 'Phụ gia mạ kẽm kiềm ZN-80', category: 'finished', unit: 'kg', location: 'A-03-2', hazard: 'corrosive' },
]

/** Danh sách tài xế tiêu chuẩn của công ty */
export const QUICK_DRIVERS = [
  { id: 1, name: 'Nguyễn Văn Hùng', phone: '0912.334.556', defaultPlate: '59C-123.45' },
  { id: 2, name: 'Trần Đình Trọng', phone: '0988.776.554', defaultPlate: '50H-882.19' },
  { id: 3, name: 'Lê Văn Toàn', phone: '0903.221.443', defaultPlate: '51D-456.78' },
  { id: 4, name: 'Phạm Quốc Huy', phone: '0977.112.233', defaultPlate: '60C-991.23' },
]

/** Danh sách xe tải tiêu chuẩn của đội xe công ty */
export const QUICK_TRUCKS = [
  { id: 1, plate: '59C-123.45', type: 'Xe tải 2.5 Tấn', payload: 2500 },
  { id: 2, plate: '50H-882.19', type: 'Xe tải 3.5 Tấn', payload: 3500 },
  { id: 3, plate: '51D-456.78', type: 'Xe tải 5.0 Tấn', payload: 5000 },
  { id: 4, plate: '60C-991.23', type: 'Xe chuyên dụng bồn', payload: 8000 },
]
