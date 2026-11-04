<script setup>
import { ref, reactive, watch, onMounted, onBeforeUnmount } from 'vue'
import { Loader2 } from 'lucide-vue-next'
import { companyProfileApi } from '@/core/api/common'
import { testProcessesApi } from '@/modules/lab/api'
import { assetUrl } from '@/core/utils/apiAsset'
import { PAGE_WIDTH, LETTERHEAD_HEIGHT } from '@/modules/lab/constants/testProcess'
import { usePageCan } from '@/core/auth/store'

// Thông tin in ở đầu mọi phiếu. Sửa ở đây là đổi cho tất cả phiếu, kể cả
// lưu trình đã lưu từ trước, vì phần đầu trang dựng lại lúc in.
// Chi xem (khong co common.company_profile.edit) thi an nut Luu / Doi logo
const can = usePageCan()

const form = reactive({ name_zh: '', name_en: '', address_zh: '', phone: '', fax: '' })
// Chỉ website công khai dùng - để riêng để gõ vào không dựng lại khung xem trước tờ in
const WEB_FIELDS = [
  { key: 'name_vi', label: 'Tên công ty — tiếng Việt', wide: true },
  { key: 'address_vi', label: 'Địa chỉ — tiếng Việt', wide: true },
  { key: 'tax_id', label: 'Mã số thuế' },
  { key: 'email', label: 'Email' },
  { key: 'hours_vi', label: 'Giờ làm việc — tiếng Việt' },
  { key: 'hours_en', label: 'Giờ làm việc — tiếng Anh' },
  { key: 'hours_zh', label: 'Giờ làm việc — tiếng Trung' },
  { key: 'map_query', label: 'Bản đồ — tên hoặc địa chỉ để tìm trên Google Maps', wide: true },
]
const web = reactive(Object.fromEntries(WEB_FIELDS.map(f => [f.key, ''])))
const logoUrl = ref('')
const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const message = ref('')
const errorMessage = ref('')
const fileInput = ref(null)

// Khung xem trước: backend dựng phần đầu trang bằng đúng template của tờ in,
// mình chỉ cắt lấy phần đầu và co cho vừa bề ngang chỗ trống.
const previewBox = ref(null)
const previewScale = ref(1)
const previewHtml = ref('')

function fill(profile) {
  form.name_zh = profile.name_zh || ''
  form.name_en = profile.name_en || ''
  form.address_zh = profile.address_zh || ''
  form.phone = profile.phone || ''
  form.fax = profile.fax || ''
  WEB_FIELDS.forEach(({ key }) => { web[key] = profile[key] || '' })
  logoUrl.value = assetUrl(profile.logo_url)
}

let observer = null

let previewTimer = null

async function refreshPreview() {
  try {
    previewHtml.value = await testProcessesApi.letterheadPreview({ ...form })
  } catch {
    previewHtml.value = ''
  }
}

watch(form, () => {
  clearTimeout(previewTimer)
  previewTimer = setTimeout(refreshPreview, 400)
})

onMounted(async () => {
  try {
    fill(await companyProfileApi.get())
  } finally {
    loading.value = false
  }
  await refreshPreview()

  // contentRect đã trừ phần đệm của khung, và bắt được cả lúc bố cục đổi
  // (mở thanh bên, đổi cỡ chữ) chứ không chỉ lúc đổi cỡ cửa sổ
  observer = new ResizeObserver(([entry]) => {
    previewScale.value = Math.min(entry.contentRect.width / PAGE_WIDTH, 1)
  })
  observer.observe(previewBox.value)
})

onBeforeUnmount(() => {
  clearTimeout(previewTimer)
  observer?.disconnect()
})

async function save() {
  saving.value = true
  message.value = ''
  errorMessage.value = ''
  try {
    fill(await companyProfileApi.update({ ...form, ...web }))
    message.value = 'Đã lưu. Các phiếu in và website từ giờ dùng thông tin này.'
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Không lưu được thông tin công ty'
  } finally {
    saving.value = false
  }
}

async function uploadLogo(event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploading.value = true
  message.value = ''
  errorMessage.value = ''
  try {
    const data = new FormData()
    data.append('file', file)
    fill(await companyProfileApi.uploadLogo(data))
    message.value = 'Đã đổi logo.'
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Không tải được logo lên'
  } finally {
    uploading.value = false
    event.target.value = ''
  }
}
</script>

<template>
  <div class="font-lt flex flex-col flex-1 min-h-0">
    <div class="flex flex-col gap-5 lt-surface p-6 overflow-y-auto">
      <div class="flex flex-wrap items-end gap-4">
        <div class="flex flex-col gap-0.5">
          <h1 class="text-[19px] font-semibold tracking-[-0.2px] text-lt-ink dark:text-slate-100">Thông tin công ty</h1>
          <span class="text-[12.5px] text-lt-muted dark:text-slate-400">
            Phần đầu trang này in trên mọi phiếu, kể cả lưu trình đã lưu từ trước.
          </span>
        </div>
        <div class="flex-1" />
        <button
          v-if="can('update')"
          type="button"
          class="flex items-center gap-1.5 h-[38px] px-5 rounded-[11px] bg-lt-gradient text-white text-[13.5px] font-semibold shadow-lt-accent disabled:opacity-50"
          :disabled="saving || loading"
          @click="save"
        >
          <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />Lưu thay đổi
        </button>
      </div>

      <p v-if="message" class="px-4 py-2.5 rounded-xl bg-lt-done text-[12.5px] text-lt-doneink">{{ message }}</p>
      <p v-if="errorMessage" class="px-4 py-2.5 rounded-xl bg-lt-void text-[12.5px] text-lt-voidink">{{ errorMessage }}</p>

      <!-- Xem trước phần đầu trang: chính là tờ in thật, cắt lấy phần đầu -->
      <div class="flex flex-col gap-2">
        <span class="lt-label">Xem trước — đúng kích thước khi in</span>
        <div ref="previewBox" class="flex justify-center p-4 rounded-[14px] bg-lt-paper dark:bg-slate-900 overflow-hidden">
          <div
            class="bg-white overflow-hidden shadow-[0_2px_6px_rgba(13,42,45,.10)] shrink-0"
            :style="{ width: `${PAGE_WIDTH * previewScale}px`, height: `${LETTERHEAD_HEIGHT * previewScale}px` }"
          >
            <iframe
              v-if="previewHtml"
              :srcdoc="previewHtml"
              title="Xem trước phần đầu trang"
              class="border-0 bg-white"
              :style="{
                width: `${PAGE_WIDTH}px`,
                height: '1123px',
                transform: `scale(${previewScale})`,
                transformOrigin: 'top left',
              }"
            />
          </div>
        </div>
      </div>

      <div class="flex flex-col md:flex-row gap-6">
        <div class="flex flex-col gap-2 w-full md:w-[206px] md:shrink-0">
          <span class="lt-label">Logo</span>
          <div class="flex items-center gap-3.5 p-3 rounded-xl border border-dashed border-[#CFE0DC] dark:border-slate-600">
            <img v-if="logoUrl" :src="logoUrl" alt="Logo hiện tại" class="w-[84px] h-[46px] object-contain" />
            <div class="flex flex-col gap-1">
              <button
                v-if="can('update')"
                type="button"
                class="text-[12.5px] font-semibold text-lt-tealink text-left disabled:opacity-50"
                :disabled="uploading"
                @click="fileInput?.click()"
              >
                {{ uploading ? 'Đang tải lên…' : 'Đổi logo' }}
              </button>
              <span class="text-[11px] leading-[1.35] text-lt-faint dark:text-slate-500">PNG hoặc JPG,<br />tối đa 2MB</span>
            </div>
          </div>
          <input ref="fileInput" type="file" accept="image/png,image/jpeg" class="hidden" @change="uploadLogo" />
        </div>

        <div class="flex flex-col gap-3.5 flex-1 min-w-0">
          <div class="flex flex-wrap gap-3.5">
            <div class="flex flex-col gap-1.5 flex-1 min-w-[220px]">
              <label for="c-zh" class="lt-label">Tên công ty — tiếng Trung</label>
              <input id="c-zh" v-model="form.name_zh" type="text" class="lt-field" placeholder="越南大亮化工有限公司" />
            </div>
            <div class="flex flex-col gap-1.5 flex-1 min-w-[220px]">
              <label for="c-en" class="lt-label">Tên công ty — tiếng Anh</label>
              <input id="c-en" v-model="form.name_en" type="text" class="lt-field" placeholder="DALIANG CHEMICAL VIETNAM CO.,LTD" />
            </div>
          </div>

          <div class="flex flex-col gap-1.5">
            <label for="c-addr" class="lt-label">Địa chỉ — tiếng Trung</label>
            <input id="c-addr" v-model="form.address_zh" type="text" class="lt-field" placeholder="越南平陽省新淵縣帝國社帝國工業區 D2 路" />
          </div>

          <div class="flex flex-wrap gap-3.5">
            <div class="flex flex-col gap-1.5 flex-1 min-w-[200px]">
              <label for="c-tel" class="lt-label">Điện thoại</label>
              <input id="c-tel" v-model="form.phone" type="text" class="lt-field" placeholder="0650-3651005~09" />
            </div>
            <div class="flex flex-col gap-1.5 flex-1 min-w-[200px]">
              <label for="c-fax" class="lt-label">Fax</label>
              <input id="c-fax" v-model="form.fax" type="text" class="lt-field" placeholder="0650-3651010" />
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col gap-3.5 pt-5 border-t border-lt-divider dark:border-slate-700">
        <div class="flex flex-col gap-0.5">
          <span class="text-[15px] font-semibold text-lt-ink dark:text-slate-100">Website công khai</span>
          <span class="text-[12.5px] text-lt-muted dark:text-slate-400">
            Hiện ở mục Liên hệ và chân trang. Tên tiếng Anh/Trung, địa chỉ tiếng Trung và điện thoại dùng chung với phần trên.
          </span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          <div v-for="field in WEB_FIELDS" :key="field.key" class="flex flex-col gap-1.5 min-w-0" :class="{ 'md:col-span-3': field.wide }">
            <label :for="`w-${field.key}`" class="lt-label">{{ field.label }}</label>
            <input :id="`w-${field.key}`" v-model="web[field.key]" type="text" class="lt-field" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
