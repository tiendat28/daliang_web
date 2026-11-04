/* Chu giao dien cua website, ba thu tieng - noi dung o i18n/<ngon ngu>.json.
 *
 * Phan dau moi file la nguyen van ban thiet ke goc (docs/landingpage/
 * landingpage-goc.html); cac khoa "page.*", "detail.*", "cert*"... la chu them
 * cho nhung trang con khong co trong ban goc.
 *
 * Ten/mo ta san pham, thong tin cong ty va giay to KHONG nam o day - lay tu DB
 * qua /api/v1/website/public/site (sua o cong noi bo, khong phai build lai web).
 */
import vi from '../i18n/vi.json'
import en from '../i18n/en.json'
import zh from '../i18n/zh.json'

export const LANGS = ['vi', 'en', 'zh']

export const I18N = { vi, en, zh }
