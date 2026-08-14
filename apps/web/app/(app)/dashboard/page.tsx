const STAT_CARDS = [
  { label: "Tài liệu", value: "412", note: "+18 trong tháng", noteClass: "text-confirm" },
  { label: "Lượt tải", value: "1.284", note: "30 ngày qua", noteClass: "text-muted" },
  { label: "Chờ duyệt", value: "3", note: "cũ nhất 6 ngày", noteClass: "text-muted", valueClass: "text-warning-text" },
];

const WEEK_BARS = [
  { label: "T23", height: 38, strong: false },
  { label: "T24", height: 52, strong: false },
  { label: "T25", height: 44, strong: false },
  { label: "T26", height: 71, strong: false },
  { label: "T27", height: 63, strong: false },
  { label: "T28", height: 88, strong: true },
  { label: "T29", height: 100, strong: true },
];

const TOP_DOCS = [
  { title: "QT-KT-014 · Quy trình kiểm tra chất lượng đầu vào", count: 342 },
  { title: "DM-NCC-03 · Danh mục nhà cung cấp đã đánh giá", count: 298 },
  { title: "CS-BH-2026 · Chính sách bảo hành sản phẩm 2026", count: 210 },
];

export default function DashboardPage() {
  return (
    <div className="flex-1 overflow-y-auto p-8">
      <h1 className="mb-6 text-[20px] font-semibold text-strong">Tổng quan</h1>

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        {STAT_CARDS.map((card) => (
          <div key={card.label} className="rounded-[5px] border border-border p-4">
            <div className="text-[13px] text-muted">{card.label}</div>
            <div className={`mt-1 text-[28px] font-bold ${card.valueClass ?? "text-strong"}`}>
              {card.value}
            </div>
            <div className={`mt-1 text-[12px] ${card.noteClass}`}>{card.note}</div>
          </div>
        ))}
      </div>

      <div className="mb-6 rounded-[5px] border border-border p-4">
        <div className="mb-4 text-[14px] font-semibold text-strong">Lượt xem &amp; tải theo tuần</div>
        <div className="flex h-[110px] items-end gap-[9px]">
          {WEEK_BARS.map((bar) => (
            <div
              key={bar.label}
              className={`flex-1 rounded-t-[2px] ${bar.strong ? "bg-accent" : "bg-accent/35"}`}
              style={{ height: `${bar.height}%` }}
            />
          ))}
        </div>
        <div className="mt-2 flex gap-[9px]">
          {WEEK_BARS.map((bar) => (
            <div key={bar.label} className="flex-1 text-center font-mono text-[11px] text-faint">
              {bar.label}
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-[5px] border border-border p-4">
        <div className="mb-3 text-[14px] font-semibold text-strong">Tài liệu được tải nhiều nhất</div>
        <div className="flex flex-col gap-2.5">
          {TOP_DOCS.map((item) => (
            <div key={item.title} className="flex items-center justify-between gap-4 text-[14px]">
              <span className="truncate text-body">{item.title}</span>
              <span className="shrink-0 font-mono text-[13px] text-muted">{item.count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
