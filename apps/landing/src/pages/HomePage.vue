<!-- Trang chu - dung 100% bo cuc cua ban thiet ke goc (landingpage.html):
     hero trong khoi xanh dam, roi 5 muc Gioi thieu / San pham / Chung nhan /
     Dich vu / Lien he. Bo loc san pham o day chay ngay tai trinh duyet (nut),
     con trang /san-pham moi tach moi nhom ra mot dia chi rieng. -->
<script setup>
import { computed, ref, watchEffect } from 'vue'
import AboutBlock from '../components/AboutBlock.vue'
import CertsBlock from '../components/CertsBlock.vue'
import ContactBlock from '../components/ContactBlock.vue'
import ProductGrid from '../components/ProductGrid.vue'
import ServicesBlock from '../components/ServicesBlock.vue'
import SiteHeader from '../components/SiteHeader.vue'
import TankDiagram from '../components/TankDiagram.vue'
import { GROUPS } from '../routes'
import { pagePath, setPageTitle, siteStore, t } from '../useSite'

const filter = ref('all')
const FILTERS = ['all', ...GROUPS]

const products = computed(() =>
  filter.value === 'all'
    ? siteStore.products
    : siteStore.products.filter(product => product.group === filter.value),
)

watchEffect(() => setPageTitle(''))
</script>

<template>
  <SiteHeader>
    <div class="hero" id="top">
      <div class="hero-copy">
        <span class="eyebrow">{{ t('hero.eyebrow') }}</span>
        <h1>{{ t('hero.h1') }}</h1>
        <p>{{ t('hero.lead') }}</p>
        <div class="hero-cta">
          <router-link class="btn btn-mint" :to="pagePath('products')"><span>{{ t('hero.cta1') }}</span><svg class="icon"><use href="#i-arrow"/></svg></router-link>
          <router-link class="btn btn-line" :to="pagePath('contact')">{{ t('hero.cta2') }}</router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="hero-visual-head">
          <span>{{ t('hero.visual') }}</span>
          <span style="font-size:12px;color:#0284c7;font-weight:600">[Có thể thay bằng ảnh thật]</span>
        </div>
        <TankDiagram />
        <div class="steps">
          <div><small>{{ t('step1') }}</small><span>{{ t('grp.pre') }}</span></div>
          <div><small>{{ t('step2') }}</small><span>{{ t('grp.add') }}</span></div>
          <div><small>{{ t('step3') }}</small><span>{{ t('grp.pas') }}</span></div>
        </div>
      </div>
    </div>
  </SiteHeader>

  <main>
    <section id="about" class="wrap sec">
      <AboutBlock />
    </section>

    <section id="products" class="wrap sec">
      <div class="products-head">
        <div class="sec-title">
          <small>{{ t('prod.eyebrow') }}</small>
          <h2>{{ t('prod.title') }}</h2>
        </div>
        <div class="filters" role="group" :aria-label="t('a11y.filter')">
          <button
            v-for="key in FILTERS" :key="key" type="button"
            :aria-pressed="filter === key" @click="filter = key"
          >{{ t('grp.' + key) }}</button>
        </div>
      </div>
      <ProductGrid :products="products" />
    </section>

    <section id="certs" class="wrap sec">
      <CertsBlock />
    </section>

    <section id="services" class="wrap sec">
      <div class="sec-title center">
        <small>{{ t('svc.eyebrow') }}</small>
        <h2>{{ t('svc.title') }}</h2>
        <p>{{ t('svc.sub') }}</p>
      </div>
      <ServicesBlock />
    </section>

    <section id="contact" class="wrap sec">
      <ContactBlock />
    </section>
  </main>
</template>
