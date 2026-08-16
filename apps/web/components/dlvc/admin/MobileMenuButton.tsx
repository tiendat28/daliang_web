"use client";

import { useSidebar } from "./SidebarContext";

export default function MobileMenuButton() {
  const { open } = useSidebar();
  return (
    <button
      type="button"
      onClick={open}
      aria-label="Mở menu"
      className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[9px] border border-dlvc-border bg-dlvc-surface text-[16px] transition-[border-color,box-shadow] duration-150 hover:border-dlvc-accent hover:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] min-[1001px]:hidden"
    >
      ☰
    </button>
  );
}
