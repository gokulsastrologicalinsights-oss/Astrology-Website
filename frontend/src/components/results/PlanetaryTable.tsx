"use client";

import React from "react";
import { PlanetInfo, AscendantInfo } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaName, getRasiName, getNakshatraName, getLordName } from "@/lib/translations";
import { formatDms } from "@/lib/formatters";

interface PlanetaryTableProps {
  planets: PlanetInfo[];
  ascendant: AscendantInfo;
}

export function PlanetaryTable({ planets, ascendant }: PlanetaryTableProps) {
  const { language, t } = useLanguage();

  return (
    <div className="w-full overflow-x-auto rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
      <table className="w-full text-left text-xs sm:text-sm text-[#1E293B]">
        <thead className="bg-[#FAF7F0] text-[#0F172A] border-b border-[#E2DCD5] uppercase text-[11px] tracking-wider font-semibold">
          <tr>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.planet}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.sign}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.degreeInSign}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.longitude}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.nakshatra}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.pada}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.lord}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.speed}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.retrograde}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#F1EBE4]">
          {/* Ascendant Row */}
          <tr className="bg-[#FAF6EC]/50 font-medium">
            <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#784E0E] font-semibold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#B8860B] inline-block" />
              {t.ascendant}
            </td>
            <td className="px-3 py-2 sm:px-4 sm:py-2.5">
              {getRasiName(ascendant.sign_index, language)}
            </td>
            <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs">
              {formatDms(ascendant.degree_in_sign)}
            </td>
            <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
              {formatDms(ascendant.degree)}
            </td>
            <td className="px-3 py-2 sm:px-4 sm:py-2.5">
              {getNakshatraName(ascendant.nakshatra.name, language)}
            </td>
            <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono">
              {ascendant.nakshatra.pada}
            </td>
            <td className="px-3 py-2 sm:px-4 sm:py-2.5">
              {getLordName(ascendant.nakshatra.lord, language)}
            </td>
            <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#94A3B8]">
              —
            </td>
            <td className="px-3 py-2 sm:px-4 sm:py-2.5">
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                {t.direct}
              </span>
            </td>
          </tr>

          {/* Planet Rows */}
          {planets.map((p) => {
            const planetLabel = getGrahaName(p.name, language);
            const rasiLabel = getRasiName(p.sign_index, language);
            const nakshatraLabel = getNakshatraName(p.nakshatra.name, language);
            const lordLabel = getLordName(p.nakshatra.lord, language);

            return (
              <tr key={p.name} className="hover:bg-[#FAF8F5] transition-colors">
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-medium text-[#0F172A]">
                  {planetLabel}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#334155]">
                  {rasiLabel}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#0F172A]">
                  {formatDms(p.degree_in_sign)}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                  {formatDms(p.longitude)}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#334155]">
                  {nakshatraLabel}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono">
                  {p.nakshatra.pada}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#475569]">
                  {lordLabel}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                  {p.speed_deg_per_day.toFixed(3)}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5">
                  {p.is_retrograde ? (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                      {t.retrograde}
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-50 text-slate-600 border border-slate-200">
                      {t.direct}
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
