"use client";

import { useState } from "react";

const LANGS = ["VI", "EN"] as const;

export default function LangToggle() {
  const [active, setActive] = useState<(typeof LANGS)[number]>("VI");

  return (
    <div className="inline-flex overflow-hidden rounded border border-border text-[12px] font-semibold">
      {LANGS.map((lang) => (
        <button
          key={lang}
          type="button"
          onClick={() => setActive(lang)}
          className={
            active === lang
              ? "bg-accent px-2.5 py-1 text-card"
              : "bg-transparent px-2.5 py-1 text-muted hover:text-body"
          }
        >
          {lang}
        </button>
      ))}
    </div>
  );
}
