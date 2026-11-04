<!-- /tai-lieu - /en/documents - /zh/documents
     Tra cuu MSDS/TDS theo ma, kem tai lieu cua cac ma dang len web. -->
<script setup>
import CertsBlock from '../components/CertsBlock.vue'
import DocLinks from '../components/DocLinks.vue'
import SitePage from '../components/SitePage.vue'
import { productPath, siteStore, t, tr } from '../useSite'
</script>

<template>
  <SitePage :title="t('page.docs.title')" :subtitle="t('page.docs.sub')" :crumbs="[{ label: t('ft.msds') }]">
    <section class="wrap sec sec-first">
      <CertsBlock />
    </section>

    <section class="wrap sec sec-last">
      <div class="sec-title">
        <small>{{ t('nav.products') }}</small>
        <h2>{{ t('docs.all') }}</h2>
        <p>{{ t('docs.note') }}</p>
      </div>
      <div class="doc-list">
        <div v-for="product in siteStore.products" :key="product.code" class="doc-item">
          <svg class="icon"><use href="#i-file"/></svg>
          <div>
            <b>{{ tr(product.name) }}</b>
            <span>{{ t('grp.' + product.group) }} · <span class="code">{{ product.code }}</span></span>
            <div class="pcard-links doc-item-links">
              <DocLinks :product="product" />
              <router-link class="push" :to="productPath(product)">{{ t('prod.detail') }} <svg class="icon"><use href="#i-arrow"/></svg></router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </SitePage>
</template>
