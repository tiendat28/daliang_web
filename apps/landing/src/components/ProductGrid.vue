<!-- Luoi the san pham - dung o trang chu, trang /san-pham va muc "cung nhom"
     cua trang chi tiet. -->
<script setup>
import { productPath, t, tr } from '../useSite'
import DocLinks from './DocLinks.vue'

defineProps({
  products: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="grid3">
    <p v-if="!products.length" class="empty">{{ t('prod.empty') }}</p>
    <article v-for="product in products" :key="product.code" class="pcard">
      <div class="pcard-img"><img src="/images/logo-dlvc.png" alt="Daliang" /></div>
      <div class="pcard-meta">
        <span class="badge" :class="'b-' + product.group">{{ t('grp.' + product.group) }}</span>
        <span class="code">{{ product.code }}</span>
      </div>
      <h3>{{ tr(product.name) }}</h3>
      <p>{{ tr(product.desc) }}</p>
      <div class="pcard-links">
        <router-link :to="productPath(product)">{{ t('prod.detail') }} <svg class="icon"><use href="#i-arrow"/></svg></router-link>
        <DocLinks :product="product" push />
      </div>
    </article>
  </div>
</template>
