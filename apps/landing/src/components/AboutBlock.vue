<!-- Khoi "Ve Daliang VN": anh ben trai, ba gia tri ben phai. Dung o trang chu
     va trang /gioi-thieu. -->
<script setup>
import { t } from '../useSite'

const VALUES = [
  { icon: 'flask', title: 'v1.t', desc: 'v1.d' },
  { icon: 'tool', title: 'v2.t', desc: 'v2.d' },
  { icon: 'file', title: 'v3.t', desc: 'v3.d' },
]
</script>

<template>
  <div class="about">
    <div class="ph">[Ảnh nhà máy / phòng thí nghiệm]</div>
    <div class="about-body">
      <div class="sec-title">
        <small>{{ t('about.eyebrow') }}</small>
        <h2>{{ t('about.title') }}</h2>
        <p>{{ t('about.text') }}</p>
      </div>
      <div class="values">
        <div v-for="value in VALUES" :key="value.icon" class="value">
          <i><svg class="icon"><use :href="'#i-' + value.icon"/></svg></i>
          <div><b>{{ t(value.title) }}</b><span>{{ t(value.desc) }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>
