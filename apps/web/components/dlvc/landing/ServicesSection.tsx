const SERVICES = [
  { icon: "🔧", title: "Tư vấn kỹ thuật quy trình mạ", desc: "Khảo sát quy trình hiện tại và đề xuất giải pháp hoá chất phù hợp với từng dây chuyền." },
  { icon: "🧪", title: "Hỗ trợ pha chế & vận hành bể", desc: "Kỹ thuật viên hỗ trợ trực tiếp tại nhà máy trong giai đoạn triển khai và hiệu chỉnh bể mạ." },
  { icon: "📚", title: "Đào tạo vận hành", desc: "Hướng dẫn kỹ thuật viên nhà máy thao tác đúng, an toàn với từng loại hoá chất." },
  { icon: "🔬", title: "Kiểm tra chất lượng", desc: "Phân tích mẫu, kiểm soát nồng độ và chất lượng lớp mạ theo yêu cầu khách hàng." },
  { icon: "📄", title: "Hồ sơ an toàn hoá chất", desc: "Cung cấp đầy đủ MSDS 16 mục cho từng sản phẩm, phục vụ hồ sơ pháp lý của nhà máy." },
  { icon: "🚚", title: "Giao hàng đúng tiến độ", desc: "Đóng gói an toàn, giao hàng đúng hẹn để không làm gián đoạn sản xuất." },
];

export default function ServicesSection() {
  return (
    <section id="services" className="bg-dlvc-paper py-16 min-[900px]:py-22">
      <div className="mx-auto max-w-292.5 px-7">
        <div className="mb-11 max-w-160">
          <div className="font-dlvc-mono text-[12px] font-semibold tracking-[0.12em] text-dlvc-cobalt uppercase">
            Dịch vụ
          </div>
          <h2 className="mt-2.5 text-[32px] font-extrabold text-dlvc-landing-ink">
            Hỗ trợ kỹ thuật xuyên suốt quy trình
          </h2>
          <p className="mt-3 text-[15px] text-dlvc-landing-ink-soft">
            Không chỉ cung cấp hoá chất – đội ngũ kỹ thuật đồng hành cùng nhà máy từ pha chế đến vận hành ổn định.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4.5 min-[640px]:grid-cols-2 min-[900px]:grid-cols-3">
          {SERVICES.map((s) => (
            <div
              key={s.title}
              className="rounded-2xl border border-dlvc-landing-border bg-dlvc-surface p-6 transition-[transform,box-shadow,border-color] duration-150 hover:-translate-y-1 hover:border-dlvc-cobalt hover:shadow-[0_14px_32px_-12px_rgba(34,211,238,0.4)]"
            >
              <div className="mb-4 flex h-10.5 w-10.5 items-center justify-center rounded-[10px] bg-dlvc-cobalt-soft text-[19px] text-dlvc-cobalt-deep">
                {s.icon}
              </div>
              <h4 className="mb-2 text-[15.5px] font-bold text-dlvc-landing-ink">{s.title}</h4>
              <p className="text-[13px] text-dlvc-landing-ink-soft">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
