<!-- Khung chung cua website: bo icon, trang dang xem, chan trang.
     Ngon ngu lay tu route (meta.lang); noi dung goi API dung mot lan. -->
<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import FloatingContact from './components/FloatingContact.vue'
import SiteFooter from './components/SiteFooter.vue'
import SiteIconSprite from './components/SiteIconSprite.vue'
import { loadSite, setLang } from './useSite'

const route = useRoute()

watch(() => route.meta.lang, setLang, { immediate: true })
onMounted(loadSite)
</script>

<template>
  <SiteIconSprite />
  <router-view />
  <SiteFooter />
  <FloatingContact />
</template>
