<!-- Hinh ve day chuyen mau trong khung hero.
     Mau dung dich hoa chat tuoi sang, ruc ro:
     1. Tay dau: Xanh ngoc tuoi (Emerald Mint)
     2. Rua nuoc: Xanh nuoc bien tinh khiet (Sky Blue)
     3. Tay gi: Vang ho phach sang (Amber Gold)
     4. Hoat hoa: Tim thach anh hien dai (Electric Purple)
     5. Ma: Xanh ngoc xi ma sang bong (Electric Cyan)
     6. Thu dong: Xanh duong cong nghe (Ocean Cobalt) -->
<script setup>
import { computed } from 'vue'
import { t } from '../useSite'

const COLORS = ['#10b981', '#38bdf8', '#f59e0b', '#a855f7', '#06b6d4', '#3b82f6']

const tanks = computed(() =>
  t('tanks').map((name, index) => ({ name, x: 20 + index * 84, fill: COLORS[index] })),
)
</script>

<template>
  <svg viewBox="0 0 530 290" role="img" aria-label="Plating line">
    <template v-for="tank in tanks" :key="tank.name">
      <!-- Than be hoa chat: vien xanh nhat sang, nen trang trong suot -->
      <rect :x="tank.x" y="120" width="70" height="120" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <!-- Dung dich hoa chat ben trong: mau tuoi sang, co do trong suot tu nhien -->
      <rect :x="tank.x + 5" y="150" width="60" height="85" rx="5" :fill="tank.fill" opacity="0.85"/>
      <!-- Ten be hoa chat -->
      <text :x="tank.x + 35" y="266" text-anchor="middle" fill="#334155" font-size="12" font-weight="600">{{ tank.name }}</text>
    </template>
    <!-- Duong ray cau truc phia tren -->
    <path d="M10 70 H520" stroke="#cbd5e1" stroke-width="2"/>
    <!-- Xe con / cum cau nang: mau cyan hien dai -->
    <rect x="250" y="56" width="60" height="28" rx="6" fill="#0284c7"/>
    <!-- Day cap tha gio ma vao be -->
    <path d="M280 84 V140" stroke="#0284c7" stroke-width="2" stroke-dasharray="4 4"/>
    <!-- Gio dung chi tiet kim loai can ma -->
    <rect x="266" y="140" width="28" height="36" rx="4" fill="#ffffff" stroke="#0284c7" stroke-width="2"/>
  </svg>
</template>
