/* So do dia chi cua website cong khai.
 *
 * Tieng Viet la mac dinh nen khong co tien to (/gioi-thieu), hai thu tieng con
 * lai chay duoi /en va /zh. Moi trang co mot "page key" dung chung cho ca ba
 * ngon ngu - doi ngon ngu la doi slug cua dung trang dang xem, khong bat khach
 * quay ve trang chu.
 *
 *   vi                          en                           zh
 *   /                           /en                          /zh
 *   /gioi-thieu                 /en/about                    /zh/about
 *   /san-pham/tien-xu-ly        /en/products/pretreatment    /zh/products/pretreatment
 *   /san-pham/:nhom/:ma         /en/products/:group/:code    /zh/products/:group/:code
 *   /chung-nhan                 /en/certificates             /zh/certificates
 *   /tai-lieu                   /en/documents                /zh/documents
 *   /dich-vu                    /en/services                 /zh/services
 *   /lien-he                    /en/contact                  /zh/contact
 */
import { LANGS } from './i18n'

export const PREFIX = { vi: '', en: '/en', zh: '/zh' }

export const PAGE_SLUG = {
  vi: { about: 'gioi-thieu', products: 'san-pham', certs: 'chung-nhan', docs: 'tai-lieu', services: 'dich-vu', contact: 'lien-he' },
  en: { about: 'about', products: 'products', certs: 'certificates', docs: 'documents', services: 'services', contact: 'contact' },
  zh: { about: 'about', products: 'products', certs: 'certificates', docs: 'documents', services: 'services', contact: 'contact' },
}

// Ba nhom cua so do web. Khoa (pre/add/pas) trung voi cot "group" trong DB.
export const GROUP_SLUG = {
  vi: { pre: 'tien-xu-ly', add: 'phu-gia-ma', pas: 'thu-dong' },
  en: { pre: 'pretreatment', add: 'plating-additives', pas: 'passivation' },
  zh: { pre: 'pretreatment', add: 'plating-additives', pas: 'passivation' },
}

export const GROUPS = ['pre', 'add', 'pas']

export function normalizeLang(lang) {
  return LANGS.includes(lang) ? lang : 'vi'
}

/** Dia chi cua mot trang theo ngon ngu. group/code de tro toi nhom / ma cu the. */
export function sitePath(page, lang, { group, code } = {}) {
  const l = normalizeLang(lang)
  const prefix = PREFIX[l]
  if (page === 'home') return prefix || '/'

  const slug = PAGE_SLUG[l][page]
  if (page === 'products' && group) {
    const groupSlug = GROUP_SLUG[l][group] || group
    return code ? `${prefix}/${slug}/${groupSlug}/${encodeURIComponent(code)}` : `${prefix}/${slug}/${groupSlug}`
  }
  return `${prefix}/${slug}`
}

/** Doi slug tren URL nguoc ve khoa nhom; slug la va thi tra null. */
export function groupFromSlug(lang, slug) {
  const table = GROUP_SLUG[normalizeLang(lang)]
  return GROUPS.find(key => table[key] === slug) || null
}

/** Cung mot trang, sang ngon ngu khac - dung cho ba nut VI/EN/中文. */
export function switchLangPath(route, nextLang) {
  const page = route.meta?.page || 'home'
  const group = route.params.group ? groupFromSlug(route.meta?.lang, route.params.group) : null
  return sitePath(page, nextLang, { group, code: route.params.code })
}

const VIEWS = {
  home: () => import('./pages/HomePage.vue'),
  about: () => import('./pages/AboutPage.vue'),
  products: () => import('./pages/ProductsPage.vue'),
  productDetail: () => import('./pages/ProductDetailPage.vue'),
  certs: () => import('./pages/CertificatesPage.vue'),
  docs: () => import('./pages/DocumentsPage.vue'),
  services: () => import('./pages/ServicesPage.vue'),
  contact: () => import('./pages/ContactPage.vue'),
}

/** Sinh toan bo route cua website - 3 ngon ngu x 9 trang. */
export function siteRoutes() {
  const routes = []
  for (const lang of LANGS) {
    const prefix = PREFIX[lang]
    const slug = PAGE_SLUG[lang]
    const page = (name, path, component, meta = {}) => routes.push({
      path,
      name: `site-${lang}-${name}`,
      component,
      meta: { site: true, lang, page: meta.page || name, ...meta },
    })

    page('home', prefix || '/', VIEWS.home)
    page('about', `${prefix}/${slug.about}`, VIEWS.about)
    page('products', `${prefix}/${slug.products}`, VIEWS.products)
    page('products-group', `${prefix}/${slug.products}/:group`, VIEWS.products, { page: 'products' })
    page('product-detail', `${prefix}/${slug.products}/:group/:code`, VIEWS.productDetail, { page: 'products' })
    page('certs', `${prefix}/${slug.certs}`, VIEWS.certs)
    page('docs', `${prefix}/${slug.docs}`, VIEWS.docs)
    page('services', `${prefix}/${slug.services}`, VIEWS.services)
    page('contact', `${prefix}/${slug.contact}`, VIEWS.contact)
  }
  return routes
}
