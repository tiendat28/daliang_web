<script setup>
const props = defineProps({
  fields: { type: Array, required: true },
  modelValue: { type: Object, required: true },
})
const emit = defineEmits(['update:modelValue', 'submit'])

function updateField(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}
</script>

<template>
  <form class="grid grid-cols-2 gap-x-4 gap-y-4" @submit.prevent="emit('submit')">
    <div v-for="field in fields" :key="field.key" :class="field.full || field.type === 'textarea' ? 'col-span-2' : ''">
      <label class="field-label mb-1">{{ field.label }}</label>

      <select
        v-if="field.type === 'select'"
        :value="modelValue[field.key]"
        class="w-full field-input focus:outline-none focus:ring-2 focus:ring-brand-400"
        @change="updateField(field.key, $event.target.value)"
      >
        <option value="" disabled>-- Chọn --</option>
        <option v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>

      <textarea
        v-else-if="field.type === 'textarea'"
        :value="modelValue[field.key]"
        rows="3"
        class="w-full field-input focus:outline-none focus:ring-2 focus:ring-brand-400"
        @input="updateField(field.key, $event.target.value)"
      />

      <input
        v-else
        :type="field.type || 'text'"
        :value="modelValue[field.key]"
        class="w-full field-input focus:outline-none focus:ring-2 focus:ring-brand-400"
        @input="updateField(field.key, field.type === 'number' ? Number($event.target.value) : $event.target.value)"
      />
    </div>

    <div class="col-span-2 flex justify-end gap-2 pt-2">
      <slot name="actions" />
    </div>
  </form>
</template>
