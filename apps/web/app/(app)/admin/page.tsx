import FolderSidebar from "@/components/mock/FolderSidebar";

const TABS = ["Phân quyền", "Người dùng", "Phòng ban", "Nhật ký", "Cấu hình"];

type PermissionRow = {
  subject: string;
  description: string;
  values: [boolean, boolean, boolean, boolean];
};

const ROWS: PermissionRow[] = [
  { subject: "Phòng Kỹ thuật", description: "14 người", values: [true, true, true, false] },
  {
    subject: "Nguyễn Văn A",
    description: "Trưởng phòng Kỹ thuật",
    values: [true, true, true, true],
  },
  { subject: "Phòng Kinh doanh", description: "9 người", values: [true, true, false, false] },
  {
    subject: "Khách vãng lai",
    description: "Chỉ tài liệu công khai",
    values: [true, false, false, false],
  },
];

function Mark({ granted }: { granted: boolean }) {
  return (
    <span className={granted ? "font-bold text-confirm" : "text-border-strong"}>
      {granted ? "✓" : "—"}
    </span>
  );
}

export default function AdminPage() {
  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex items-center gap-6 border-b border-border px-6 text-[14px]">
        {TABS.map((tab) => (
          <span
            key={tab}
            className={
              tab === "Phân quyền"
                ? "relative flex h-[46px] items-center font-semibold text-accent after:absolute after:right-0 after:bottom-0 after:left-0 after:h-[2px] after:bg-accent"
                : "flex h-[46px] cursor-default items-center text-muted"
            }
          >
            {tab}
          </span>
        ))}
      </div>

      <div className="flex min-h-0 flex-1">
        <FolderSidebar showShortcuts={false} className="w-[200px]" />

        <div className="flex min-w-0 flex-1 flex-col overflow-y-auto">
          <div className="flex items-center justify-between px-6 py-4">
            <div>
              <div className="text-[15px] font-semibold text-strong">
                Quyền trên thư mục Kỹ thuật
              </div>
              <div className="mt-0.5 text-[12px] text-muted">Áp dụng cho cả thư mục con</div>
            </div>
            <button type="button" className="h-9 rounded border border-border px-4 text-[14px] text-body">
              + Cấp quyền
            </button>
          </div>

          <div className="grid grid-cols-[1fr_90px_90px_90px_90px] border-b border-border bg-subtle">
            <div className="px-4 py-2 font-mono text-[11px] font-semibold tracking-wide text-muted uppercase">
              Đối tượng
            </div>
            <div className="px-2 py-2 text-center font-mono text-[11px] font-semibold tracking-wide text-muted uppercase">
              Xem
            </div>
            <div className="px-2 py-2 text-center font-mono text-[11px] font-semibold tracking-wide text-muted uppercase">
              Tải
            </div>
            <div className="px-2 py-2 text-center font-mono text-[11px] font-semibold tracking-wide text-muted uppercase">
              Sửa
            </div>
            <div className="px-2 py-2 text-center font-mono text-[11px] font-semibold tracking-wide text-muted uppercase">
              Quản lý
            </div>
          </div>

          {ROWS.map((row) => (
            <div
              key={row.subject}
              className="grid grid-cols-[1fr_90px_90px_90px_90px] items-center border-b border-border-light"
            >
              <div className="px-4 py-3.5">
                <div className="text-[14px] font-semibold text-strong">{row.subject}</div>
                <div className="text-[12px] text-muted">{row.description}</div>
              </div>
              {row.values.map((granted, i) => (
                <div key={i} className="px-2 py-3.5 text-center">
                  <Mark granted={granted} />
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
