import Link from "next/link";
import type { Metadata } from "next";
import LangToggle from "@/components/mock/LangToggle";

export const metadata: Metadata = {
  title: "Daliang · Hệ thống quản lý tài liệu",
  description: "Daliang xây dựng hệ thống quản lý tài liệu giúp doanh nghiệp lưu trữ, tra cứu và kiểm soát phiên bản tài liệu tập trung.",
};

const STATS = [
  { value: "1.200+", label: "tài liệu đang quản lý" },
  { value: "8", label: "phòng ban sử dụng" },
  { value: "OCR", label: "tự động nhận diện văn bản" },
  { value: "99,9%", label: "thời gian hoạt động" },
];

const FEATURES = [
  {
    title: "Lưu trữ tập trung",
    desc: "Toàn bộ tài liệu kỹ thuật, hợp đồng, quy trình được tổ chức theo thư mục phòng ban, tránh thất lạc và trùng lặp phiên bản.",
  },
  {
    title: "Tìm kiếm toàn văn",
    desc: "Tìm theo tên file hoặc nội dung bên trong, kể cả tài liệu scan nhờ OCR tự động khi tải lên.",
  },
  {
    title: "Phân quyền chi tiết",
    desc: "Kiểm soát ai được xem, tải về, chỉnh sửa hay quản lý theo từng vai trò — từ quản trị viên đến khách/đối tác.",
  },
  {
    title: "Quy trình duyệt & phiên bản",
    desc: "Theo dõi trạng thái nháp — chờ duyệt — đã duyệt và lịch sử phiên bản của từng tài liệu.",
  },
];

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-page">
      <header className="flex h-15 shrink-0 items-center gap-6 border-b border-border bg-card px-6">
        <Link href="/" className="text-[17px] font-bold text-strong">
          Daliang
        </Link>

        <nav className="flex items-center gap-5 text-[14px]">
          <a href="#tinh-nang" className="text-muted hover:text-body">
            Tính năng
          </a>
          <a href="#ve-chung-toi" className="text-muted hover:text-body">
            Về chúng tôi
          </a>
          <a href="#lien-he" className="text-muted hover:text-body">
            Liên hệ
          </a>
        </nav>

        <div className="flex-1" />

        <LangToggle />

        <Link
          href="/portal"
          className="h-9 items-center rounded border border-border px-4 text-[14px] text-body hover:text-strong hidden sm:flex"
        >
          Cổng tra cứu
        </Link>

        <Link
          href="/login"
          className="flex h-9 items-center rounded bg-accent px-4 text-[14px] font-semibold text-card hover:bg-accent-hover"
        >
          Đăng nhập nội bộ
        </Link>
      </header>

      <section className="flex flex-col items-center gap-5 bg-panel px-6 py-20 text-center">
        <span className="rounded-full bg-accent-subtle px-3 py-1 text-[13px] font-semibold text-accent-hover">
          Hệ thống quản lý tài liệu doanh nghiệp
        </span>
        <h1 className="max-w-2xl text-[34px] font-bold leading-tight text-strong sm:text-[42px]">
          Số hoá kho tài liệu, tra cứu trong vài giây
        </h1>
        <p className="max-w-xl text-[15px] text-muted">
          Daliang giúp doanh nghiệp lưu trữ, phân quyền và tìm kiếm mọi tài liệu — từ quy trình
          kỹ thuật, hợp đồng đến báo cáo tài chính — trên một nền tảng duy nhất.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <Link
            href="/portal"
            className="flex h-11 items-center rounded bg-accent px-6 text-[14px] font-semibold text-card hover:bg-accent-hover"
          >
            Xem cổng tra cứu công khai
          </Link>
          <Link
            href="/login"
            className="flex h-11 items-center rounded border border-border bg-card px-6 text-[14px] font-semibold text-body hover:text-strong"
          >
            Đăng nhập nội bộ
          </Link>
        </div>
      </section>

      <section className="border-b border-border bg-card px-6 py-10">
        <div className="mx-auto grid max-w-4xl grid-cols-2 gap-6 sm:grid-cols-4">
          {STATS.map((stat) => (
            <div key={stat.label} className="flex flex-col items-center text-center">
              <span className="text-[24px] font-bold text-accent">{stat.value}</span>
              <span className="text-[13px] text-muted">{stat.label}</span>
            </div>
          ))}
        </div>
      </section>

      <section id="tinh-nang" className="px-6 py-16">
        <div className="mx-auto max-w-4xl">
          <h2 className="text-center text-[24px] font-bold text-strong">Tính năng chính</h2>
          <p className="mx-auto mt-2 max-w-xl text-center text-[14px] text-muted">
            Được thiết kế cho nhu cầu quản lý tài liệu của doanh nghiệp sản xuất và văn phòng.
          </p>

          <div className="mt-10 grid gap-5 sm:grid-cols-2">
            {FEATURES.map((f) => (
              <div key={f.title} className="rounded border border-border bg-card p-5">
                <h3 className="text-[15px] font-semibold text-strong">{f.title}</h3>
                <p className="mt-2 text-[14px] text-muted">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="ve-chung-toi" className="border-y border-border bg-subtle px-6 py-16">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-[24px] font-bold text-strong">Về chúng tôi</h2>
          <p className="mt-4 text-[15px] text-muted">
            Daliang được xây dựng để giải quyết bài toán tài liệu phân tán, khó tra cứu và thiếu
            kiểm soát phiên bản trong doanh nghiệp. Chúng tôi tập trung vào trải nghiệm tìm kiếm
            nhanh, phân quyền rõ ràng và quy trình duyệt tài liệu chặt chẽ, giúp mọi phòng ban —
            từ kỹ thuật, kinh doanh đến kế toán và nhân sự — làm việc trên cùng một nguồn dữ liệu
            tin cậy.
          </p>
        </div>
      </section>

      <section id="lien-he" className="px-6 py-16">
        <div className="mx-auto flex max-w-2xl flex-col items-center gap-4 text-center">
          <h2 className="text-[24px] font-bold text-strong">Liên hệ</h2>
          <p className="text-[14px] text-muted">
            Cần tư vấn triển khai hệ thống quản lý tài liệu cho doanh nghiệp của bạn?
          </p>
          <a
            href="mailto:lienhe@daliang.vn"
            className="flex h-11 items-center rounded bg-accent px-6 text-[14px] font-semibold text-card hover:bg-accent-hover"
          >
            lienhe@daliang.vn
          </a>
        </div>
      </section>

      <footer className="border-t border-border bg-card px-6 py-6">
        <div className="mx-auto flex max-w-4xl flex-col items-center justify-between gap-2 text-[13px] text-faint sm:flex-row">
          <span>© 2026 Daliang. Đã đăng ký bản quyền.</span>
          <div className="flex items-center gap-4">
            <Link href="/portal" className="hover:text-muted">
              Cổng tra cứu
            </Link>
            <Link href="/login" className="hover:text-muted">
              Đăng nhập
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
