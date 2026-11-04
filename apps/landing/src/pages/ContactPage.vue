<!-- /lien-he - /en/contact - /zh/contact -->
<script setup>
import ContactBlock from '../components/ContactBlock.vue'
import SitePage from '../components/SitePage.vue'
import { t } from '../useSite'
</script>

<template>
  <SitePage :title="t('page.contact.title')" :subtitle="t('page.contact.sub')" :crumbs="[{ label: t('nav.contact') }]">
    <section class="wrap sec sec-first">
      <ContactBlock />
    </section>
  </SitePage>
</template>
