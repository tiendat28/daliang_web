"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import LangToggle from "@/components/mock/LangToggle";

const NAV_LINKS = [
  { href: "/documents", label: "Tài liệu" },
  { href: "/dashboard", label: "Thống kê" },
  { href: "/admin", label: "Quản trị" },
];

export default function AppHeader() {
  const pathname = usePathname();

  return (
    <header className="flex h-15 shrink-0 items-center gap-6 border-b border-border bg-card px-6">
      <span className="text-[17px] font-bold text-strong">Kho tài liệu</span>

      <nav className="flex items-center gap-5 text-[14px]">
        {NAV_LINKS.map((link) => {
          const isActive = pathname.startsWith(link.href);
          return (
            <Link
              key={link.href}
              href={link.href}
              className={isActive ? "font-semibold text-accent" : "text-muted hover:text-body"}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>

      <input
        type="text"
        placeholder="Tìm theo tên file hoặc nội dung bên trong…"
        className="h-9 w-full max-w-130 rounded border-none bg-subtle px-3 text-[14px] text-body placeholder:text-faint focus:outline-none"
      />

      <div className="flex-1" />

      <LangToggle />

      <button
        type="button"
        className="h-9 rounded bg-accent px-4 text-[14px] font-semibold text-card hover:bg-accent-hover"
      >
        Tải lên
      </button>

      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-subtle text-[13px] font-semibold text-accent-hover">
        A
      </span>
    </header>
  );
}
