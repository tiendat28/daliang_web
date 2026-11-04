<!-- /san-pham va /san-pham/:nhom (cung /en/products/:group, /zh/products/:group).
     Khac trang chu: moi nhom co dia chi rieng nen bo loc la link chu khong
     phai nut - nhin van y het (.filters a dung chung kieu voi button). -->
<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ProductGrid from '../components/ProductGrid.vue'
import SitePage from '../components/SitePage.vue'
import { GROUPS, groupFromSlug } from '../routes'
import { pagePath, siteStore, t } from '../useSite'

const route = useRoute()

// Khong co slug = "Tat ca"; slug la khong khop nhom nao -> luoi rong
const group = computed(() => (route.params.group ? groupFromSlug(siteStore.lang, route.params.group) : null))
const products = computed(() => {
  if (!route.params.group) return siteStore.products
  return siteStore.products.filter(p => p.group === group.value)
})

const title = computed(() => (group.value ? t('grp.' + group.value) : t('page.products.title')))
const crumbs = computed(() => (group.value
  ? [{ label: t('nav.products'), page: 'products' }, { label: title.value }]
  : [{ label: t('nav.products') }]))
</script>

<template>
  <SitePage :title="title" :subtitle="t('page.products.sub')" :crumbs="crumbs">
    <section class="wrap sec sec-first sec-last">
      <div class="products-head">
        <div class="sec-title">
          <small>{{ t('prod.eyebrow') }}</small>
          <h2>{{ t('prod.title') }}</h2>
        </div>
        <div class="filters" role="group" :aria-label="t('a11y.filter')">
          <router-link :to="pagePath('products')" :aria-pressed="!route.params.group">{{ t('grp.all') }}</router-link>
          <router-link
            v-for="key in GROUPS" :key="key"
            :to="pagePath('products', { group: key })" :aria-pressed="group === key"
          >{{ t('grp.' + key) }}</router-link>
        </div>
      </div>
      <p v-if="siteStore.loading" class="empty">{{ t('loading') }}</p>
      <ProductGrid v-else :products="products" />
    </section>
  </SitePage>
</template>
