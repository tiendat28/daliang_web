import { folderTree, shortcuts, type FolderNode } from "@/lib/mock-data";

function FolderItem({ node, depth = 0 }: { node: FolderNode; depth?: number }) {
  const selected = depth === 0 && node.name === "Kỹ thuật";

  return (
    <div>
      <div
        className={
          "flex h-[34px] items-center rounded text-[14px] " +
          (selected
            ? "bg-accent-subtle font-semibold text-accent-hover"
            : depth === 0
              ? "text-body hover:bg-subtle"
              : "text-dim hover:bg-subtle")
        }
        style={{ paddingLeft: 10 + depth * 16, paddingRight: 10 }}
      >
        {node.name}
      </div>
      {node.children?.map((child) => (
        <FolderItem key={child.name} node={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export default function FolderSidebar({
  showShortcuts = true,
  className = "",
}: {
  showShortcuts?: boolean;
  className?: string;
}) {
  return (
    <aside className={`shrink-0 border-r border-border bg-panel px-3 py-4 ${className}`}>
      <div className="mb-2 px-2 text-[11px] font-semibold tracking-wide text-faint uppercase">
        Thư mục · Folders
      </div>
      <nav className="flex flex-col gap-0.5">
        {folderTree.map((node) => (
          <FolderItem key={node.name} node={node} />
        ))}
      </nav>

      {showShortcuts && (
        <>
          <div className="my-4 border-t border-border-light" />
          <nav className="flex flex-col gap-0.5">
            {shortcuts.map((shortcut) => (
              <div
                key={shortcut.label}
                className="flex h-[34px] items-center justify-between rounded px-2.5 text-[14px] text-body hover:bg-subtle"
              >
                <span>{shortcut.label}</span>
                {shortcut.badge !== undefined && (
                  <span className="rounded-full bg-warning-bg px-2 py-0.5 font-mono text-[11px] text-warning-text">
                    {shortcut.badge}
                  </span>
                )}
              </div>
            ))}
          </nav>
        </>
      )}
    </aside>
  );
}
