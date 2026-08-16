import ProcessStrip from "./ProcessStrip";

export default function Hero() {
  return (
    <section id="hero" className="overflow-hidden bg-dlvc-graphite pt-19 text-white">
      <div className="mx-auto grid max-w-292.5 grid-cols-1 items-center gap-12.5 px-7 pb-15 min-[900px]:grid-cols-[1.15fr_0.85fr]">
        <div>
          <div className="font-dlvc-mono text-[12px] font-semibold tracking-[0.12em] text-dlvc-amber uppercase">
            Hoá chất chuyên dụng ngành xi mạ
          </div>
          <h1 className="mt-4 mb-4.5 text-[32px] leading-[1.14] font-extrabold min-[900px]:text-[44px]">
            Đồng hành cùng từng lớp mạ –<br />
            từ tiền xử lý đến <span className="text-dlvc-amber">hoàn thiện</span>.
          </h1>
          <p className="mb-7.5 max-w-120 text-[16px] text-[#b7bec4]">
            Công ty TNHH Hóa chất Daliang VN cung cấp hoá chất tiền xử lý, phụ gia mạ và dung dịch thụ động cho các
            nhà máy xi mạ công nghiệp tại Việt Nam, kèm hồ sơ an toàn hoá chất (MSDS) đầy đủ cho từng sản phẩm.
          </p>
          <div className="flex flex-wrap gap-3.5">
            <a
              href="#products"
              className="inline-flex items-center gap-2 rounded-lg bg-dlvc-cobalt-deep px-6 py-3.25 text-[14.5px] font-bold text-white transition-[filter,box-shadow,transform] duration-150 hover:-translate-y-px hover:shadow-[0_0_0_4px_var(--color-dlvc-cobalt-soft),0_0_26px_rgba(34,211,238,0.4)] hover:brightness-[1.3]"
            >
              Xem sản phẩm
            </a>
            <a
              href="#contact"
              className="inline-flex items-center gap-2 rounded-lg border-[1.5px] border-white/35 px-6 py-3.25 text-[14.5px] font-bold text-white transition-[border-color,color,box-shadow] duration-150 hover:border-dlvc-cobalt hover:text-dlvc-cobalt hover:shadow-[0_0_20px_rgba(34,211,238,0.4)]"
            >
              Liên hệ tư vấn kỹ thuật
            </a>
          </div>
        </div>

        <div className="relative flex aspect-square items-center justify-center rounded-[20px] border border-[#2b323a] bg-[radial-gradient(circle_at_30%_30%,#3a4048,transparent_60%),linear-gradient(135deg,#20262c,#12161a)]">
          <div className="flex aspect-square w-[70%] items-center justify-center rounded-full border-2 border-dashed border-[#3d4650]">
            <div
              className="aspect-square w-[56%] rounded-full shadow-[0_0_60px_rgba(31,95,166,0.35)]"
              style={{
                background:
                  "conic-gradient(from 210deg, var(--color-dlvc-chrome), var(--color-dlvc-cobalt), var(--color-dlvc-amber), var(--color-dlvc-chrome))",
              }}
            />
          </div>
        </div>
      </div>

      <ProcessStrip />
    </section>
  );
}
