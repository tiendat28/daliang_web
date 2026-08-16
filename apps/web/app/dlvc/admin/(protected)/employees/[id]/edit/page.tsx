import { notFound, redirect } from "next/navigation";
import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canManageEmployees, employeeScopeDepartmentId, isAdmin, isDepartmentHead } from "@/lib/dlvc/permissions";
import EmployeeForm from "../../EmployeeForm";
import { updateEmployee } from "../../actions";

function toDateInput(date: Date | null): string {
  if (!date) return "";
  return date.toISOString().slice(0, 10);
}

export default async function EditEmployeePage(props: PageProps<"/dlvc/admin/employees/[id]/edit">) {
  const { id } = await props.params;
  const employeeId = Number(id);
  if (!Number.isInteger(employeeId)) notFound();

  const session = await auth();
  if (!canManageEmployees(session)) redirect("/dlvc/admin");

  const employee = await prisma.employee.findUnique({ where: { id: employeeId } });
  if (!employee) notFound();

  const canEdit = isAdmin(session) || (isDepartmentHead(session) && session?.user?.departmentId === employee.departmentId);
  if (!canEdit) redirect(`/dlvc/admin/employees/${employeeId}`);

  const scopedDeptId = employeeScopeDepartmentId(session);

  const [departments, positions] = await Promise.all([
    prisma.adminDepartment.findMany({
      where: scopedDeptId ? { id: scopedDeptId } : undefined,
      orderBy: { departmentName: "asc" },
    }),
    prisma.position.findMany({ orderBy: { positionName: "asc" } }),
  ]);

  const boundUpdate = updateEmployee.bind(null, employeeId);

  return (
    <div className="mx-auto max-w-175">
      <div className="mb-5.5">
        <h1 className="text-[21px] font-bold tracking-tight text-dlvc-ink">Chỉnh sửa nhân viên</h1>
        <p className="mt-0.75 text-[13px] text-dlvc-ink-soft">{employee.fullName} · {employee.employeeCode}</p>
      </div>

      <div className="rounded-[14px] border border-dlvc-border bg-dlvc-surface p-6">
        <EmployeeForm
          action={boundUpdate}
          departments={departments}
          positions={positions}
          submitLabel="Lưu thay đổi"
          cancelHref={`/dlvc/admin/employees/${employeeId}`}
          restrictedDepartmentId={scopedDeptId}
          initialValues={{
            employeeCode: employee.employeeCode,
            fullName: employee.fullName,
            departmentId: employee.departmentId,
            positionId: employee.positionId,
            hireDate: toDateInput(employee.hireDate),
            terminationDate: toDateInput(employee.terminationDate),
            dateOfBirth: toDateInput(employee.dateOfBirth),
            gender: employee.gender,
            status: employee.status,
            phone: employee.phone,
            email: employee.email,
            address: employee.address,
          }}
        />
      </div>
    </div>
  );
}
