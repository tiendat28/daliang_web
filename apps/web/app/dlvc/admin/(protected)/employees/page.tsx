import Link from "next/link";
import { redirect } from "next/navigation";
import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canManageEmployees, employeeScopeDepartmentId } from "@/lib/dlvc/permissions";
import { formatDateVn } from "@/lib/dlvc/format";
import { EMPLOYEE_STATUS_LABEL } from "@/lib/dlvc/labels";
import DepartmentPill from "@/components/dlvc/admin/DepartmentPill";
import StatusBadge from "@/components/dlvc/admin/StatusBadge";
import EmployeesFilterBar from "./EmployeesFilterBar";

export default async function EmployeesPage(props: PageProps<"/dlvc/admin/employees">) {
  const session = await auth();

  if (!canManageEmployees(session)) {
    if (session?.user?.employeeId) {
      redirect(`/dlvc/admin/employees/${session.user.employeeId}`);
    }
    redirect("/dlvc/admin");
  }

  const searchParams = await props.searchParams;
  const deptParam = Array.isArray(searchParams.dept) ? searchParams.dept[0] : searchParams.dept;
  const qParam = Array.isArray(searchParams.q) ? searchParams.q[0] : searchParams.q;

  const scopedDeptId = employeeScopeDepartmentId(session);
  const selectedDeptId = deptParam ? Number(deptParam) : scopedDeptId;

  const [departments, employees, totalActive] = await Promise.all([
    prisma.adminDepartment.findMany({
      where: scopedDeptId ? { id: scopedDeptId } : undefined,
      orderBy: { departmentName: "asc" },
    }),
    prisma.employee.findMany({
      where: {
        departmentId: selectedDeptId ?? undefined,
        ...(qParam
          ? {
              OR: [
                { fullName: { contains: qParam, mode: "insensitive" } },
                { employeeCode: { contains: qParam, mode: "insensitive" } },
              ],
            }
          : {}),
      },
      include: { department: true, position: true },
      orderBy: { fullName: "asc" },
    }),
    prisma.employee.count({ where: { status: "active", departmentId: scopedDeptId ?? undefined } }),
  ]);

  return (
    <div>
      <div className="mb-5.5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[21px] font-bold tracking-tight text-dlvc-ink">Nhân sự</h1>
          <p className="mt-0.75 text-[13px] text-dlvc-ink-soft">
            {totalActive} nhân viên đang hoạt động {scopedDeptId ? "trong phòng ban" : "trên toàn công ty"}
          </p>
        </div>
        <Link
          href="/dlvc/admin/employees/new"
          className="flex h-10 items-center gap-1.5 rounded-[9px] bg-dlvc-sidebar px-4 text-[13.5px] font-semibold text-white transition-[filter,box-shadow,transform] duration-150 hover:-translate-y-px hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] hover:brightness-125"
        >
          + Thêm nhân viên
        </Link>
      </div>

      <EmployeesFilterBar departments={departments} />

      <div className="overflow-hidden rounded-[14px] border border-dlvc-border bg-dlvc-surface">
        <div className="overflow-x-auto">
          <table className="w-full min-w-175 border-collapse">
            <thead>
              <tr className="bg-[#fafaf7]">
                {["Nhân viên", "Phòng ban", "Chức vụ", "Ngày vào làm", "Trạng thái"].map((h) => (
                  <th
                    key={h}
                    className="border-b border-dlvc-border px-4.5 py-3.25 text-left text-[11px] font-semibold tracking-[0.05em] text-dlvc-ink-soft uppercase"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {employees.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4.5 py-8 text-center text-[13px] text-dlvc-ink-soft">
                    Không tìm thấy nhân viên phù hợp.
                  </td>
                </tr>
              ) : (
                employees.map((emp) => {
                  const status = EMPLOYEE_STATUS_LABEL[emp.status] ?? { label: emp.status, variant: "ok" as const };
                  return (
                    <tr key={emp.id} className="border-b border-[#f1f2ed] last:border-b-0 hover:bg-[#fafaf7]">
                      <td className="px-4.5 py-3.25">
                        <Link href={`/dlvc/admin/employees/${emp.id}`} className="block">
                          <div className="text-[13.5px] font-semibold text-dlvc-ink">{emp.fullName}</div>
                          <div className="mt-0.5 font-dlvc-mono text-[11.5px] text-dlvc-ink-soft">{emp.employeeCode}</div>
                        </Link>
                      </td>
                      <td className="px-4.5 py-3.25">
                        <DepartmentPill name={emp.department.departmentName} color={emp.department.color} />
                      </td>
                      <td className="px-4.5 py-3.25 text-[13.5px] text-dlvc-ink">{emp.position?.positionName ?? "—"}</td>
                      <td className="px-4.5 py-3.25 font-dlvc-mono text-[13px] text-dlvc-ink">
                        {formatDateVn(emp.hireDate)}
                      </td>
                      <td className="px-4.5 py-3.25">
                        <StatusBadge label={status.label} variant={status.variant} />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
