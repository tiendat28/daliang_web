<!-- 10 ma du phong 2FA - chi hien mot lan, nhac nguoi dung luu lai. -->
<script setup>
import { ref } from 'vue'
import { Copy, Download } from 'lucide-vue-next'

const props = defineProps({ codes: { type: Array, required: true } })
const copied = ref(false)

async function copy() {
  await navigator.clipboard.writeText(props.codes.join('\n'))
  copied.value = true
}

function download() {
  const blob = new Blob([`Mã dự phòng 2FA - Daliang VN\n\n${props.codes.join('\n')}\n`], { type: 'text/plain' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'ma-du-phong-daliang.txt'
  link.click()
  URL.revokeObjectURL(link.href)
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <p class="m-0 text-sm leading-[1.55] text-dl-body dark:text-slate-300">
      Lưu các mã này ở nơi an toàn. Mất điện thoại thì dùng <b>một</b> mã để đăng nhập thay mã 6 số —
      mỗi mã chỉ dùng được một lần. Mã chỉ hiện <b>lần này</b>.
    </p>
    <div class="grid grid-cols-2 gap-2 rounded-[14px] border border-dl-line bg-dl-panel p-3 font-mono text-sm text-dl-body dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
      <span v-for="code in codes" :key="code" class="text-center">{{ code }}</span>
    </div>
    <div class="flex gap-2">
      <button type="button" class="dl-btn-line flex-1" @click="copy">
        <Copy class="w-4 h-4" /> {{ copied ? 'Đã chép' : 'Chép' }}
      </button>
      <button type="button" class="dl-btn-line flex-1" @click="download">
        <Download class="w-4 h-4" /> Tải file
      </button>
    </div>
  </div>
</template>
