type KpiCardProps = {
  label: string;
  value: string | number;
  delta?: string;
  down?: boolean;
  accentColor?: string;
};

export default function KpiCard({ label, value, delta, down, accentColor }: KpiCardProps) {
  return (
    <div
      className="rounded-[14px] border border-dlvc-border bg-dlvc-surface px-5 py-4.5 transition-transform duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_24px_-8px_rgba(34,211,238,0.45)]"
      style={{ borderLeft: `4px solid ${accentColor ?? "var(--color-dlvc-accent)"}` }}
    >
      <div className="text-[12px] font-semibold tracking-[0.04em] text-dlvc-ink-soft uppercase">{label}</div>
      <div className="mt-1.5 font-dlvc-mono text-[28px] font-semibold text-dlvc-ink">{value}</div>
      {delta ? (
        <div className={`mt-1.25 text-[12px] font-medium ${down ? "text-dlvc-danger" : "text-dlvc-ok"}`}>{delta}</div>
      ) : null}
    </div>
  );
}
