"use client";

import { useActionState } from "react";
import Link from "next/link";
import type { DocumentFormState } from "../actions";

type Dept = { id: number; departmentName: string };
type DocType = { id: number; typeName: string; departmentId: number | null };

const inputClass =
  "h-10 w-full rounded-[9px] border border-dlvc-border bg-dlvc-bg px-3 text-[13.5px] text-dlvc-ink transition-[border-color,box-shadow] duration-150 focus:border-dlvc-accent focus:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] focus:outline-none";
const labelClass = "flex flex-col gap-1.5 text-[12.5px] font-medium text-dlvc-ink-soft";

export default function UploadForm({
  action,
  departments,
  documentTypes,
  defaultDepartmentId,
}: {
  action: (state: DocumentFormState, formData: FormData) => Promise<DocumentFormState>;
  departments: Dept[];
  documentTypes: DocType[];
  defaultDepartmentId?: number;
}) {
  const [state, formAction, pending] = useActionState<DocumentFormState, FormData>(action, undefined);

  return (
    <form action={formAction} className="flex flex-col gap-4">
      <label className={labelClass}>
        Tên tài liệu
        <input name="title" required placeholder="Ví dụ: Quy trình vận hành máy CNC-04" className={inputClass} />
      </label>

      <div className="grid grid-cols-1 gap-4 min-[560px]:grid-cols-2">
        <label className={labelClass}>
          Phòng ban
          <select name="departmentId" required defaultValue={defaultDepartmentId ?? ""} className={inputClass}>
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
          Loại tài liệu
          <select name="documentTypeId" defaultValue="" className={inputClass}>
            <option value="">— Không —</option>
            {documentTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.typeName}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label className={labelClass}>
        Tệp tài liệu
        <input
          type="file"
          name="file"
          required
          className="rounded-[9px] border border-dlvc-border bg-dlvc-bg px-3 py-2 text-[13.5px] text-dlvc-ink file:mr-3 file:rounded-md file:border-0 file:bg-dlvc-sidebar file:px-3 file:py-1.5 file:text-[12.5px] file:font-semibold file:text-white"
        />
      </label>

      <label className={labelClass}>
        Ngày hết hạn (nếu có)
        <input type="date" name="expiryDate" className={inputClass} />
      </label>

      <label className={labelClass}>
        Ghi chú
        <textarea name="notes" rows={3} className={`${inputClass} h-auto resize-vertical py-2`} />
      </label>

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
          {pending ? "Đang tải lên…" : "Tải lên"}
        </button>
        <Link
          href="/dlvc/admin/documents"
          className="flex h-10 items-center rounded-[9px] border border-dlvc-border bg-dlvc-surface px-5 text-[13.5px] font-semibold text-dlvc-ink transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]"
        >
          Huỷ
        </Link>
      </div>
    </form>
  );
}
