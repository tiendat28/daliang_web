import { computed, onUnmounted } from 'vue'
import { pageSearch } from '@/core/store/pageSearch'

/**
 * Lọc danh sách theo ô tìm kiếm trên Topbar (dùng chung cho mọi trang).
 * `valuesOf(row)` trả về các giá trị của 1 dòng được đem ra so khớp.
 * Rời trang thì tự xoá từ khoá đang gõ.
 */
export function useSearchedRows(rows, valuesOf) {
  onUnmounted(() => { pageSearch.query = '' })

  return computed(() => {
    const query = pageSearch.query.trim().toLowerCase()
    if (!query) return rows.value
    return rows.value.filter(row =>
      valuesOf(row).some(value => String(value ?? '').toLowerCase().includes(query))
    )
  })
}
