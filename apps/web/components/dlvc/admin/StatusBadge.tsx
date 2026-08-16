type Variant = "ok" | "warn" | "danger";

const VARIANT_STYLE: Record<Variant, { color: string; rotate: string }> = {
  ok: { color: "var(--color-dlvc-ok)", rotate: "-2deg" },
  warn: { color: "var(--color-dlvc-warn)", rotate: "1.5deg" },
  danger: { color: "var(--color-dlvc-danger)", rotate: "-1.5deg" },
};

export default function StatusBadge({ label, variant }: { label: string; variant: Variant }) {
  const style = VARIANT_STYLE[variant];
  return (
    <span
      className="inline-block rounded-[3px] border-[1.5px] border-dashed px-2.5 py-0.75 font-dlvc-mono text-[10.5px] font-semibold tracking-[0.06em] uppercase"
      style={{ color: style.color, borderColor: style.color, transform: `rotate(${style.rotate})` }}
    >
      {label}
    </span>
  );
}
