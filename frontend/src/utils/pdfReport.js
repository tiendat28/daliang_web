let vietnameseFontBase64 = null

async function loadVietnameseFont() {
  if (vietnameseFontBase64) return vietnameseFontBase64
  const buf = await fetch('/fonts/NotoSans-Regular.ttf').then(r => r.arrayBuffer())
  let binary = ''
  const bytes = new Uint8Array(buf)
  const chunk = 0x8000
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk))
  }
  vietnameseFontBase64 = btoa(binary)
  return vietnameseFontBase64
}

/** Builds a simple titled table PDF (Vietnamese-safe font) and triggers download. */
export async function exportTablePdf({ title, headers, rows, filename, orientation = 'landscape' }) {
  await exportMultiTablePdf({ sections: [{ title, headers, rows }], filename, orientation })
}

/** Builds a PDF with one titled table per section (each on its own page) and triggers download. */
export async function exportMultiTablePdf({ sections, filename, orientation = 'landscape' }) {
  const [{ default: JsPDF }, autoTableModule, fontBase64] = await Promise.all([
    import('jspdf'), import('jspdf-autotable'), loadVietnameseFont(),
  ])
  const autoTable = autoTableModule.default

  const doc = new JsPDF({ orientation })
  doc.addFileToVFS('NotoSans-Regular.ttf', fontBase64)
  doc.addFont('NotoSans-Regular.ttf', 'NotoSans', 'normal')

  sections.forEach(({ title, headers, rows }, i) => {
    if (i > 0) doc.addPage()
    doc.setFont('NotoSans')
    doc.setFontSize(14)
    doc.text(title, 14, 15)
    autoTable(doc, {
      head: [headers], body: rows, startY: 20,
      styles: { font: 'NotoSans', fontSize: 8 },
      headStyles: { font: 'NotoSans', fillColor: [22, 111, 108] },
    })
  })

  doc.save(filename)
}
