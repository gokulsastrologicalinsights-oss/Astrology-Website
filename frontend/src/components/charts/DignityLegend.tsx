"use client";

import React from "react";
import { useLanguage } from "@/lib/i18n";

interface DignityLegendProps {
  className?: string;
  compact?: boolean;
}

export function DignityLegend({ className = "", compact = false }: DignityLegendProps) {
  const { language } = useLanguage();

  return (
    <div
      className={`flex flex-wrap items-center justify-center gap-3 sm:gap-4.5 py-1.5 px-3 rounded-md bg-[#FAF8F2] border border-[#E8DFC8] text-[11px] sm:text-xs select-none shadow-2xs ${className}`}
    >
      {/* Ucham (Exalted) - Green */}
      <div className="flex items-center gap-1.5 font-medium">
        <span className="w-2.5 h-2.5 rounded-full bg-[#16A34A] ring-1 ring-[#16A34A]/30 shrink-0" />
        <span className="text-[#16A34A] font-bold">
          {language === "ta" ? "உச்சம் (Ucham)" : "Ucham (Exalted)"}
        </span>
      </div>

      {/* Neecham (Debilitated) - Red */}
      <div className="flex items-center gap-1.5 font-medium">
        <span className="w-2.5 h-2.5 rounded-full bg-[#DC2626] ring-1 ring-[#DC2626]/30 shrink-0" />
        <span className="text-[#DC2626] font-bold">
          {language === "ta" ? "நீசம் (Neecham)" : "Neecham (Debilitated)"}
        </span>
      </div>

      {/* Dik Balam (Directional Strength) - Yellow */}
      <div className="flex items-center gap-1.5 font-medium">
        <span className="w-2.5 h-2.5 rounded-full bg-[#CA8A04] ring-1 ring-[#CA8A04]/30 shrink-0" />
        <span className="text-[#CA8A04] font-bold">
          {language === "ta" ? "திக் பலம் (Dik Balam)" : "Dik Balam (Directional)"}
        </span>
      </div>
    </div>
  );
}
