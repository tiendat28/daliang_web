"use client";

import { useActionState } from "react";
import type { InvoiceFormState } from "../actions";

const inputClass =
  "h-10 w-full rounded-[9px] border border-dlvc-border bg-dlvc-bg px-3 text-[13.5px] text-dlvc-ink transition-[border-color,box-shadow] duration-150 focus:border-dlvc-accent focus:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] focus:outline-none";
const labelClass = "flex flex-col gap-1.5 text-[12.5px] font-medium text-dlvc-ink-soft";

export default function RecordPaymentForm({
  action,
  remainingAmount,
}: {
  action: (state: InvoiceFormState, formData: FormData) => Promise<InvoiceFormState>;
  remainingAmount: number;
}) {
  const [state, formAction, pending] = useActionState<InvoiceFormState, FormData>(action, undefined);

  return (
    <form action={formAction} className="flex flex-col gap-3.5">
      <div className="grid grid-cols-1 gap-3.5 min-[480px]:grid-cols-2">
        <label className={labelClass}>
          Số tiền (còn lại: {remainingAmount.toLocaleString("vi-VN")} ₫)
          <input type="number" name="amount" min={1} step={1} required defaultValue={remainingAmount} className={inputClass} />
        </label>
        <label className={labelClass}>
          Ngày thanh toán
          <input type="date" name="paymentDate" required defaultValue={new Date().toISOString().slice(0, 10)} className={inputClass} />
        </label>
        <label className={labelClass}>
          Phương thức
          <select name="method" defaultValue="bank_transfer" className={inputClass}>
            <option value="bank_transfer">Chuyển khoản</option>
            <option value="cash">Tiền mặt</option>
            <option value="card">Thẻ</option>
          </select>
        </label>
      </div>

      {state?.error ? (
        <p className="rounded-lg border border-dlvc-danger/30 bg-dlvc-danger/10 px-3.5 py-2.5 text-[13px] font-medium text-dlvc-danger">
          {state.error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={pending}
        className="flex h-10 w-fit items-center gap-1.5 rounded-[9px] bg-dlvc-sidebar px-4 text-[13.5px] font-semibold text-white transition-[filter,box-shadow,transform] duration-150 hover:not-disabled:-translate-y-px hover:not-disabled:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] hover:not-disabled:brightness-125 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {pending ? "Đang ghi nhận…" : "Ghi nhận thanh toán"}
      </button>
    </form>
  );
}
