import Link from "next/link";
import { docs } from "@/lib/mock-data";
import FileBadge from "@/components/mock/FileBadge";
import LangToggle from "@/components/mock/LangToggle";

export default function PortalPage() {
  const publicDocs = docs.filter((doc) => doc.visibility === "public");

  return (
    <div className="flex min-h-screen flex-col bg-page">
      <header className="flex h-[54px] shrink-0 items-center justify-between border-b border-border px-6">
        <span className="text-[15px] font-semibold text-strong">Cổng tra cứu tài liệu</span>
        <div className="flex items-center gap-3">
          <LangToggle />
          <Link
            href="/login"
            className="flex h-8 items-center rounded border border-border px-3 text-[13px] text-body"
          >
            Đăng nhập nội bộ
          </Link>
        </div>
      </header>

      <div className="flex flex-col items-center gap-4 bg-panel px-6 py-12 text-center">
        <h1 className="text-[22px] font-semibold text-strong">Tra cứu tài liệu đã công bố</h1>
        <input
          type="text"
          placeholder="Tìm theo tên tài liệu…"
          className="h-11 w-full max-w-[460px] rounded border border-border bg-card px-4 text-[14px] text-body placeholder:text-faint focus:outline-none"
        />
        <span className="text-[13px] text-muted">128 tài liệu công khai · cập nhật 09/08/2026</span>
      </div>

      <div className="mx-auto w-full max-w-3xl flex-1 px-6 py-6">
        <div className="flex flex-col">
          {publicDocs.map((doc) => (
            <Link
              key={doc.id}
              href={`/documents/${doc.id}`}
              className="flex items-center gap-4 border-b border-border-light py-3.5"
            >
              <FileBadge kind={doc.kind} />
              <div className="min-w-0 flex-1">
                <div className="truncate text-[15px] font-semibold text-strong">{doc.title}</div>
                <div className="truncate text-[13px] text-muted">
                  {doc.code} · v{doc.version} · {doc.updatedAt}
                </div>
              </div>
              <span className="shrink-0 text-[14px] font-semibold text-accent">Xem</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
