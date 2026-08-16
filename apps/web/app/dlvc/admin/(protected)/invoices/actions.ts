"use server";

import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { Prisma, prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canManageInvoices } from "@/lib/dlvc/permissions";
import { computeInvoiceStatus } from "@/lib/dlvc/invoice";

export type InvoiceFormState = { error?: string } | undefined;

type LineItemInput = { itemName: string; unit: string; quantity: number; unitPrice: number };

const PARTNER_TYPE_VALUES = ["supplier", "customer", "both"] as const;
const PAYMENT_METHOD_VALUES = ["cash", "bank_transfer", "card"] as const;

export async function createInvoice(_prevState: InvoiceFormState, formData: FormData): Promise<InvoiceFormState> {
  const session = await auth();
  if (!canManageInvoices(session)) return { error: "Bạn không có quyền tạo hoá đơn." };
  const employeeId = session?.user?.employeeId;
  if (!employeeId) return { error: "Tài khoản của bạn chưa gắn với hồ sơ nhân viên." };

  const invoiceNumber = String(formData.get("invoiceNumber") ?? "").trim();
  const type = String(formData.get("type") ?? "");
  const issueDateRaw = String(formData.get("issueDate") ?? "");
  const dueDateRaw = String(formData.get("dueDate") ?? "");
  const notes = String(formData.get("notes") ?? "").trim();
  const itemsRaw = String(formData.get("itemsJson") ?? "[]");

  if (!invoiceNumber) return { error: "Vui lòng nhập số hoá đơn." };
  if (type !== "sale" && type !== "purchase") return { error: "Vui lòng chọn loại hoá đơn." };
  if (!issueDateRaw) return { error: "Vui lòng chọn ngày lập." };

  let items: LineItemInput[];
  try {
    items = JSON.parse(itemsRaw);
  } catch {
    return { error: "Danh sách mặt hàng không hợp lệ." };
  }
  const validItems = items.filter((it) => it.itemName?.trim() && it.quantity > 0 && it.unitPrice >= 0);
  if (validItems.length === 0) return { error: "Vui lòng thêm ít nhất một dòng hàng hợp lệ." };

  // Resolve partner: either an existing partnerId, or create a new one inline.
  const partnerIdRaw = String(formData.get("partnerId") ?? "");
  const newPartnerName = String(formData.get("newPartnerName") ?? "").trim();
  let partnerId: number;

  if (partnerIdRaw) {
    partnerId = Number(partnerIdRaw);
  } else if (newPartnerName) {
    const newPartnerType = String(formData.get("newPartnerType") ?? "");
    if (!(PARTNER_TYPE_VALUES as readonly string[]).includes(newPartnerType)) {
      return { error: "Vui lòng chọn loại đối tác." };
    }
    const partnerCode = `PTN-${Date.now().toString(36).toUpperCase()}`;
    try {
      const partner = await prisma.partner.create({
        data: {
          partnerCode,
          partnerName: newPartnerName,
          type: newPartnerType as (typeof PARTNER_TYPE_VALUES)[number],
          taxCode: String(formData.get("newPartnerTaxCode") ?? "").trim() || null,
          phone: String(formData.get("newPartnerPhone") ?? "").trim() || null,
          email: String(formData.get("newPartnerEmail") ?? "").trim() || null,
        },
      });
      partnerId = partner.id;
    } catch {
      return { error: "Không thể tạo đối tác mới." };
    }
  } else {
    return { error: "Vui lòng chọn hoặc tạo đối tác." };
  }

  const totalAmount = validItems.reduce((sum, it) => sum + it.quantity * it.unitPrice, 0);
  const vatPercent = Number(formData.get("vatPercent") ?? 0);
  const vatAmount = Number.isFinite(vatPercent) && vatPercent > 0 ? Math.round((totalAmount * vatPercent) / 100) : 0;

  try {
    const invoice = await prisma.invoice.create({
      data: {
        invoiceNumber,
        type,
        partnerId,
        createdBy: employeeId,
        issueDate: new Date(issueDateRaw),
        dueDate: dueDateRaw ? new Date(dueDateRaw) : null,
        totalAmount,
        vatAmount,
        status: "unpaid",
        notes: notes || null,
        items: {
          create: validItems.map((it) => ({
            itemName: it.itemName.trim(),
            unit: it.unit?.trim() || null,
            quantity: it.quantity,
            unitPrice: it.unitPrice,
          })),
        },
      },
    });
    revalidatePath("/dlvc/admin/invoices");
    redirect(`/dlvc/admin/invoices/${invoice.id}`);
  } catch (err) {
    if (err instanceof Prisma.PrismaClientKnownRequestError && err.code === "P2002") {
      return { error: "Số hoá đơn đã tồn tại." };
    }
    throw err;
  }
}

export async function recordPayment(
  invoiceId: number,
  _prevState: InvoiceFormState,
  formData: FormData,
): Promise<InvoiceFormState> {
  const session = await auth();
  if (!canManageInvoices(session)) return { error: "Bạn không có quyền ghi nhận thanh toán." };
  const employeeId = session?.user?.employeeId;
  if (!employeeId) return { error: "Tài khoản của bạn chưa gắn với hồ sơ nhân viên." };

  const amountRaw = String(formData.get("amount") ?? "");
  const paymentDateRaw = String(formData.get("paymentDate") ?? "");
  const methodRaw = String(formData.get("method") ?? "");
  const amount = Number(amountRaw);

  if (!amount || amount <= 0) return { error: "Vui lòng nhập số tiền hợp lệ." };
  if (!paymentDateRaw) return { error: "Vui lòng chọn ngày thanh toán." };

  const invoice = await prisma.invoice.findUnique({ where: { id: invoiceId }, include: { payments: true } });
  if (!invoice) return { error: "Không tìm thấy hoá đơn." };

  await prisma.payment.create({
    data: {
      invoiceId,
      amount,
      paymentDate: new Date(paymentDateRaw),
      method: (PAYMENT_METHOD_VALUES as readonly string[]).includes(methodRaw)
        ? (methodRaw as (typeof PAYMENT_METHOD_VALUES)[number])
        : null,
      confirmedBy: employeeId,
    },
  });

  const paidSum =
    invoice.payments.reduce((sum, p) => sum + Number(p.amount.toString()), 0) + amount;
  const newStatus = computeInvoiceStatus(invoice, paidSum);
  await prisma.invoice.update({ where: { id: invoiceId }, data: { status: newStatus } });

  revalidatePath(`/dlvc/admin/invoices/${invoiceId}`);
  revalidatePath("/dlvc/admin/invoices");
}
