import type { Metadata } from "next";
import LandingHeader from "@/components/mock/LandingHeader";
import LandingFooter from "@/components/mock/LandingFooter";

export const metadata: Metadata = {
  title: "Về chúng tôi · Daliang",
  description: "Câu chuyện, sứ mệnh và định hướng của Daliang trong việc xây dựng hệ thống quản lý tài liệu doanh nghiệp.",
};

export default function VeChungToiPage() {
  return (
    <div className="flex min-h-screen flex-col bg-page">
      <LandingHeader />

      <section className="flex flex-col items-center gap-4 bg-panel px-6 py-16 text-center">
        <h1 className="text-[30px] font-bold text-strong sm:text-[36px]">Về chúng tôi</h1>
        <p className="max-w-xl text-[15px] text-muted">
          Daliang được xây dựng để giải quyết bài toán tài liệu phân tán, khó tra cứu và thiếu
          kiểm soát phiên bản trong doanh nghiệp.
        </p>
      </section>

      <section className="flex-1 px-6 py-16">
        <div className="mx-auto flex max-w-2xl flex-col gap-6 text-[15px] text-body">
          <p>
            Chúng tôi tập trung vào trải nghiệm tìm kiếm nhanh, phân quyền rõ ràng và quy trình
            duyệt tài liệu chặt chẽ, giúp mọi phòng ban — từ kỹ thuật, kinh doanh đến kế toán và
            nhân sự — làm việc trên cùng một nguồn dữ liệu tin cậy.
          </p>
        </div>
      </section>

      <LandingFooter />
    </div>
  );
}
