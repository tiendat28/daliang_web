import { ref } from 'vue'
import { companyProductsApi, labChemicalsApi, testProcessesApi } from '../api/resources'

/**
 * Ba danh mục mà StepListEditor cần: sản phẩm công ty, hóa chất PTN và danh
 * sách hạng mục đã dùng. Màn hình nào có trình soạn bước cũng gọi cái này.
 *
 * Trả về cả `load()` để nơi gọi tự quyết lúc nào nạp (thường chạy song song
 * với dữ liệu chính của trang).
 */
export function useStepEditorLookups() {
  const products = ref([])
  const labChemicals = ref([])
  const operationOptions = ref([])

  async function load() {
    const [productList, chemicalList, operations] = await Promise.all([
      companyProductsApi.list(),
      labChemicalsApi.list(),
      testProcessesApi.operationSuggestions(),
    ])
    products.value = productList
    labChemicals.value = chemicalList
    operationOptions.value = operations
  }

  return { products, labChemicals, operationOptions, load }
}
