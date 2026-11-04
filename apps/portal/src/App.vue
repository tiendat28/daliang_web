<script setup>
import { useRoute } from 'vue-router'
import AdminLayout from '@/core/layouts/AdminLayout.vue'
import GlobalToast from '@/core/components/GlobalToast.vue'

// Trang dang nhap / quen mat khau tu co khung (AuthLayout), khong sidebar
const route = useRoute()
</script>

<template>
  <GlobalToast />
  <router-view v-if="route.meta.layout === 'auth'" />
  <AdminLayout v-else>
    <router-view />
  </AdminLayout>
</template>
