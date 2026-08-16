const STAGES = [
  { num: "01", label: "Tiền xử lý", color: "var(--color-dlvc-chrome)" },
  { num: "02", label: "Phụ gia mạ", color: "var(--color-dlvc-cobalt)" },
  { num: "03", label: "Thụ động", color: "var(--color-dlvc-amber)" },
];

export default function ProcessStrip() {
  return (
    <div className="mx-auto max-w-292.5 border-t border-[#2b323a]">
      <div className="grid grid-cols-1 min-[900px]:grid-cols-3">
        {STAGES.map((s, i) => (
          <div
            key={s.num}
            className={`flex items-center gap-3.5 px-7 py-5.5 ${
              i < STAGES.length - 1 ? "border-b border-[#2b323a] min-[900px]:border-r min-[900px]:border-b-0" : ""
            }`}
          >
            <span className="h-2.25 w-2.25 shrink-0 rounded-full" style={{ background: s.color }} />
            <span className="font-dlvc-mono text-[12px] font-semibold text-[#8a939b]">{s.num}</span>
            <span className="text-[14.5px] font-bold text-white">{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
