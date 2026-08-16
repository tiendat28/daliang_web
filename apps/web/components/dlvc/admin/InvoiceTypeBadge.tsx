export default function InvoiceTypeBadge({ type }: { type: string }) {
  const isSale = type === "sale";
  const color = isSale ? "var(--color-dlvc-dept-hoa-don)" : "var(--color-dlvc-invoice-purchase)";
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-[#f3f4ef] py-0.75 pr-2.25 pl-1.75 text-[12px] font-semibold text-dlvc-ink">
      <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: color }} />
      {isSale ? "Bán" : "Mua"}
    </span>
  );
}
