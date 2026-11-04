<!-- /gioi-thieu - /en/about - /zh/about -->
<script setup>
import AboutBlock from '../components/AboutBlock.vue'
import ServicesBlock from '../components/ServicesBlock.vue'
import SitePage from '../components/SitePage.vue'
import { t } from '../useSite'
</script>

<template>
  <SitePage :title="t('page.about.title')" :subtitle="t('page.about.sub')" :crumbs="[{ label: t('nav.about') }]">
    <section class="wrap sec sec-first">
      <AboutBlock />
    </section>
    <section class="wrap sec sec-last">
      <div class="sec-title center">
        <small>{{ t('svc.eyebrow') }}</small>
        <h2>{{ t('svc.title') }}</h2>
        <p>{{ t('svc.sub') }}</p>
      </div>
      <ServicesBlock />
    </section>
  </SitePage>
</template>
