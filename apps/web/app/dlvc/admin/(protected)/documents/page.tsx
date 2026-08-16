import Link from "next/link";
import { prisma } from "@daliang/db";
import DepartmentTabs from "@/components/dlvc/admin/DepartmentTabs";
import DocumentCard, { type DocumentCardData } from "@/components/dlvc/admin/DocumentCard";

export default async function DocumentsPage(props: PageProps<"/dlvc/admin/documents">) {
  const searchParams = await props.searchParams;
  const deptParam = Array.isArray(searchParams.dept) ? searchParams.dept[0] : searchParams.dept;

  const departments = await prisma.adminDepartment.findMany({ orderBy: { departmentName: "asc" } });
  const activeDeptId = deptParam ? Number(deptParam) : departments[0]?.id;

  const documents = activeDeptId
    ? await prisma.adminDocument.findMany({
        where: { departmentId: activeDeptId },
        include: { uploader: true },
        orderBy: { updatedAt: "desc" },
      })
    : [];

  const cards: DocumentCardData[] = documents.map((d) => ({
    id: d.id,
    title: d.title,
    fileFormat: d.fileFormat,
    fileSizeKb: d.fileSizeKb,
    status: d.status,
    updatedAt: d.updatedAt,
    uploaderName: d.uploader.fullName,
    departmentColor: departments.find((dep) => dep.id === activeDeptId)?.color ?? null,
  }));

  return (
    <div>
      <div className="mb-5.5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[21px] font-bold tracking-tight text-dlvc-ink">Tài liệu phòng ban</h1>
          <p className="mt-0.75 text-[13px] text-dlvc-ink-soft">Lưu trữ và phê duyệt tài liệu theo từng bộ phận</p>
        </div>
        <Link
          href="/dlvc/admin/documents/upload"
          className="flex h-10 items-center gap-1.5 rounded-[9px] bg-dlvc-sidebar px-4 text-[13.5px] font-semibold text-white transition-[filter,box-shadow,transform] duration-150 hover:-translate-y-px hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] hover:brightness-125"
        >
          + Tải tài liệu lên
        </Link>
      </div>

      <DepartmentTabs departments={departments} />

      {cards.length === 0 ? (
        <div className="rounded-[14px] border border-dlvc-border bg-dlvc-surface px-5 py-10 text-center text-[13px] text-dlvc-ink-soft">
          Chưa có tài liệu nào trong phòng ban này.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3.5 min-[640px]:grid-cols-2 min-[1000px]:grid-cols-3">
          {cards.map((doc) => (
            <DocumentCard key={doc.id} doc={doc} />
          ))}
        </div>
      )}
    </div>
  );
}
