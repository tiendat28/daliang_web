<!-- Khoi lien he: form ben trai, ban do + thong tin cong ty ben phai.
     Form gui thang vao bang contact_leads qua /api/v1/website/public/contact-leads. -->
<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { siteApi } from '../api'
import { mailHref, siteStore, t, telHref, tr } from '../useSite'

const route = useRoute()

const form = reactive({ name: '', company: '', phone: '', email: '', product: '', message: '' })
const note = ref('')
const noteError = ref(false)
const sending = ref(false)

const company = computed(() => siteStore.company)
const mapQuery = computed(() => (company.value?.map_query || '').trim())
const mapSrc = computed(() => {
  const hl = siteStore.lang === 'zh' ? 'zh-CN' : siteStore.lang
  return `https://maps.google.com/maps?q=${encodeURIComponent(mapQuery.value)}&hl=${hl}&z=15&output=embed`
})
const directionHref = computed(() =>
  mapQuery.value ? `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(mapQuery.value)}` : '#',
)

async function submit() {
  if (!form.name.trim() || !form.phone.trim()) {
    noteError.value = true
    note.value = t('f.err')
    return
  }
  sending.value = true
  noteError.value = false
  note.value = t('f.sending')
  try {
    await siteApi.createLead({
      ...form,
      lang: siteStore.lang,
      source_path: route.fullPath.slice(0, 255),
    })
    note.value = t('f.ok')
    Object.keys(form).forEach(key => { form[key] = '' })
  } catch {
    noteError.value = true
    note.value = t('f.fail')
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <div class="contact">
    <div class="contact-form">
      <div class="sec-title">
        <small>{{ t('ct.eyebrow') }}</small>
        <h2>{{ t('ct.title') }}</h2>
        <p>{{ t('ct.sub') }}</p>
      </div>
      <div class="quick">
        <a class="call" :href="telHref(company?.phone)"><svg class="icon"><use href="#i-phone"/></svg><span>{{ t('ct.call') }}</span></a>
        <a class="dir" :href="directionHref" target="_blank" rel="noopener"><svg class="icon"><use href="#i-nav"/></svg><span>{{ t('ct.dir') }}</span></a>
      </div>
      <form novalidate @submit.prevent="submit">
        <div class="field"><label for="f-name">{{ t('f.name') }}</label><input id="f-name" v-model="form.name" name="name" required autocomplete="name" :placeholder="t('f.ph.name')"></div>
        <div class="field"><label for="f-co">{{ t('f.co') }}</label><input id="f-co" v-model="form.company" name="company" autocomplete="organization" :placeholder="t('f.ph.co')"></div>
        <div class="field"><label for="f-phone">{{ t('f.phone') }}</label><input id="f-phone" v-model="form.phone" name="phone" type="tel" required autocomplete="tel" :placeholder="t('f.ph.phone')"></div>
        <div class="field"><label for="f-mail">Email</label><input id="f-mail" v-model="form.email" name="email" type="email" autocomplete="email" :placeholder="t('f.ph.mail')"></div>
        <div class="field full"><label for="f-prod">{{ t('f.prod') }}</label><input id="f-prod" v-model="form.product" name="product" :placeholder="t('f.ph.prod')"></div>
        <div class="field full"><label for="f-msg">{{ t('f.msg') }}</label><textarea id="f-msg" v-model="form.message" name="message" rows="4" :placeholder="t('f.ph.msg')"></textarea></div>
        <button class="btn btn-grad" type="submit" :disabled="sending">{{ t('f.send') }}</button>
        <div class="form-note" aria-live="polite" :style="noteError ? 'color:#b42318' : ''">{{ note }}</div>
      </form>
    </div>
    <div class="contact-side">
      <div class="map">
        <iframe v-if="mapQuery" :key="mapSrc" title="Google Maps" loading="lazy" referrerpolicy="no-referrer-when-downgrade" :src="mapSrc"></iframe>
        <div v-else class="ph" style="height:100%;border-radius:0">{{ t('map.ph') }}</div>
      </div>
      <div class="info">
        <div><svg class="icon"><use href="#i-pin"/></svg><div><small>{{ t('i.addr') }}</small><span>{{ tr(company?.address) }}</span></div></div>
        <div><svg class="icon"><use href="#i-phone"/></svg><div><small>Hotline</small><a :href="telHref(company?.phone)">{{ company?.phone }}</a></div></div>
        <div><svg class="icon"><use href="#i-mail"/></svg><div><small>Email</small><a :href="mailHref(company?.email)">{{ company?.email }}</a></div></div>
        <div><svg class="icon"><use href="#i-clock"/></svg><div><small>{{ t('i.hours') }}</small><span>{{ tr(company?.hours) }}</span></div></div>
      </div>
    </div>
  </div>
</template>
