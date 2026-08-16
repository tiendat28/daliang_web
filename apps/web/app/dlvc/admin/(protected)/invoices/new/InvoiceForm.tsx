"use client";

import { useActionState, useState } from "react";
import Link from "next/link";
import type { InvoiceFormState } from "../actions";

type Partner = { id: number; partnerName: string; partnerCode: string };
type LineItem = { itemName: string; unit: string; quantity: number; unitPrice: number };

const inputClass =
  "h-10 w-full rounded-[9px] border border-dlvc-border bg-dlvc-bg px-3 text-[13.5px] text-dlvc-ink transition-[border-color,box-shadow] duration-150 focus:border-dlvc-accent focus:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] focus:outline-none";
const labelClass = "flex flex-col gap-1.5 text-[12.5px] font-medium text-dlvc-ink-soft";

function emptyItem(): LineItem {
  return { itemName: "", unit: "", quantity: 1, unitPrice: 0 };
}

export default function InvoiceForm({
  action,
  partners,
}: {
  action: (state: InvoiceFormState, formData: FormData) => Promise<InvoiceFormState>;
  partners: Partner[];
}) {
  const [state, formAction, pending] = useActionState<InvoiceFormState, FormData>(action, undefined);
  const [items, setItems] = useState<LineItem[]>([emptyItem()]);
  const [creatingPartner, setCreatingPartner] = useState(partners.length === 0);
  const [vatPercent, setVatPercent] = useState(0);

  const subtotal = items.reduce((sum, it) => sum + (Number(it.quantity) || 0) * (Number(it.unitPrice) || 0), 0);
  const vatAmount = Math.round((subtotal * vatPercent) / 100);
  const total = subtotal + vatAmount;

  function updateItem(index: number, patch: Partial<LineItem>) {
    setItems((prev) => prev.map((it, i) => (i === index ? { ...it, ...patch } : it)));
  }

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <input type="hidden" name="itemsJson" value={JSON.stringify(items)} />

      <div className="grid grid-cols-1 gap-4 min-[640px]:grid-cols-2">
        <label className={labelClass}>
          Số hoá đơn
          <input name="invoiceNumber" required placeholder="HD-2026-0001" className={`${inputClass} font-dlvc-mono`} />
        </label>
        <label className={labelClass}>
          Loại hoá đơn
          <select name="type" required defaultValue="sale" className={inputClass}>
            <option value="sale">Bán</option>
            <option value="purchase">Mua</option>
          </select>
        </label>
        <label className={labelClass}>
          Ngày lập
          <input type="date" name="issueDate" required defaultValue={new Date().toISOString().slice(0, 10)} className={inputClass} />
        </label>
        <label className={labelClass}>
          Hạn thanh toán
          <input type="date" name="dueDate" className={inputClass} />
        </label>
      </div>

      <div className="rounded-[12px] border border-dlvc-border p-4">
        <div className="mb-3 flex items-center justify-between">
          <h4 className="text-[13.5px] font-bold text-dlvc-ink">Đối tác</h4>
          {partners.length > 0 ? (
            <button
              type="button"
              onClick={() => setCreatingPartner((v) => !v)}
              className="text-[12px] font-semibold text-dlvc-accent-dark"
            >
              {creatingPartner ? "Chọn đối tác có sẵn" : "+ Tạo đối tác mới"}
            </button>
          ) : null}
        </div>

        {creatingPartner ? (
          <div className="grid grid-cols-1 gap-3.5 min-[560px]:grid-cols-2">
            <label className={labelClass}>
              Tên đối tác
              <input name="newPartnerName" required={creatingPartner} className={inputClass} />
            </label>
            <label className={labelClass}>
              Loại
              <select name="newPartnerType" defaultValue="customer" className={inputClass}>
                <option value="customer">Khách hàng</option>
                <option value="supplier">Nhà cung cấp</option>
                <option value="both">Cả hai</option>
              </select>
            </label>
            <label className={labelClass}>
              Mã số thuế
              <input name="newPartnerTaxCode" className={inputClass} />
            </label>
            <label className={labelClass}>
              Điện thoại
              <input name="newPartnerPhone" className={inputClass} />
            </label>
            <label className={`${labelClass} min-[560px]:col-span-2`}>
              Email
              <input type="email" name="newPartnerEmail" className={inputClass} />
            </label>
          </div>
        ) : (
          <label className={labelClass}>
            Chọn đối tác
            <select name="partnerId" required={!creatingPartner} defaultValue="" className={inputClass}>
              <option value="" disabled>
                Chọn đối tác
              </option>
              {partners.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.partnerName} ({p.partnerCode})
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      <div className="rounded-[12px] border border-dlvc-border p-4">
        <div className="mb-3 flex items-center justify-between">
          <h4 className="text-[13.5px] font-bold text-dlvc-ink">Mặt hàng</h4>
          <button
            type="button"
            onClick={() => setItems((prev) => [...prev, emptyItem()])}
            className="text-[12px] font-semibold text-dlvc-accent-dark"
          >
            + Thêm dòng
          </button>
        </div>

        <div className="flex flex-col gap-2.5">
          {items.map((item, index) => (
            <div key={index} className="grid grid-cols-[1fr_70px_90px_120px_28px] items-center gap-2">
              <input
                placeholder="Tên hàng"
                value={item.itemName}
                onChange={(e) => updateItem(index, { itemName: e.target.value })}
                className={inputClass}
              />
              <input
                placeholder="ĐVT"
                value={item.unit}
                onChange={(e) => updateItem(index, { unit: e.target.value })}
                className={inputClass}
              />
              <input
                type="number"
                min={0}
                step="any"
                placeholder="SL"
                value={item.quantity}
                onChange={(e) => updateItem(index, { quantity: Number(e.target.value) })}
                className={`${inputClass} font-dlvc-mono`}
              />
              <input
                type="number"
                min={0}
                step="any"
                placeholder="Đơn giá"
                value={item.unitPrice}
                onChange={(e) => updateItem(index, { unitPrice: Number(e.target.value) })}
                className={`${inputClass} font-dlvc-mono`}
              />
              <button
                type="button"
                onClick={() => setItems((prev) => prev.filter((_, i) => i !== index))}
                disabled={items.length === 1}
                className="flex h-10 w-7 items-center justify-center rounded-[9px] text-dlvc-danger disabled:opacity-30"
                aria-label="Xoá dòng"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        <div className="mt-3 flex flex-wrap items-center justify-end gap-x-6 gap-y-2 border-t border-dlvc-border pt-3">
          <label className="flex items-center gap-2 text-[13px] font-medium text-dlvc-ink-soft">
            Thuế GTGT (VAT)
            <select
              name="vatPercent"
              value={vatPercent}
              onChange={(e) => setVatPercent(Number(e.target.value))}
              className="h-8 rounded-md border border-dlvc-border bg-dlvc-bg px-2 font-dlvc-mono text-[13px] text-dlvc-ink"
            >
              <option value={0}>0%</option>
              <option value={5}>5%</option>
              <option value={8}>8%</option>
              <option value={10}>10%</option>
            </select>
          </label>
          <div className="text-[13px] text-dlvc-ink-soft">
            Tạm tính: <span className="font-dlvc-mono text-dlvc-ink">{subtotal.toLocaleString("vi-VN")} ₫</span>
          </div>
          <div className="text-[14px] font-semibold text-dlvc-ink">
            Tổng cộng: <span className="font-dlvc-mono">{total.toLocaleString("vi-VN")} ₫</span>
          </div>
        </div>
      </div>

      <label className={labelClass}>
        Ghi chú
        <textarea name="notes" rows={2} className={`${inputClass} h-auto resize-vertical py-2`} />
      </label>

      {state?.error ? (
        <p className="rounded-lg border border-dlvc-danger/30 bg-dlvc-danger/10 px-3.5 py-2.5 text-[13px] font-medium text-dlvc-danger">
          {state.error}
        </p>
      ) : null}

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={pending}
          className="flex h-10 items-center gap-1.5 rounded-[9px] bg-dlvc-sidebar px-5 text-[13.5px] font-semibold text-white transition-[filter,box-shadow,transform] duration-150 hover:not-disabled:-translate-y-px hover:not-disabled:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] hover:not-disabled:brightness-125 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {pending ? "Đang tạo…" : "Tạo hoá đơn"}
        </button>
        <Link
          href="/dlvc/admin/invoices"
          className="flex h-10 items-center rounded-[9px] border border-dlvc-border bg-dlvc-surface px-5 text-[13.5px] font-semibold text-dlvc-ink transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]"
        >
          Huỷ
        </Link>
      </div>
    </form>
  );
}
