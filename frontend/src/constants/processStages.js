// Công đoạn mạ của sản phẩm công ty — khớp enum ProcessStage ở backend.
export const PROCESS_STAGES = [
  { value: 'pre_treatment', label: 'Tiền xử lý' },
  { value: 'plating', label: 'Mạ' },
  { value: 'post_plating', label: 'Sau mạ' },
]

const LABELS = Object.fromEntries(PROCESS_STAGES.map(s => [s.value, s.label]))

export function processStageLabel(value) {
  return LABELS[value] ?? value ?? ''
}
