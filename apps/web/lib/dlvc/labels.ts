export const EMPLOYEE_STATUS_LABEL: Record<string, { label: string; variant: "ok" | "warn" | "danger" }> = {
  active: { label: "Đang làm", variant: "ok" },
  probation: { label: "Thử việc", variant: "warn" },
  on_leave: { label: "Nghỉ phép", variant: "warn" },
  terminated: { label: "Đã nghỉ", variant: "danger" },
};

export const GENDER_LABEL: Record<string, string> = {
  male: "Nam",
  female: "Nữ",
  other: "Khác",
};

export const DOCUMENT_STATUS_LABEL: Record<string, { label: string; variant: "ok" | "warn" | "danger" }> = {
  pending: { label: "Chờ duyệt", variant: "warn" },
  approved: { label: "Đã duyệt", variant: "ok" },
  rejected: { label: "Từ chối", variant: "danger" },
  expired: { label: "Hết hạn", variant: "danger" },
};

export const DOCUMENT_ACTION_LABEL: Record<string, string> = {
  uploaded: "đã tải lên",
  updated: "cập nhật",
  approved: "duyệt",
  rejected: "từ chối",
  deleted: "xoá",
};

export const INVOICE_STATUS_LABEL: Record<string, { label: string; variant: "ok" | "warn" | "danger" }> = {
  unpaid: { label: "Chưa thanh toán", variant: "warn" },
  paid: { label: "Đã thanh toán", variant: "ok" },
  overdue: { label: "Quá hạn", variant: "danger" },
  cancelled: { label: "Đã huỷ", variant: "danger" },
};
