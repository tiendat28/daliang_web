import Container from "@/components/Container";
import LocaleSwitcher from "@/components/LocaleSwitcher";
import { getDictionary, getLocale } from "@/lib/i18n";

export default async function AdminHome() {
  const locale = await getLocale();
  const dict = getDictionary(locale);

  return (
    <Container>
      <div className="mb-3 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
          {dict.admin.heading}
        </h1>
        <LocaleSwitcher current={locale} />
      </div>
      <p className="text-zinc-600 dark:text-zinc-400">{dict.admin.subheading}</p>
    </Container>
  );
}
