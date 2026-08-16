"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

type Dept = { id: number; departmentName: string };

export default function EmployeesFilterBar({ departments }: { departments: Dept[] }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const activeDept = searchParams.get("dept") ?? "";
  const [query, setQuery] = useState(searchParams.get("q") ?? "");

  useEffect(() => {
    const handle = setTimeout(() => {
      const params = new URLSearchParams(searchParams.toString());
      if (query) params.set("q", query);
      else params.delete("q");
      const next = params.toString();
      router.replace(next ? `${pathname}?${next}` : pathname);
    }, 300);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  function setDept(id: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (id) params.set("dept", id);
    else params.delete("dept");
    const next = params.toString();
    router.replace(next ? `${pathname}?${next}` : pathname);
  }

  return (
    <div className="mb-4.5 flex flex-wrap items-center gap-2.5">
      <button
        type="button"
        onClick={() => setDept("")}
        className={
          activeDept === ""
            ? "rounded-lg bg-dlvc-sidebar px-3.25 py-1.75 text-[12.5px] font-medium text-white"
            : "rounded-lg border border-dlvc-border bg-dlvc-surface px-3.25 py-1.75 text-[12.5px] font-medium text-dlvc-ink-soft transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]"
        }
      >
        Tất cả
      </button>
      {departments.map((d) => (
        <button
          key={d.id}
          type="button"
          onClick={() => setDept(String(d.id))}
          className={
            activeDept === String(d.id)
              ? "rounded-lg bg-dlvc-sidebar px-3.25 py-1.75 text-[12.5px] font-medium text-white"
              : "rounded-lg border border-dlvc-border bg-dlvc-surface px-3.25 py-1.75 text-[12.5px] font-medium text-dlvc-ink-soft transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]"
          }
        >
          {d.departmentName}
        </button>
      ))}

      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Tìm theo tên hoặc mã nhân viên…"
        className="ml-auto h-9 w-full max-w-70 rounded-lg border border-dlvc-border bg-dlvc-surface px-3 text-[13px] text-dlvc-ink transition-[border-color,box-shadow] duration-150 focus:border-dlvc-accent focus:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] focus:outline-none"
      />
    </div>
  );
}
