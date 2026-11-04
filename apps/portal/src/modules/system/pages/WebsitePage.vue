<!-- /system/website - hai viec cua website cong khai:
       - Don khach gui (form "Nhan bao gia"): xem, danh dau da xu ly.
       - San pham tren web: chon ma nao hien o nhom nao (nen 5-10 ma moi nhom).
     Ten/mo ta tieng Anh, tieng Trung sua o Ky thuat -> San pham cong ty. -->
<script setup>
import { computed, onMounted, ref } from 'vue'
import { Loader2, Search } from 'lucide-vue-next'
import { errorMessage } from '@/core/api/errors'
import { productsApi } from '@/core/api/common'
import { can } from '@/core/auth/store'
import { formatDateTime } from '@/core/utils/format'
import { contactLeadsApi, productWebsiteApi } from '../api'

const GROUPS = [
  { value: 'pre', label: 'Tiền xử lý' },
  { value: 'add', label: 'Phụ gia mạ' },
  { value: 'pas', label: 'Thụ động' },
]
const LANGS = { vi: 'Tiếng Việt', en: 'English', zh: '中文' }

const tab = ref('leads')
const error = ref('')

// ---------- Don khach gui ----------
const leads = ref([])
const onlyOpen = ref(true)
const shownLeads = computed(() => leads.value.filter(lead => !onlyOpen.value || !lead.is_handled))
const canHandle = computed(() => can('website.contact_leads.update'))

async function toggleHandled(lead) {
  try {
    Object.assign(lead, await contactLeadsApi.setHandled(lead.id, !lead.is_handled))
  } catch (e) {
    error.value = errorMessage(e)
  }
}

// ---------- San pham tren web ----------
const canEditProducts = computed(() => can('common.products.update'))
const products = ref([])
const query = ref('')
const onlyOnWeb = ref(true)
const savingId = ref(null)

const counts = computed(() => Object.fromEntries(
  GROUPS.map(g => [g.value, products.value.filter(p => p.web_group === g.value).length]),
))
const shownProducts = computed(() => {
  const q = query.value.trim().toLowerCase()
  return products.value.filter(p =>
    (!onlyOnWeb.value || p.web_group) &&
    (!q || `${p.code} ${p.name} ${p.name_en || ''} ${p.category || ''}`.toLowerCase().includes(q)))
})

async function setGroup(product, value) {
  savingId.value = product.id
  try {
    const saved = await productWebsiteApi.update(product.id, { web_group: value || null })
    product.web_group = saved.web_group
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    savingId.value = null
  }
}

const loading = ref(true)
onMounted(async () => {
  try {
    const [leadRows, productRows] = await Promise.all([
      contactLeadsApi.list(),
      can('common.products.view') ? productsApi.list() : [],
    ])
    leads.value = leadRows
    products.value = productRows
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm flex flex-col min-h-0 flex-1">
    <div class="flex flex-wrap items-center gap-2 p-5 pb-3 shrink-0">
      <button
        v-for="item in [{ key: 'leads', label: `Đơn khách gửi (${leads.filter(l => !l.is_handled).length} chưa xử lý)` }, { key: 'products', label: 'Sản phẩm trên web' }]"
        :key="item.key" type="button"
        class="h-9 px-4 rounded-xl text-sm font-medium"
        :class="tab === item.key ? 'bg-brand-gradient text-white' : 'text-slate-500 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'"
        @click="tab = item.key"
      >{{ item.label }}</button>
    </div>
    <p v-if="error" class="px-5 pb-3 text-sm text-red-600">{{ error }}</p>
    <div v-if="loading" class="py-10 flex justify-center"><Loader2 class="w-5 h-5 animate-spin text-slate-400" /></div>

    <!-- Don khach gui -->
    <div v-else-if="tab === 'leads'" class="flex-1 min-h-0 overflow-auto px-5 pb-5">
      <label class="flex items-center gap-2 text-sm text-slate-500 mb-3">
        <input v-model="onlyOpen" type="checkbox" class="rounded" /> Chỉ đơn chưa xử lý
      </label>
      <p v-if="!shownLeads.length" class="py-8 text-center text-sm text-slate-400">Không có đơn nào.</p>
      <div class="flex flex-col gap-2">
        <article v-for="lead in shownLeads" :key="lead.id" class="p-4 rounded-xl border border-slate-200 dark:border-slate-700" :class="{ 'opacity-60': lead.is_handled }">
          <div class="flex flex-wrap items-start justify-between gap-2">
            <div>
              <div class="font-medium text-slate-700 dark:text-slate-200">{{ lead.name }}<span v-if="lead.company" class="font-normal text-slate-500"> — {{ lead.company }}</span></div>
              <div class="text-sm text-slate-500">
                <a :href="`tel:${lead.phone}`" class="text-brand-600">{{ lead.phone }}</a>
                <template v-if="lead.email"> · <a :href="`mailto:${lead.email}`" class="text-brand-600">{{ lead.email }}</a></template>
              </div>
            </div>
            <div class="text-right text-xs text-slate-400">
              {{ formatDateTime(lead.created_at) }}<br>{{ LANGS[lead.lang] || lead.lang }} · {{ lead.source_path }}
            </div>
          </div>
          <p v-if="lead.product" class="text-sm mt-2 text-slate-600 dark:text-slate-300"><b>Sản phẩm quan tâm:</b> {{ lead.product }}</p>
          <p v-if="lead.message" class="text-sm mt-1 text-slate-600 dark:text-slate-300 whitespace-pre-line">{{ lead.message }}</p>
          <button v-if="canHandle" type="button" class="mt-2 text-sm text-brand-600" @click="toggleHandled(lead)">
            {{ lead.is_handled ? 'Đánh dấu chưa xử lý' : 'Đánh dấu đã xử lý' }}
          </button>
        </article>
      </div>
    </div>

    <!-- San pham tren web -->
    <div v-else class="flex-1 min-h-0 flex flex-col px-5 pb-5">
      <div class="flex flex-wrap items-center gap-3 mb-3 text-sm">
        <span v-for="g in GROUPS" :key="g.value" class="px-3 py-1 rounded-full" :class="counts[g.value] > 10 ? 'bg-amber-50 text-amber-700' : 'bg-brand-50 dark:bg-slate-700 text-brand-700 dark:text-brand-300'">
          {{ g.label }}: {{ counts[g.value] }} mã
        </span>
        <span class="text-xs text-slate-400">Nên để 5–10 mã mỗi nhóm.</span>
      </div>
      <div class="flex flex-wrap items-center gap-3 mb-3">
        <div class="relative flex-1 min-w-[200px]">
          <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input v-model="query" placeholder="Tìm mã, tên, nhóm…" class="w-full field-input pl-9" />
        </div>
        <label class="flex items-center gap-2 text-sm text-slate-500">
          <input v-model="onlyOnWeb" type="checkbox" class="rounded" /> Chỉ mã đang lên web
        </label>
      </div>
      <div class="flex-1 min-h-0 overflow-auto">
        <table class="w-full min-w-[460px] text-sm">
          <thead>
            <tr class="text-left text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
              <th class="py-2 pr-4 font-medium">Mã</th>
              <th class="py-2 pr-4 font-medium">Tên</th>
              <th class="py-2 font-medium w-48">Hiện trên web</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in shownProducts" :key="product.id" class="border-b border-slate-100 dark:border-slate-700/60">
              <td class="py-2 pr-4 font-mono text-xs text-slate-700 dark:text-slate-200">{{ product.code }}</td>
              <td class="py-2 pr-4 text-slate-600 dark:text-slate-300">
                {{ product.name }}
                <span v-if="product.web_group && (!product.name_zh || !product.description_en)" class="text-xs text-amber-600"> · thiếu bản dịch</span>
              </td>
              <td class="py-2">
                <select
                  :value="product.web_group || ''" class="w-full field-input"
                  :disabled="!canEditProducts || savingId === product.id"
                  @change="setGroup(product, $event.target.value)"
                >
                  <option value="">Không hiện</option>
                  <option v-for="g in GROUPS" :key="g.value" :value="g.value">{{ g.label }}</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
