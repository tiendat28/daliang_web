import { notFound } from "next/navigation";
import { activityLogs, docs } from "@/lib/mock-data";

const BODY_LINE_WIDTHS = ["100%", "96%", "100%", "72%", "98%", "88%", "100%", "64%"];

const VERSION_TIMELINE = [
  { version: "v3 — hiện hành", meta: "Nguyễn Văn A · 04/08/2026 · Cập nhật theo tiêu chuẩn mới" },
  { version: "v2", meta: "Nguyễn Văn A · 12/05/2026 · Sửa lỗi mục 4.2" },
  { version: "v1", meta: "Trần Thị B · 02/01/2026 · Phát hành lần đầu" },
];

export default async function DocumentDetailPage(props: PageProps<"/documents/[id]">) {
  const { id } = await props.params;
  const doc = docs.find((d) => d.id === id);
  if (!doc) notFound();

  return (
    <div className="grid min-h-screen md:grid-cols-[1fr_380px]">
      <div className="flex flex-col">
        <div className="flex items-center justify-between gap-4 border-b border-border px-8 py-5">
          <div>
            <div className="font-mono text-[12px] text-muted">
              {doc.folder} · {doc.code}
            </div>
            <h1 className="mt-1 text-[19px] font-semibold text-strong">{doc.title}</h1>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <button
              type="button"
              className="h-9 rounded border border-border px-4 text-[14px] text-body"
            >
              Chia sẻ
            </button>
            <button
              type="button"
              className="h-9 rounded bg-accent px-4 text-[14px] font-semibold text-card hover:bg-accent-hover"
            >
              Tải về
            </button>
          </div>
        </div>

        <div className="flex flex-1 items-center justify-center bg-border-light p-7">
          <div className="w-[390px] border border-border-strong bg-card px-8 py-[34px]">
            <div className="mb-4 h-[9px] rounded-sm bg-border-strong" style={{ width: "58%" }} />
            <div className="mb-6 h-[9px] rounded-sm bg-border-strong" style={{ width: "44%" }} />
            <div className="flex flex-col gap-3">
              {BODY_LINE_WIDTHS.map((width, i) => (
                <div
                  key={i}
                  className="h-[6px] rounded-sm"
                  style={{
                    width,
                    background: width === "72%" ? "var(--color-mark)" : "var(--color-border-light)",
                  }}
                />
              ))}
            </div>
            <div className="mt-8 flex items-center justify-between border-t border-border-light pt-3 font-mono text-[11px] text-muted">
              <span>Trang 3 / 12</span>
              <span>
                {doc.code} · v{doc.version}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col divide-y divide-border border-t border-border md:border-t-0 md:border-l">
        <div className="flex flex-col gap-2.5 px-6 py-5">
          <div className="mb-1 text-[11px] font-semibold tracking-wide text-faint uppercase">
            Thông tin
          </div>
          <InfoRow
            label="Trạng thái"
            value={doc.status === "approved" ? "Đã duyệt · Công khai" : "Chờ duyệt"}
            accent
          />
          <InfoRow label="Phiên bản" value={`v${doc.version}`} />
          <InfoRow label="Dung lượng" value={doc.sizeLabel} />
          <InfoRow label="Người tải lên" value={doc.uploadedBy} />
          <InfoRow label="Người duyệt" value="Lê Văn C" />
        </div>

        <div className="flex flex-col gap-4 px-6 py-5">
          <div className="text-[11px] font-semibold tracking-wide text-faint uppercase">Phiên bản</div>
          <div className="flex flex-col gap-4">
            {VERSION_TIMELINE.map((item, i) => (
              <div key={item.version} className="flex gap-3">
                <span
                  className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${i === 0 ? "bg-accent" : "bg-border-strong"}`}
                />
                <div className="min-w-0">
                  <div className="text-[14px] font-semibold text-strong">{item.version}</div>
                  <div className="truncate text-[12px] text-muted">{item.meta}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-3 px-6 py-5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold tracking-wide text-faint uppercase">Nhật ký</span>
            <span className="cursor-pointer text-[12px] font-semibold text-accent">Xem tất cả</span>
          </div>
          <div className="flex flex-col gap-2.5">
            {activityLogs.slice(0, 4).map((log) => (
              <div key={log.id} className="flex items-center justify-between gap-3 text-[13px]">
                <span className="truncate text-body">
                  {log.actor} {log.action}
                </span>
                <span className="shrink-0 font-mono text-[11px] text-faint">{log.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="flex items-center justify-between text-[13px]">
      <span className="text-muted">{label}</span>
      <span className={accent ? "font-semibold text-accent-hover" : "text-body"}>{value}</span>
    </div>
  );
}
