import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import UploadForm from "./UploadForm";
import { uploadDocument } from "../actions";

export default async function UploadDocumentPage() {
  const session = await auth();

  const [departments, documentTypes] = await Promise.all([
    prisma.adminDepartment.findMany({ orderBy: { departmentName: "asc" } }),
    prisma.documentType.findMany({ orderBy: { typeName: "asc" } }),
  ]);

  return (
    <div className="mx-auto max-w-175">
      <div className="mb-5.5">
        <h1 className="text-[21px] font-bold tracking-tight text-dlvc-ink">Tải tài liệu lên</h1>
        <p className="mt-0.75 text-[13px] text-dlvc-ink-soft">
          Tài liệu sẽ ở trạng thái chờ duyệt cho đến khi trưởng phòng hoặc quản trị viên phê duyệt.
        </p>
      </div>

      <div className="rounded-[14px] border border-dlvc-border bg-dlvc-surface p-6">
        <UploadForm
          action={uploadDocument}
          departments={departments}
          documentTypes={documentTypes}
          defaultDepartmentId={session?.user?.departmentId ?? undefined}
        />
      </div>
    </div>
  );
}
