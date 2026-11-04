<!-- Khung cua moi trang con (moi trang tru trang chu): khoi xanh dam co
     duong dan phan cap + tieu de, roi noi dung trang trong <main>.
     Tieu de tab trinh duyet cung dat o day, doi theo ngon ngu. -->
<script setup>
import { watchEffect } from 'vue'
import { pagePath, setPageTitle, t } from '../useSite'
import SiteHeader from './SiteHeader.vue'

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  // [{ label, page?, group? }] - muc khong co page thi chi in chu
  crumbs: { type: Array, default: () => [] },
})

watchEffect(() => setPageTitle(props.title))
</script>

<template>
  <SiteHeader>
    <div class="page-head">
      <div class="crumbs">
        <router-link :to="pagePath('home')">{{ t('crumb.home') }}</router-link>
        <template v-for="crumb in crumbs" :key="crumb.label">
          <svg class="icon"><use href="#i-arrow"/></svg>
          <router-link v-if="crumb.page" :to="pagePath(crumb.page, { group: crumb.group })">{{ crumb.label }}</router-link>
          <span v-else>{{ crumb.label }}</span>
        </template>
      </div>
      <h1>{{ title }}</h1>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
  </SiteHeader>

  <main>
    <slot />
  </main>
</template>
