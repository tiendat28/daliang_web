const NAV_LINKS = [
  { href: "#about", label: "Giới thiệu" },
  { href: "#products", label: "Sản phẩm" },
  { href: "#services", label: "Dịch vụ" },
  { href: "#contact", label: "Liên hệ" },
];

export default function LandingFooter() {
  return (
    <footer className="bg-dlvc-graphite py-12.5 text-[#9ba5ad]">
      <div className="mx-auto max-w-292.5 px-7">
        <div className="mb-5.5 grid grid-cols-1 gap-10 border-b border-[#2b323a] pb-8.5 min-[900px]:grid-cols-[1.3fr_1fr_1fr]">
          <div>
            <div className="mb-3.5 flex items-center gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-linear-to-br from-dlvc-cobalt to-dlvc-cobalt-deep text-[12px] font-extrabold text-[#0b1620]">
                DV
              </div>
              <span className="text-[14.5px] font-bold text-white">DALIANG VN</span>
            </div>
            <p className="max-w-70 text-[13px]">
              Hoá chất chuyên dụng cho ngành xi mạ công nghiệp – tiền xử lý, phụ gia mạ, thụ động – kèm hồ sơ an toàn
              hoá chất đầy đủ.
            </p>
          </div>

          <div>
            <h5 className="mb-3.5 text-[13px] tracking-[0.03em] text-white">Điều hướng</h5>
            <ul className="flex flex-col gap-2.25">
              {NAV_LINKS.map((l) => (
                <li key={l.href}>
                  <a href={l.href} className="text-[13.5px] text-[#9ba5ad] hover:text-dlvc-cobalt">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h5 className="mb-3.5 text-[13px] tracking-[0.03em] text-white">Liên hệ</h5>
            <ul className="flex flex-col gap-2.25 text-[13.5px]">
              <li>KCN Đất Cuốc, Bắc Tân Uyên, TP.HCM</li>
              <li>0274-3651 005-009</li>
              <li>lienhe@daliangvn.com</li>
            </ul>
          </div>
        </div>

        <div className="flex flex-wrap justify-between gap-2.5 text-[12px] text-[#6e7880]">
          <span>© 2026 Công ty TNHH Hóa chất Daliang VN. Bảo lưu mọi quyền.</span>
          <span>Nội dung mẫu – vui lòng chỉnh sửa trước khi sử dụng chính thức.</span>
        </div>
      </div>
    </footer>
  );
}
