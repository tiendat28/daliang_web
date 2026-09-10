<script setup>
import { reactive, computed, ref, watch } from 'vue'
import { Pencil, Trash2, Plus, ArrowUp, ArrowDown, ArrowUpDown, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  columns: { type: Array, required: true }, // [{ key, label, sortable, filterable }]
  rows: { type: Array, required: true },
  title: { type: String, default: '' },
})

const emit = defineEmits(['add', 'edit', 'delete'])

const sortState = reactive({ key: null, dir: 'asc' })
const columnFilters = reactive({})
const pageSize = ref(10)
const currentPage = ref(1)
const pageSizeOptions = [10, 20, 50, 100]

function optionsFor(col) {
  const values = new Set(props.rows.map(r => r[col.key]).filter(v => v !== null && v !== undefined && v !== ''))
  return [...values].sort((a, b) => String(a).localeCompare(String(b), 'vi'))
}

function displayValue(col, value) {
  return col.format ? col.format(value) : value
}

const displayRows = computed(() => {
  let list = props.rows.filter(row =>
    props.columns.every(col => {
      const f = columnFilters[col.key]
      return !f || row[col.key] === f
    })
  )
  if (sortState.key) {
    list = [...list].sort((a, b) => {
      const cmp = String(a[sortState.key] ?? '').localeCompare(String(b[sortState.key] ?? ''), 'vi', { numeric: true })
      return sortState.dir === 'asc' ? cmp : -cmp
    })
  }
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(displayRows.value.length / pageSize.value)))

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return displayRows.value.slice(start, start + pageSize.value)
})

watch([displayRows, pageSize], () => {
  if (currentPage.value > totalPages.value) currentPage.value = totalPages.value
})

function toggleSort(col) {
  if (!col.sortable) return
  if (sortState.key === col.key) {
    sortState.dir = sortState.dir === 'asc' ? 'desc' : 'asc'
  } else {
    sortState.key = col.key
    sortState.dir = 'asc'
  }
}
</script>

<template>
  <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm flex flex-col">
    <div class="flex flex-wrap items-center justify-between gap-3 p-5 pb-4 sticky top-0 z-20 bg-white dark:bg-slate-800 rounded-t-2xl shrink-0">
      <h2 class="font-semibold text-slate-700 dark:text-slate-200">{{ title }}</h2>
      <div class="flex flex-wrap items-center gap-2">
        <slot name="header-actions" />
        <button
          class="flex items-center gap-1 text-sm bg-brand-gradient text-white px-4 py-2 rounded-xl shadow"
          @click="emit('add')"
        >
          <Plus class="w-4 h-4" /> Thêm mới
        </button>
      </div>
    </div>

    <div class="overflow-auto px-5 max-h-[65vh]">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-800 dark:text-slate-100 border-b-2 border-slate-300 dark:border-slate-600 sticky top-0 z-10 bg-white dark:bg-slate-800">
            <th class="py-2 pr-4 font-semibold w-12">STT</th>
            <th
              v-for="col in columns"
              :key="col.key"
              class="py-2 pr-4 font-semibold"
            >
              <label
                v-if="col.filterable"
                class="relative inline-flex items-center gap-1 cursor-pointer select-none hover:text-brand-600"
                :class="columnFilters[col.key] ? 'text-brand-600' : ''"
              >
                {{ columnFilters[col.key] ? displayValue(col, columnFilters[col.key]) : col.label }}
                <ChevronDown class="w-3.5 h-3.5" />
                <select v-model="columnFilters[col.key]" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer">
                  <option value="">{{ col.label }} — Tất cả</option>
                  <option v-for="opt in optionsFor(col)" :key="opt" :value="opt">{{ displayValue(col, opt) }}</option>
                </select>
              </label>
              <span
                v-else
                class="inline-flex items-center gap-1"
                :class="col.sortable ? 'cursor-pointer select-none hover:text-brand-600' : ''"
                @click="toggleSort(col)"
              >
                {{ col.label }}
                <template v-if="col.sortable">
                  <ArrowUp v-if="sortState.key === col.key && sortState.dir === 'asc'" class="w-3.5 h-3.5" />
                  <ArrowDown v-else-if="sortState.key === col.key && sortState.dir === 'desc'" class="w-3.5 h-3.5" />
                  <ArrowUpDown v-else class="w-3.5 h-3.5 opacity-40" />
                </template>
              </span>
            </th>
            <th class="py-2 w-24"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="displayRows.length === 0">
            <td :colspan="columns.length + 2" class="py-6 text-center text-slate-400">Chưa có dữ liệu</td>
          </tr>
          <tr
            v-for="(row, index) in pagedRows"
            :key="row.id"
            class="border-b border-slate-200 dark:border-slate-700 hover:bg-brand-50/40 dark:hover:bg-slate-700/40"
          >
            <td class="py-3 pr-4 text-slate-500 dark:text-slate-400 align-top">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
            <td v-for="col in columns" :key="col.key" class="py-3 pr-4 text-slate-700 dark:text-slate-200 align-top">
              <slot :name="`cell-${col.key}`" :row="row">{{ displayValue(col, row[col.key]) }}</slot>
            </td>
            <td class="py-3 align-top">
              <div class="flex items-center gap-2">
                <slot name="row-actions" :row="row" />
                <button class="text-slate-400 hover:text-brand-600" @click="emit('edit', row)">
                  <Pencil class="w-4 h-4" />
                </button>
                <button class="text-slate-400 hover:text-red-500" @click="emit('delete', row)">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="displayRows.length > 0" class="flex flex-wrap items-center justify-between gap-3 p-5 pt-4 mt-0 border-t border-slate-100 dark:border-slate-700 text-sm text-slate-500 dark:text-slate-400 shrink-0">
      <div class="flex items-center gap-2">
        <span>Hiển thị</span>
        <select v-model.number="pageSize" class="rounded-lg border border-slate-200 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 px-2 py-1 text-sm">
          <option v-for="opt in pageSizeOptions" :key="opt" :value="opt">{{ opt }}</option>
        </select>
        <span>/ trang · {{ displayRows.length }} dòng</span>
      </div>
      <div class="flex items-center gap-1">
        <button
          class="w-8 h-8 rounded-lg flex items-center justify-center disabled:opacity-30 hover:bg-brand-50 dark:hover:bg-slate-700"
          :disabled="currentPage <= 1"
          @click="currentPage--"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <span class="px-2">Trang {{ currentPage }} / {{ totalPages }}</span>
        <button
          class="w-8 h-8 rounded-lg flex items-center justify-center disabled:opacity-30 hover:bg-brand-50 dark:hover:bg-slate-700"
          :disabled="currentPage >= totalPages"
          @click="currentPage++"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
