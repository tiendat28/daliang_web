import { createReportSheet, styleDataCell } from './excelReport'
import { formatFormula } from './chemFormula'

/** " THÁNG 9/2026" nếu có chọn tháng/năm, ngược lại rỗng. */
function periodTitleSuffix(period) {
  if (!period?.month || !period?.year) return ''
  return ` THÁNG ${Number(period.month)}/${period.year}`
}

/** " T9" ngắn gọn để gắn vào tên sheet (giới hạn 31 ký tự). */
function periodSheetSuffix(period) {
  if (!period?.month || !period?.year) return ''
  return ` T${Number(period.month)}`
}

/** Sheet "Hóa chất PTN" — cùng format đã dùng ở trang Hóa chất. */
export async function addLabChemicalsSheet(wb, rows, period) {
  const ws = await createReportSheet(wb, {
    sheetName: `Hóa chất PTN${periodSheetSuffix(period)}`, title: `QUẢN LÝ HÓA CHẤT${periodTitleSuffix(period)}`,
    columnWidths: [6, 26, 12, 11, 11, 11, 9, 38],
    headerLabels: ['STT', 'TÊN', 'PHÂN LOẠI', 'Nguyên', 'Lẻ', 'Tổng', 'ĐƠN VỊ', 'GHI CHÚ'],
    titleSpan: 3, companySpan: 3,
  })
  rows.forEach((r, i) => {
    const nguyen = r.total_volume ?? 0
    const le = r.remaining_volume ?? 0
    const values = [i + 1, formatFormula(r.code), r.type || '', nguyen, le, nguyen + le, r.unit || '', r.note || '']
    const row = ws.getRow(4 + i)
    values.forEach((v, ci) => styleDataCell(row.getCell(ci + 1), v, { align: ci === 1 || ci === 7 ? 'left' : 'center' }))
  })
}

/** Sheet "Chất chỉ thị" — cùng format đã dùng ở trang Hóa chất. */
export async function addIndicatorsSheet(wb, rows, period) {
  const ws = await createReportSheet(wb, {
    sheetName: `Chất chỉ thị${periodSheetSuffix(period)}`, title: `CHẤT CHỈ THỊ${periodTitleSuffix(period)}`,
    columnWidths: [6, 26, 16, 14, 12, 30],
    headerLabels: ['STT', 'TÊN', 'PHÂN LOẠI', 'KHỐI LƯỢNG', 'ĐƠN VỊ', 'GHI CHÚ'],
    titleSpan: 2, companySpan: 2,
  })
  rows.forEach((r, i) => {
    const values = [i + 1, r.name, r.type || '', r.quantity ?? 0, r.unit || '', r.note || '']
    const row = ws.getRow(4 + i)
    values.forEach((v, ci) => styleDataCell(row.getCell(ci + 1), v, { align: ci === 1 || ci === 5 ? 'left' : 'center' }))
  })
}

/** Sheet "Thiết bị" — cùng format đã dùng ở trang Thiết bị (1 dòng/phân loại, gộp ô tên). */
export async function addEquipmentSheet(wb, rows, period) {
  const ws = await createReportSheet(wb, {
    sheetName: `Thiết bị${periodSheetSuffix(period)}`, title: `DỤNG CỤ THÍ NGHIỆM${periodTitleSuffix(period)}`,
    columnWidths: [6, 26, 16, 11, 9, 30],
    headerLabels: ['STT', 'TÊN', 'PHÂN LOẠI', 'SỐ LƯỢNG', 'ĐƠN VỊ', 'GHI CHÚ'],
    titleSpan: 2, companySpan: 2,
  })
  let excelRow = 4
  rows.forEach((eq, i) => {
    const variants = eq.variants.length ? eq.variants : [{ classification: '', quantity: 0, unit: '', note: '' }]
    const startRow = excelRow
    variants.forEach((v, vi) => {
      const noteText = vi === 0 && eq.note ? [eq.note, v.note].filter(Boolean).join(' — ') : (v.note || '')
      const values = [vi === 0 ? i + 1 : null, null, v.classification || '', v.quantity ?? 0, v.unit || '', noteText]
      const row = ws.getRow(excelRow)
      values.forEach((val, ci) => styleDataCell(row.getCell(ci + 1), val, { align: ci === 1 || ci === 5 ? 'left' : 'center' }))
      excelRow++
    })
    const endRow = excelRow - 1
    if (endRow > startRow) {
      ws.mergeCells(startRow, 1, endRow, 1)
      ws.mergeCells(startRow, 2, endRow, 2)
    }
    ws.getCell(startRow, 2).value = eq.name
    ws.getCell(startRow, 2).font = { name: 'Times New Roman', bold: true, size: 11 }
  })
}

function formatDateSlash(dateStr) {
  if (!dateStr) return ''
  const [y, m, d] = dateStr.split('-')
  return `${d}/${m}/${y}`
}

/**
 * Sheet "Đơn hàng HCTN" — gộp theo lô đơn (cùng KH + cùng ngày pha) cho STT/Khách hàng/
 * Ngày pha, và gộp thêm Tên sản phẩm/Nồng độ/Số lượng/Ngày xuất/Ghi chú khi giá trị trùng với
 * dòng liền trước trong cùng lô (đúng mẫu ảnh: 1 lô có thể gồm nhiều hóa chất).
 */
export async function addChemicalOrdersSheet(wb, orders, chemicals, customers, period) {
  const headerLabels = ['STT', 'Tên sản phẩm', 'Nồng độ', 'Số lượng', 'Hóa chất', 'Lượng', 'Sử dụng', 'Khách hàng', 'Ngày pha', 'Ngày xuất', 'Ghi chú']
  const ws = await createReportSheet(wb, {
    sheetName: `Đơn hàng HCTN${periodSheetSuffix(period)}`, title: `ĐƠN HÀNG HCTN${periodTitleSuffix(period)}`,
    columnWidths: [6, 18, 10, 10, 14, 10, 10, 16, 12, 12, 20],
    headerLabels, titleSpan: 5, companySpan: 4,
  })

  const leftCols = new Set([2, 5, 8, 11]) // Tên sản phẩm, Hóa chất, Khách hàng, Ghi chú
  const mergeCols = [1, 2, 3, 4, 8, 9, 10, 11] // STT, Tên sản phẩm, Nồng độ, Số lượng, Khách hàng, Ngày pha, Ngày xuất, Ghi chú

  const sorted = [...orders].sort((a, b) => String(a.mix_date ?? '').localeCompare(String(b.mix_date ?? '')))

  const runStart = {}
  const prevVal = {}
  const closeRun = (col, endRow) => {
    if (runStart[col] != null && endRow > runStart[col]) ws.mergeCells(runStart[col], col, endRow, col)
    runStart[col] = null
  }

  let excelRow = 4
  let stt = 0
  let prevBatchKey = null

  sorted.forEach((o) => {
    const chem = chemicals.find(c => c.id === o.lab_chemical_id)
    const batchKey = `${o.customer_id}|${o.mix_date || ''}`
    const newBatch = batchKey !== prevBatchKey
    if (newBatch) { stt++; prevBatchKey = batchKey }

    const values = [
      stt,
      o.product_name || chem?.name || '',
      o.concentration || '',
      o.order_quantity || '',
      chem ? formatFormula(chem.code) : '',
      o.amount || '',
      [o.used_amount ?? '', o.unit || ''].filter(v => v !== '').join(' '),
      customers.find(c => c.id === o.customer_id)?.name || '',
      formatDateSlash(o.mix_date),
      formatDateSlash(o.issue_date),
      o.note || '',
    ]

    const row = ws.getRow(excelRow)
    values.forEach((val, i) => {
      const col = i + 1
      const align = leftCols.has(col) ? 'left' : 'center'
      if (mergeCols.includes(col)) {
        const sameAsPrev = !newBatch && prevVal[col] === val
        if (sameAsPrev) {
          styleDataCell(row.getCell(col), null, { align })
        } else {
          closeRun(col, excelRow - 1)
          runStart[col] = excelRow
          styleDataCell(row.getCell(col), val, { align })
        }
        prevVal[col] = val
      } else {
        styleDataCell(row.getCell(col), val, { align })
      }
    })

    excelRow++
  })

  mergeCols.forEach(col => closeRun(col, excelRow - 1))
}

/**
 * Sheet dạng chung (chưa có mẫu riêng được duyệt) — vẫn dùng logo/tên công ty/header
 * xanh/viền/Times New Roman cho đồng bộ, cột tự co theo độ dài tiêu đề.
 */
export async function addGenericSheet(wb, { sheetName, title, headerLabels, rows, period }) {
  const logoEnd = 2
  const remaining = Math.max(headerLabels.length - logoEnd, 2)
  const titleSpan = Math.ceil(remaining / 2)
  const companySpan = remaining - titleSpan
  const columnWidths = headerLabels.map(h => Math.max(10, h.length + 6))

  const ws = await createReportSheet(wb, {
    sheetName: `${sheetName}${periodSheetSuffix(period)}`.slice(0, 31),
    title: `${title}${periodTitleSuffix(period)}`,
    columnWidths, headerLabels, titleSpan, companySpan,
  })
  rows.forEach((r, i) => {
    const row = ws.getRow(4 + i)
    r.forEach((v, ci) => styleDataCell(row.getCell(ci + 1), v, { align: ci === 1 ? 'left' : 'center' }))
  })
}
