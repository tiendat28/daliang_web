"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

type Dept = { id: number; departmentName: string; color: string | null };

export default function DepartmentTabs({ departments }: { departments: Dept[] }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const active = searchParams.get("dept") ?? String(departments[0]?.id ?? "");

  function setDept(id: string) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("dept", id);
    router.replace(`${pathname}?${params.toString()}`);
  }

  return (
    <div className="mb-4.5 flex flex-wrap gap-2">
      {departments.map((d) => {
        const isActive = active === String(d.id);
        const color = d.color ?? "var(--color-dlvc-accent)";
        return (
          <button
            key={d.id}
            type="button"
            onClick={() => setDept(String(d.id))}
            style={isActive ? { background: color, borderColor: color } : undefined}
            className={
              isActive
                ? "flex items-center gap-2 rounded-[9px] border px-3.75 py-2 text-[13px] font-semibold text-white"
                : "flex items-center gap-2 rounded-[9px] border border-dlvc-border bg-dlvc-surface px-3.75 py-2 text-[13px] font-semibold text-dlvc-ink-soft transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]"
            }
          >
            <span
              className="h-2 w-2 shrink-0 rounded-full"
              style={{ background: isActive ? "#fff" : color }}
            />
            {d.departmentName}
          </button>
        );
      })}
    </div>
  );
}
