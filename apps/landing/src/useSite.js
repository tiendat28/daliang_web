/* Trang thai dung chung cua website cong khai: ngon ngu dang xem + noi dung
 * lay tu /api/v1/website/public/site (goi dung mot lan cho ca phien - trang nao cung can
 * thong tin cong ty o header/footer, bo loc san pham chay ngay tai trinh duyet).
 */
import { reactive } from 'vue'
import { siteApi } from './api'
import { I18N } from './i18n'
import { normalizeLang, sitePath } from './routes'

export const siteStore = reactive({
  lang: 'vi',
  loading: false,
  loaded: false,
  company: null,
  products: [],
  certificates: [],
})

/** Chu giao dien theo ngon ngu dang xem; thieu khoa thi lay ban tieng Viet. */
export function t(key) {
  return I18N[siteStore.lang]?.[key] ?? I18N.vi[key] ?? key
}

/** Truong da dich tu API ({ vi, en, zh }); thieu ban dich thi dung tieng Viet. */
export function tr(field) {
  const val = field?.[siteStore.lang]
  if (val && typeof val === 'string' && val.trim()) return val
  const vi = field?.vi
  if (vi && typeof vi === 'string' && vi.trim()) return vi
  return field?.en || field?.zh || ''
}

export function setLang(lang) {
  siteStore.lang = normalizeLang(lang)
  document.documentElement.lang = siteStore.lang
}

export function setPageTitle(pageTitle) {
  document.title = pageTitle ? `${pageTitle} — ${t('title')}` : t('title')
}

export async function loadSite() {
  if (siteStore.loaded || siteStore.loading) return
  siteStore.loading = true
  try {
    Object.assign(siteStore, await siteApi.site(), { loaded: true })
  } catch {
    // Mat mang thi trang van dung: chu tinh van hien, chi thieu san pham va lien he
  } finally {
    siteStore.loading = false
  }
}

/** Dia chi mot trang theo ngon ngu dang xem - vd pagePath('products', { group: 'pre' }). */
export function pagePath(page, params) {
  return sitePath(page, siteStore.lang, params)
}

export function productPath(product) {
  return pagePath('products', { group: product.group, code: product.code })
}

export function findProduct(code) {
  const wanted = String(code || '').trim().toUpperCase()
  return siteStore.products.find(p => p.code.toUpperCase() === wanted) || null
}

/** Link mo file trong bang documents (MSDS, TDS, ban scan giay to); chua co file thi '#'. */
export function fileHref(documentId) {
  return documentId ? siteApi.fileUrl(documentId) : '#'
}

export function telHref(phone) {
  const digits = String(phone || '').replace(/[^\d+]/g, '')
  return digits ? `tel:${digits}` : '#'
}

export function mailHref(email) {
  const value = String(email || '')
  return value.includes('@') && !value.startsWith('[') ? `mailto:${value}` : '#'
}
