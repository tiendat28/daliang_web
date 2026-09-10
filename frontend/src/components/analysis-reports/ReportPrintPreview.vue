<script setup>
import { Printer } from 'lucide-vue-next'
import { formatFormula } from '../../utils/chemFormula'
import { formatDate } from '../../utils/format'

defineProps({
  report: { type: Object, required: true },
  customerName: { type: String, default: '' },
})

function printReport() {
  window.print()
}
</script>

<template>
  <div>
    <div id="print-report" class="bg-white text-black p-6" style="font-family: 'Times New Roman', Georgia, serif;">
      <table class="w-full border-collapse border-2 border-black text-sm" style="table-layout: fixed;">
        <colgroup>
          <col style="width: 20%" />
          <col style="width: 18%" />
          <col style="width: 27%" />
          <col style="width: 35%" />
        </colgroup>
        <tbody>
          <tr>
            <td class="border border-black text-center align-middle p-2" rowspan="2">
              <img src="/images/logo-dlvc.png" alt="DLVC" class="w-24 h-auto mx-auto" />
            </td>
            <td class="border border-black text-center p-2" colspan="3">
              <p>越南大亮化工有限公司</p>
              <p class="font-bold">DALIANG CHEMICAL VIETNAM CO.,LTD</p>
            </td>
          </tr>
          <tr>
            <td class="border border-black text-center p-3 text-xl font-bold tracking-wide" colspan="3">BÁO CÁO KẾT QUẢ PHÂN TÍCH</td>
          </tr>

          <tr>
            <td class="border border-black p-2 whitespace-nowrap">Tên khách hàng:</td>
            <td class="border border-black p-2 text-center font-bold" colspan="3">{{ customerName }}</td>
          </tr>
          <tr>
            <td class="border border-black p-2 whitespace-nowrap">Ngày nhận mẫu:</td>
            <td class="border border-black p-2 text-center" colspan="3">{{ formatDate(report.sample_receive_date) }}</td>
          </tr>
          <tr>
            <td class="border border-black p-2 whitespace-nowrap">Ngày phân tích:</td>
            <td class="border border-black p-2 text-center" colspan="3">{{ formatDate(report.issue_date) }}</td>
          </tr>

          <tr class="font-bold text-center">
            <td class="border border-black p-2">Mẫu phân tích</td>
            <td class="border border-black p-2">Thành phần</td>
            <td class="border border-black p-2">Kết quả phân tích</td>
            <td class="border border-black p-2">Ghi chú</td>
          </tr>

          <template v-for="s in report.samples" :key="s.id">
            <tr v-for="(c, ci) in (s.components.length ? s.components : [{ id: `${s.id}-empty`, name: '', result: '', note: '' }])" :key="c.id">
              <td v-if="ci === 0" class="border border-black p-2 text-center font-bold align-middle" :rowspan="s.components.length || 1">{{ s.name }}</td>
              <td class="border border-black p-2 text-center">{{ formatFormula(c.name) }}</td>
              <td class="border border-black p-2 text-center">{{ c.result }}</td>
              <td class="border border-black p-2 text-center">{{ c.note }}</td>
            </tr>
          </template>
        </tbody>
      </table>

      <p v-if="report.note" class="mt-4 text-sm">Ghi chú: {{ report.note }}</p>

      <div class="flex justify-between text-center mt-10 px-10">
        <div>
          <p class="italic">Nhân viên hóa nghiệm</p>
          <p v-for="(name, i) in report.completed_by" :key="i" class="font-bold" :class="i === 0 ? 'mt-8' : 'mt-1'">{{ name }}</p>
        </div>
        <div>
          <p class="italic">Người duyệt</p>
          <p class="font-bold mt-8">{{ report.approved_by || '' }}</p>
        </div>
      </div>
    </div>

    <div class="flex justify-end mt-4 print:hidden">
      <button type="button" class="flex items-center gap-1 px-4 py-2 rounded-xl bg-brand-gradient text-white text-sm" @click="printReport">
        <Printer class="w-4 h-4" /> In báo cáo
      </button>
    </div>
  </div>
</template>
