import Link from "next/link";
import Container from "@/components/Container";
import LocaleSwitcher from "@/components/LocaleSwitcher";
import { getDictionary, getLocale } from "@/lib/i18n";

export default async function PortalHome() {
  const locale = await getLocale();
  const dict = getDictionary(locale);

  return (
    <Container>
      <div className="mb-8 flex items-center justify-between">
        <span className="text-lg font-semibold text-black dark:text-zinc-50">
          {dict.common.appName}
        </span>
        <LocaleSwitcher current={locale} />
      </div>

      <h1 className="mb-3 text-3xl font-semibold text-black dark:text-zinc-50">
        {dict.portal.heading}
      </h1>
      <p className="mb-8 max-w-2xl text-zinc-600 dark:text-zinc-400">
        {dict.portal.subheading}
      </p>

      <nav className="flex gap-4 text-sm">
        <Link href="/internal" className="underline">
          {dict.nav.internal}
        </Link>
        <Link href="/admin" className="underline">
          {dict.nav.admin}
        </Link>
      </nav>
    </Container>
  );
}
