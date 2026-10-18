"use client";

import React from "react";
import { PlanetaryKpPosition, CalculationMetadata } from "@/lib/types";
import { formatDms } from "@/lib/formatters";
import { getGrahaName, getRasiName, getLordName } from "@/lib/translations";

interface KpBirthChartTabProps {
  planets: PlanetaryKpPosition[];
  metadata?: CalculationMetadata;
  language: "en" | "ta";
}

export function KpBirthChartTab({ planets, metadata, language }: KpBirthChartTabProps) {
  if (!planets || planets.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-[#E2DCD5] text-[#64748B]">
        {language === "ta"
          ? "கிரக நிலைகள் கிடைக்கவில்லை. தயவுசெய்து கணக்கீட்டை இயக்கவும்."
          : "Planetary positions not available. Please run the calculation."}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Info Banner */}
      {metadata && (
        <div className="p-4 rounded-xl bg-[#FAF6EC] border border-[#D8BD80] flex flex-wrap items-center justify-between gap-3 text-xs text-[#102A4C]">
          <div>
            <span className="font-bold text-[#8C6D23]">
              {language === "ta" ? "அயனாம்சம்:" : "Ayanamsa:"}
            </span>{" "}
            {metadata.ayanamsa_name} ({metadata.ayanamsa_deg.toFixed(4)}°)
          </div>
          <div>
            <span className="font-bold text-[#8C6D23]">
              {language === "ta" ? "பாவக முறை:" : "House System:"}
            </span>{" "}
            {metadata.house_system_name}
          </div>
          <div>
            <span className="font-bold text-[#8C6D23]">
              {language === "ta" ? "நேர மண்டலம்:" : "Timezone:"}
            </span>{" "}
            {metadata.local_timezone} (UTC {metadata.utc_offset_hours !== undefined ? (metadata.utc_offset_hours >= 0 ? `+${metadata.utc_offset_hours}` : metadata.utc_offset_hours) : "+05:30"})
          </div>
        </div>
      )}

      {/* Planetary Table */}
      <div className="overflow-x-auto rounded-xl border border-[#E2DCD5] shadow-xs bg-white">
        <table className="min-w-full divide-y divide-[#E2DCD5] text-xs sm:text-sm">
          <thead className="bg-[#F8FAFC] text-[#475569] font-semibold">
            <tr>
              <th className="px-3 py-3 text-left">
                {language === "ta" ? "கிரகம்" : "Planet"}
              </th>
              <th className="px-3 py-3 text-left">
                {language === "ta" ? "பாகை (ராசி)" : "Longitude (Sign)"}
              </th>
              <th className="px-3 py-3 text-left">
                {language === "ta" ? "ராசி அதிபதி" : "Sign Lord"}
              </th>
              <th className="px-3 py-3 text-left">
                {language === "ta" ? "நட்சத்திர அதிபதி" : "Star Lord"}
              </th>
              <th className="px-3 py-3 text-left">
                <span className="text-[#B8860B] font-bold">
                  {language === "ta" ? "உப-அதிபதி (Sub)" : "Sub-Lord"}
                </span>
              </th>
              <th className="px-3 py-3 text-left">
                <span className="text-[#3478F6] font-bold">
                  {language === "ta" ? "உப-உப (Sub-Sub)" : "Sub-Sub-Lord"}
                </span>
              </th>
              <th className="px-3 py-3 text-center">
                <span className="text-emerald-700 font-bold">
                  {language === "ta" ? "KP எண்" : "KP #"}
                </span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F1F5F9] text-[#1E293B]">
            {planets.map((p) => {
              const signDeg = p.longitude % 30.0;
              return (
                <tr key={p.planet} className="hover:bg-[#FAF6EC]/60 transition-colors">
                  <td className="px-3 py-2.5 font-bold text-[#102A4C] whitespace-nowrap">
                    {getGrahaName(p.planet, language)}
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap font-mono text-xs">
                    {formatDms(signDeg)} in {getRasiName(p.sign_index, language)}
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    {getLordName(p.sign_lord, language)}
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    {getLordName(p.star_lord, language)}
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-md font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                      {getLordName(p.sub_lord, language)}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-md font-semibold bg-[#EBF2FE] text-[#2563EB] border border-[#BFDBFE]">
                      {getLordName(p.sub_sub_lord, language)}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-center font-bold text-emerald-700 whitespace-nowrap">
                    #{p.kp_number}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="text-[11px] text-[#64748B] space-y-1">
        <p>
          * <strong>KP Sub-Lord</strong> is the primary predictive arbiter in Krishnamurti Paddhati, determined by the 249-division Vimshottari subdivision.
        </p>
        <p>
          * <strong>Sub-Sub-Lord</strong> provides micro-degree fine tuning, dividing each sub-period proportionately by 120-year planetary periods.
        </p>
      </div>
    </div>
  );
}
