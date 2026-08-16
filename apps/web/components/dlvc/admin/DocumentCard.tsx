import Link from "next/link";
import { formatDateVn, formatFileSizeKb } from "@/lib/dlvc/format";
import { DOCUMENT_STATUS_LABEL } from "@/lib/dlvc/labels";
import StatusBadge from "./StatusBadge";

export type DocumentCardData = {
  id: number;
  title: string;
  fileFormat: string | null;
  fileSizeKb: number | null;
  status: string;
  updatedAt: Date;
  uploaderName: string;
  departmentColor: string | null;
};

export default function DocumentCard({ doc }: { doc: DocumentCardData }) {
  const status = DOCUMENT_STATUS_LABEL[doc.status] ?? { label: doc.status, variant: "ok" as const };

  return (
    <Link
      href={`/dlvc/admin/documents/${doc.id}`}
      className="block rounded-xl border border-dlvc-border bg-dlvc-surface p-4 transition-transform duration-150 hover:-translate-y-0.75 hover:shadow-[0_12px_28px_-10px_rgba(34,211,238,0.45)]"
      style={{ borderTop: `4px solid ${doc.departmentColor ?? "var(--color-dlvc-accent)"}` }}
    >
      <div className="text-[11px] font-bold tracking-[0.04em] text-dlvc-ink-soft uppercase">
        {doc.fileFormat ?? "FILE"} {doc.fileSizeKb ? `· ${formatFileSizeKb(doc.fileSizeKb)}` : ""}
      </div>
      <h4 className="mt-2 mb-2.5 text-[14px] leading-tight font-bold text-dlvc-ink">{doc.title}</h4>
      <div className="mb-3 text-[11.5px] text-dlvc-ink-soft">
        {doc.uploaderName} · Cập nhật {formatDateVn(doc.updatedAt)}
      </div>
      <div className="flex items-center justify-between">
        <StatusBadge label={status.label} variant={status.variant} />
      </div>
    </Link>
  );
}
