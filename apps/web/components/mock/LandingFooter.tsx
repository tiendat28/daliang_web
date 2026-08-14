import Link from "next/link";

export default function LandingFooter() {
  return (
    <footer className="border-t border-border bg-card px-6 py-6">
      <div className="mx-auto flex max-w-4xl flex-col items-center justify-between gap-2 text-[13px] text-faint sm:flex-row">
        <span>© KD Gibel. Đã đăng ký bản quyền.</span>
        <div className="flex items-center gap-4">
          <Link href="/ve-chung-toi" className="hover:text-muted">
            Về chúng tôi
          </Link>
          <Link href="/lien-he" className="hover:text-muted">
            Liên hệ
          </Link>
          <Link href="/portal" className="hover:text-muted">
            Cổng tra cứu
          </Link>
          <Link href="/login" className="hover:text-muted">
            Đăng nhập
          </Link>
        </div>
      </div>
    </footer>
  );
}
