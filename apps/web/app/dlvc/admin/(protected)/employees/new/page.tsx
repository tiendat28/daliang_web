import { redirect } from "next/navigation";
import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canManageEmployees, employeeScopeDepartmentId } from "@/lib/dlvc/permissions";
import EmployeeForm from "../EmployeeForm";
import { createEmployee } from "../actions";

export default async function NewEmployeePage() {
  const session = await auth();
  if (!canManageEmployees(session)) {
    redirect("/dlvc/admin");
  }

  const scopedDeptId = employeeScopeDepartmentId(session);

  const [departments, positions] = await Promise.all([
    prisma.adminDepartment.findMany({
      where: scopedDeptId ? { id: scopedDeptId } : undefined,
      orderBy: { departmentName: "asc" },
    }),
    prisma.position.findMany({ orderBy: { positionName: "asc" } }),
  ]);

  return (
    <div className="mx-auto max-w-175">
      <div className="mb-5.5">
        <h1 className="text-[21px] font-bold tracking-tight text-dlvc-ink">Thêm nhân viên</h1>
        <p className="mt-0.75 text-[13px] text-dlvc-ink-soft">Nhập thông tin nhân viên mới.</p>
      </div>

      <div className="rounded-[14px] border border-dlvc-border bg-dlvc-surface p-6">
        <EmployeeForm
          action={createEmployee}
          departments={departments}
          positions={positions}
          submitLabel="Thêm nhân viên"
          cancelHref="/dlvc/admin/employees"
          restrictedDepartmentId={scopedDeptId}
        />
      </div>
    </div>
  );
}
