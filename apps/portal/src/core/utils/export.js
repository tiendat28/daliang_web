/**
 * Universal CSV Export Utility with UTF-8 BOM
 * Đảm bảo file CSV tải về mở trực tiếp bằng Microsoft Excel trên Windows không bị lỗi font Tiếng Việt.
 */

/**
 * Xuất dữ liệu bảng ra file CSV
 * @param {string} filename - Tên file tải về (VD: 'ton_kho_theo_lo_2026-09-29.csv')
 * @param {string[]} headers - Mảng tiêu đề các cột
 * @param {Array<Array<any>>} rows - Mảng 2 chiều chứa các dòng dữ liệu
 */
export function exportToCsv(filename, headers, rows) {
  const sanitize = (val) => {
    if (val === null || val === undefined) return '""'
    const str = String(val).replace(/"/g, '""')
    return `"${str}"`
  }

  const csvContent = '\uFEFF' + [
    headers.map(sanitize).join(','),
    ...rows.map(row => row.map(sanitize).join(',')),
  ].join('\r\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  const finalName = filename.toLowerCase().endsWith('.csv') ? filename : `${filename}.csv`
  link.setAttribute('download', finalName)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
