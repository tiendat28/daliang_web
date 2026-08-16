import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { isAdmin, isDepartmentHead } from "@/lib/dlvc/permissions";
import { formatDateVn } from "@/lib/dlvc/format";
import { EMPLOYEE_STATUS_LABEL, GENDER_LABEL, DOCUMENT_STATUS_LABEL } from "@/lib/dlvc/labels";
import DepartmentPill from "@/components/dlvc/admin/DepartmentPill";
import StatusBadge from "@/components/dlvc/admin/StatusBadge";

export default async function EmployeeDetailPage(props: PageProps<"/dlvc/admin/employees/[id]">) {
  const { id } = await props.params;
  const employeeId = Number(id);
  if (!Number.isInteger(employeeId)) notFound();

  const session = await auth();

  const employee = await prisma.employee.findUnique({
    where: { id: employeeId },
    include: {
      department: true,
      position: true,
      uploadedDocuments: { include: { department: true }, orderBy: { createdAt: "desc" } },
      approvedDocuments: { include: { department: true }, orderBy: { approvedAt: "desc" } },
    },
  });

  if (!employee) notFound();

  const canView =
    isAdmin(session) ||
    (isDepartmentHead(session) && session?.user?.departmentId === employee.departmentId) ||
    session?.user?.employeeId === employee.id;

  if (!canView) redirect("/dlvc/admin");

  const canEdit = isAdmin(session) || (isDepartmentHead(session) && session?.user?.departmentId === employee.departmentId);
  const status = EMPLOYEE_STATUS_LABEL[employee.status] ?? { label: employee.status, variant: "ok" as const };

  return (
    <div className="mx-auto max-w-225">
      <div className="mb-5.5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link href="/dlvc/admin/employees" className="text-[12.5px] font-medium text-dlvc-ink-soft hover:text-dlvc-accent-dark">
            ← Danh sách nhân sự
          </Link>
          <h1 className="mt-1.5 text-[21px] font-bold tracking-tight text-dlvc-ink">{employee.fullName}</h1>
          <p className="mt-0.75 font-dlvc-mono text-[12.5px] text-dlvc-ink-soft">{employee.employeeCode}</p>
        </div>
        {canEdit ? (
          <Link
            href={`/dlvc/admin/employees/${employee.id}/edit`}
            className="flex h-10 items-center rounded-[9px] border border-dlvc-border bg-dlvc-surface px-4 text-[13.5px] font-semibold text-dlvc-ink transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]"
          >
            Chỉnh sửa
          </Link>
        ) : null}
      </div>

      <div className="grid grid-cols-1 gap-4.5 min-[900px]:grid-cols-[1fr_1.4fr]">
        <div className="rounded-[14px] border border-dlvc-border bg-dlvc-surface p-5">
          <h3 className="mb-4 text-[14.5px] font-bold text-dlvc-ink">Thông tin cá nhân</h3>
          <dl className="flex flex-col gap-3.5 text-[13px]">
            <Field label="Phòng ban">
              <DepartmentPill name={employee.department.departmentName} color={employee.department.color} />
            </Field>
            <Field label="Chức vụ">{employee.position?.positionName ?? "—"}</Field>
            <Field label="Trạng thái">
              <StatusBadge label={status.label} variant={status.variant} />
            </Field>
            <Field label="Ngày vào làm">{formatDateVn(employee.hireDate)}</Field>
            {employee.terminationDate ? <Field label="Ngày nghỉ việc">{formatDateVn(employee.terminationDate)}</Field> : null}
            {employee.dateOfBirth ? <Field label="Ngày sinh">{formatDateVn(employee.dateOfBirth)}</Field> : null}
            {employee.gender ? <Field label="Giới tính">{GENDER_LABEL[employee.gender] ?? employee.gender}</Field> : null}
            {employee.phone ? <Field label="Điện thoại">{employee.phone}</Field> : null}
            {employee.email ? <Field label="Email">{employee.email}</Field> : null}
            {employee.address ? <Field label="Địa chỉ">{employee.address}</Field> : null}
          </dl>
        </div>

        <div className="flex flex-col gap-4.5">
          <DocList title="Tài liệu đã tải lên" documents={employee.uploadedDocuments} emptyText="Chưa tải lên tài liệu nào." />
          <DocList title="Tài liệu đã duyệt" documents={employee.approvedDocuments} emptyText="Chưa duyệt tài liệu nào." />
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

type DocRow = {
  id: number;
  title: string;
  status: string;
  department: { departmentName: string; color: string | null };
};

function DocList({ title, documents, emptyText }: { title: string; documents: DocRow[]; emptyText: string }) {
  return (
    <div className="overflow-hidden rounded-[14px] border border-dlvc-border bg-dlvc-surface">
      <div className="border-b border-dlvc-border px-5 py-4">
        <h3 className="text-[14.5px] font-bold text-dlvc-ink">{title}</h3>
      </div>
      <div className="py-1.5">
        {documents.length === 0 ? (
          <p className="px-5 py-4 text-[13px] text-dlvc-ink-soft">{emptyText}</p>
        ) : (
          documents.map((doc) => {
            const status = DOCUMENT_STATUS_LABEL[doc.status] ?? { label: doc.status, variant: "ok" as const };
            return (
              <div key={doc.id} className="flex items-center justify-between gap-3 border-b border-[#f1f2ed] px-5 py-3 last:border-b-0">
                <div className="min-w-0">
                  <div className="truncate text-[13px] font-semibold text-dlvc-ink">{doc.title}</div>
                  <div className="mt-0.5 text-[11.5px] text-dlvc-ink-soft">{doc.department.departmentName}</div>
                </div>
                <StatusBadge label={status.label} variant={status.variant} />
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
