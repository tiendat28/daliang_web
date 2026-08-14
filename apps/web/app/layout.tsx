import type { Metadata } from "next";
import { Source_Sans_3, Source_Code_Pro } from "next/font/google";
import "./globals.css";

const sourceSans = Source_Sans_3({
  variable: "--font-source-sans",
  subsets: ["latin", "vietnamese"],
});

const sourceCode = Source_Code_Pro({
  variable: "--font-source-code",
  subsets: ["latin", "vietnamese"],
});

export const metadata: Metadata = {
  title: "Daliang Docs",
  description: "Hệ thống quản lý tài liệu Daliang",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="vi"
      className={`${sourceSans.variable} ${sourceCode.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
