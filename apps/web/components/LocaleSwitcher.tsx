"use client";

import { useRouter } from "next/navigation";
import { locales, type Locale } from "@/lib/locale";

export default function LocaleSwitcher({ current }: { current: Locale }) {
  const router = useRouter();

  function setLocale(locale: Locale) {
    document.cookie = `locale=${locale}; path=/; max-age=31536000`;
    router.refresh();
  }

  return (
    <div className="flex gap-2 text-sm">
      {locales.map((locale) => (
        <button
          key={locale}
          onClick={() => setLocale(locale)}
          className={
            locale === current
              ? "font-semibold text-black underline dark:text-zinc-50"
              : "text-zinc-500 hover:underline dark:text-zinc-400"
          }
        >
          {locale.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
