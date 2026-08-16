import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canManageInvoices, canViewInvoices } from "@/lib/dlvc/permissions";
import { computeInvoiceStatus, invoiceGrandTotal } from "@/lib/dlvc/invoice";
import { formatDateVn, formatVnd } from "@/lib/dlvc/format";
import { INVOICE_STATUS_LABEL } from "@/lib/dlvc/labels";
import StatusBadge from "@/components/dlvc/admin/StatusBadge";
import InvoiceTypeBadge from "@/components/dlvc/admin/InvoiceTypeBadge";
import RecordPaymentForm from "./RecordPaymentForm";
import { recordPayment } from "../actions";

const METHOD_LABEL: Record<string, string> = {
  cash: "Tiền mặt",
  bank_transfer: "Chuyển khoản",
  card: "Thẻ",
};

export default async function InvoiceDetailPage(props: PageProps<"/dlvc/admin/invoices/[id]">) {
  const session = await auth();
  if (!canViewInvoices(session)) redirect("/dlvc/admin");

  const { id } = await props.params;
  const invoiceId = Number(id);
  if (!Number.isInteger(invoiceId)) notFound();

  const invoice = await prisma.invoice.findUnique({
    where: { id: invoiceId },
    include: {
      partner: true,
      creator: true,
      items: true,
      payments: { include: { confirmer: true }, orderBy: { paymentDate: "desc" } },
    },
  });
  if (!invoice) notFound();

  const paidSum = invoice.payments.reduce((sum, p) => sum + Number(p.amount.toString()), 0);
  const grandTotal = invoiceGrandTotal(invoice);
  const remaining = Math.max(0, grandTotal - paidSum);
  const status = computeInvoiceStatus(invoice, paidSum);
  const statusInfo = INVOICE_STATUS_LABEL[status] ?? { label: status, variant: "ok" as const };
  const canRecordPayment = canManageInvoices(session) && status !== "paid" && status !== "cancelled";

  const boundRecordPayment = recordPayment.bind(null, invoice.id);

  return (
    <div className="mx-auto max-w-200">
      <div className="mb-5.5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link href="/dlvc/admin/invoices" className="text-[12.5px] font-medium text-dlvc-ink-soft hover:text-dlvc-accent-dark">
            ← Hoá đơn mua bán
          </Link>
          <h1 className="mt-1.5 font-dlvc-mono text-[21px] font-bold tracking-tight text-dlvc-ink">
            {invoice.invoiceNumber}
          </h1>
          <div className="mt-2 flex items-center gap-2.5">
            <InvoiceTypeBadge type={invoice.type} />
            <StatusBadge label={statusInfo.label} variant={statusInfo.variant} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4.5 min-[900px]:grid-cols-[1fr_1.3fr]">
        <div className="flex flex-col gap-4.5">
          <div className="rounded-[14px] border border-dlvc-border bg-dlvc-surface p-5">
            <h3 className="mb-4 text-[14.5px] font-bold text-dlvc-ink">Thông tin hoá đơn</h3>
            <dl className="flex flex-col gap-3.5 text-[13px]">
              <Field label="Đối tác">{invoice.partner.partnerName}</Field>
              <Field label="Ngày lập">{formatDateVn(invoice.issueDate)}</Field>
              {invoice.dueDate ? <Field label="Hạn thanh toán">{formatDateVn(invoice.dueDate)}</Field> : null}
              <Field label="Người lập">{invoice.creator.fullName}</Field>
              <Field label="Tạm tính">{formatVnd(invoice.totalAmount)}</Field>
              {Number(invoice.vatAmount?.toString() ?? 0) > 0 ? (
                <Field label="Thuế GTGT (VAT)">{formatVnd(invoice.vatAmount!)}</Field>
              ) : null}
              <Field label="Tổng cộng">{formatVnd(grandTotal)}</Field>
              <Field label="Đã thanh toán">{formatVnd(paidSum)}</Field>
              <Field label="Còn lại">{formatVnd(remaining)}</Field>
              {invoice.notes ? <Field label="Ghi chú">{invoice.notes}</Field> : null}
            </dl>
          </div>

          <div className="overflow-hidden rounded-[14px] border border-dlvc-border bg-dlvc-surface">
            <div className="border-b border-dlvc-border px-5 py-4">
              <h3 className="text-[14.5px] font-bold text-dlvc-ink">Mặt hàng</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-100 border-collapse text-[13px]">
                <thead>
                  <tr className="bg-[#fafaf7]">
                    <th className="px-4 py-2.5 text-left text-[11px] font-semibold text-dlvc-ink-soft uppercase">Tên hàng</th>
                    <th className="px-4 py-2.5 text-right text-[11px] font-semibold text-dlvc-ink-soft uppercase">SL</th>
                    <th className="px-4 py-2.5 text-right text-[11px] font-semibold text-dlvc-ink-soft uppercase">Đơn giá</th>
                    <th className="px-4 py-2.5 text-right text-[11px] font-semibold text-dlvc-ink-soft uppercase">Thành tiền</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.items.map((item) => (
                    <tr key={item.id} className="border-t border-[#f1f2ed]">
                      <td className="px-4 py-2.5 text-dlvc-ink">
                        {item.itemName} {item.unit ? <span className="text-dlvc-ink-soft">({item.unit})</span> : null}
                      </td>
                      <td className="px-4 py-2.5 text-right font-dlvc-mono text-dlvc-ink">{item.quantity.toString()}</td>
                      <td className="px-4 py-2.5 text-right font-dlvc-mono text-dlvc-ink">{formatVnd(item.unitPrice)}</td>
                      <td className="px-4 py-2.5 text-right font-dlvc-mono font-semibold text-dlvc-ink">
                        {formatVnd(item.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-4.5">
          <div className="overflow-hidden rounded-[14px] border border-dlvc-border bg-dlvc-surface">
            <div className="border-b border-dlvc-border px-5 py-4">
              <h3 className="text-[14.5px] font-bold text-dlvc-ink">Lịch sử thanh toán</h3>
            </div>
            <div className="py-1.5">
              {invoice.payments.length === 0 ? (
                <p className="px-5 py-4 text-[13px] text-dlvc-ink-soft">Chưa có khoản thanh toán nào.</p>
              ) : (
                invoice.payments.map((p) => (
                  <div key={p.id} className="flex items-center justify-between gap-3 border-b border-[#f1f2ed] px-5 py-3 last:border-b-0">
                    <div>
                      <div className="font-dlvc-mono text-[13.5px] font-semibold text-dlvc-ink">{formatVnd(p.amount)}</div>
                      <div className="mt-0.5 text-[11.5px] text-dlvc-ink-soft">
                        {formatDateVn(p.paymentDate)} · {p.method ? METHOD_LABEL[p.method] : "—"}
                        {p.confirmer ? ` · ${p.confirmer.fullName}` : ""}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {canRecordPayment ? (
            <div className="rounded-[14px] border border-dlvc-border bg-dlvc-surface p-5">
              <h3 className="mb-4 text-[14.5px] font-bold text-dlvc-ink">Ghi nhận thanh toán</h3>
              <RecordPaymentForm action={boundRecordPayment} remainingAmount={remaining} />
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 border-b border-[#f1f2ed] pb-3.5 last:border-b-0 last:pb-0">
      <dt className="shrink-0 text-dlvc-ink-soft">{label}</dt>
      <dd className="text-right font-medium text-dlvc-ink">{children}</dd>
    </div>
  );
}
