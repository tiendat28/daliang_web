import { prisma } from "@daliang/db";
import Container from "@/components/Container";
import LocaleSwitcher from "@/components/LocaleSwitcher";
import { getDictionary, getLocale } from "@/lib/i18n";

function formatDate(date: Date) {
  return new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

export default async function InternalHome() {
  const [locale, documents] = await Promise.all([
    getLocale(),
    prisma.document.findMany({
      where: { deletedAt: null },
      include: { owner: true },
      orderBy: { createdAt: "desc" },
    }),
  ]);
  const dict = getDictionary(locale);

  return (
    <Container>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
          {dict.internal.heading}
        </h1>
        <LocaleSwitcher current={locale} />
      </div>

      <div className="overflow-x-auto rounded-lg border border-black/8 dark:border-white/[.145]">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-black/8 bg-black/2 dark:border-white/[.145] dark:bg-white/4">
              <th className="px-4 py-3 font-medium text-zinc-600 dark:text-zinc-400">
                {dict.internal.columns.name}
              </th>
              <th className="px-4 py-3 font-medium text-zinc-600 dark:text-zinc-400">
                {dict.internal.columns.code}
              </th>
              <th className="px-4 py-3 font-medium text-zinc-600 dark:text-zinc-400">
                {dict.internal.columns.version}
              </th>
              <th className="px-4 py-3 font-medium text-zinc-600 dark:text-zinc-400">
                {dict.internal.columns.createdAt}
              </th>
              <th className="px-4 py-3 font-medium text-zinc-600 dark:text-zinc-400">
                {dict.internal.columns.owner}
              </th>
            </tr>
          </thead>
          <tbody>
            {documents.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-4 py-6 text-center text-zinc-500 dark:text-zinc-400"
                >
                  {dict.internal.empty}
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr
                  key={doc.id}
                  className="border-b border-black/6 last:border-0 dark:border-white/10"
                >
                  <td className="px-4 py-3 text-black dark:text-zinc-50">
                    {doc.titleVi}
                  </td>
                  <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                    {doc.code}
                  </td>
                  <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                    {doc.version}
                  </td>
                  <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                    {formatDate(doc.createdAt)}
                  </td>
                  <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                    {doc.owner.fullName}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Container>
  );
}
