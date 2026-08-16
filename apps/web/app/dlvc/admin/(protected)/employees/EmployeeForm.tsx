"use client";

import { useActionState } from "react";
import Link from "next/link";
import type { EmployeeFormState } from "./actions";

type Dept = { id: number; departmentName: string };
type Pos = { id: number; positionName: string };

type EmployeeFormValues = {
  employeeCode: string;
  fullName: string;
  departmentId: number;
  positionId: number | null;
  hireDate: string;
  terminationDate: string | null;
  dateOfBirth: string | null;
  gender: string | null;
  status: string;
  phone: string | null;
  email: string | null;
  address: string | null;
};

const inputClass =
  "h-10 w-full rounded-[9px] border border-dlvc-border bg-dlvc-bg px-3 text-[13.5px] text-dlvc-ink transition-[border-color,box-shadow] duration-150 focus:border-dlvc-accent focus:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] focus:outline-none";
const labelClass = "flex flex-col gap-1.5 text-[12.5px] font-medium text-dlvc-ink-soft";

export default function EmployeeForm({
  action,
  departments,
  positions,
  initialValues,
  submitLabel,
  cancelHref,
  restrictedDepartmentId,
}: {
  action: (state: EmployeeFormState, formData: FormData) => Promise<EmployeeFormState>;
  departments: Dept[];
  positions: Pos[];
  initialValues?: Partial<EmployeeFormValues>;
  submitLabel: string;
  cancelHref: string;
  restrictedDepartmentId?: number | null;
}) {
  const [state, formAction, pending] = useActionState<EmployeeFormState, FormData>(action, undefined);

  return (
    <form action={formAction} className="flex flex-col gap-4">
      <div className="grid grid-cols-1 gap-4 min-[640px]:grid-cols-2">
        <label className={labelClass}>
          Mã nhân viên
          <input
            name="employeeCode"
            defaultValue={initialValues?.employeeCode}
            required
            placeholder="NV-0001"
            className={`${inputClass} font-dlvc-mono`}
          />
        </label>
        <label className={labelClass}>
          Họ và tên
          <input name="fullName" defaultValue={initialValues?.fullName} required className={inputClass} />
        </label>

        <label className={labelClass}>
          Phòng ban
          <select
            name="departmentId"
            required
            defaultValue={initialValues?.departmentId ?? restrictedDepartmentId ?? ""}
            disabled={!!restrictedDepartmentId}
            className={inputClass}
          >
            <option value="" disabled>
              Chọn phòng ban
            </option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.departmentName}
              </option>
            ))}
          </select>
        </label>
        <label className={labelClass}>
          Chức vụ
          <select name="positionId" defaultValue={initialValues?.positionId ?? ""} className={inputClass}>
            <option value="">— Không —</option>
            {positions.map((p) => (
              <option key={p.id} value={p.id}>
                {p.positionName}
              </option>
            ))}
          </select>
        </label>

        <label className={labelClass}>
          Ngày vào làm
          <input type="date" name="hireDate" defaultValue={initialValues?.hireDate} required className={inputClass} />
        </label>
        <label className={labelClass}>
          Trạng thái
          <select name="status" defaultValue={initialValues?.status ?? "active"} className={inputClass}>
            <option value="active">Đang làm</option>
            <option value="probation">Thử việc</option>
            <option value="on_leave">Nghỉ phép</option>
            <option value="terminated">Đã nghỉ</option>
          </select>
        </label>

        <label className={labelClass}>
          Ngày sinh
          <input type="date" name="dateOfBirth" defaultValue={initialValues?.dateOfBirth ?? ""} className={inputClass} />
        </label>
        <label className={labelClass}>
          Giới tính
          <select name="gender" defaultValue={initialValues?.gender ?? ""} className={inputClass}>
            <option value="">— Không —</option>
            <option value="male">Nam</option>
            <option value="female">Nữ</option>
            <option value="other">Khác</option>
          </select>
        </label>

        <label className={labelClass}>
          Số điện thoại
          <input name="phone" defaultValue={initialValues?.phone ?? ""} className={inputClass} />
        </label>
        <label className={labelClass}>
          Email
          <input type="email" name="email" defaultValue={initialValues?.email ?? ""} className={inputClass} />
        </label>

        <label className={`${labelClass} min-[640px]:col-span-2`}>
          Địa chỉ
          <input name="address" defaultValue={initialValues?.address ?? ""} className={inputClass} />
        </label>

        <label className={labelClass}>
          Ngày nghỉ việc (nếu có)
          <input
            type="date"
            name="terminationDate"
            defaultValue={initialValues?.terminationDate ?? ""}
            className={inputClass}
          />
        </label>
      </div>

      {state?.error ? (
        <p className="rounded-lg border border-dlvc-danger/30 bg-dlvc-danger/10 px-3.5 py-2.5 text-[13px] font-medium text-dlvc-danger">
          {state.error}
        </p>
      ) : null}

      <div className="mt-1 flex items-center gap-3">
        <button
          type="submit"
          disabled={pending}
          className="flex h-10 items-center gap-1.5 rounded-[9px] bg-dlvc-sidebar px-5 text-[13.5px] font-semibold text-white transition-[filter,box-shadow,transform] duration-150 hover:not-disabled:-translate-y-px hover:not-disabled:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] hover:not-disabled:brightness-125 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {pending ? "Đang lưu…" : submitLabel}
        </button>
        <Link
          href={cancelHref}
          className="flex h-10 items-center rounded-[9px] border border-dlvc-border bg-dlvc-surface px-5 text-[13.5px] font-semibold text-dlvc-ink transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]"
        >
          Huỷ
        </Link>
      </div>
    </form>
  );
}
