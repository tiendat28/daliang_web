import { signOut } from "@/auth";
import MobileMenuButton from "./MobileMenuButton";

function initials(name: string) {
  const parts = name.trim().split(/\s+/);
  return parts.slice(-2).map((p) => p[0]?.toUpperCase() ?? "").join("");
}

export default function Topbar({ userName, notificationCount }: { userName: string; notificationCount: number }) {
  return (
    <div className="flex h-16 items-center justify-between gap-5 border-b border-dlvc-border bg-dlvc-surface px-4 min-[1001px]:px-6.5">
      <div className="flex flex-1 items-center gap-3">
        <MobileMenuButton />
        <div className="flex max-w-100 flex-1 items-center gap-2.5 rounded-[9px] border border-dlvc-border bg-[#f3f4ef] px-3 py-2 text-[13.5px] text-dlvc-ink-soft">
          🔍 <span className="hidden sm:inline">Tìm nhân sự, tài liệu, hoá đơn…</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex h-9 w-9 items-center justify-center rounded-[9px] border border-dlvc-border bg-dlvc-surface text-[15px] transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]">
          🔔
          {notificationCount > 0 ? (
            <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full border-2 border-dlvc-surface bg-dlvc-danger font-dlvc-mono text-[9.5px] text-white">
              {notificationCount}
            </span>
          ) : null}
        </div>

        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-dlvc-dept-ke-toan text-[12.5px] font-bold text-dlvc-sidebar">
          {initials(userName)}
        </div>

        <form
          action={async () => {
            "use server";
            await signOut({ redirectTo: "/dlvc/admin/login" });
          }}
        >
          <button
            type="submit"
            title="Đăng xuất"
            className="flex h-9 w-9 items-center justify-center rounded-[9px] border border-dlvc-border bg-dlvc-surface text-[15px] transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)]"
          >
            ⏻
          </button>
        </form>
      </div>
    </div>
  );
}
