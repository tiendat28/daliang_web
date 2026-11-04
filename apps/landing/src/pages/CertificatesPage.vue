<!-- /chung-nhan - /en/certificates - /zh/certificates -->
<script setup>
import CertsBlock from '../components/CertsBlock.vue'
import SitePage from '../components/SitePage.vue'
import { t } from '../useSite'
</script>

<template>
  <SitePage :title="t('page.certs.title')" :subtitle="t('page.certs.sub')" :crumbs="[{ label: t('nav.certs') }]">
    <section class="wrap sec sec-first sec-last">
      <CertsBlock />
    </section>
  </SitePage>
</template>
