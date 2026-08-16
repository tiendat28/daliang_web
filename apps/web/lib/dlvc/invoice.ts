type Money = number | string | { toString(): string };

type InvoiceLike = {
  status: string;
  dueDate: Date | null;
  totalAmount: Money;
  vatAmount?: Money | null;
};

export type InvoiceRuntimeStatus = "unpaid" | "paid" | "overdue" | "cancelled";

function toNumber(value: Money | null | undefined): number {
  if (value === null || value === undefined) return 0;
  return Number(value.toString());
}

/** Grand total the partner owes: line-items subtotal (`totalAmount`) plus VAT. */
export function invoiceGrandTotal(invoice: InvoiceLike): number {
  return toNumber(invoice.totalAmount) + toNumber(invoice.vatAmount);
}

/**
 * Derives the invoice's effective status from paid-so-far vs grand total/due
 * date, without requiring a cron job. `cancelled` is a terminal manual state.
 */
export function computeInvoiceStatus(invoice: InvoiceLike, paidSum: number, now: Date = new Date()): InvoiceRuntimeStatus {
  if (invoice.status === "cancelled") return "cancelled";

  const grandTotal = invoiceGrandTotal(invoice);
  if (grandTotal > 0 && paidSum >= grandTotal) return "paid";
  if (invoice.dueDate && now > invoice.dueDate) return "overdue";
  return "unpaid";
}
