import { getLogoPngBase64 } from './logo'

export const EXCEL_BORDER = {
  top: { style: 'thin', color: { argb: 'FF000000' } },
  left: { style: 'thin', color: { argb: 'FF000000' } },
  bottom: { style: 'thin', color: { argb: 'FF000000' } },
  right: { style: 'thin', color: { argb: 'FF000000' } },
}
export const HEADER_GREEN = 'FF92D050'
export const BRAND_RED = 'FFC00000'

const colLetter = (n) => String.fromCharCode(64 + n)

/**
 * Builds the shared DLVC report header (logo + title + company name, merged
 * across `titleSpan`/`companySpan` columns after a 2-column logo cell) plus
 * the green column-header row (row 3). Caller fills data rows from row 4.
 */
export async function createReportSheet(workbook, {
  sheetName, title, titleFontSize = 12, columnWidths, headerLabels, titleSpan, companySpan,
}) {
  const ws = workbook.addWorksheet(sheetName)
  ws.columns = columnWidths.map(width => ({ width }))
  ws.getRow(1).height = 40
  ws.getRow(2).height = 26

  const logoEnd = 2
  const titleEnd = logoEnd + titleSpan
  const companyEnd = titleEnd + companySpan

  ws.mergeCells(`A1:${colLetter(logoEnd)}2`)
  ws.mergeCells(`${colLetter(logoEnd + 1)}1:${colLetter(titleEnd)}2`)
  ws.mergeCells(`${colLetter(titleEnd + 1)}1:${colLetter(companyEnd)}1`)
  ws.mergeCells(`${colLetter(titleEnd + 1)}2:${colLetter(companyEnd)}2`)

  const titleCell = ws.getCell(1, logoEnd + 1)
  titleCell.value = title
  titleCell.font = { name: 'Times New Roman', bold: true, size: titleFontSize }
  titleCell.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true }

  const companyCell1 = ws.getCell(1, titleEnd + 1)
  companyCell1.value = '越南大亮化工有限公司'
  companyCell1.font = { name: 'Times New Roman', color: { argb: BRAND_RED }, size: 11 }
  companyCell1.alignment = { horizontal: 'center', vertical: 'middle' }

  const companyCell2 = ws.getCell(2, titleEnd + 1)
  companyCell2.value = 'DALIANG CHEMICAL VIETNAM CO.,LTD'
  companyCell2.font = { name: 'Times New Roman', color: { argb: BRAND_RED }, bold: true, size: 11 }
  companyCell2.alignment = { horizontal: 'center', vertical: 'middle' }

  ws.getCell(1, 1).border = EXCEL_BORDER
  titleCell.border = EXCEL_BORDER
  companyCell1.border = EXCEL_BORDER

  const logoBase64 = await getLogoPngBase64()
  const imageId = workbook.addImage({ base64: logoBase64, extension: 'png' })
  ws.addImage(imageId, { tl: { col: 0.25, row: 0.15 }, ext: { width: 130, height: 56 } })

  const headerRow = ws.getRow(3)
  headerLabels.forEach((label, i) => {
    const cell = headerRow.getCell(i + 1)
    cell.value = label
    cell.font = { name: 'Times New Roman', bold: true, size: 11 }
    cell.alignment = { horizontal: 'center', vertical: 'middle' }
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: HEADER_GREEN } }
    cell.border = EXCEL_BORDER
  })

  return ws
}

/** Sets a data cell's value (if not null/undefined), border and alignment in one call. */
export function styleDataCell(cell, value, { align = 'center' } = {}) {
  if (value !== null && value !== undefined) cell.value = value
  cell.border = EXCEL_BORDER
  cell.alignment = { horizontal: align, vertical: 'middle' }
  cell.font = { name: 'Times New Roman', size: 11 }
}

export async function downloadWorkbook(workbook, filename) {
  const buffer = await workbook.xlsx.writeBuffer()
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
