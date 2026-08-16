import Link from "next/link";
import { redirect } from "next/navigation";
import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canManageInvoices, canViewInvoices } from "@/lib/dlvc/permissions";
import { computeInvoiceStatus, invoiceGrandTotal } from "@/lib/dlvc/invoice";
import { formatDateVn, formatVnd } from "@/lib/dlvc/format";
import { INVOICE_STATUS_LABEL } from "@/lib/dlvc/labels";
import StatusBadge from "@/components/dlvc/admin/StatusBadge";
import InvoiceTypeBadge from "@/components/dlvc/admin/InvoiceTypeBadge";
import InvoiceFilterBar from "./InvoiceFilterBar";

export default async function InvoicesPage(props: PageProps<"/dlvc/admin/invoices">) {
  const session = await auth();
  if (!canViewInvoices(session)) redirect("/dlvc/admin");

  const searchParams = await props.searchParams;
  const typeParam = Array.isArray(searchParams.type) ? searchParams.type[0] : searchParams.type;
  const statusParam = Array.isArray(searchParams.status) ? searchParams.status[0] : searchParams.status;

  const invoices = await prisma.invoice.findMany({
    where: typeParam ? { type: typeParam as "sale" | "purchase" } : undefined,
    include: { partner: true, payments: true },
    orderBy: { issueDate: "desc" },
  });

  const rows = invoices
    .map((inv) => {
      const paidSum = inv.payments.reduce((sum, p) => sum + Number(p.amount.toString()), 0);
      return { invoice: inv, status: computeInvoiceStatus(inv, paidSum) };
    })
    .filter((row) => !statusParam || row.status === statusParam);

  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  const thisMonth = invoices.filter((i) => i.issueDate >= monthStart && i.issueDate < monthEnd);
  const thisMonthTotal = thisMonth.reduce((sum, i) => sum + invoiceGrandTotal(i), 0);

  return (
    <div>
      <div className="mb-5.5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[21px] font-bold tracking-tight text-dlvc-ink">Hoá đơn mua bán</h1>
          <p className="mt-0.75 text-[13px] text-dlvc-ink-soft">
            {thisMonth.length} hoá đơn trong tháng {now.getMonth() + 1}/{now.getFullYear()} · Tổng giá trị{" "}
            {formatVnd(thisMonthTotal)}
          </p>
        </div>
        {canManageInvoices(session) ? (
          <Link
            href="/dlvc/admin/invoices/new"
            className="flex h-10 items-center gap-1.5 rounded-[9px] bg-dlvc-sidebar px-4 text-[13.5px] font-semibold text-white transition-[filter,box-shadow,transform] duration-150 hover:-translate-y-px hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] hover:brightness-125"
          >
            + Tạo hoá đơn
          </Link>
        ) : null}
      </div>

      <InvoiceFilterBar />

      <div className="overflow-hidden rounded-[14px] border border-dlvc-border bg-dlvc-surface">
        <div className="overflow-x-auto">
          <table className="w-full min-w-200 border-collapse">
            <thead>
              <tr className="bg-[#fafaf7]">
                {["Số hoá đơn", "Loại", "Đối tác", "Ngày lập", "Giá trị", "Trạng thái"].map((h) => (
                  <th
                    key={h}
                    className="border-b border-dlvc-border px-4.5 py-3.25 text-left text-[11px] font-semibold tracking-[0.05em] text-dlvc-ink-soft uppercase"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4.5 py-8 text-center text-[13px] text-dlvc-ink-soft">
                    Không tìm thấy hoá đơn phù hợp.
                  </td>
                </tr>
              ) : (
                rows.map(({ invoice, status }) => {
                  const statusInfo = INVOICE_STATUS_LABEL[status] ?? { label: status, variant: "ok" as const };
                  return (
                    <tr key={invoice.id} className="border-b border-[#f1f2ed] last:border-b-0 hover:bg-[#fafaf7]">
                      <td className="px-4.5 py-3.25">
                        <Link
                          href={`/dlvc/admin/invoices/${invoice.id}`}
                          className="font-dlvc-mono text-[13px] font-semibold text-dlvc-ink"
                        >
                          {invoice.invoiceNumber}
                        </Link>
                      </td>
                      <td className="px-4.5 py-3.25">
                        <InvoiceTypeBadge type={invoice.type} />
                      </td>
                      <td className="px-4.5 py-3.25 text-[13.5px] text-dlvc-ink">{invoice.partner.partnerName}</td>
                      <td className="px-4.5 py-3.25 font-dlvc-mono text-[13px] text-dlvc-ink">
                        {formatDateVn(invoice.issueDate)}
                      </td>
                      <td className="px-4.5 py-3.25 font-dlvc-mono text-[13px] text-dlvc-ink">
                        {formatVnd(invoiceGrandTotal(invoice))}
                      </td>
                      <td className="px-4.5 py-3.25">
                        <StatusBadge label={statusInfo.label} variant={statusInfo.variant} />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
