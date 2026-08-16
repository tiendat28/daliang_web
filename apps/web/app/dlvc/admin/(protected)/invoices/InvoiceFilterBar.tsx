"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

const TYPE_OPTIONS = [
  { value: "", label: "Tất cả" },
  { value: "sale", label: "Hoá đơn bán" },
  { value: "purchase", label: "Hoá đơn mua" },
];

const STATUS_OPTIONS = [
  { value: "", label: "Tất cả trạng thái" },
  { value: "unpaid", label: "Chưa thanh toán" },
  { value: "paid", label: "Đã thanh toán" },
  { value: "overdue", label: "Quá hạn" },
  { value: "cancelled", label: "Đã huỷ" },
];

export default function InvoiceFilterBar() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const activeType = searchParams.get("type") ?? "";
  const activeStatus = searchParams.get("status") ?? "";

  function update(key: "type" | "status", value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set(key, value);
    else params.delete(key);
    const next = params.toString();
    router.replace(next ? `${pathname}?${next}` : pathname);
  }

  return (
    <div className="mb-4.5 flex flex-wrap items-center gap-2.5">
      {TYPE_OPTIONS.map((opt) => (
        <Chip key={opt.value} active={activeType === opt.value} onClick={() => update("type", opt.value)}>
          {opt.label}
        </Chip>
      ))}
      <span className="mx-1 h-5 w-px bg-dlvc-border" />
      {STATUS_OPTIONS.map((opt) => (
        <Chip key={opt.value} active={activeStatus === opt.value} onClick={() => update("status", opt.value)}>
          {opt.label}
        </Chip>
      ))}
    </div>
  );
}

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        active
          ? "rounded-lg bg-dlvc-sidebar px-3.25 py-1.75 text-[12.5px] font-medium text-white"
          : "rounded-lg border border-dlvc-border bg-dlvc-surface px-3.25 py-1.75 text-[12.5px] font-medium text-dlvc-ink-soft transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]"
      }
    >
      {children}
    </button>
  );
}
