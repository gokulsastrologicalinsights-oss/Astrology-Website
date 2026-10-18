"use client";

import React from "react";
import { HouseInfo } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getRasiName, getNakshatraName, getLordName } from "@/lib/translations";
import { formatDms } from "@/lib/formatters";

interface HousesTableProps {
  houses: HouseInfo[];
}

export function HousesTable({ houses }: HousesTableProps) {
  const { language, t } = useLanguage();

  return (
    <div className="w-full overflow-x-auto rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
      <table className="w-full text-left text-xs sm:text-sm text-[#1E293B]">
        <thead className="bg-[#FAF7F0] text-[#0F172A] border-b border-[#E2DCD5] uppercase text-[11px] tracking-wider font-semibold">
          <tr>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.house}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.sign}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.degreeInSign}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.cuspDegree}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.nakshatra}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.pada}</th>
            <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.starLord}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#F1EBE4]">
          {houses.map((h) => {
            const rasiLabel = getRasiName(h.sign_index, language);
            const nakshatraLabel = getNakshatraName(h.nakshatra, language);
            const starLordLabel = getLordName(h.star_lord, language);
            const isKendra = [1, 4, 7, 10].includes(h.house_number);

            return (
              <tr
                key={`house-${h.house_number}`}
                className={`transition-colors ${
                  isKendra ? "bg-[#FAF7F0]/40 font-medium" : "hover:bg-[#FAF8F5]"
                }`}
              >
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-semibold text-[#0F172A] flex items-center gap-2">
                  <span
                    className={`inline-flex items-center justify-center w-5 h-5 rounded-full text-[11px] ${
                      isKendra
                        ? "bg-[#B8860B] text-white"
                        : "bg-[#E2DCD5] text-[#334155]"
                    }`}
                  >
                    {h.house_number}
                  </span>
                  <span>
                    {language === "ta" ? `${h.house_number}ம் பாவம்` : `Bhava ${h.house_number}`}
                  </span>
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#334155]">
                  {rasiLabel}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#0F172A]">
                  {formatDms(h.degree_in_sign)}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                  {formatDms(h.cusp_degree)}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#334155]">
                  {nakshatraLabel}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono">
                  {h.pada}
                </td>
                <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#475569]">
                  {starLordLabel}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
