/** Loi tu API -> mot cau tieng Viet de hien len form. */
export function errorMessage(error, fallback = 'Có lỗi xảy ra, vui lòng thử lại') {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail.replace(/\s*\([^)]*\)$/, '').trim() || fallback
  // 422 cua FastAPI: danh sach loi theo tung truong
  if (Array.isArray(detail) && detail.length) return detail[0].msg?.replace(/^Value error, /, '').replace(/\s*\([^)]*\)$/, '').trim() || fallback
  if (error?.response?.status === 403) return 'Bạn không có quyền thực hiện thao tác này'
  if (!error?.response) return 'Không kết nối được máy chủ'
  return fallback
}
