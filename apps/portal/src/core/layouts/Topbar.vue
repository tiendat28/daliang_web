<!-- Dau trang mac dinh cua moi trang (tieu de lay tu meta.title cua route). Trang can
     nut rieng tren dau trang thi dat meta.hideTopbar va tu dung PageHeader. -->
<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from './PageHeader.vue'
import { pageSearch } from '@/core/store/pageSearch'

// Doi trang thi xoa chu dang tim cua trang truoc
const route = useRoute()
watch(() => route.name, () => { pageSearch.query = '' })
</script>

<template>
  <PageHeader />
</template>
