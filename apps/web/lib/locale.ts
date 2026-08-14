import vi from "@/messages/vi.json";
import en from "@/messages/en.json";

export const locales = ["vi", "en"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "vi";

const dictionaries = { vi, en } satisfies Record<Locale, unknown>;

export type Dictionary = typeof vi;

export function getDictionary(locale: Locale): Dictionary {
  return dictionaries[locale];
}
