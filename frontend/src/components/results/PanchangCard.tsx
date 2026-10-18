"use client";

import React from "react";
import { PanchangInfo } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getNakshatraName } from "@/lib/translations";
import { Compass, Moon, Sun, Sparkles, CalendarDays } from "lucide-react";

interface PanchangCardProps {
  panchang?: PanchangInfo;
}

export function PanchangCard({ panchang }: PanchangCardProps) {
  const { language, t } = useLanguage();

  if (!panchang) {
    return (
      <div className="p-8 text-center bg-white rounded-lg border border-[#E2DCD5] text-[#64748B]">
        {t.notAvailableYet}
      </div>
    );
  }

  const items = [
    {
      label: t.panchangTithi,
      value: `${panchang.tithi.paksha} ${panchang.tithi.name} (${panchang.tithi.number})`,
      icon: Moon,
      color: "text-indigo-600 bg-indigo-50 border-indigo-100",
    },
    {
      label: t.panchangNakshatra,
      value: getNakshatraName(panchang.nakshatra, language),
      icon: Sparkles,
      color: "text-amber-600 bg-amber-50 border-amber-100",
    },
    {
      label: t.panchangYoga,
      value: `${panchang.yoga.name} (#${panchang.yoga.number})`,
      icon: Compass,
      color: "text-emerald-600 bg-emerald-50 border-emerald-100",
    },
    {
      label: t.panchangKarana,
      value: panchang.karana,
      icon: Sun,
      color: "text-orange-600 bg-orange-50 border-orange-100",
    },
    {
      label: t.panchangVara,
      value: panchang.vara,
      icon: CalendarDays,
      color: "text-slate-600 bg-slate-50 border-slate-100",
    },
  ];

  return (
    <div className="bg-white rounded-lg border border-[#E2DCD5] p-5 shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-[#E2DCD5] mb-4">
        <div>
          <h4 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider">
            {language === "ta" ? "பிறப்பு பஞ்சாங்கம் (ஐந்து அங்கங்கள்)" : "Birth Panchang (Five Limbs)"}
          </h4>
          <p className="text-xs text-[#64748B] mt-0.5">
            {language === "ta"
              ? "பிறந்த துல்லிய கணத்தில் பஞ்சாங்க நிலைகள்"
              : "Astronomical Panchang markers at exact birth moment"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {items.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              className="p-3 rounded-lg border border-[#E2DCD5] bg-[#FAF8F5] flex flex-col justify-between"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className={`p-1.5 rounded-md border ${item.color}`}>
                  <Icon className="w-3.5 h-3.5" />
                </span>
                <span className="text-[11px] font-semibold text-[#475569] uppercase tracking-wider">
                  {item.label}
                </span>
              </div>
              <div className="text-sm font-bold text-[#0F172A] truncate" title={item.value}>
                {item.value}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
