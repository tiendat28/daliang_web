"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSidebar } from "./SidebarContext";

type NavCounts = {
  employees: number;
  documents: number;
  invoices: number;
};

type SidebarProps = {
  counts: NavCounts;
  userName: string;
  userRole: string;
};

const NAV_ITEMS = [
  { href: "/dlvc/admin", label: "Tổng quan", icon: "◈", group: "operate" as const },
  { href: "/dlvc/admin/employees", label: "Nhân sự", icon: "👤", group: "manage" as const, countKey: "employees" as const },
  { href: "/dlvc/admin/documents", label: "Tài liệu phòng ban", icon: "📁", group: "manage" as const, countKey: "documents" as const },
  { href: "/dlvc/admin/invoices", label: "Hoá đơn mua bán", icon: "💳", group: "manage" as const, countKey: "invoices" as const },
];

function initials(name: string) {
  const parts = name.trim().split(/\s+/);
  return parts.slice(-2).map((p) => p[0]?.toUpperCase() ?? "").join("");
}

export default function Sidebar({ counts, userName, userRole }: SidebarProps) {
  const pathname = usePathname();
  const { mobileOpen, close } = useSidebar();

  return (
    <>
      {mobileOpen ? (
        <div className="fixed inset-0 z-30 bg-black/40 min-[1001px]:hidden" onClick={close} aria-hidden />
      ) : null}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-62 shrink-0 flex-col bg-dlvc-sidebar px-4 py-5.5 text-[#edefea] transition-transform duration-200 min-[1001px]:static min-[1001px]:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center gap-2.5 px-2.5 pt-1.5 pb-6.5">
          <div className="flex h-8.5 w-8.5 shrink-0 items-center justify-center rounded-lg bg-linear-to-br from-dlvc-accent to-dlvc-accent-dark text-[15px] font-extrabold text-[#0b1620] shadow-[0_0_14px_rgba(34,211,238,0.45)]">
            VP
          </div>
          <div className="leading-[1.15]">
            <div className="text-[14.5px] font-bold tracking-wide">VĂN PHÒNG SỐ</div>
            <div className="text-[11px] text-[#9aa6ae]">Quản trị nội bộ</div>
          </div>
        </div>

        <NavGroup label="Điều hành">
          {NAV_ITEMS.filter((item) => item.group === "operate").map((item) => (
            <NavLink key={item.href} item={item} active={pathname === item.href} count={null} onNavigate={close} />
          ))}
        </NavGroup>

        <NavGroup label="Quản lý">
          {NAV_ITEMS.filter((item) => item.group === "manage").map((item) => (
            <NavLink
              key={item.href}
              item={item}
              active={pathname === item.href || pathname.startsWith(item.href + "/")}
              count={item.countKey ? counts[item.countKey] : null}
              onNavigate={close}
            />
          ))}
        </NavGroup>

        <NavGroup label="Hệ thống">
          <div className="mb-0.5 flex cursor-default items-center gap-2.75 rounded-[9px] border-l-[3px] border-transparent px-3 py-2.5 text-[14px] font-medium text-[#71818c]">
            <span className="w-4.25 shrink-0 text-center text-[14px]">⚙</span> Cài đặt
          </div>
          <div className="mb-0.5 flex cursor-default items-center gap-2.75 rounded-[9px] border-l-[3px] border-transparent px-3 py-2.5 text-[14px] font-medium text-[#71818c]">
            <span className="w-4.25 shrink-0 text-center text-[14px]">🔐</span> Phân quyền
          </div>
        </NavGroup>

        <div className="mt-auto border-t border-white/8 pt-3">
          <div className="flex items-center gap-2.5 px-1">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#3a4b5a] text-[12.5px] font-bold text-[#edefea]">
              {initials(userName)}
            </div>
            <div className="min-w-0">
              <div className="truncate text-[13px] font-semibold text-[#edefea]">{userName}</div>
              <div className="truncate text-[11px] text-[#8b98a1]">{userRole}</div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

function NavGroup({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-4.5">
      <div className="px-3 pb-2 text-[10.5px] font-semibold tracking-[0.09em] text-[#71818c] uppercase">{label}</div>
      {children}
    </div>
  );
}

function NavLink({
  item,
  active,
  count,
  onNavigate,
}: {
  item: (typeof NAV_ITEMS)[number];
  active: boolean;
  count: number | null;
  onNavigate: () => void;
}) {
  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      className={
        active
          ? "mb-0.5 flex items-center gap-2.75 rounded-[9px] border-l-[3px] border-dlvc-accent bg-dlvc-sidebar-soft px-3 py-2.5 text-[14px] font-medium text-white shadow-[0_0_16px_-4px_rgba(34,211,238,0.45)]"
          : "mb-0.5 flex items-center gap-2.75 rounded-[9px] border-l-[3px] border-transparent px-3 py-2.5 text-[14px] font-medium text-[#c9d1d6] transition-[background-color,color,box-shadow] duration-150 hover:bg-dlvc-sidebar-soft hover:text-white hover:shadow-[inset_0_0_0_1px_rgba(34,211,238,0.25)]"
      }
    >
      <span className="w-4.25 shrink-0 text-center text-[14px]">{item.icon}</span>
      {item.label}
      {count !== null ? (
        <span className="ml-auto rounded-[5px] bg-white/8 px-1.5 py-0.5 font-dlvc-mono text-[11px] text-[#b9c2c8]">
          {count}
        </span>
      ) : null}
    </Link>
  );
}
