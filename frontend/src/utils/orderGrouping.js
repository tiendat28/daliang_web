// Nhóm các dòng đơn hàng theo lô (cùng KH + cùng ngày pha) — cùng quy tắc gộp
// STT/Tên sản phẩm/Nồng độ/Khách hàng/Ngày xuất đang dùng khi xuất Excel (xem reportSheets.js).
const MERGE_FIELDS = ['stt', 'product_name', 'concentration', 'customer_id', 'mix_date', 'issue_date']

export function groupChemicalOrders(orders) {
  const sorted = [...orders].sort((a, b) => {
    const cmp = String(a.mix_date ?? '').localeCompare(String(b.mix_date ?? ''))
    return cmp !== 0 ? cmp : a.id - b.id
  })

  let stt = 0
  let prevBatchKey = null
  const withStt = sorted.map((order) => {
    const batchKey = `${order.customer_id}|${order.mix_date || ''}`
    if (batchKey !== prevBatchKey) {
      stt++
      prevBatchKey = batchKey
    }
    return { order, stt, batchKey }
  })

  const spanArrays = Object.fromEntries(MERGE_FIELDS.map(f => [f, new Array(withStt.length).fill(0)]))
  MERGE_FIELDS.forEach((field) => {
    let runStart = 0
    for (let i = 1; i <= withStt.length; i++) {
      const prev = withStt[i - 1]
      const curr = withStt[i]
      const boundary = !curr
        || curr.batchKey !== prev.batchKey
        || (field !== 'stt' && curr.order[field] !== prev.order[field])
      if (boundary) {
        spanArrays[field][runStart] = i - runStart
        runStart = i
      }
    }
  })

  return withStt.map((row, i) => ({
    ...row,
    spans: Object.fromEntries(MERGE_FIELDS.map(f => [f, spanArrays[f][i]])),
  }))
}
