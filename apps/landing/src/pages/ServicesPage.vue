<!-- /dich-vu - /en/services - /zh/services -->
<script setup>
import ContactBlock from '../components/ContactBlock.vue'
import ServicesBlock from '../components/ServicesBlock.vue'
import SitePage from '../components/SitePage.vue'
import { t } from '../useSite'
</script>

<template>
  <SitePage :title="t('page.services.title')" :subtitle="t('page.services.sub')" :crumbs="[{ label: t('nav.services') }]">
    <section class="wrap sec sec-first">
      <div class="sec-title">
        <small>{{ t('svc.eyebrow') }}</small>
        <h2>{{ t('svc.title') }}</h2>
        <p>{{ t('svc.sub') }}</p>
      </div>
      <ServicesBlock />
    </section>
    <section class="wrap sec">
      <ContactBlock />
    </section>
  </SitePage>
</template>
