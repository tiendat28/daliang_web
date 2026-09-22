<script setup>
import { computed, nextTick, onUnmounted, ref } from 'vue'
import { Plus, Search, X, Pencil } from 'lucide-vue-next'
import Modal from '../components/Modal.vue'
import FormActions from '../components/FormActions.vue'
import { companyProductsApi } from '../api/resources'
import { useCrudResource } from '../composables/useCrudResource'
import { productSearch } from '../store/productSearch'

// Mỗi mã là một thẻ: đầu thẻ có mã + nhóm + tên, thân thẻ có giai đoạn, vật liệu,
// công dụng và các "chế độ sử dụng" — mỗi chế độ một bảng thông số, mỗi thông số
// một dòng. Thông số lưu nguyên văn ("Nhiệt độ: 50-75°C"), tách ở dấu ":" đầu
// tiên để canh hai cột cho dễ đọc.

function emptyMode(name = 'Chung') {
  return { name, paramsText: '' }
}

function emptyForm() {
  return {
    code: '', name: '', name_en: '', category: '', usage_stage: '', materials: '', description: '',
    modes: [emptyMode()],
  }
}

const { rows, showModal, editingId, form, load, openAdd, openEdit } = useCrudResource(
  companyProductsApi, emptyForm,
  {
    mapRowToForm: row => ({
      code: row.code,
      name: row.name,
      name_en: row.name_en || '',
      category: row.category || '',
      usage_stage: row.usage_stage || '',
      materials: row.materials || '',
      description: row.description || '',
      modes: row.modes.length
        ? row.modes.map(m => ({ name: m.name, paramsText: m.params.join('\n') }))
        : [emptyMode()],
    }),
  },
)

const groupFilter = ref('')
onUnmounted(() => { productSearch.query = '' })

// Bỏ dấu để gõ "tay dau" vẫn ra "Tẩy dầu"
function noAccent(value) {
  return String(value || '').normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase()
}

const groups = computed(() =>
  [...new Set(rows.value.map(p => p.category).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'vi')),
)

function splitParam(raw) {
  const text = String(raw)
  const i = text.indexOf(':')
  return i > 0 && i < text.length - 1
    ? { name: text.slice(0, i).trim(), value: text.slice(i + 1).trim() }
    : { name: text.trim(), value: '' }
}

// Sắp xếp, tách thông số và chuỗi tìm kiếm bỏ dấu chỉ làm một lần mỗi lần tải
// danh sách — gõ tìm kiếm thì chỉ còn lọc.
const cards = computed(() => rows.value
  .map(p => ({
    ...p,
    haystack: noAccent([p.code, p.name, p.name_en, p.category, p.usage_stage, p.materials, p.description].join(' ')),
    modes: p.modes.map(m => ({ ...m, rows: m.params.map(splitParam) })),
  }))
  .sort((a, b) =>
    (a.category || '').localeCompare(b.category || '', 'vi')
    || a.code.localeCompare(b.code, 'vi', { numeric: true })))

const filteredRows = computed(() => {
  const query = noAccent(productSearch.query.trim())
  return cards.value.filter(p =>
    (!groupFilter.value || p.category === groupFilter.value) && (!query || p.haystack.includes(query)))
})

const countLabel = computed(() => filteredRows.value.length === rows.value.length
  ? `${rows.value.length} mã`
  : `${filteredRows.value.length} / ${rows.value.length} mã`)

// ---------- Form ----------
const errorMessage = ref('')
const codeInput = ref(null)
const nameInput = ref(null)

function startAdd() {
  errorMessage.value = ''
  openAdd()
  nextTick(() => codeInput.value?.focus())
}

function startEdit(row) {
  errorMessage.value = ''
  openEdit(row)
  nextTick(() => nameInput.value?.focus())
}

function addMode() {
  form.value.modes.push(emptyMode(''))
}

function removeMode(index) {
  form.value.modes.splice(index, 1)
  if (!form.value.modes.length) form.value.modes.push(emptyMode())
}

function buildPayload(f) {
  const trimmed = key => f[key].trim() || null
  return {
    code: f.code.trim(),
    name: f.name.trim(),
    name_en: trimmed('name_en'),
    category: trimmed('category'),
    usage_stage: trimmed('usage_stage'),
    materials: trimmed('materials'),
    description: trimmed('description'),
    modes: f.modes
      .map(m => ({
        name: m.name.trim() || 'Chung',
        params: m.paramsText.split('\n').map(s => s.trim()).filter(Boolean),
      }))
      .filter(m => m.params.length),
  }
}

async function save() {
  errorMessage.value = ''
  const payload = buildPayload(form.value)
  try {
    if (editingId.value) await companyProductsApi.update(editingId.value, payload)
    else await companyProductsApi.create(payload)
  } catch (error) {
    errorMessage.value = error.response?.status === 400
      ? `Mã ${payload.code} đã tồn tại`
      : 'Không lưu được, thử lại sau.'
    return
  }
  showModal.value = false
  await load()
}

async function removeEditing() {
  if (!confirm(`Xoá mã ${form.value.code} khỏi danh mục?`)) return
  await companyProductsApi.remove(editingId.value)
  showModal.value = false
  await load()
}
</script>

<template>
  <!-- Thanh trên: dính ở đầu vùng cuộn để lọc được khi đang xem giữa danh sách -->
  <div class="sticky top-0 z-10 bg-white/90 dark:bg-slate-800/90 backdrop-blur rounded-2xl shadow-sm p-4 sm:p-5 mb-4 shrink-0">
    <div class="flex flex-wrap items-center gap-3">
      <h2 class="font-semibold text-slate-700 dark:text-slate-200">Sản phẩm công ty</h2>
      <span class="font-mono text-xs px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200 dark:bg-brand-900/40 dark:text-brand-300 dark:border-brand-800">
        {{ countLabel }}
      </span>
      <span class="flex-1" />
      <button
        class="flex items-center justify-center gap-1 text-sm bg-brand-gradient text-white w-9 h-9 sm:w-auto sm:h-auto sm:px-4 sm:py-2 rounded-full sm:rounded-xl shadow shrink-0"
        title="Thêm hóa chất"
        @click="startAdd"
      >
        <Plus class="w-4 h-4" />
        <span class="hidden sm:inline">Thêm hóa chất</span>
      </button>
    </div>
    <div class="flex flex-col sm:flex-row gap-2 mt-3">
      <label class="relative flex-1 min-w-0">
        <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        <input
          v-model="productSearch.query"
          type="search"
          placeholder="Tìm mã, tên, công dụng…"
          autocomplete="off"
          class="field-input w-full !pl-9 bg-white focus:outline-none focus:ring-2 focus:ring-brand-400"
        />
      </label>
      <select
        v-model="groupFilter"
        aria-label="Lọc theo nhóm"
        class="field-input bg-white sm:w-72 focus:outline-none focus:ring-2 focus:ring-brand-400"
      >
        <option value="">Tất cả nhóm</option>
        <option v-for="g in groups" :key="g" :value="g">{{ g }}</option>
      </select>
    </div>
  </div>

  <!-- Lưới thẻ: 1 cột điện thoại → 2 → 3 cột màn hình rộng; thẻ giữ chiều cao tự nhiên -->
  <div v-if="filteredRows.length" class="grid gap-4 grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 items-start">
    <article
      v-for="p in filteredRows"
      :key="p.id"
      class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl shadow-sm overflow-hidden flex flex-col"
    >
      <header class="px-4 pt-3.5 pb-3 bg-slate-50 dark:bg-slate-700/40 border-b border-slate-100 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2 min-w-0">
          <span class="font-mono text-[13.5px] font-bold px-2 py-0.5 rounded-md bg-brand-700 text-white dark:bg-brand-400 dark:text-slate-900 shrink-0">
            {{ p.code }}
          </span>
          <span
            v-if="p.category"
            class="text-[11.5px] text-slate-500 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 px-2 py-0.5 rounded-full truncate"
            :title="p.category"
          >{{ p.category }}</span>
        </div>
        <h3 class="text-[15.5px] font-semibold leading-snug text-slate-800 dark:text-slate-100">{{ p.name }}</h3>
        <p v-if="p.name_en" class="text-[12.5px] italic text-slate-400 dark:text-slate-400 mt-0.5">{{ p.name_en }}</p>
      </header>

      <div class="px-4 py-3 flex flex-col gap-3">
        <dl v-if="p.usage_stage || p.materials" class="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-[13px]">
          <template v-if="p.usage_stage">
            <dt class="text-slate-400 whitespace-nowrap">Giai đoạn</dt>
            <dd class="text-slate-600 dark:text-slate-300">{{ p.usage_stage }}</dd>
          </template>
          <template v-if="p.materials">
            <dt class="text-slate-400 whitespace-nowrap">Vật liệu</dt>
            <dd class="text-slate-600 dark:text-slate-300">{{ p.materials }}</dd>
          </template>
        </dl>

        <div v-if="p.description">
          <div class="text-[11px] font-bold tracking-widest uppercase text-slate-400 mb-1.5">Công dụng</div>
          <p class="text-[13.5px] text-slate-600 dark:text-slate-300">{{ p.description }}</p>
        </div>

        <div v-if="p.modes.length">
          <div class="text-[11px] font-bold tracking-widest uppercase text-slate-400 mb-1.5">Thông số vận hành</div>
          <div class="space-y-2">
            <div
              v-for="m in p.modes"
              :key="m.id"
              class="rounded-xl border border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/40 overflow-hidden"
            >
              <div class="text-[12.5px] font-semibold px-3 py-1.5 text-brand-700 bg-brand-50/70 border-b border-slate-100 dark:text-brand-300 dark:bg-brand-900/30 dark:border-slate-700">
                {{ m.name }}
              </div>
              <ul class="py-1">
                <li
                  v-for="(param, i) in m.rows"
                  :key="i"
                  class="flex gap-3 items-baseline px-3 py-1 text-[13px] border-t border-dashed border-slate-200 dark:border-slate-700 first:border-t-0"
                >
                  <span class="flex-1 min-w-0 text-slate-600 dark:text-slate-300">{{ param.name }}</span>
                  <span
                    v-if="param.value"
                    class="font-mono text-[12.5px] font-semibold text-right text-slate-800 dark:text-slate-100 max-w-[56%] [overflow-wrap:anywhere]"
                  >{{ param.value }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <footer class="mt-auto px-4 py-2.5 border-t border-slate-100 dark:border-slate-700 flex justify-end">
        <button
          class="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700"
          @click="startEdit(p)"
        >
          <Pencil class="w-3.5 h-3.5" /> Sửa
        </button>
      </footer>
    </article>
  </div>

  <div v-else-if="rows.length" class="text-center py-16 text-slate-400">
    <strong class="block text-slate-600 dark:text-slate-300 text-base mb-1">Không tìm thấy hóa chất nào</strong>
    Thử từ khóa khác hoặc bỏ bộ lọc nhóm.
  </div>

  <Modal :show="showModal" size="lg" :title="editingId ? `Sửa mã ${form.code}` : 'Thêm hóa chất mới'" @close="showModal = false">
    <datalist id="product-groups">
      <option v-for="g in groups" :key="g" :value="g" />
    </datalist>

    <form class="space-y-4" @submit.prevent="save">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="min-w-0">
          <label class="field-label mb-1">Mã hóa chất <span class="text-red-500">*</span></label>
          <input
            ref="codeInput"
            v-model="form.code"
            required
            :disabled="!!editingId"
            placeholder="VD: DU-252"
            autocomplete="off"
            class="w-full field-input disabled:opacity-60 disabled:cursor-not-allowed"
          />
          <p v-if="editingId" class="text-xs text-slate-400 mt-1">Không sửa được mã sau khi đã lưu.</p>
        </div>
        <div class="min-w-0">
          <label class="field-label mb-1">Nhóm phân loại <span class="text-red-500">*</span></label>
          <input v-model="form.category" required list="product-groups" placeholder="VD: Chất tẩy dầu mỡ" autocomplete="off" class="w-full field-input" />
        </div>
        <div class="min-w-0 sm:col-span-2">
          <label class="field-label mb-1">Tên tiếng Việt <span class="text-red-500">*</span></label>
          <input ref="nameInput" v-model="form.name" required placeholder="VD: Chất tẩy dầu điện phân" autocomplete="off" class="w-full field-input" />
        </div>
        <div class="min-w-0 sm:col-span-2">
          <label class="field-label mb-1">Tên tiếng Anh</label>
          <input v-model="form.name_en" placeholder="VD: Electro-cleaner" autocomplete="off" class="w-full field-input" />
        </div>
        <div class="min-w-0">
          <label class="field-label mb-1">Giai đoạn sử dụng</label>
          <input v-model="form.usage_stage" placeholder="VD: Tẩy dầu mỡ" autocomplete="off" class="w-full field-input" />
        </div>
        <div class="min-w-0">
          <label class="field-label mb-1">Vật liệu áp dụng</label>
          <input v-model="form.materials" placeholder="VD: Thép và hợp kim đồng" autocomplete="off" class="w-full field-input" />
        </div>
        <div class="min-w-0 sm:col-span-2">
          <label class="field-label mb-1">Công dụng</label>
          <textarea v-model="form.description" rows="3" placeholder="Mô tả ngắn gọn công dụng, đặc tính nổi bật…" class="w-full field-input resize-y" />
        </div>
      </div>

      <div class="pt-4 border-t border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <h4 class="text-xs font-bold tracking-wider uppercase text-slate-400">Thông số vận hành</h4>
          <span class="flex-1" />
          <button type="button" class="flex items-center gap-1 text-sm text-brand-600 dark:text-brand-400" @click="addMode">
            <Plus class="w-4 h-4" /> Thêm chế độ
          </button>
        </div>
        <div
          v-for="(m, i) in form.modes"
          :key="i"
          class="rounded-xl border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-900/40 p-3 mb-2.5"
        >
          <div class="flex items-center gap-2 mb-2">
            <input v-model="m.name" placeholder="Tên chế độ — VD: Thép · Điện phân" autocomplete="off" class="flex-1 field-input bg-white" />
            <button type="button" class="text-red-400 hover:text-red-500 shrink-0 p-1" aria-label="Xoá chế độ" @click="removeMode(i)">
              <X class="w-4 h-4" />
            </button>
          </div>
          <label class="field-label mb-1 text-xs">Thông số — <strong>mỗi dòng một thông số</strong></label>
          <textarea
            v-model="m.paramsText"
            rows="4"
            :placeholder="'Nồng độ DU-252: 50-100 g/L\nNhiệt độ: 40-60°C\nThời gian (catot): 1-9 phút\nMật độ dòng: 4.0-10 A/dm²'"
            class="w-full field-input bg-white font-mono text-[12.5px] leading-relaxed resize-y"
          />
        </div>
      </div>

      <p v-if="errorMessage" class="text-sm text-red-500">{{ errorMessage }}</p>

      <div class="flex items-center gap-2 pt-2">
        <button
          v-if="editingId"
          type="button"
          class="px-3 py-2 rounded-xl text-sm text-red-500 border border-red-200 dark:border-red-900 hover:bg-red-50 dark:hover:bg-red-950/40"
          @click="removeEditing"
        >
          Xoá mã này
        </button>
        <span class="flex-1" />
        <FormActions @cancel="showModal = false" />
      </div>
    </form>
  </Modal>
</template>
