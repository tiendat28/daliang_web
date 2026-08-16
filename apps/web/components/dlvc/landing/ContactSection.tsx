import ContactForm from "./ContactForm";

// TODO: nội dung mẫu, cần khách hàng xác nhận — email liên hệ "lienhe@daliangvn.com"
// là địa chỉ ví dụ, cần thay bằng email thật của DLVC trước khi đăng chính thức.
const CONTACT_EMAIL = "lienhe@daliangvn.com";

export default function ContactSection() {
  return (
    <section id="contact" className="bg-dlvc-paper py-16 min-[900px]:py-22">
      <div className="mx-auto max-w-292.5 px-7">
        <div className="mb-11 max-w-160">
          <div className="font-dlvc-mono text-[12px] font-semibold tracking-[0.12em] text-dlvc-amber uppercase">
            Liên hệ
          </div>
          <h2 className="mt-2.5 text-[32px] font-extrabold text-dlvc-landing-ink">
            Trao đổi nhu cầu hoá chất của nhà máy bạn
          </h2>
          <p className="mt-3 text-[15px] text-dlvc-landing-ink-soft">
            Để lại thông tin, đội ngũ kỹ thuật sẽ liên hệ tư vấn trong thời gian sớm nhất.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-10 min-[900px]:grid-cols-2">
          <ContactForm />

          <div>
            <div className="mb-4.5 rounded-2xl bg-dlvc-graphite p-8 text-white">
              <InfoRow icon="📍" label="Địa chỉ nhà máy">
                Lô B7, Ô 2, Đường D2, KCN Đất Cuốc, Xã Bắc Tân Uyên, TP. Hồ Chí Minh
              </InfoRow>
              <InfoRow icon="☎" label="Điện thoại">
                0274-3651 005-009
              </InfoRow>
              <InfoRow icon="📠" label="Fax">
                0274.3651.010
              </InfoRow>
              <InfoRow icon="✉" label="Email" last>
                {CONTACT_EMAIL} <span className="opacity-60">(ví dụ)</span>
              </InfoRow>
            </div>
            <div className="flex h-37.5 items-center justify-center rounded-2xl border border-dlvc-landing-border bg-[repeating-linear-gradient(45deg,#e9ebe5,#e9ebe5_10px,#e3e5de_10px,#e3e5de_20px)] font-dlvc-mono text-[12.5px] text-dlvc-landing-ink-soft">
              [ Vị trí bản đồ – KCN Đất Cuốc ]
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function InfoRow({
  icon,
  label,
  children,
  last,
}: {
  icon: string;
  label: string;
  children: React.ReactNode;
  last?: boolean;
}) {
  return (
    <div className={`flex gap-3.5 py-3.25 ${last ? "" : "border-b border-[#2b323a]"}`}>
      <span className="w-4 text-[15px] text-dlvc-amber">{icon}</span>
      <div className="text-[13.5px] leading-relaxed text-[#d8dbde]">
        <b className="mb-0.75 block text-[12px] font-semibold tracking-[0.04em] text-white uppercase">{label}</b>
        {children}
      </div>
    </div>
  );
}
