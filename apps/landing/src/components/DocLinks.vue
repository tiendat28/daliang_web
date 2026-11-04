<!-- Cap link MSDS / TDS cua mot ma - lap o the san pham, trang chi tiet va
     trang tra cuu. File lay tu bang documents (xem api/public_site.py). -->
<script setup>
import { fileHref } from '../useSite'

defineProps({
  product: { type: Object, required: true },
  // Day cap link sang le phai (the san pham, ban goc dung lop .push)
  push: { type: Boolean, default: false },
})
</script>

<template>
  <a class="dl" :class="{ push }" :href="fileHref(product.msds_id)" target="_blank" rel="noopener"><svg class="icon"><use href="#i-download"/></svg>MSDS</a>
  <a class="dl" :href="fileHref(product.tds_id)" target="_blank" rel="noopener"><svg class="icon"><use href="#i-download"/></svg>TDS</a>
</template>
