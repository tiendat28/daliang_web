import type { FileKind } from "@/lib/mock-data";

const LABEL: Record<FileKind, string> = {
  pdf: "PDF",
  doc: "DOC",
  xls: "XLS",
};

const BG_CLASS: Record<FileKind, string> = {
  pdf: "bg-accent",
  doc: "bg-doc",
  xls: "bg-xls",
};

export default function FileBadge({ kind }: { kind: FileKind }) {
  return (
    <span
      className={`inline-flex h-[30px] w-[26px] shrink-0 items-center justify-center rounded-[2px] text-[9px] font-semibold text-card ${BG_CLASS[kind]}`}
    >
      {LABEL[kind]}
    </span>
  );
}
