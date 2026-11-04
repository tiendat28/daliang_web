<!-- Khoi "Giay to & chung nhan": o tra cuu MSDS ben trai, the giay to ben phai.
     Giay to la file loai "Chung nhan" o trang Tai lieu cua app noi bo; chua tai
     len file nao thi hien bon the cho nhu ban thiet ke goc. -->
<script setup>
import { computed, ref } from 'vue'
import { siteApi } from '../api'
import { fileHref, siteStore, t, tr } from '../useSite'
import DocLinks from './DocLinks.vue'

const ICONS = ['file', 'shield', 'check', 'layers']

// Bon loai giay to ban goc de san - dong phu la cho can dien, khong dich
const PLACEHOLDERS = [
  { title: 'cert1.t', sub: '[Mã số doanh nghiệp]' },
  { title: 'cert2.t', sub: '[Số giấy — cơ quan cấp]' },
  { title: 'cert3.t', sub: '[ISO 9001 / ISO 14001 — nếu có]' },
  { title: 'cert4.t', sub: '[Tên phòng thử nghiệm, năm]' },
]

const cards = computed(() => {
  const list = siteStore.certificates.length
    ? siteStore.certificates.map(c => ({ key: c.id, title: c.title, sub: '', href: fileHref(c.id) }))
    : PLACEHOLDERS.map(p => ({ key: p.title, title: t(p.title), sub: p.sub, href: '#' }))
  return list.map((card, index) => ({ ...card, icon: ICONS[index % ICONS.length] }))
})

const code = ref('')
const result = ref(null)   // null = chua tra | { found: ket qua API, co the null = khong thay }

async function lookup() {
  const wanted = code.value.trim()
  if (!wanted) { result.value = null; return }
  try {
    result.value = { found: await siteApi.lookup(wanted) }
  } catch {
    result.value = { found: null }
  }
}
</script>

<template>
  <div class="certs">
    <div class="certs-side">
      <div class="sec-title">
        <small>{{ t('certs.eyebrow') }}</small>
        <h2>{{ t('certs.title') }}</h2>
      </div>
      <div class="lookup">
        <label for="msds-code">{{ t('certs.lookup') }}</label>
        <div class="lookup-row">
          <input id="msds-code" v-model="code" type="text" placeholder="VD: NI-534C" autocomplete="off" @keydown.enter="lookup">
          <button type="button" @click="lookup">{{ t('certs.find') }}</button>
        </div>
        <div class="lookup-result" aria-live="polite">
          <template v-if="result?.found">
            <b>{{ t('certs.found') }} {{ result.found.code }}<template v-if="result.found.name"> — {{ tr(result.found.name) }}</template></b><br>
            <span class="pcard-links lookup-links"><DocLinks :product="result.found" /></span>
          </template>
          <template v-else-if="result">{{ t('certs.notfound') }}</template>
        </div>
        <small>{{ t('certs.langs') }}</small>
      </div>
    </div>
    <div class="docs">
      <div v-for="card in cards" :key="card.key" class="doc">
        <div class="ph">[Ảnh giấy tờ]</div>
        <div class="doc-body">
          <svg class="icon"><use :href="'#i-' + card.icon"/></svg>
          <div><b>{{ card.title }}</b><span>{{ card.sub }}</span></div>
        </div>
        <a :href="card.href" target="_blank" rel="noopener"><svg class="icon"><use href="#i-eye"/></svg>{{ t('certs.view') }}</a>
      </div>
    </div>
  </div>
</template>
