"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import LangToggle from "@/components/mock/LangToggle";

const NAV_LINKS = [
  { href: "/#tinh-nang", label: "Tính năng" },
  { href: "/ve-chung-toi", label: "Về chúng tôi" },
  { href: "/lien-he", label: "Liên hệ" },
];

export default function LandingHeader() {
  const pathname = usePathname();

  return (
    <header className="flex h-15 shrink-0 items-center gap-6 border-b border-border bg-card px-6">
      <Link href="/" className="text-[17px] font-bold text-strong">
        Daliang
      </Link>

      <nav className="flex items-center gap-5 text-[14px]">
        {NAV_LINKS.map((link) => {
          const isActive = pathname === link.href;
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

      <div className="flex-1" />

      <LangToggle />

      <Link
        href="/portal"
        className="h-9 items-center rounded border border-border px-4 text-[14px] text-body hover:text-strong hidden sm:flex"
      >
        Cổng tra cứu
      </Link>

      <Link
        href="/login"
        className="flex h-9 items-center rounded bg-accent px-4 text-[14px] font-semibold text-card hover:bg-accent-hover"
      >
        Đăng nhập nội bộ
      </Link>
    </header>
  );
}
