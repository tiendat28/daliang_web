"use client";

import { useState } from "react";

const NAV_LINKS = [
  { href: "#hero", label: "Trang chủ" },
  { href: "#about", label: "Giới thiệu" },
  { href: "#products", label: "Sản phẩm" },
  { href: "#services", label: "Dịch vụ" },
  { href: "#contact", label: "Liên hệ" },
];

export default function LandingHeader() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-dlvc-graphite/92 backdrop-blur-sm">
      <div className="mx-auto flex max-w-292.5 items-center justify-between px-7 py-4">
        <a href="#hero" className="flex items-center gap-3">
          <div className="flex h-8.5 w-8.5 shrink-0 items-center justify-center rounded-md bg-linear-to-br from-dlvc-cobalt to-dlvc-cobalt-deep text-[13px] font-extrabold text-[#0b1620]">
            DV
          </div>
          <div className="leading-tight">
            <div className="text-[14.5px] font-bold text-white">DALIANG VN</div>
            <div className="font-dlvc-mono text-[10.5px] tracking-[0.06em] text-[#9ba5ad]">
              HOÁ CHẤT XỬ LÝ BỀ MẶT
            </div>
          </div>
        </a>

        <ul className="hidden gap-7.5 min-[900px]:flex">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-[14px] font-medium text-[#d8dbde] transition-colors duration-150 hover:text-dlvc-cobalt hover:[text-shadow:0_0_12px_rgba(34,211,238,0.4)]"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden items-center gap-4.5 min-[900px]:flex">
          <a
            href="#contact"
            className="inline-flex items-center gap-2 rounded-lg border-[1.5px] border-white/35 px-6 py-3.25 text-[14.5px] font-bold text-white transition-[border-color,color,box-shadow] duration-150 hover:border-dlvc-cobalt hover:text-dlvc-cobalt hover:shadow-[0_0_20px_rgba(34,211,238,0.4)]"
          >
            Liên hệ báo giá
          </a>
        </div>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-label="Mở menu"
          className="text-[22px] text-white min-[900px]:hidden"
        >
          {open ? "✕" : "☰"}
        </button>
      </div>

      {open ? (
        <div className="border-t border-white/10 px-7 py-4 min-[900px]:hidden">
          <ul className="flex flex-col gap-3.5">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="text-[14.5px] font-medium text-[#d8dbde]"
                >
                  {link.label}
                </a>
              </li>
            ))}
            <li>
              <a
                href="#contact"
                onClick={() => setOpen(false)}
                className="inline-flex items-center gap-2 rounded-lg border-[1.5px] border-white/35 px-5 py-2.5 text-[14px] font-bold text-white"
              >
                Liên hệ báo giá
              </a>
            </li>
          </ul>
        </div>
      ) : null}
    </header>
  );
}
