import { cookies } from "next/headers";
import { defaultLocale, locales, type Locale } from "@/lib/locale";

export { getDictionary, locales, defaultLocale } from "@/lib/locale";
export type { Locale, Dictionary } from "@/lib/locale";

export async function getLocale(): Promise<Locale> {
  const store = await cookies();
  const value = store.get("locale")?.value;
  return locales.includes(value as Locale) ? (value as Locale) : defaultLocale;
}
