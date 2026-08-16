export type DeptDocCount = {
  id: number;
  name: string;
  color: string | null;
  count: number;
};

export default function DepartmentDocsCard({ items }: { items: DeptDocCount[] }) {
  const max = Math.max(1, ...items.map((i) => i.count));

  return (
    <div className="overflow-hidden rounded-[14px] border border-dlvc-border bg-dlvc-surface">
      <div className="border-b border-dlvc-border px-5 py-4">
        <h3 className="text-[14.5px] font-bold text-dlvc-ink">Tài liệu theo phòng ban</h3>
      </div>
      <div className="py-1.5">
        {items.map((dept) => {
          const color = dept.color ?? "var(--color-dlvc-accent)";
          const width = Math.round((dept.count / max) * 100);
          return (
            <div key={dept.id} className="flex items-center gap-3 border-b border-[#f1f2ed] px-5 py-3.5 last:border-b-0">
              <div className="h-2.5 w-2.5 shrink-0 rounded-[3px]" style={{ background: color }} />
              <div className="min-w-0 flex-1">
                <div className="text-[13px] font-semibold text-dlvc-ink">{dept.name}</div>
                <div className="mt-1.25 h-1.25 overflow-hidden rounded-[3px] bg-dlvc-bg">
                  <div className="h-full rounded-[3px]" style={{ width: `${width}%`, background: color }} />
                </div>
              </div>
              <div className="font-dlvc-mono text-[12.5px] text-dlvc-ink-soft">{dept.count}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
