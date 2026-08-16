"use server";

import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { Prisma, prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canManageEmployees, employeeScopeDepartmentId } from "@/lib/dlvc/permissions";

export type EmployeeFormState = { error?: string } | undefined;

const STATUS_VALUES = ["active", "probation", "on_leave", "terminated"] as const;
const GENDER_VALUES = ["male", "female", "other"] as const;

function readEmployeeInput(formData: FormData) {
  const employeeCode = String(formData.get("employeeCode") ?? "").trim();
  const fullName = String(formData.get("fullName") ?? "").trim();
  const departmentIdRaw = String(formData.get("departmentId") ?? "");
  const hireDateRaw = String(formData.get("hireDate") ?? "");

  if (!employeeCode) return { error: "Vui lòng nhập mã nhân viên." } as const;
  if (!fullName) return { error: "Vui lòng nhập họ tên." } as const;
  if (!departmentIdRaw) return { error: "Vui lòng chọn phòng ban." } as const;
  if (!hireDateRaw) return { error: "Vui lòng chọn ngày vào làm." } as const;

  const positionIdRaw = String(formData.get("positionId") ?? "");
  const genderRaw = String(formData.get("gender") ?? "");
  const statusRaw = String(formData.get("status") ?? "active");
  const terminationDateRaw = String(formData.get("terminationDate") ?? "");
  const dateOfBirthRaw = String(formData.get("dateOfBirth") ?? "");
  const email = String(formData.get("email") ?? "").trim();

  return {
    data: {
      employeeCode,
      fullName,
      departmentId: Number(departmentIdRaw),
      positionId: positionIdRaw ? Number(positionIdRaw) : null,
      hireDate: new Date(hireDateRaw),
      terminationDate: terminationDateRaw ? new Date(terminationDateRaw) : null,
      dateOfBirth: dateOfBirthRaw ? new Date(dateOfBirthRaw) : null,
      gender: (GENDER_VALUES as readonly string[]).includes(genderRaw) ? (genderRaw as (typeof GENDER_VALUES)[number]) : null,
      status: (STATUS_VALUES as readonly string[]).includes(statusRaw) ? (statusRaw as (typeof STATUS_VALUES)[number]) : "active",
      phone: String(formData.get("phone") ?? "").trim() || null,
      email: email || null,
      address: String(formData.get("address") ?? "").trim() || null,
    },
  } as const;
}

export async function createEmployee(_prevState: EmployeeFormState, formData: FormData): Promise<EmployeeFormState> {
  const session = await auth();
  if (!canManageEmployees(session)) {
    return { error: "Bạn không có quyền thực hiện thao tác này." };
  }

  const parsed = readEmployeeInput(formData);
  if ("error" in parsed) return { error: parsed.error };

  const scopedDeptId = employeeScopeDepartmentId(session);
  if (scopedDeptId && parsed.data.departmentId !== scopedDeptId) {
    return { error: "Bạn chỉ có thể thêm nhân viên trong phòng ban của mình." };
  }

  try {
    await prisma.employee.create({ data: parsed.data });
  } catch (err) {
    if (err instanceof Prisma.PrismaClientKnownRequestError && err.code === "P2002") {
      return { error: "Mã nhân viên hoặc email đã tồn tại." };
    }
    throw err;
  }

  revalidatePath("/dlvc/admin/employees");
  redirect("/dlvc/admin/employees");
}

export async function updateEmployee(
  employeeId: number,
  _prevState: EmployeeFormState,
  formData: FormData,
): Promise<EmployeeFormState> {
  const session = await auth();
  if (!canManageEmployees(session)) {
    return { error: "Bạn không có quyền thực hiện thao tác này." };
  }

  const parsed = readEmployeeInput(formData);
  if ("error" in parsed) return { error: parsed.error };

  const scopedDeptId = employeeScopeDepartmentId(session);
  if (scopedDeptId) {
    const target = await prisma.employee.findUnique({ where: { id: employeeId }, select: { departmentId: true } });
    if (!target || target.departmentId !== scopedDeptId || parsed.data.departmentId !== scopedDeptId) {
      return { error: "Bạn chỉ có thể sửa nhân viên trong phòng ban của mình." };
    }
  }

  try {
    await prisma.employee.update({ where: { id: employeeId }, data: parsed.data });
  } catch (err) {
    if (err instanceof Prisma.PrismaClientKnownRequestError && err.code === "P2002") {
      return { error: "Mã nhân viên hoặc email đã tồn tại." };
    }
    throw err;
  }

  revalidatePath("/dlvc/admin/employees");
  revalidatePath(`/dlvc/admin/employees/${employeeId}`);
  redirect(`/dlvc/admin/employees/${employeeId}`);
}
