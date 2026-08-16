import { redirect } from "next/navigation";
import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canManageInvoices } from "@/lib/dlvc/permissions";
import InvoiceForm from "./InvoiceForm";
import { createInvoice } from "../actions";

export default async function NewInvoicePage() {
  const session = await auth();
  if (!canManageInvoices(session)) redirect("/dlvc/admin/invoices");

  const partners = await prisma.partner.findMany({ orderBy: { partnerName: "asc" } });

  return (
    <div className="mx-auto max-w-200">
      <div className="mb-5.5">
        <h1 className="text-[21px] font-bold tracking-tight text-dlvc-ink">Tạo hoá đơn</h1>
        <p className="mt-0.75 text-[13px] text-dlvc-ink-soft">Tổng giá trị được tính tự động từ các dòng hàng.</p>
      </div>

      <div className="rounded-[14px] border border-dlvc-border bg-dlvc-surface p-6">
        <InvoiceForm action={createInvoice} partners={partners} />
      </div>
    </div>
  );
}
