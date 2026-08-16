// TODO: nội dung mẫu, cần khách hàng xác nhận — số liệu thống kê dưới đây (15+/30+/50+/100%)
// là placeholder minh hoạ, chưa phải số liệu thật của DLVC.
const STATS = [
  { n: "15+", l: "năm kinh nghiệm ngành hoá chất mạ" },
  { n: "30+", l: "sản phẩm hoá chất chuyên dụng" },
  { n: "50+", l: "nhà máy đang hợp tác" },
  { n: "100%", l: "sản phẩm có MSDS đầy đủ" },
];

export default function AboutSection() {
  return (
    <section id="about" className="bg-dlvc-surface py-16 min-[900px]:py-22">
      <div className="mx-auto grid max-w-292.5 grid-cols-1 gap-15 px-7 min-[900px]:grid-cols-2">
        <div>
          <div className="font-dlvc-mono text-[12px] font-semibold tracking-[0.12em] text-dlvc-cobalt uppercase">
            Giới thiệu công ty
          </div>
          <h2 className="mt-2.5 mb-4.5 text-[28px] font-extrabold text-dlvc-landing-ink">
            Đối tác hoá chất cho ngành xi mạ công nghiệp
          </h2>
          <p className="mb-4 text-[15px] text-dlvc-landing-ink-soft">
            Công ty TNHH Hóa chất Daliang VN (DLVC) chuyên sản xuất và cung cấp hoá chất phục vụ quy trình xử lý bề
            mặt kim loại – từ tẩy dầu, tẩy gỉ, hoạt hoá bề mặt cho đến phụ gia mạ kẽm, mạ niken, mạ đồng và dung dịch
            thụ động sau mạ.
          </p>
          <p className="mb-4 text-[15px] text-dlvc-landing-ink-soft">
            Nhà máy đặt tại KCN Đất Cuốc, Bắc Tân Uyên, TP. Hồ Chí Minh, phục vụ các nhà máy xi mạ, gia công kim loại
            trong và ngoài khu vực. Mọi sản phẩm đều đi kèm Phiếu an toàn hoá chất (MSDS) đầy đủ 16 mục theo đúng
            chuẩn quy định.
          </p>
          <a
            href="#contact"
            className="mt-1.5 inline-flex items-center gap-2 rounded-lg bg-dlvc-graphite px-6 py-3.25 text-[14.5px] font-bold text-white transition-[box-shadow,border] duration-150 hover:border hover:border-dlvc-cobalt hover:shadow-[0_0_20px_rgba(34,211,238,0.4)]"
          >
            Trao đổi nhu cầu của bạn
          </a>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {STATS.map((s) => (
            <div key={s.l} className="rounded-xl border border-dlvc-landing-border bg-dlvc-paper p-5">
              <div className="font-dlvc-mono text-[28px] font-bold text-dlvc-cobalt">{s.n}</div>
              <div className="mt-1 text-[12.5px] text-dlvc-landing-ink-soft">{s.l}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
