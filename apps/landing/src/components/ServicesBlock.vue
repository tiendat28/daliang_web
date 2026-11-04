<!-- Bon the dich vu. Dung o trang chu va trang /dich-vu. -->
<script setup>
import { t } from '../useSite'

const SERVICES = [
  { icon: 'chart', title: 's1.t', desc: 's1.d' },
  { icon: 'flask', title: 's2.t', desc: 's2.d' },
  { icon: 'drop', title: 's3.t', desc: 's3.d' },
  { icon: 'truck', title: 's4.t', desc: 's4.d' },
]
</script>

<template>
  <div class="grid4">
    <div v-for="service in SERVICES" :key="service.icon" class="svc">
      <i><svg class="icon"><use :href="'#i-' + service.icon"/></svg></i>
      <h3>{{ t(service.title) }}</h3>
      <p>{{ t(service.desc) }}</p>
    </div>
  </div>
</template>
