<!-- /san-pham/:nhom/:ma - chi tiet mot ma hang. Ban thiet ke goc khong ve
     trang nay nen bo cuc dung cac lop o muc "Phan them" cua site.css.
     Thong so van hanh la cac "che do su dung" cua danh muc noi bo (tieng Viet). -->
<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DocLinks from '../components/DocLinks.vue'
import ProductGrid from '../components/ProductGrid.vue'
import SitePage from '../components/SitePage.vue'
import { findProduct, pagePath, siteStore, t, tr } from '../useSite'

const route = useRoute()

const product = computed(() => findProduct(route.params.code))

const title = computed(() => {
  if (product.value) return tr(product.value.name)
  return siteStore.loading ? t('loading') : t('detail.notfound')
})

const crumbs = computed(() => {
  const rows = [{ label: t('nav.products'), page: 'products' }]
  if (product.value) {
    const { group, code } = product.value
    rows.push({ label: t('grp.' + group), page: 'products', group }, { label: code })
  }
  return rows
})

const related = computed(() => siteStore.products
  .filter(p => p.group === product.value?.group && p.code !== product.value.code)
  .slice(0, 3))
</script>

<template>
  <SitePage :title="title" :subtitle="product?.code" :crumbs="crumbs">
    <section class="wrap sec sec-first sec-last">
      <p v-if="!product" class="empty">{{ siteStore.loading ? t('loading') : t('detail.notfound') }}</p>

      <template v-else>
        <div class="detail">
          <div class="detail-main">
            <router-link class="back" :to="pagePath('products', { group: product.group })">
              <svg class="icon"><use href="#i-arrow"/></svg>{{ t('detail.back') }}
            </router-link>
            <p class="detail-lead">{{ tr(product.desc) }}</p>
            <div class="spec">
              <div class="spec-row"><b>{{ t('detail.code') }}</b><span class="code">{{ product.code }}</span></div>
              <div class="spec-row"><b>{{ t('detail.group') }}</b><span>{{ t('grp.' + product.group) }}</span></div>
              <div v-if="product.materials" class="spec-row"><b>{{ t('detail.materials') }}</b><span>{{ product.materials }}</span></div>
            </div>
            <template v-if="product.modes.length">
              <h3 class="detail-sub">{{ t('detail.spec') }}</h3>
              <div class="spec">
                <div v-for="mode in product.modes" :key="mode.name" class="spec-row">
                  <b>{{ mode.name }}</b>
                  <ul class="spec-params"><li v-for="param in mode.params" :key="param">{{ param }}</li></ul>
                </div>
              </div>
            </template>
          </div>
          <div class="detail-side">
            <div class="detail-art"><img src="/images/logo-dlvc.png" alt="Daliang" /></div>
            <div class="detail-box">
              <b>{{ t('detail.docs') }}</b>
              <div class="pcard-links detail-links"><DocLinks :product="product" /></div>
            </div>
            <div class="detail-box">
              <b>{{ t('detail.cta') }}</b>
              <p>{{ t('detail.ctaText') }}</p>
              <router-link class="btn btn-grad" :to="pagePath('contact')">{{ t('detail.ask') }}</router-link>
            </div>
          </div>
        </div>

        <div v-if="related.length" class="related">
          <div class="sec-title">
            <small>{{ t('prod.eyebrow') }}</small>
            <h2>{{ t('detail.related') }}</h2>
          </div>
          <ProductGrid :products="related" />
        </div>
      </template>
    </section>
  </SitePage>
</template>
