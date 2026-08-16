import Link from "next/link";
import { notFound } from "next/navigation";
import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canApproveDocumentsForDepartment } from "@/lib/dlvc/permissions";
import { formatDateVn, formatFileSizeKb, formatRelativeVn } from "@/lib/dlvc/format";
import { DOCUMENT_STATUS_LABEL, DOCUMENT_ACTION_LABEL } from "@/lib/dlvc/labels";
import DepartmentPill from "@/components/dlvc/admin/DepartmentPill";
import StatusBadge from "@/components/dlvc/admin/StatusBadge";
import DocumentReviewButtons from "./DocumentReviewButtons";

export default async function DocumentDetailPage(props: PageProps<"/dlvc/admin/documents/[id]">) {
  const { id } = await props.params;
  const documentId = Number(id);
  if (!Number.isInteger(documentId)) notFound();

  const searchParams = await props.searchParams;
  const tabParam = Array.isArray(searchParams.tab) ? searchParams.tab[0] : searchParams.tab;
  const activeTab = tabParam === "history" ? "history" : "info";

  const [session, document] = await Promise.all([
    auth(),
    prisma.adminDocument.findUnique({
      where: { id: documentId },
      include: {
        department: true,
        documentType: true,
        uploader: true,
        approver: true,
        history: { include: { performer: true }, orderBy: { performedAt: "desc" } },
      },
    }),
  ]);

  if (!document) notFound();

  const status = DOCUMENT_STATUS_LABEL[document.status] ?? { label: document.status, variant: "ok" as const };
  const canReview = document.status === "pending" && canApproveDocumentsForDepartment(session, document.departmentId);

  return (
    <div className="mx-auto max-w-200">
      <div className="mb-5.5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link
            href="/dlvc/admin/documents"
            className="text-[12.5px] font-medium text-dlvc-ink-soft hover:text-dlvc-accent-dark"
          >
            ← Tài liệu phòng ban
          </Link>
          <h1 className="mt-1.5 text-[21px] font-bold tracking-tight text-dlvc-ink">{document.title}</h1>
          <div className="mt-2 flex items-center gap-2.5">
            <DepartmentPill name={document.department.departmentName} color={document.department.color} />
            <StatusBadge label={status.label} variant={status.variant} />
          </div>
        </div>
        {canReview ? <DocumentReviewButtons documentId={document.id} /> : null}
      </div>

      <div className="mb-4.5 flex gap-1 border-b border-dlvc-border">
        <TabLink href={`/dlvc/admin/documents/${document.id}`} active={activeTab === "info"}>
          Thông tin
        </TabLink>
        <TabLink href={`/dlvc/admin/documents/${document.id}?tab=history`} active={activeTab === "history"}>
          Lịch sử ({document.history.length})
        </TabLink>
      </div>

      {activeTab === "info" ? (
        <div className="rounded-[14px] border border-dlvc-border bg-dlvc-surface p-5">
          <dl className="flex flex-col gap-3.5 text-[13px]">
            <Field label="Loại tài liệu">{document.documentType?.typeName ?? "—"}</Field>
            <Field label="Định dạng">
              {document.fileFormat ?? "—"} {document.fileSizeKb ? `· ${formatFileSizeKb(document.fileSizeKb)}` : ""}
            </Field>
            <Field label="Người tải lên">{document.uploader.fullName}</Field>
            <Field label="Ngày cập nhật">{formatDateVn(document.updatedAt)}</Field>
            {document.approver ? (
              <Field label="Người duyệt">
                {document.approver.fullName}
                {document.approvedAt ? ` · ${formatDateVn(document.approvedAt)}` : ""}
              </Field>
            ) : null}
            {document.expiryDate ? <Field label="Ngày hết hạn">{formatDateVn(document.expiryDate)}</Field> : null}
            {document.notes ? <Field label="Ghi chú">{document.notes}</Field> : null}
            <Field label="Tệp tin">
              <a
                href={document.filePath}
                target="_blank"
                rel="noreferrer"
                className="font-medium text-dlvc-accent-dark underline underline-offset-2"
              >
                Tải xuống
              </a>
            </Field>
          </dl>
        </div>
      ) : (
        <div className="overflow-hidden rounded-[14px] border border-dlvc-border bg-dlvc-surface">
          {document.history.length === 0 ? (
            <p className="px-5 py-6 text-center text-[13px] text-dlvc-ink-soft">Chưa có lịch sử.</p>
          ) : (
            document.history.map((h) => (
              <div key={h.id} className="flex items-center justify-between gap-3 border-b border-[#f1f2ed] px-5 py-3.5 last:border-b-0">
                <div className="text-[13px] text-dlvc-ink">
                  <span className="font-semibold">{h.performer.fullName}</span>{" "}
                  {DOCUMENT_ACTION_LABEL[h.action] ?? h.action}
                  {h.notes ? <span className="text-dlvc-ink-soft"> — {h.notes}</span> : null}
                </div>
                <div className="shrink-0 font-dlvc-mono text-[11.5px] text-dlvc-ink-soft">
                  {formatRelativeVn(h.performedAt)}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

function TabLink({ href, active, children }: { href: string; active: boolean; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className={
        active
          ? "border-b-2 border-dlvc-accent px-3.5 py-2.5 text-[13.5px] font-semibold text-dlvc-accent-dark"
          : "border-b-2 border-transparent px-3.5 py-2.5 text-[13.5px] font-medium text-dlvc-ink-soft hover:text-dlvc-ink"
      }
    >
      {children}
    </Link>
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
