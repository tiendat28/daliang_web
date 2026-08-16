// TODO: nội dung mẫu, cần khách hàng xác nhận — tên nhóm sản phẩm và mã sản phẩm
// (EB-C, FD-23, NI-534C...) dưới đây là ví dụ minh hoạ, cần đối chiếu lại danh mục
// sản phẩm thực tế của DLVC trước khi đăng chính thức.
const STAGES = [
  {
    num: "01",
    title: "Tiền xử lý",
    desc: "Tẩy dầu, tẩy gỉ và hoạt hoá bề mặt kim loại, đảm bảo bề mặt sạch, đồng nhất trước khi đưa vào bể mạ.",
    codes: ["EB-C", "FD-23"],
    accent: "var(--color-dlvc-chrome)",
  },
  {
    num: "02",
    title: "Phụ gia mạ",
    desc: "Phụ gia cho mạ kẽm, mạ niken, mạ đồng – kiểm soát độ bóng, độ dày và độ bám dính của lớp mạ.",
    codes: ["NI-534C", "CU-4", "CUB-01", "DN-958"],
    accent: "var(--color-dlvc-cobalt)",
  },
  {
    num: "03",
    title: "Thụ động",
    desc: "Dung dịch thụ động sau mạ, tăng khả năng chống ăn mòn và kéo dài tuổi thọ lớp mạ hoàn thiện.",
    codes: ["CRT-650", "CRT-68", "CHB-9742"],
    accent: "var(--color-dlvc-amber)",
  },
];

export default function ProductsSection() {
  return (
    <section id="products" className="bg-dlvc-graphite-soft py-16 text-white min-[900px]:py-22">
      <div className="mx-auto max-w-292.5 px-7">
        <div className="mb-11 max-w-160">
          <div className="font-dlvc-mono text-[12px] font-semibold tracking-[0.12em] text-dlvc-amber uppercase">
            Dòng sản phẩm
          </div>
          <h2 className="mt-2.5 text-[32px] font-extrabold">Hoá chất theo từng giai đoạn xử lý bề mặt</h2>
          <p className="mt-3 text-[15px] text-[#aeb6bc]">
            Ba nhóm sản phẩm chính, tương ứng với ba giai đoạn của một quy trình xi mạ hoàn chỉnh.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-5 min-[900px]:grid-cols-3">
          {STAGES.map((stage) => (
            <div
              key={stage.num}
              className="relative overflow-hidden rounded-2xl border border-[#2c333b] bg-[#1d232a] p-7 pt-8 transition-[transform,box-shadow,border-color] duration-150 hover:-translate-y-1 hover:border-dlvc-cobalt hover:shadow-[0_0_0_1px_rgba(34,211,238,0.4),0_16px_36px_-14px_rgba(0,0,0,0.5)]"
              style={{ borderTop: `5px solid ${stage.accent}` }}
            >
              <div className="mb-3.5 font-dlvc-mono text-[13px] text-[#8a939b]">GIAI ĐOẠN {stage.num}</div>
              <h3 className="mb-2.5 text-[19px] font-extrabold">{stage.title}</h3>
              <p className="mb-5 text-[13.5px] text-[#a9b1b7]">{stage.desc}</p>
              <div className="flex flex-wrap gap-2">
                {stage.codes.map((code) => (
                  <span
                    key={code}
                    className="rounded-md border border-white/10 bg-white/6 px-2.5 py-1.25 font-dlvc-mono text-[11.5px] text-[#d8dbde] transition-colors duration-150 hover:border-dlvc-cobalt hover:bg-dlvc-cobalt/16 hover:text-white"
                  >
                    {code}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <p className="mt-5.5 text-[12.5px] text-[#7f8a92] italic">
          * Tên nhóm sản phẩm và mã sản phẩm ở trên là nội dung ví dụ – vui lòng đối chiếu lại danh mục thực tế trước
          khi đăng.
        </p>
      </div>
    </section>
  );
}
