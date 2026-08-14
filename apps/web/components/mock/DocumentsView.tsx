"use client";

import { useState } from "react";
import Link from "next/link";
import type { Doc } from "@/lib/mock-data";
import FileBadge from "@/components/mock/FileBadge";
import FolderSidebar from "@/components/mock/FolderSidebar";

const GRID_COLS = "grid-cols-[44px_1fr_130px_96px_110px_130px]";

function HeaderCell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center px-3 py-2 font-mono text-[11px] font-semibold tracking-wide text-muted uppercase">
      {children}
    </div>
  );
}

function Pill({ tone, children }: { tone: "accent" | "warning"; children: React.ReactNode }) {
  return (
    <span
      className={
        "shrink-0 rounded-[3px] px-1.5 py-0.5 text-[11px] font-semibold " +
        (tone === "accent" ? "bg-accent-subtle text-accent-hover" : "bg-warning-bg text-warning-text")
      }
    >
      {children}
    </span>
  );
}

function FilterChip({ label }: { label: string }) {
  return (
    <span className="flex h-7 items-center rounded-full border border-border px-3 text-[13px] text-body">
      {label}
    </span>
  );
}

export default function DocumentsView({ docs }: { docs: Doc[] }) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="flex min-h-0 flex-1">
      {drawerOpen && (
        <div
          className="fixed inset-0 z-30 bg-strong/40 md:hidden"
          onClick={() => setDrawerOpen(false)}
        />
      )}

      <div
        className={
          "fixed inset-y-0 left-0 z-40 w-[236px] transform transition-transform duration-200 md:static md:z-auto md:translate-x-0 " +
          (drawerOpen ? "translate-x-0" : "-translate-x-full")
        }
      >
        <FolderSidebar className="h-full w-[236px]" />
      </div>

      <div className="flex min-w-0 flex-1 flex-col overflow-y-auto">
        <div className="border-b border-border px-4 py-2 md:hidden">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            className="flex h-8 items-center gap-2 rounded border border-border px-3 text-[13px] text-body"
          >
            <span className="flex flex-col gap-[3px]">
              <span className="h-[2px] w-4 bg-body" />
              <span className="h-[2px] w-4 bg-body" />
              <span className="h-[2px] w-4 bg-body" />
            </span>
            Thư mục
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2 border-b border-border px-6 py-3">
          <FilterChip label="Loại file: PDF" />
          <FilterChip label="Người tải: Nguyễn Văn A" />
          <FilterChip label="2026" />
          <button
            type="button"
            className="h-7 rounded-full border border-dashed border-border px-3 text-[13px] text-muted"
          >
            + Bộ lọc
          </button>
          <div className="flex-1" />
          <span className="text-[13px] whitespace-nowrap text-muted">412 tài liệu</span>
        </div>

        <div className={`hidden border-b border-border bg-subtle md:grid ${GRID_COLS}`}>
          <div />
          <HeaderCell>Tên tài liệu / Title</HeaderCell>
          <HeaderCell>Mã / Code</HeaderCell>
          <HeaderCell>Bản / Ver</HeaderCell>
          <HeaderCell>Ngày / Date</HeaderCell>
          <HeaderCell>Người tải / By</HeaderCell>
        </div>
        <div className="hidden md:block">
          {docs.map((doc, i) => (
            <Link
              key={doc.id}
              href={`/documents/${doc.id}`}
              className={
                `${GRID_COLS} grid items-center border-b border-border-light hover:bg-subtle/60 ` +
                (i === 0 ? "bg-accent/5" : "")
              }
            >
              <div className="flex items-center justify-center py-3.5">
                <FileBadge kind={doc.kind} />
              </div>
              <div className="min-w-0 px-3 py-3.5">
                <div className="flex items-center gap-2">
                  <span className="truncate text-[15px] font-semibold text-strong">{doc.title}</span>
                  {doc.status === "pending" ? (
                    <Pill tone="warning">Chờ duyệt</Pill>
                  ) : doc.visibility === "public" ? (
                    <Pill tone="accent">Công khai</Pill>
                  ) : null}
                </div>
                <div className="mt-0.5 truncate text-[13px] text-muted">
                  {doc.snippet ? (
                    <span dangerouslySetInnerHTML={{ __html: doc.snippet }} />
                  ) : (
                    `${doc.folder} · ${doc.uploadedBy}`
                  )}
                </div>
              </div>
              <div className="truncate px-3 py-3.5 font-mono text-[13px] text-body">{doc.code}</div>
              <div className="px-3 py-3.5 font-mono text-[13px] text-body">v{doc.version}</div>
              <div className="px-3 py-3.5 font-mono text-[13px] text-body">{doc.updatedAt}</div>
              <div className="truncate px-3 py-3.5 text-[13px] text-body">{doc.uploadedBy}</div>
            </Link>
          ))}
        </div>

        <div className="flex flex-col md:hidden">
          {docs.map((doc) => (
            <Link
              key={doc.id}
              href={`/documents/${doc.id}`}
              className="flex items-center gap-3 border-b border-border-light px-4 py-3"
            >
              <FileBadge kind={doc.kind} />
              <div className="min-w-0">
                <div className="truncate text-[15px] font-semibold text-strong">{doc.title}</div>
                <div className="truncate text-[13px] text-muted">
                  {doc.code} · v{doc.version} · {doc.updatedAt}
                </div>
              </div>
            </Link>
          ))}
        </div>

        <div className="mt-auto flex items-center justify-between px-6 py-3 text-[13px] text-muted">
          <span>Hiển thị 1–5 trong 412</span>
          <div className="flex gap-1.5">
            {[1, 2, 3].map((n) => (
              <span
                key={n}
                className={
                  "flex h-[30px] w-[30px] items-center justify-center rounded text-[13px] " +
                  (n === 1 ? "bg-accent font-semibold text-card" : "border border-border text-body")
                }
              >
                {n}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
