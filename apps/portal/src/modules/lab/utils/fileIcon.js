import { FileText, FileSpreadsheet, FileImage, FileArchive, File as FileGeneric } from 'lucide-vue-next'

const EXT_STYLES = {
  pdf: { icon: FileText, className: 'bg-red-100 text-red-600 dark:bg-red-500/20 dark:text-red-400' },
  doc: { icon: FileText, className: 'bg-blue-100 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400' },
  docx: { icon: FileText, className: 'bg-blue-100 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400' },
  xls: { icon: FileSpreadsheet, className: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400' },
  xlsx: { icon: FileSpreadsheet, className: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400' },
  png: { icon: FileImage, className: 'bg-purple-100 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400' },
  jpg: { icon: FileImage, className: 'bg-purple-100 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400' },
  jpeg: { icon: FileImage, className: 'bg-purple-100 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400' },
  webp: { icon: FileImage, className: 'bg-purple-100 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400' },
  zip: { icon: FileArchive, className: 'bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400' },
  rar: { icon: FileArchive, className: 'bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400' },
}

const DEFAULT_STYLE = { icon: FileGeneric, className: 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-300' }

export function fileKind(filename) {
  const ext = (filename || '').split('.').pop()?.toLowerCase() || ''
  return EXT_STYLES[ext] || DEFAULT_STYLE
}
