<script setup>
import { ref, computed } from 'vue'
import { Copy, GripVertical, X, History, ChevronRight } from 'lucide-vue-next'
import SuggestInput from './SuggestInput.vue'
import ChemicalField from './ChemicalField.vue'
import { TIME_UNITS, TEMP_MODES, CONCENTRATION_UNITS } from '../../constants/testProcess'
import { formatConcentration, stripHtml } from '../../utils/testProcessFormat'

// Một bước đang mở để sửa. `step` là phần tử của mảng bước bên view cha nên sửa
// thẳng vào thuộc tính của nó (không gán lại cả object).
const props = defineProps({
  step: { type: Object, required: true },
  index: { type: Number, required: true },
  products: { type: Array, default: () => [] },
  labChemicals: { type: Array, default: () => [] },
  operationOptions: { type: Array, default: () => [] },
  fillingLast: { type: Boolean, default: false },
})

const emit = defineEmits(['remove', 'duplicate', 'fill-last'])

// Id riêng cho từng ô nhập, để <label for> và <datalist> không đụng nhau giữa các bước
const uid = `step-${Math.random().toString(36).slice(2, 9)}`

const showPrintOverrides = ref(
  Boolean(props.step.time_text || props.step.temp_text || props.step.ph_text || props.step.note),
)

const concentrations = computed(() => props.step.concentrations)

function addConcentration() {
  props.step.concentrations.push({ component: '', value_min: null, value_max: null, unit: 'g/l', text_override: null })
}

function removeConcentration(index) {
  props.step.concentrations.splice(index, 1)
}

function setTempMode(mode) {
  props.step.temp_mode = mode
  if (mode !== 'range') {
    props.step.temp_min = null
    props.step.temp_max = null
  }
}

/** Chữ sẽ in ra cho một dòng nồng độ — để người nhập thấy ngay kết quả. */
function concentrationHint(row) {
  return formatConcentration(row)
}
</script>

<template>
  <div class="flex flex-col gap-3.5 p-3.5 rounded-[14px] border border-lt-focus dark:border-slate-600 bg-white dark:bg-slate-800 shadow-[0_0_0_3px_rgba(23,191,168,.10)]">
    <!-- Hạng mục -->
    <div class="flex items-center gap-2.5">
      <GripVertical class="w-3.5 h-3.5 text-[#B9C9C7] shrink-0 cursor-grab" />
      <span class="flex items-center justify-center w-[22px] h-[22px] shrink-0 rounded-[7px] bg-lt-gradient text-[12px] font-semibold text-white">
        {{ index + 1 }}
      </span>
      <SuggestInput
        v-model="step.operation"
        :options="operationOptions"
        :input-id="`${uid}-operation`"
        placeholder="Hạng mục, ví dụ Mạ kẽm kiềm"
        input-class="h-9 flex-1"
        class="flex-1 min-w-0"
      />
      <button
        type="button"
        class="flex items-center gap-1 px-2 h-7 rounded-lg text-[12px] font-medium text-lt-tealink hover:bg-lt-wash dark:hover:bg-slate-700 disabled:opacity-50 shrink-0"
        :disabled="fillingLast || !step.operation"
        title="Lấy thông số của lần gần nhất dùng hạng mục này"
        @click="emit('fill-last')"
      >
        <History class="w-[15px] h-[15px]" />
        <span class="hidden lg:inline">Điền theo lần gần nhất</span>
      </button>
      <button
        type="button"
        class="w-7 h-7 flex items-center justify-center rounded-lg text-lt-muted hover:bg-lt-wash dark:hover:bg-slate-700 shrink-0"
        :aria-label="`Nhân bản bước ${index + 1}`"
        @click="emit('duplicate')"
      >
        <Copy class="w-[15px] h-[15px]" />
      </button>
      <button
        type="button"
        class="w-7 h-7 flex items-center justify-center rounded-lg text-lt-voidink hover:bg-lt-void/60 shrink-0"
        :aria-label="`Xóa bước ${index + 1}`"
        @click="emit('remove')"
      >
        <X class="w-[15px] h-[15px]" />
      </button>
    </div>

    <!-- Thời gian + pH -->
    <div class="flex flex-wrap gap-3.5">
      <div class="flex flex-col gap-1.5">
        <label :for="`${uid}-time-min`" class="lt-label">Thời gian</label>
        <div class="flex items-center gap-1.5">
          <input :id="`${uid}-time-min`" v-model.number="step.time_min" type="number" step="any" class="lt-num w-14" />
          <span class="text-lt-hint">–</span>
          <input v-model.number="step.time_max" type="number" step="any" aria-label="Thời gian tối đa" class="lt-num w-14" />
          <select v-model="step.time_unit" aria-label="Đơn vị thời gian" class="lt-num w-[88px] px-2 text-left">
            <option :value="null">—</option>
            <option v-for="unit in TIME_UNITS" :key="unit.value" :value="unit.value">{{ unit.label }}</option>
          </select>
        </div>
      </div>

      <div class="flex flex-col gap-1.5">
        <label :for="`${uid}-ph-min`" class="lt-label">pH</label>
        <div class="flex items-center gap-1.5">
          <input :id="`${uid}-ph-min`" v-model.number="step.ph_min" type="number" step="any" min="0" max="14" class="lt-num w-[52px]" />
          <span class="text-lt-hint">–</span>
          <input v-model.number="step.ph_max" type="number" step="any" min="0" max="14" aria-label="pH tối đa" class="lt-num w-[52px]" />
        </div>
      </div>
    </div>

    <!-- Nhiệt độ -->
    <div class="flex flex-col gap-1.5">
      <span class="lt-label">Nhiệt độ</span>
      <div class="flex flex-wrap items-center gap-2">
        <div class="flex p-[3px] rounded-[9px] bg-lt-paper dark:bg-slate-700">
          <button
            v-for="mode in TEMP_MODES"
            :key="mode.value"
            type="button"
            :aria-pressed="step.temp_mode === mode.value"
            class="px-2.5 py-[5px] rounded-[7px] text-[12.5px]"
            :class="step.temp_mode === mode.value
              ? 'bg-white dark:bg-slate-800 font-semibold text-lt-tealink shadow-sm'
              : 'text-lt-muted dark:text-slate-300'"
            @click="setTempMode(mode.value)"
          >
            {{ mode.label }}
          </button>
        </div>
        <template v-if="step.temp_mode === 'range'">
          <input v-model.number="step.temp_min" type="number" step="any" aria-label="Nhiệt độ tối thiểu" class="lt-num w-[50px]" />
          <span class="text-lt-hint">–</span>
          <input v-model.number="step.temp_max" type="number" step="any" aria-label="Nhiệt độ tối đa" class="lt-num w-[50px]" />
          <span class="text-[13px] text-lt-label dark:text-slate-300">°C</span>
        </template>
      </div>
    </div>

    <!-- Nồng độ -->
    <div class="flex flex-col gap-2">
      <span class="lt-label">Nồng độ</span>
      <div v-for="(row, rowIndex) in concentrations" :key="rowIndex" class="flex flex-wrap items-center gap-1.5">
        <input
          v-model="row.component"
          type="text"
          :aria-label="`Thành phần dòng ${rowIndex + 1}`"
          placeholder="Zn^2+"
          class="lt-num w-[120px] text-left"
        />
        <input v-model.number="row.value_min" type="number" step="any" :aria-label="`Giá trị đầu dòng ${rowIndex + 1}`" class="lt-num w-[62px]" />
        <span class="text-lt-hint">–</span>
        <input v-model.number="row.value_max" type="number" step="any" :aria-label="`Giá trị cuối dòng ${rowIndex + 1}`" class="lt-num w-[62px]" />
        <input
          v-model="row.unit"
          type="text"
          :list="`${uid}-units`"
          :aria-label="`Đơn vị dòng ${rowIndex + 1}`"
          placeholder="g/l"
          class="lt-num w-[74px]"
        />
        <span class="flex-1 min-w-[120px] text-[12.5px] text-lt-faint dark:text-slate-500 truncate" :title="stripHtml(concentrationHint(row))">
          in ra: <span v-html="concentrationHint(row)" />
        </span>
        <button
          type="button"
          class="w-7 h-7 flex items-center justify-center rounded-lg text-lt-muted hover:bg-lt-wash dark:hover:bg-slate-700 shrink-0"
          :aria-label="`Xóa dòng nồng độ ${rowIndex + 1}`"
          @click="removeConcentration(rowIndex)"
        >
          <X class="w-[15px] h-[15px]" />
        </button>
      </div>
      <datalist :id="`${uid}-units`">
        <option v-for="unit in CONCENTRATION_UNITS" :key="unit" :value="unit" />
      </datalist>
      <button
        type="button"
        class="self-start py-1 text-[12.5px] font-semibold text-lt-tealink"
        @click="addConcentration"
      >
        + Thêm dòng nồng độ
      </button>
    </div>

    <!-- Hóa chất -->
    <div class="flex flex-col gap-1.5">
      <label :for="`${uid}-chemicals`" class="lt-label">Hóa chất</label>
      <ChemicalField
        v-model="step.chemicals"
        :products="products"
        :lab-chemicals="labChemicals"
        :input-id="`${uid}-chemicals`"
      />
    </div>

    <!-- Chữ in tùy chỉnh + ghi chú -->
    <button
      type="button"
      class="flex items-center gap-1.5 self-start text-[12.5px] font-medium text-lt-muted dark:text-slate-400"
      @click="showPrintOverrides = !showPrintOverrides"
    >
      <ChevronRight class="w-3.5 h-3.5 transition-transform" :class="showPrintOverrides ? 'rotate-90' : ''" />
      Tùy chỉnh chữ in cho bước này
    </button>

    <div v-if="showPrintOverrides" class="flex flex-col gap-3 p-3 rounded-xl bg-lt-card dark:bg-slate-700/40 border border-lt-soft dark:border-slate-600">
      <p class="text-[12px] leading-[1.45] text-lt-faint dark:text-slate-400">
        Điền vào đây thì phiếu in nguyên văn ô này, bỏ qua các ô số ở trên. Dùng cho
        trường hợp đặc biệt như “2 lần × 3 phút”.
      </p>
      <div class="flex flex-wrap gap-3">
        <div class="flex flex-col gap-1.5 flex-1 min-w-[160px]">
          <label :for="`${uid}-time-text`" class="lt-label">Chữ in — Thời gian</label>
          <input :id="`${uid}-time-text`" v-model="step.time_text" type="text" class="lt-field" />
        </div>
        <div class="flex flex-col gap-1.5 flex-1 min-w-[160px]">
          <label :for="`${uid}-temp-text`" class="lt-label">Chữ in — Nhiệt độ</label>
          <input :id="`${uid}-temp-text`" v-model="step.temp_text" type="text" class="lt-field" />
        </div>
        <div class="flex flex-col gap-1.5 flex-1 min-w-[160px]">
          <label :for="`${uid}-ph-text`" class="lt-label">Chữ in — pH</label>
          <input :id="`${uid}-ph-text`" v-model="step.ph_text" type="text" class="lt-field" />
        </div>
      </div>
      <div class="flex flex-col gap-1.5">
        <label :for="`${uid}-note`" class="lt-label">
          Ghi chú bước <span class="font-normal text-lt-faint">— không in lên phiếu</span>
        </label>
        <input :id="`${uid}-note`" v-model="step.note" type="text" class="lt-field" />
      </div>
    </div>
  </div>
</template>
