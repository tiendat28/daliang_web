import type { Metadata } from "next";
import LoginForm from "./LoginForm";

export const metadata: Metadata = {
  title: "Đăng nhập — Văn phòng số DLVC",
};

export default async function AdminLoginPage(props: PageProps<"/dlvc/admin/login">) {
  const searchParams = await props.searchParams;
  const callbackUrlParam = searchParams.callbackUrl;
  const callbackUrl = Array.isArray(callbackUrlParam) ? callbackUrlParam[0] : callbackUrlParam;

  return (
    <div className="flex min-h-screen items-center justify-center bg-dlvc-bg px-6 py-12">
      <div className="w-full max-w-100 rounded-2xl border border-dlvc-border bg-dlvc-surface p-8 shadow-[0_20px_50px_-24px_rgba(22,35,46,0.35)]">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-linear-to-br from-dlvc-accent to-dlvc-accent-dark text-[15px] font-extrabold text-[#0b1620] shadow-[0_0_14px_rgba(34,211,238,0.45)]">
            VP
          </div>
          <div className="leading-tight">
            <div className="text-[14.5px] font-bold tracking-wide text-dlvc-ink">VĂN PHÒNG SỐ</div>
            <div className="text-[11px] text-dlvc-ink-soft">Quản trị nội bộ</div>
          </div>
        </div>

        <h1 className="mb-1 text-[20px] font-bold text-dlvc-ink">Đăng nhập</h1>
        <p className="mb-6 text-[13px] text-dlvc-ink-soft">
          Đăng nhập bằng tài khoản nội bộ để truy cập hệ thống quản trị.
        </p>

        <LoginForm callbackUrl={callbackUrl} />
      </div>
    </div>
  );
}
