<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  AlertTriangle,
  ArrowDownLeft,
  ArrowUpRight,
  BarChart3,
  Bell,
  Check,
  CreditCard,
  Download,
  FileCheck2,
  FileSpreadsheet,
  FileText,
  Mail,
  Pencil,
  Plus,
  Receipt,
  Search,
  Send,
  Trash2,
  Wallet,
  X,
} from 'lucide-vue-next'
import Modal from '@/core/components/Modal.vue'
import FormActions from '@/core/components/FormActions.vue'
import AlertBanner from '@/core/components/AlertBanner.vue'
import { formatCurrency, formatDate } from '@/core/utils/format'
import { exportToCsv } from '@/core/utils/export'
import { errorMessage } from '@/core/api/errors'
import client from '@/core/api/client'
import { accountingApi } from '../api'

const route = useRoute()
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const successMsg = ref('')

const dashboard = ref(null)
const invoices = ref([])
const bankAccounts = ref([])
const customers = ref([])
const products = ref([])

const searchQuery = ref('')
const activeTab = ref('all') // all | pending | overdue

// Modal states
const showReceiptModal = ref(false)
const showPaymentModal = ref(false)
const showInvoiceModal = ref(false)
const showRemindModal = ref(false)

// Forms
const receiptForm = ref({
  partner_name: '',
  customer_id: null,
  invoice_id: null,
  payment_method: 'bank',
  bank_account: 'Vietcombank - CN Tân Bình',
  amount: '',
  voucher_date: new Date().toISOString().slice(0, 10),
  description: '',
})

const paymentForm = ref({
  partner_name: '',
  category: 'supplier_payment',
  payment_method: 'bank',
  bank_account: 'Vietcombank - CN Tân Bình',
  amount: '',
  voucher_date: new Date().toISOString().slice(0, 10),
  description: '',
})

const invoiceForm = ref({
  invoice_code: '',
  customer_name: '',
  customer_id: null,
  invoice_date: new Date().toISOString().slice(0, 10),
  due_date: new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10),
  tax_rate: 10,
  einvoice_status: 'issued',
  note: '',
  items: [
    { product_name: '', unit: 'Kg', quantity: 1, unit_price: 0, amount: 0 },
  ],
})

const remindData = ref({
  invoice: null,
  channel: 'email',
  note: '',
})

// Computed Filtered Invoices
const filteredInvoices = computed(() => {
  let list = invoices.value || []
  const today = new Date().toISOString().slice(0, 10)

  if (activeTab.value === 'pending') {
    list = list.filter(inv => inv.payment_status === 'pending' || inv.payment_status === 'partial')
  } else if (activeTab.value === 'overdue') {
    list = list.filter(inv => inv.payment_status !== 'paid' && inv.due_date && inv.due_date < today)
  }

  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(inv =>
      (inv.invoice_code || '').toLowerCase().includes(q) ||
      (inv.customer_name || '').toLowerCase().includes(q) ||
      String(inv.total_amount || '').includes(q)
    )
  }
  return list
})

// Computed Filtered Overdue Debts
const filteredOverdueDebts = computed(() => {
  const debts = dashboard.value?.overdue_debts || []
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return debts
  return debts.filter(d =>
    d.customer_name.toLowerCase().includes(q) ||
    d.invoice_code.toLowerCase().includes(q)
  )
})

// Subtotal & Total for Create Invoice Form
const formSubtotal = computed(() => {
  return invoiceForm.value.items.reduce((sum, item) => sum + (Number(item.quantity || 0) * Number(item.unit_price || 0)), 0)
})

const formTaxAmount = computed(() => {
  return Math.round(formSubtotal.value * (Number(invoiceForm.value.tax_rate || 0) / 100))
})

const formTotalAmount = computed(() => {
  return formSubtotal.value + formTaxAmount.value
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [dash, invList, accList] = await Promise.all([
      accountingApi.getDashboard(),
      accountingApi.listInvoices({ type: 'sales' }),
      accountingApi.listBankAccounts().catch(() => []),
    ])
    dashboard.value = dash
    invoices.value = invList
    bankAccounts.value = accList

    // Load customer suggestions in background
    client.get('/common/customers').then(r => { customers.value = r.data || [] }).catch(() => {})
    client.get('/common/products').then(r => { products.value = r.data || [] }).catch(() => {})
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

// Open modals
function openReceipt(invoice = null) {
  receiptForm.value = {
    partner_name: invoice ? invoice.customer_name : '',
    customer_id: invoice?.customer_id || null,
    invoice_id: invoice?.id || null,
    payment_method: 'bank',
    bank_account: bankAccounts.value[0]?.name || 'Vietcombank - CN Tân Bình',
    amount: invoice ? Math.max(0, invoice.total_amount - invoice.paid_amount) : '',
    voucher_date: new Date().toISOString().slice(0, 10),
    description: invoice ? `Thanh toán hoá đơn ${invoice.invoice_code}` : 'Thu tiền hàng hoá chất',
  }
  showReceiptModal.value = true
}

function openPayment() {
  paymentForm.value = {
    partner_name: '',
    category: 'supplier_payment',
    payment_method: 'bank',
    bank_account: bankAccounts.value[0]?.name || 'Vietcombank - CN Tân Bình',
    amount: '',
    voucher_date: new Date().toISOString().slice(0, 10),
    description: '',
  }
  showPaymentModal.value = true
}

function openCreateInvoice() {
  invoiceForm.value = {
    invoice_code: '',
    customer_name: '',
    customer_id: null,
    invoice_date: new Date().toISOString().slice(0, 10),
    due_date: new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10),
    tax_rate: 10,
    einvoice_status: 'issued',
    note: '',
    items: [
      { product_name: '', unit: 'Kg', quantity: 1, unit_price: 0, amount: 0 },
    ],
  }
  showInvoiceModal.value = true
}

function openRemind(item) {
  remindData.value = {
    invoice: item,
    channel: 'email',
    note: '',
  }
  showRemindModal.value = true
}

// Add / remove items in invoice form
function addInvoiceItem() {
  invoiceForm.value.items.push({
    product_name: '',
    unit: 'Kg',
    quantity: 1,
    unit_price: 0,
    amount: 0,
  })
}

function removeInvoiceItem(idx) {
  if (invoiceForm.value.items.length > 1) {
    invoiceForm.value.items.splice(idx, 1)
  }
}

function onProductSelect(item, prodName) {
  item.product_name = prodName
}

// Customer select in invoice form
function onCustomerSelect(name) {
  invoiceForm.value.customer_name = name
  const found = customers.value.find(c => c.name === name)
  if (found) invoiceForm.value.customer_id = found.id
}

// Actions save
async function saveReceipt() {
  saving.value = true
  error.value = ''
  try {
    await accountingApi.createVoucher({
      voucher_type: 'receipt',
      category: 'sales_receipt',
      partner_name: receiptForm.value.partner_name,
      customer_id: receiptForm.value.customer_id,
      invoice_id: receiptForm.value.invoice_id,
      payment_method: receiptForm.value.payment_method,
      bank_account: receiptForm.value.bank_account,
      amount: Number(receiptForm.value.amount),
      voucher_date: receiptForm.value.voucher_date,
      description: receiptForm.value.description,
    })
    showReceiptModal.value = false
    successMsg.value = 'Đã lập phiếu thu thành công!'
    setTimeout(() => { successMsg.value = '' }, 4000)
    await loadData()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    saving.value = false
  }
}

async function savePayment() {
  saving.value = true
  error.value = ''
  try {
    await accountingApi.createVoucher({
      voucher_type: 'payment',
      category: paymentForm.value.category,
      partner_name: paymentForm.value.partner_name,
      payment_method: paymentForm.value.payment_method,
      bank_account: paymentForm.value.bank_account,
      amount: Number(paymentForm.value.amount),
      voucher_date: paymentForm.value.voucher_date,
      description: paymentForm.value.description,
    })
    showPaymentModal.value = false
    successMsg.value = 'Đã lập phiếu chi thành công!'
    setTimeout(() => { successMsg.value = '' }, 4000)
    await loadData()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    saving.value = false
  }
}

async function saveInvoice() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      invoice_code: invoiceForm.value.invoice_code || undefined,
      invoice_type: 'sales',
      customer_name: invoiceForm.value.customer_name,
      customer_id: invoiceForm.value.customer_id,
      invoice_date: invoiceForm.value.invoice_date,
      due_date: invoiceForm.value.due_date,
      subtotal: formSubtotal.value,
      tax_rate: Number(invoiceForm.value.tax_rate),
      tax_amount: formTaxAmount.value,
      total_amount: formTotalAmount.value,
      paid_amount: 0,
      payment_status: 'pending',
      einvoice_status: invoiceForm.value.einvoice_status,
      note: invoiceForm.value.note,
      items: invoiceForm.value.items.map(it => ({
        product_name: it.product_name,
        unit: it.unit || 'Kg',
        quantity: Number(it.quantity || 1),
        unit_price: Number(it.unit_price || 0),
        tax_rate: Number(invoiceForm.value.tax_rate || 10),
        amount: Number(it.quantity || 1) * Number(it.unit_price || 0),
      })),
    }
    await accountingApi.createInvoice(payload)
    showInvoiceModal.value = false
    successMsg.value = 'Đã tạo hoá đơn thành công!'
    setTimeout(() => { successMsg.value = '' }, 4000)
    await loadData()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    saving.value = false
  }
}

async function sendRemind() {
  saving.value = true
  error.value = ''
  try {
    const item = remindData.value.invoice
    if (item?.id) {
      await accountingApi.remindDebt(item.id, {
        channel: remindData.value.channel,
        note: remindData.value.note,
      })
    }
    showRemindModal.value = false
    successMsg.value = `Đã gửi văn bản nhắc nợ tới ${item?.customer_name || 'khách hàng'}!`
    setTimeout(() => { successMsg.value = '' }, 4000)
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    saving.value = false
  }
}

async function removeInvoice(row) {
  if (!confirm(`Xoá hoá đơn ${row.invoice_code} của ${row.customer_name}?`)) return
  try {
    await accountingApi.deleteInvoice(row.id)
    await loadData()
  } catch (e) {
    error.value = errorMessage(e)
  }
}

// Export CSV / Excel with UTF-8 BOM
function exportInvoices() {
  if (!filteredInvoices.value.length) return
  const headers = ['Số hoá đơn', 'Khách hàng', 'Ngày', 'Giá trị', 'Đã thu', 'Thanh toán', 'HĐĐT']
  const rows = filteredInvoices.value.map(r => [
    r.invoice_code,
    r.customer_name,
    r.invoice_date,
    r.total_amount,
    r.paid_amount,
    r.payment_status === 'paid' ? 'Đã thu' : r.payment_status === 'partial' ? 'Thu một phần' : 'Chờ thanh toán',
    r.einvoice_status === 'issued' ? 'Đã phát hành' : 'Chờ ký số',
  ])
  exportToCsv(`danh_sach_hoa_don_${new Date().toISOString().slice(0, 10)}.csv`, headers, rows)
}

// Watch route for tab navigation
watch(() => route.meta.tab, (tab) => {
  if (tab === 'sales-invoices') activeTab.value = 'all'
  else if (tab === 'receivables') activeTab.value = 'pending'
  else if (tab === 'payables') activeTab.value = 'all'
}, { immediate: true })

onMounted(loadData)
</script>

<template>
  <div class="accounting-container">
    <!-- Top Header -->
    <header class="flex flex-wrap items-center justify-between gap-3 sm:gap-4">
      <div class="flex flex-col gap-1">
        <h1 class="m-0 text-xl sm:text-[26px] font-bold text-dl-ink dark:text-slate-100 tracking-tight">Kế toán</h1>
      </div>

      <div class="flex flex-wrap items-center gap-2 sm:gap-2.5 w-full sm:w-auto">
        <label class="flex items-center gap-2 h-9 sm:h-10 flex-1 min-w-[180px] sm:flex-initial sm:w-72 px-3 sm:px-3.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-500 shadow-sm transition-all focus-within:border-dl-teal focus-within:ring-2 focus-within:ring-dl-teal/10">
          <Search class="w-4 h-4 shrink-0 text-slate-400" />
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Tìm kiếm…"
            class="w-full bg-transparent border-0 outline-none text-sm text-slate-800 dark:text-slate-100 placeholder:text-slate-400"
          />
        </label>

        <button
          type="button"
          aria-label="Thông báo"
          class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-dl-teal flex items-center justify-center cursor-pointer shadow-sm transition-colors shrink-0"
          title="Thông báo công nợ"
        >
          <Bell class="w-4 h-4" />
        </button>

        <div class="flex flex-wrap items-center gap-1.5 sm:gap-2 w-full sm:w-auto">
          <button
            type="button"
            class="h-9 sm:h-10 px-3 sm:px-4 rounded-xl bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-700 text-xs sm:text-sm font-semibold inline-flex items-center gap-1.5 sm:gap-2 hover:border-slate-300 dark:hover:border-slate-600 shadow-sm cursor-pointer whitespace-nowrap transition-all"
            @click="openReceipt()"
          >
            <Receipt class="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Phiếu thu
          </button>

          <button
            type="button"
            class="h-9 sm:h-10 px-3 sm:px-4 rounded-xl bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-700 text-xs sm:text-sm font-semibold inline-flex items-center gap-1.5 sm:gap-2 hover:border-slate-300 dark:hover:border-slate-600 shadow-sm cursor-pointer whitespace-nowrap transition-all"
            @click="openPayment()"
          >
            <Receipt class="w-4 h-4 text-violet-600 dark:text-violet-400" />
            Phiếu chi
          </button>

          <button
            type="button"
            class="h-9 sm:h-10 px-3 sm:px-4 rounded-xl bg-gradient-to-r from-[#0b7d72] to-[#0e6f8a] text-white border-0 text-xs sm:text-sm font-semibold inline-flex items-center gap-1.5 sm:gap-2 hover:opacity-95 shadow-md shadow-teal-700/20 cursor-pointer whitespace-nowrap transition-all"
            @click="openCreateInvoice()"
          >
            <Plus class="w-4 h-4" />
            Tạo hoá đơn
          </button>
        </div>
      </div>
    </header>

    <!-- Success & Error Alerts -->
    <AlertBanner
      :success-msg="successMsg"
      :error="error"
      @close-success="successMsg = ''"
      @close-error="error = ''"
    />

    <!-- 4 KPI Stat Cards -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="h-28 rounded-[20px] bg-white/70 dark:bg-slate-800/70 animate-pulse" />
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <!-- Card 1: Doanh thu -->
      <article class="stat-card">
        <div class="flex items-start justify-between gap-3">
          <div class="flex flex-col gap-1.5">
            <span class="text-[13px] font-medium text-slate-500 dark:text-slate-400">Doanh thu {{ dashboard?.revenue_month_label || 'tháng 9' }}</span>
            <span class="text-[26px] font-bold text-slate-900 dark:text-slate-100 tracking-tight">[1,12 tỷ]</span>
            <span class="text-xs font-medium text-emerald-600 dark:text-emerald-400">so với T8: +{{ dashboard?.revenue_growth_pct || 14 }}%</span>
          </div>
          <span class="stat-icon bg-[#d3f4ee] dark:bg-teal-900/40 text-[#0f5f56] dark:text-teal-300">
            <BarChart3 class="w-5 h-5" />
          </span>
        </div>
      </article>

      <!-- Card 2: Phải thu -->
      <article class="stat-card">
        <div class="flex items-start justify-between gap-3">
          <div class="flex flex-col gap-1.5">
            <span class="text-[13px] font-medium text-slate-500 dark:text-slate-400">Phải thu</span>
            <span class="text-[26px] font-bold text-slate-900 dark:text-slate-100 tracking-tight">[486 tr]</span>
            <span class="text-xs text-slate-500 dark:text-slate-400">{{ dashboard?.receivables_count || 18 }} hoá đơn</span>
          </div>
          <span class="stat-icon bg-[#e0f0fb] dark:bg-sky-900/40 text-[#0b5a85] dark:text-sky-300">
            <FileText class="w-5 h-5" />
          </span>
        </div>
      </article>

      <!-- Card 3: Phải trả -->
      <article class="stat-card">
        <div class="flex items-start justify-between gap-3">
          <div class="flex flex-col gap-1.5">
            <span class="text-[13px] font-medium text-slate-500 dark:text-slate-400">Phải trả</span>
            <span class="text-[26px] font-bold text-slate-900 dark:text-slate-100 tracking-tight">[312 tr]</span>
            <span class="text-xs text-slate-500 dark:text-slate-400">{{ dashboard?.payables_suppliers_count || 7 }} nhà cung cấp</span>
          </div>
          <span class="stat-icon bg-[#ece8fb] dark:bg-purple-900/40 text-[#5b3fb0] dark:text-purple-300">
            <Receipt class="w-5 h-5" />
          </span>
        </div>
      </article>

      <!-- Card 4: Tồn quỹ -->
      <article class="stat-card">
        <div class="flex items-start justify-between gap-3">
          <div class="flex flex-col gap-1.5">
            <span class="text-[13px] font-medium text-slate-500 dark:text-slate-400">Tồn quỹ</span>
            <span class="text-[26px] font-bold text-slate-900 dark:text-slate-100 tracking-tight">[254 tr]</span>
            <span class="text-xs text-slate-500 dark:text-slate-400">tiền mặt + ngân hàng</span>
          </div>
          <span class="stat-icon bg-[#e3f5ea] dark:bg-emerald-900/40 text-[#166534] dark:text-emerald-300">
            <Wallet class="w-5 h-5" />
          </span>
        </div>
      </article>
    </div>

    <!-- Middle Section: Chart (Left) + Overdue Debts (Right) -->
    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_470px] gap-5 items-start">
      <!-- Thu - chi 6 tháng SVG Chart -->
      <section class="stat-card !p-5">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h2 class="m-0 text-base font-bold text-slate-900 dark:text-slate-100">Thu – chi 6 tháng</h2>
          <div class="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
            <span class="inline-flex items-center gap-1.5 font-medium">
              <span class="w-2.5 h-2.5 rounded-[3px] bg-[#0f8f82]" />
              Thu
            </span>
            <span class="inline-flex items-center gap-1.5 font-medium">
              <span class="w-2.5 h-2.5 rounded-[3px] bg-[#9b8ce0]" />
              Chi
            </span>
            <span class="text-slate-400 dark:text-slate-500">(triệu đồng, số mẫu)</span>
          </div>
        </div>

        <div class="w-full overflow-x-auto">
          <svg class="w-full min-w-[580px] h-[260px]" viewBox="0 0 650 260" role="img" aria-label="Biểu đồ cột thu chi 6 tháng">
            <!-- Grid Lines & Y Axis -->
            <path d="M36 230 H640" stroke="#eef2f6" class="dark:stroke-slate-700/60" stroke-width="1" />
            <text x="30" y="234" text-anchor="end" font-size="11" fill="#8795a8" font-family="Be Vietnam Pro, sans-serif">0</text>

            <path d="M36 163 H640" stroke="#eef2f6" class="dark:stroke-slate-700/60" stroke-width="1" />
            <text x="30" y="167" text-anchor="end" font-size="11" fill="#8795a8" font-family="Be Vietnam Pro, sans-serif">400</text>

            <path d="M36 97 H640" stroke="#eef2f6" class="dark:stroke-slate-700/60" stroke-width="1" />
            <text x="30" y="101" text-anchor="end" font-size="11" fill="#8795a8" font-family="Be Vietnam Pro, sans-serif">800</text>

            <path d="M36 30 H640" stroke="#eef2f6" class="dark:stroke-slate-700/60" stroke-width="1" />
            <text x="30" y="34" text-anchor="end" font-size="11" fill="#8795a8" font-family="Be Vietnam Pro, sans-serif">1200</text>

            <!-- T4 -->
            <rect x="50" y="93" width="26" height="137" rx="5" fill="#0f8f82" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T4 Thu: 900 tr</title>
            </rect>
            <rect x="80" y="128" width="26" height="102" rx="5" fill="#9b8ce0" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T4 Chi: 670 tr</title>
            </rect>
            <text x="78" y="252" text-anchor="middle" font-size="12" font-weight="500" fill="#5b6b7f" font-family="Be Vietnam Pro, sans-serif">T4</text>

            <!-- T5 -->
            <rect x="150" y="78" width="26" height="152" rx="5" fill="#0f8f82" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T5 Thu: 1000 tr</title>
            </rect>
            <rect x="180" y="113" width="26" height="117" rx="5" fill="#9b8ce0" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T5 Chi: 770 tr</title>
            </rect>
            <text x="178" y="252" text-anchor="middle" font-size="12" font-weight="500" fill="#5b6b7f" font-family="Be Vietnam Pro, sans-serif">T5</text>

            <!-- T6 -->
            <rect x="250" y="103" width="26" height="127" rx="5" fill="#0f8f82" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T6 Thu: 830 tr</title>
            </rect>
            <rect x="280" y="117" width="26" height="113" rx="5" fill="#9b8ce0" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T6 Chi: 740 tr</title>
            </rect>
            <text x="278" y="252" text-anchor="middle" font-size="12" font-weight="500" fill="#5b6b7f" font-family="Be Vietnam Pro, sans-serif">T6</text>

            <!-- T7 -->
            <rect x="350" y="57" width="26" height="173" rx="5" fill="#0f8f82" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T7 Thu: 1140 tr</title>
            </rect>
            <rect x="380" y="110" width="26" height="120" rx="5" fill="#9b8ce0" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T7 Chi: 790 tr</title>
            </rect>
            <text x="378" y="252" text-anchor="middle" font-size="12" font-weight="500" fill="#5b6b7f" font-family="Be Vietnam Pro, sans-serif">T7</text>

            <!-- T8 -->
            <rect x="450" y="67" width="26" height="163" rx="5" fill="#0f8f82" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T8 Thu: 1070 tr</title>
            </rect>
            <rect x="480" y="103" width="26" height="127" rx="5" fill="#9b8ce0" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T8 Chi: 830 tr</title>
            </rect>
            <text x="478" y="252" text-anchor="middle" font-size="12" font-weight="500" fill="#5b6b7f" font-family="Be Vietnam Pro, sans-serif">T8</text>

            <!-- T9 -->
            <rect x="550" y="43" width="26" height="187" rx="5" fill="#0f8f82" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T9 Thu: 1230 tr</title>
            </rect>
            <rect x="580" y="115" width="26" height="115" rx="5" fill="#9b8ce0" class="hover:opacity-85 transition-opacity cursor-pointer">
              <title>T9 Chi: 750 tr</title>
            </rect>
            <text x="578" y="252" text-anchor="middle" font-size="12" font-weight="500" fill="#5b6b7f" font-family="Be Vietnam Pro, sans-serif">T9</text>
          </svg>
        </div>
      </section>

      <!-- Công nợ quá hạn Card -->
      <section class="stat-card !p-5">
        <div class="flex items-center justify-between gap-3 mb-3.5">
          <h2 class="m-0 text-base font-bold text-slate-900 dark:text-slate-100">Công nợ quá hạn</h2>
          <span class="inline-flex items-center h-6 px-2.5 rounded-full bg-[#fde4e4] dark:bg-rose-950/60 text-[#9b1c1c] dark:text-rose-300 text-xs font-semibold whitespace-nowrap">
            {{ filteredOverdueDebts.length }} khách
          </span>
        </div>

        <div class="flex flex-col divide-y divide-slate-100 dark:divide-slate-700/60">
          <div
            v-for="item in filteredOverdueDebts"
            :key="item.invoice_code"
            class="flex items-center justify-between gap-2 py-3"
          >
            <div class="flex flex-col gap-0.5 min-w-0">
              <span class="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">{{ item.customer_name }}</span>
              <span class="text-xs text-slate-500 dark:text-slate-400">
                <span class="font-mono text-slate-600 dark:text-slate-300">{{ item.invoice_code }}</span> · quá {{ item.days_overdue }} ngày
              </span>
            </div>

            <div class="flex items-center gap-2.5 shrink-0">
              <b class="text-sm font-bold text-slate-900 dark:text-slate-100 whitespace-nowrap">
                {{ formatCurrency(item.amount) }}
              </b>
              <button
                type="button"
                class="h-8.5 px-3.5 rounded-xl bg-[#e6f4f1] dark:bg-teal-950/60 text-[#0f5f56] dark:text-teal-300 hover:bg-[#d8f0ec] text-xs font-semibold inline-flex items-center gap-1.5 cursor-pointer whitespace-nowrap transition-colors"
                @click="openRemind(item)"
              >
                <Mail class="w-3.5 h-3.5" />
                Nhắc nợ
              </button>
            </div>
          </div>

          <p v-if="!filteredOverdueDebts.length" class="py-6 text-center text-sm text-slate-400">
            Không có khách hàng nợ quá hạn.
          </p>
        </div>
      </section>
    </div>

    <!-- Bottom Section: Hoá đơn bán gần đây -->
    <section class="stat-card !p-0 overflow-hidden">
      <div class="flex flex-wrap items-center justify-between gap-3 p-5 pb-4">
        <h2 class="m-0 text-base font-bold text-slate-900 dark:text-slate-100">Hoá đơn bán gần đây</h2>

        <div class="flex flex-wrap items-center gap-2">
          <!-- Filter Tabs -->
          <div class="inline-flex gap-1 p-1 rounded-xl bg-slate-100 dark:bg-slate-800">
            <button
              v-for="t in [
                { key: 'all', label: 'Tất cả' },
                { key: 'pending', label: 'Chờ thu' },
                { key: 'overdue', label: 'Quá hạn' },
              ]"
              :key="t.key"
              type="button"
              class="h-8 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer"
              :class="activeTab === t.key ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
              @click="activeTab = t.key"
            >
              {{ t.label }}
            </button>
          </div>

          <!-- Export Excel Button -->
          <button
            type="button"
            class="h-9 px-3.5 rounded-xl bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 text-xs font-semibold inline-flex items-center gap-2 hover:border-slate-300 dark:hover:border-slate-600 shadow-sm cursor-pointer whitespace-nowrap transition-colors"
            @click="exportInvoices"
          >
            <Download class="w-3.5 h-3.5" />
            Xuất Excel
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto px-5 pb-5">
        <table class="w-full text-sm">
          <thead>
            <tr>
              <th class="table-th">Số hoá đơn</th>
              <th class="table-th">Khách hàng</th>
              <th class="table-th">Ngày</th>
              <th class="table-th">Giá trị</th>
              <th class="table-th">Thanh toán</th>
              <th class="table-th">Hoá đơn điện tử</th>
              <th class="table-th text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
            <tr v-for="row in filteredInvoices" :key="row.id" class="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
              <td class="table-td">
                <span class="font-mono font-semibold text-slate-900 dark:text-slate-100">{{ row.invoice_code }}</span>
              </td>
              <td class="table-td font-medium text-slate-800 dark:text-slate-200">{{ row.customer_name }}</td>
              <td class="table-td text-slate-500 dark:text-slate-400 whitespace-nowrap">{{ formatDate(row.invoice_date) }}</td>
              <td class="table-td">
                <b class="font-bold text-slate-900 dark:text-slate-100 whitespace-nowrap">{{ formatCurrency(row.total_amount) }}</b>
              </td>
              <td class="table-td whitespace-nowrap">
                <span
                  class="badge"
                  :class="row.payment_status === 'paid' ? 'badge-ok' : row.payment_status === 'partial' ? 'badge-info' : 'badge-warn'"
                >
                  {{ row.payment_status === 'paid' ? 'Đã thu' : row.payment_status === 'partial' ? 'Thu một phần' : 'Chờ thanh toán' }}
                </span>
              </td>
              <td class="table-td whitespace-nowrap">
                <span
                  class="badge"
                  :class="row.einvoice_status === 'issued' ? 'badge-ok' : 'badge-warn'"
                >
                  {{ row.einvoice_status === 'issued' ? 'Đã phát hành' : 'Chờ ký số' }}
                </span>
              </td>
              <td class="table-td text-right whitespace-nowrap">
                <div class="flex items-center justify-end gap-1.5">
                  <button
                    v-if="row.payment_status !== 'paid'"
                    type="button"
                    class="h-8 px-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold text-emerald-700 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 inline-flex items-center gap-1 transition-colors"
                    title="Thu tiền cho hoá đơn này"
                    @click="openReceipt(row)"
                  >
                    <Receipt class="w-3.5 h-3.5" />
                    Thu tiền
                  </button>
                  <button
                    type="button"
                    class="w-8 h-8 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-400 hover:text-rose-600 hover:border-rose-200 inline-flex items-center justify-center transition-colors"
                    title="Xoá hoá đơn"
                    @click="removeInvoice(row)"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-if="!filteredInvoices.length" class="py-8 text-center text-sm text-slate-400">
          Chưa có hoá đơn bán nào.
        </p>
      </div>
    </section>

    <!-- Modal 1: Phiếu thu -->
    <Modal :show="showReceiptModal" title="Lập phiếu thu tiền" @close="showReceiptModal = false">
      <form class="grid grid-cols-1 sm:grid-cols-2 gap-4" @submit.prevent="saveReceipt">
        <div class="sm:col-span-2">
          <label class="field-label mb-1">Khách hàng / Người nộp tiền</label>
          <input
            v-model="receiptForm.partner_name"
            list="customer-list"
            class="w-full field-input"
            placeholder="Nhập tên công ty hoặc chọn từ danh sách…"
            required
          />
          <datalist id="customer-list">
            <option v-for="c in customers" :key="c.id" :value="c.name" />
          </datalist>
        </div>

        <div>
          <label class="field-label mb-1">Hình thức thanh toán</label>
          <select v-model="receiptForm.payment_method" class="w-full field-input">
            <option value="bank">Chuyển khoản ngân hàng (TK 112)</option>
            <option value="cash">Tiền mặt tại quỹ (TK 111)</option>
          </select>
        </div>

        <div>
          <label class="field-label mb-1">Tài khoản đích</label>
          <input v-model="receiptForm.bank_account" class="w-full field-input" />
        </div>

        <div>
          <label class="field-label mb-1">Số tiền thu (₫)</label>
          <input v-model="receiptForm.amount" type="number" min="1" step="any" class="w-full field-input font-bold" required />
        </div>

        <div>
          <label class="field-label mb-1">Ngày lập phiếu</label>
          <input v-model="receiptForm.voucher_date" type="date" class="w-full field-input" required />
        </div>

        <div class="sm:col-span-2">
          <label class="field-label mb-1">Lý do thu tiền</label>
          <input v-model="receiptForm.description" class="w-full field-input" placeholder="Ví dụ: Thu tiền bán hóa chất xi mạ…" />
        </div>

        <div class="sm:col-span-2 flex justify-end gap-2 pt-2">
          <FormActions :disabled="saving" @cancel="showReceiptModal = false" />
        </div>
      </form>
    </Modal>

    <!-- Modal 2: Phiếu chi -->
    <Modal :show="showPaymentModal" title="Lập phiếu chi tiền" @close="showPaymentModal = false">
      <form class="grid grid-cols-1 sm:grid-cols-2 gap-4" @submit.prevent="savePayment">
        <div class="sm:col-span-2">
          <label class="field-label mb-1">Người nhận tiền / Đơn vị thụ hưởng</label>
          <input v-model="paymentForm.partner_name" class="w-full field-input" placeholder="Tên nhà cung cấp hoặc nhân viên…" required />
        </div>

        <div>
          <label class="field-label mb-1">Hạng mục chi</label>
          <select v-model="paymentForm.category" class="w-full field-input">
            <option value="supplier_payment">Trả tiền nhà cung cấp (TK 331)</option>
            <option value="transportation">Chi phí vận chuyển / xe giao hàng</option>
            <option value="factory_expense">Chi phí vận hành xưởng / điện nước</option>
            <option value="salary">Chi trả lương / tạm ứng</option>
            <option value="other">Chi phí khác</option>
          </select>
        </div>

        <div>
          <label class="field-label mb-1">Hình thức chi</label>
          <select v-model="paymentForm.payment_method" class="w-full field-input">
            <option value="bank">Chuyển khoản ngân hàng (TK 112)</option>
            <option value="cash">Tiền mặt tại quỹ (TK 111)</option>
          </select>
        </div>

        <div>
          <label class="field-label mb-1">Số tiền chi (₫)</label>
          <input v-model="paymentForm.amount" type="number" min="1" step="any" class="w-full field-input font-bold" required />
        </div>

        <div>
          <label class="field-label mb-1">Ngày chi</label>
          <input v-model="paymentForm.voucher_date" type="date" class="w-full field-input" required />
        </div>

        <div class="sm:col-span-2">
          <label class="field-label mb-1">Lý do chi tiền</label>
          <input v-model="paymentForm.description" class="w-full field-input" placeholder="Ví dụ: Thanh toán tiền nhập Axit H2SO4…" />
        </div>

        <div class="sm:col-span-2 flex justify-end gap-2 pt-2">
          <FormActions :disabled="saving" @cancel="showPaymentModal = false" />
        </div>
      </form>
    </Modal>

    <!-- Modal 3: Tạo hoá đơn -->
    <Modal :show="showInvoiceModal" title="Tạo hoá đơn bán hàng" size="lg" @close="showInvoiceModal = false">
      <form class="flex flex-col gap-4" @submit.prevent="saveInvoice">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label class="field-label mb-1">Mã hoá đơn (để trống tự sinh)</label>
            <input v-model="invoiceForm.invoice_code" class="w-full field-input font-mono" placeholder="HĐ-000422" />
          </div>
          <div class="sm:col-span-2">
            <label class="field-label mb-1">Khách hàng</label>
            <input
              v-model="invoiceForm.customer_name"
              list="customer-list-inv"
              class="w-full field-input"
              placeholder="Chọn khách hàng hoặc nhập tên mới…"
              required
              @input="onCustomerSelect($event.target.value)"
            />
            <datalist id="customer-list-inv">
              <option v-for="c in customers" :key="c.id" :value="c.name" />
            </datalist>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label class="field-label mb-1">Ngày lập hoá đơn</label>
            <input v-model="invoiceForm.invoice_date" type="date" class="w-full field-input" required />
          </div>
          <div>
            <label class="field-label mb-1">Hạn thanh toán</label>
            <input v-model="invoiceForm.due_date" type="date" class="w-full field-input" />
          </div>
          <div>
            <label class="field-label mb-1">Trạng thái HĐĐT</label>
            <select v-model="invoiceForm.einvoice_status" class="w-full field-input">
              <option value="issued">Đã phát hành</option>
              <option value="pending_signature">Chờ ký số</option>
              <option value="draft">Bản nháp</option>
            </select>
          </div>
        </div>

        <!-- Chi tiết mặt hàng -->
        <div class="flex flex-col gap-2 pt-2 border-t border-slate-200 dark:border-slate-700">
          <div class="flex items-center justify-between">
            <span class="text-sm font-bold text-slate-800 dark:text-slate-100">Chi tiết sản phẩm / hoá chất</span>
            <button
              type="button"
              class="h-8 px-3 rounded-lg bg-teal-50 dark:bg-teal-950/50 text-dl-teal text-xs font-semibold inline-flex items-center gap-1.5 hover:bg-teal-100 transition-colors"
              @click="addInvoiceItem"
            >
              <Plus class="w-3.5 h-3.5" /> Thêm dòng
            </button>
          </div>

          <div class="flex flex-col gap-2.5 max-h-60 overflow-y-auto pr-1">
            <div
              v-for="(item, idx) in invoiceForm.items"
              :key="idx"
              class="grid grid-cols-12 gap-2 items-center bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-xl border border-slate-200/80 dark:border-slate-700/60"
            >
              <div class="col-span-12 sm:col-span-5">
                <input
                  v-model="item.product_name"
                  list="product-list-inv"
                  class="w-full field-input text-xs"
                  placeholder="Tên sản phẩm / hoá chất xi mạ…"
                  required
                />
              </div>
              <div class="col-span-3 sm:col-span-2">
                <input v-model="item.unit" class="w-full field-input text-xs text-center" placeholder="ĐVT" />
              </div>
              <div class="col-span-4 sm:col-span-2">
                <input v-model="item.quantity" type="number" min="0.1" step="any" class="w-full field-input text-xs text-right font-medium" placeholder="SL" required />
              </div>
              <div class="col-span-4 sm:col-span-2">
                <input v-model="item.unit_price" type="number" min="0" step="any" class="w-full field-input text-xs text-right font-medium" placeholder="Đơn giá" required />
              </div>
              <div class="col-span-1 text-center">
                <button
                  type="button"
                  class="text-slate-400 hover:text-rose-500"
                  title="Xoá dòng"
                  @click="removeInvoiceItem(idx)"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
          <datalist id="product-list-inv">
            <option v-for="p in products" :key="p.id" :value="`${p.code} - ${p.name_vi}`" />
          </datalist>
        </div>

        <!-- Summary -->
        <div class="flex flex-col items-end gap-1.5 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm">
          <div class="flex justify-between w-full sm:w-64 text-slate-500 dark:text-slate-400 text-xs">
            <span>Tiền hàng trước thuế:</span>
            <b class="text-slate-800 dark:text-slate-100">{{ formatCurrency(formSubtotal) }}</b>
          </div>
          <div class="flex justify-between w-full sm:w-64 text-slate-500 dark:text-slate-400 text-xs">
            <span>Thuế GTGT ({{ invoiceForm.tax_rate }}%):</span>
            <b class="text-slate-800 dark:text-slate-100">{{ formatCurrency(formTaxAmount) }}</b>
          </div>
          <div class="flex justify-between w-full sm:w-64 pt-1.5 border-t border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 font-bold">
            <span>Tổng thanh toán:</span>
            <span class="text-base text-dl-teal">{{ formatCurrency(formTotalAmount) }}</span>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <FormActions :disabled="saving" @cancel="showInvoiceModal = false" />
        </div>
      </form>
    </Modal>

    <!-- Modal 4: Nhắc nợ -->
    <Modal :show="showRemindModal" title="Gửi đối chiếu & Nhắc nợ" @close="showRemindModal = false">
      <form class="flex flex-col gap-4" @submit.prevent="sendRemind">
        <div class="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50">
          <div class="flex items-start justify-between gap-2">
            <div>
              <h3 class="m-0 text-sm font-bold text-slate-900 dark:text-slate-100">{{ remindData.invoice?.customer_name }}</h3>
              <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                Chứng từ: <span class="font-mono font-semibold">{{ remindData.invoice?.invoice_code }}</span> · Đã quá hạn <b>{{ remindData.invoice?.days_overdue }} ngày</b>
              </p>
            </div>
            <span class="text-base font-bold text-rose-600 dark:text-rose-400">
              {{ formatCurrency(remindData.invoice?.amount) }}
            </span>
          </div>
        </div>

        <div>
          <label class="field-label mb-1">Phương thức gửi nhắc nợ</label>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-xs font-semibold cursor-pointer" :class="remindData.channel === 'email' ? 'border-dl-teal bg-teal-50/50 dark:bg-teal-950/30 text-dl-teal' : 'text-slate-600'">
              <input v-model="remindData.channel" type="radio" value="email" class="hidden" />
              <Mail class="w-4 h-4" /> Email tự động
            </label>
            <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-xs font-semibold cursor-pointer" :class="remindData.channel === 'zalo' ? 'border-dl-teal bg-teal-50/50 dark:bg-teal-950/30 text-dl-teal' : 'text-slate-600'">
              <input v-model="remindData.channel" type="radio" value="zalo" class="hidden" />
              <Send class="w-4 h-4" /> Tin nhắn Zalo
            </label>
            <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-xs font-semibold cursor-pointer" :class="remindData.channel === 'manual' ? 'border-dl-teal bg-teal-50/50 dark:bg-teal-950/30 text-dl-teal' : 'text-slate-600'">
              <input v-model="remindData.channel" type="radio" value="manual" class="hidden" />
              <FileText class="w-4 h-4" /> In biên bản
            </label>
          </div>
        </div>

        <div>
          <label class="field-label mb-1">Nội dung thư nhắc nợ mẫu</label>
          <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans select-all">
            Kính gửi Quý công ty <b>{{ remindData.invoice?.customer_name }}</b>,<br><br>
            Bộ phận Kế toán Công ty Daliang xin thông báo hoá đơn số <b>{{ remindData.invoice?.invoice_code }}</b> với số tiền <b>{{ formatCurrency(remindData.invoice?.amount) }}</b> hiện đã quá hạn thanh toán {{ remindData.invoice?.days_overdue }} ngày.<br>
            Kính đề nghị Quý khách hàng sắp xếp thanh toán vào số tài khoản <b>0071001234567 - Vietcombank</b> của Công ty trước ngày 05 tháng tới.<br><br>
            Trân trọng cảm ơn sự hợp tác của Quý công ty!
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button type="button" class="h-10 px-4 rounded-xl text-sm text-slate-500" @click="showRemindModal = false">Đóng</button>
          <button
            type="submit"
            class="h-10 px-5 rounded-xl bg-gradient-to-r from-[#0b7d72] to-[#0e6f8a] text-white text-sm font-semibold flex items-center gap-2 shadow-md shadow-teal-700/20"
            :disabled="saving"
          >
            <Send class="w-4 h-4" /> Xác nhận gửi
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<style scoped>
.accounting-container {
  @apply flex flex-col gap-5 max-w-[1600px] w-full mx-auto;
}

.stat-card {
  @apply bg-white dark:bg-slate-800 rounded-[20px] p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04),0_8px_24px_rgba(15,23,42,0.05)] border border-slate-100 dark:border-slate-700/60 box-border;
}

.stat-icon {
  @apply w-10 h-10 rounded-xl inline-flex items-center justify-center shrink-0;
}

.table-th {
  @apply text-left text-xs font-semibold text-slate-500 dark:text-slate-400 py-2.5 px-3 border-b border-slate-200 dark:border-slate-700 whitespace-nowrap;
}

.table-td {
  @apply py-3 px-3 border-b border-slate-100 dark:border-slate-700/60 text-slate-700 dark:text-slate-200 align-middle text-[13px];
}

.badge {
  @apply inline-flex items-center h-6 px-2.5 rounded-full text-xs font-semibold whitespace-nowrap;
}
.badge-ok {
  @apply bg-[#e3f5ea] dark:bg-emerald-950/60 text-[#166534] dark:text-emerald-300;
}
.badge-warn {
  @apply bg-[#fdf0cf] dark:bg-amber-950/60 text-[#8a4b08] dark:text-amber-300;
}
.badge-info {
  @apply bg-[#e0f0fb] dark:bg-sky-950/60 text-[#0b5a85] dark:text-sky-300;
}
</style>
