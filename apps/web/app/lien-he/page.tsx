import type { Metadata } from "next";
import LandingHeader from "@/components/mock/LandingHeader";
import LandingFooter from "@/components/mock/LandingFooter";

export const metadata: Metadata = {
  title: "Liên hệ · Daliang",
  description: "Liên hệ với Daliang để được tư vấn triển khai hệ thống quản lý tài liệu cho doanh nghiệp.",
};

export default function LienHePage() {
  return (
    <div className="flex min-h-screen flex-col bg-page">
      <LandingHeader />

      <section className="flex flex-1 flex-col items-center gap-4 px-6 py-16 text-center">
        <h1 className="text-[30px] font-bold text-strong sm:text-[36px]">Liên hệ</h1>
        <p className="max-w-xl text-[15px] text-muted">
          Cần tư vấn triển khai hệ thống quản lý tài liệu cho doanh nghiệp của bạn?
        </p>
        <a
          href="mailto:lienhe@daliang.vn"
          className="flex h-11 items-center rounded bg-accent px-6 text-[14px] font-semibold text-card hover:bg-accent-hover"
        >
          lienhe@daliang.vn
        </a>
      </section>

      <LandingFooter />
    </div>
  );
}
