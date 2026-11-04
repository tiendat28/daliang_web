<!-- Chan trang. Ba cot link tro sang cac trang cua so do web (ban goc chi co
     neo #products/#about vi la trang don). -->
<script setup>
import { computed } from 'vue'
import { pagePath, siteStore, t, tr } from '../useSite'

const year = new Date().getFullYear()
const company = computed(() => siteStore.company)
</script>

<template>
  <footer>
    <div class="wrap">
      <div class="foot">
        <div>
          <router-link class="brand" :to="pagePath('home')">
            <span class="brand-mark"><img src="/images/logo-dlvc.png" alt="Daliang" /></span>
            <span class="brand-text"><b>DALIANG</b><span>{{ t('brandSub') }}</span></span>
          </router-link>
          <p>
            <span>{{ tr(company?.name) }}</span><br>
            <span>{{ tr(company?.address) }} · {{ t('ft.tax') }} {{ company?.tax_id }}</span>
          </p>
        </div>
        <div class="foot-col">
          <b>{{ t('nav.products') }}</b>
          <router-link :to="pagePath('products', { group: 'pre' })">{{ t('grp.pre') }}</router-link>
          <router-link :to="pagePath('products', { group: 'add' })">{{ t('grp.add') }}</router-link>
          <router-link :to="pagePath('products', { group: 'pas' })">{{ t('grp.pas') }}</router-link>
        </div>
        <div class="foot-col">
          <b>{{ t('ft.company') }}</b>
          <router-link :to="pagePath('about')">{{ t('nav.about') }}</router-link>
          <router-link :to="pagePath('certs')">{{ t('nav.certs') }}</router-link>
          <router-link :to="pagePath('services')">{{ t('nav.services') }}</router-link>
        </div>
        <div class="foot-col">
          <b>{{ t('ft.support') }}</b>
          <router-link :to="pagePath('docs')">{{ t('ft.msds') }}</router-link>
          <router-link :to="pagePath('contact')">{{ t('nav.contact') }}</router-link>
          <a href="#">{{ t('ft.privacy') }}</a>
        </div>
      </div>
      <div class="copy">© {{ year }} Daliang VN.</div>
    </div>
  </footer>
</template>
