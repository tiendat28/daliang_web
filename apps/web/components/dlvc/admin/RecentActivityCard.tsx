import { formatRelativeVn } from "@/lib/dlvc/format";
import { DOCUMENT_ACTION_LABEL } from "@/lib/dlvc/labels";

export type ActivityItem = {
  id: number;
  action: string;
  performedAt: Date;
  performerName: string;
  documentTitle: string;
  departmentName: string;
  departmentColor: string | null;
};

export default function RecentActivityCard({ items }: { items: ActivityItem[] }) {
  return (
    <div className="overflow-hidden rounded-[14px] border border-dlvc-border bg-dlvc-surface">
      <div className="flex items-center justify-between border-b border-dlvc-border px-5 py-4">
        <h3 className="text-[14.5px] font-bold text-dlvc-ink">Hoạt động gần đây</h3>
      </div>
      <div className="py-1.5">
        {items.length === 0 ? (
          <p className="px-5 py-4 text-[13px] text-dlvc-ink-soft">Chưa có hoạt động nào.</p>
        ) : (
          items.map((item) => (
            <div key={item.id} className="flex gap-3 border-b border-[#f1f2ed] px-5 py-3 last:border-b-0">
              <div
                className="w-1 shrink-0 rounded"
                style={{ background: item.departmentColor ?? "var(--color-dlvc-accent)" }}
              />
              <div className="text-[13px] text-dlvc-ink">
                <span className="font-semibold">{item.performerName}</span>{" "}
                {DOCUMENT_ACTION_LABEL[item.action] ?? item.action} <b>{item.documentTitle}</b>
                <div className="mt-0.5 text-[11.5px] text-dlvc-ink-soft">
                  {item.departmentName} · {formatRelativeVn(item.performedAt)}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
