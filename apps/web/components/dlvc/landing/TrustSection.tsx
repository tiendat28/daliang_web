const TRUST_ITEMS = [
  { title: "Hồ sơ MSDS chuẩn 16 mục", desc: "Đầy đủ thông tin an toàn, GHS, vận chuyển cho từng sản phẩm." },
  { title: "Hỗ trợ kỹ thuật tại nhà máy", desc: "Đội ngũ đồng hành trực tiếp khi triển khai và xử lý sự cố bể mạ." },
  { title: "Nguồn hoá chất ổn định", desc: "Kiểm soát chất lượng chặt chẽ, đảm bảo tính nhất quán giữa các lô hàng." },
];

export default function TrustSection() {
  return (
    <section className="border-y border-dlvc-landing-border bg-dlvc-surface py-14">
      <div className="mx-auto grid max-w-292.5 grid-cols-1 gap-7 px-7 min-[900px]:grid-cols-3">
        {TRUST_ITEMS.map((item) => (
          <div key={item.title} className="flex gap-3.5">
            <div className="flex h-8.5 w-8.5 shrink-0 items-center justify-center rounded-full bg-dlvc-amber-soft font-bold text-dlvc-amber">
              ✓
            </div>
            <div>
              <h4 className="mb-1.25 text-[14.5px] font-bold text-dlvc-landing-ink">{item.title}</h4>
              <p className="text-[13px] text-dlvc-landing-ink-soft">{item.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
