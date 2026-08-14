import Link from "next/link";
import LangToggle from "@/components/mock/LangToggle";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-page p-6">
      <div className="flex w-full max-w-[720px] flex-col overflow-hidden rounded-lg border border-border sm:flex-row">
        <div className="flex w-full flex-col justify-between gap-8 bg-body p-8 text-card sm:w-1/2">
          <span className="font-mono text-[12px] font-semibold tracking-widest text-accent/80 uppercase">
            DOCS
          </span>
          <div>
            <h1 className="text-[24px] font-semibold text-card">Kho tài liệu nội bộ</h1>
            <p className="mt-2 text-[13px] text-card/70">
              Không có tài khoản nội bộ? Truy cập{" "}
              <Link href="/portal" className="underline">
                cổng tra cứu
              </Link>{" "}
              để xem tài liệu công khai.
            </p>
          </div>
        </div>

        <div className="w-full bg-card p-10 sm:w-1/2">
          <div className="mb-6 flex items-center justify-between">
            <span className="text-[20px] font-semibold text-strong">Đăng nhập</span>
            <LangToggle />
          </div>

          <div className="flex flex-col gap-4">
            <label className="flex flex-col gap-1.5 text-[13px] text-body">
              Email
              <input
                type="email"
                placeholder="ten@congty.vn"
                className="h-10 rounded border border-border bg-page px-3 text-[14px] text-strong placeholder:text-faint focus:outline-none"
              />
            </label>
            <label className="flex flex-col gap-1.5 text-[13px] text-body">
              Mật khẩu
              <input
                type="password"
                placeholder="••••••••"
                className="h-10 rounded border border-border bg-page px-3 text-[14px] text-strong placeholder:text-faint focus:outline-none"
              />
            </label>

            <div className="flex items-center justify-between text-[13px]">
              <label className="flex items-center gap-2 text-body">
                <input type="checkbox" className="h-4 w-4 rounded border-border" />
                Ghi nhớ đăng nhập
              </label>
              <a href="#" className="font-medium text-accent">
                Quên mật khẩu?
              </a>
            </div>

            <button
              type="button"
              className="h-10 w-full rounded bg-accent text-[14px] font-semibold text-card hover:bg-accent-hover"
            >
              Đăng nhập
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
