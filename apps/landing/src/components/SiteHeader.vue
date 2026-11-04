<!-- Khoi dau trang mau xanh dam: thanh menu + menu dien thoai, roi den phan
     rieng cua tung trang (hero o trang chu, .page-head o cac trang con) do
     <slot> nhan vao. Giu dung cau truc .top > .wrap > nav cua ban goc. -->
<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LANGS } from '../i18n'
import { switchLangPath } from '../routes'
import { pagePath, siteStore, t } from '../useSite'

const route = useRoute()
const router = useRouter()
const menuOpen = ref(false)

// Cac muc menu, dung thu tu cua ban goc
const MENU = ['about', 'products', 'certs', 'services', 'contact']

function goLang(lang) {
  if (lang === siteStore.lang) return
  router.push(switchLangPath(route, lang))
}

// Doi trang thi dong menu dien thoai
watch(() => route.fullPath, () => { menuOpen.value = false })
</script>

<template>
  <header class="top">
    <div class="wrap">
      <nav class="nav" :aria-label="t('a11y.nav')">
        <router-link class="brand" :to="pagePath('home')" aria-label="Daliang VN">
          <span class="brand-mark"><img src="/images/logo-dlvc.png" alt="Daliang" /></span>
          <span class="brand-text"><b>DALIANG</b><span>{{ t('brandSub') }}</span></span>
        </router-link>
        <div class="menu">
          <router-link v-for="page in MENU" :key="page" :to="pagePath(page)">{{ t('nav.' + page) }}</router-link>
        </div>
        <div class="nav-right">
          <div class="lang" role="group" :aria-label="t('a11y.lang')">
            <button
              v-for="lang in LANGS" :key="lang" type="button"
              :aria-pressed="lang === siteStore.lang"
              @click="goLang(lang)"
            >{{ lang === 'zh' ? '中文' : lang.toUpperCase() }}</button>
          </div>
          <router-link class="btn btn-mint btn-sm" :to="pagePath('contact')">{{ t('nav.quote') }}</router-link>
          <button
            class="burger" type="button" :aria-label="t('a11y.menu')"
            :aria-expanded="menuOpen" aria-controls="mobile-menu"
            @click="menuOpen = !menuOpen"
          ><svg class="icon" style="width:20px;height:20px"><use href="#i-menu"/></svg></button>
        </div>
      </nav>
      <div class="mobile-menu" :class="{ open: menuOpen }" id="mobile-menu">
        <router-link v-for="page in MENU" :key="page" :to="pagePath(page)">{{ t('nav.' + page) }}</router-link>
      </div>

      <slot />
    </div>
  </header>
</template>
