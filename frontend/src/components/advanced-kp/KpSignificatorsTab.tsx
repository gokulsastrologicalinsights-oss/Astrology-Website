"use client";

import React, { useState } from "react";
import { HouseSignificatorEntry, PlanetSignificator } from "@/lib/types";
import { getGrahaName, getRasiName, getLordName } from "@/lib/translations";

interface KpSignificatorsTabProps {
  houseSignificators?: HouseSignificatorEntry[];
  planetSignificators?: PlanetSignificator[];
  language: "en" | "ta";
}

export function KpSignificatorsTab({
  houseSignificators,
  planetSignificators,
  language,
}: KpSignificatorsTabProps) {
  const [viewMode, setViewMode] = useState<"house" | "planet">("house");

  return (
    <div className="space-y-6">
      {/* View Switcher */}
      <div className="flex items-center justify-between border-b border-[#E2DCD5] pb-3">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setViewMode("house")}
            className={`px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-lg transition-colors ${
              viewMode === "house"
                ? "bg-[#102A4C] text-white"
                : "bg-white text-[#475569] border border-[#E2DCD5] hover:bg-[#FAF6EC]"
            }`}
          >
            {language === "ta" ? "பாவக காரகத்துவங்கள் (4 நிலைகள்)" : "House Significators (4 Tiers)"}
          </button>
          <button
            type="button"
            onClick={() => setViewMode("planet")}
            className={`px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-lg transition-colors ${
              viewMode === "planet"
                ? "bg-[#102A4C] text-white"
                : "bg-white text-[#475569] border border-[#E2DCD5] hover:bg-[#FAF6EC]"
            }`}
          >
            {language === "ta" ? "கிரக காரகத்துவங்கள் (Grah Nirdeshan)" : "Planetary Significators"}
          </button>
        </div>

        <span className="text-xs text-[#64748B] hidden sm:inline">
          {viewMode === "house" ? "Bhaav Nirdeshan (A → B → C → D)" : "Grah Nirdeshan (Strength Hierarchy)"}
        </span>
      </div>

      {viewMode === "house" && (
        <div className="space-y-4">
          {/* Explanation Box */}
          <div className="p-3.5 rounded-xl bg-[#FAF6EC] border border-[#D8BD80] text-xs text-[#102A4C] space-y-1">
            <div className="font-bold text-[#8C6D23]">
              {language === "ta" ? "4-அடுக்கு காரகத்துவ வரிசை:" : "KP 4-Tier Significator Strength Hierarchy:"}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 pt-1 text-[11px]">
              <div className="p-2 rounded bg-white/70 border border-[#D8BD80]/50">
                <strong className="text-emerald-700">Level A (Strongest):</strong> Planets in star of occupants
              </div>
              <div className="p-2 rounded bg-white/70 border border-[#D8BD80]/50">
                <strong className="text-blue-700">Level B:</strong> Occupants of the house
              </div>
              <div className="p-2 rounded bg-white/70 border border-[#D8BD80]/50">
                <strong className="text-purple-700">Level C:</strong> Planets in star of house lord
              </div>
              <div className="p-2 rounded bg-white/70 border border-[#D8BD80]/50">
                <strong className="text-amber-700">Level D:</strong> Sign lord of the house
              </div>
            </div>
          </div>

          {/* House Significators Table */}
          <div className="overflow-x-auto rounded-xl border border-[#E2DCD5] shadow-xs bg-white">
            <table className="min-w-full divide-y divide-[#E2DCD5] text-xs sm:text-sm">
              <thead className="bg-[#F8FAFC] text-[#475569] font-semibold">
                <tr>
                  <th className="px-3 py-3 text-center w-12">
                    {language === "ta" ? "பாவகம்" : "House"}
                  </th>
                  <th className="px-3 py-3 text-left">
                    {language === "ta" ? "ராசி / அதிபதி" : "Sign / Lord"}
                  </th>
                  <th className="px-3 py-3 text-left">
                    <span className="text-emerald-700 font-bold">Level A</span>
                  </th>
                  <th className="px-3 py-3 text-left">
                    <span className="text-blue-700 font-bold">Level B</span>
                  </th>
                  <th className="px-3 py-3 text-left">
                    <span className="text-purple-700 font-bold">Level C</span>
                  </th>
                  <th className="px-3 py-3 text-left">
                    <span className="text-amber-700 font-bold">Level D</span>
                  </th>
                  <th className="px-3 py-3 text-left">
                    <span className="text-[#102A4C] font-bold">
                      {language === "ta" ? "காரக கிரகங்கள் (A→D)" : "All Significators"}
                    </span>
                  </th>
                  <th className="px-3 py-3 text-center">
                    <span className="text-[#B8860B] font-bold">
                      {language === "ta" ? "தீர்ப்பு அதிபதி (CSL)" : "Arbiter (CSL)"}
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] text-[#1E293B]">
                {houseSignificators?.map((h) => (
                  <tr key={h.house} className="hover:bg-[#FAF6EC]/60 transition-colors">
                    <td className="px-3 py-2.5 text-center font-bold text-[#102A4C]">
                      <span className="w-7 h-7 rounded-full bg-[#FAF2DE] border border-[#D8BD80] text-[#8C6D23] flex items-center justify-center mx-auto text-xs">
                        {h.house}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 whitespace-nowrap text-xs">
                      {getRasiName(h.sign_name, language)} ({getLordName(h.sign_lord, language)})
                    </td>
                    <td className="px-3 py-2.5 whitespace-nowrap">
                      {h.level_a.length > 0 ? (
                        <span className="font-semibold text-emerald-700">
                          {h.level_a.map((p) => getGrahaName(p, language)).join(", ")}
                        </span>
                      ) : (
                        <span className="text-[#94A3B8]">—</span>
                      )}
                    </td>
                    <td className="px-3 py-2.5 whitespace-nowrap">
                      {h.level_b.length > 0 ? (
                        <span className="font-semibold text-blue-700">
                          {h.level_b.map((p) => getGrahaName(p, language)).join(", ")}
                        </span>
                      ) : (
                        <span className="text-[#94A3B8]">—</span>
                      )}
                    </td>
                    <td className="px-3 py-2.5 whitespace-nowrap">
                      {h.level_c.length > 0 ? (
                        <span className="font-semibold text-purple-700">
                          {h.level_c.map((p) => getGrahaName(p, language)).join(", ")}
                        </span>
                      ) : (
                        <span className="text-[#94A3B8]">—</span>
                      )}
                    </td>
                    <td className="px-3 py-2.5 whitespace-nowrap">
                      {h.level_d.length > 0 ? (
                        <span className="font-semibold text-amber-700">
                          {h.level_d.map((p) => getGrahaName(p, language)).join(", ")}
                        </span>
                      ) : (
                        <span className="text-[#94A3B8]">—</span>
                      )}
                    </td>
                    <td className="px-3 py-2.5 whitespace-nowrap">
                      {h.all_significators.length > 0 ? (
                        <span className="font-bold text-[#102A4C]">
                          {h.all_significators.map((p) => getGrahaName(p, language)).join(", ")}
                        </span>
                      ) : (
                        <span className="text-[#94A3B8]">—</span>
                      )}
                    </td>
                    <td className="px-3 py-2.5 text-center whitespace-nowrap">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-md font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                        {getLordName(h.sub_lord, language)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {viewMode === "planet" && (
        <div className="overflow-x-auto rounded-xl border border-[#E2DCD5] shadow-xs bg-white">
          <table className="min-w-full divide-y divide-[#E2DCD5] text-xs sm:text-sm">
            <thead className="bg-[#F8FAFC] text-[#475569] font-semibold">
              <tr>
                <th className="px-3 py-3 text-left">
                  {language === "ta" ? "கிரகம்" : "Planet"}
                </th>
                <th className="px-3 py-3 text-left">
                  {language === "ta" ? "காரகத்துவ பாவகங்கள்" : "Signified Houses"}
                </th>
                <th className="px-3 py-3 text-left">
                  {language === "ta" ? "வலிமை வரிசை (Strength Details)" : "Strength Order (Role / Houses)"}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9] text-[#1E293B]">
              {planetSignificators?.map((p) => (
                <tr key={p.planet} className="hover:bg-[#FAF6EC]/60 transition-colors">
                  <td className="px-3 py-2.5 font-bold text-[#102A4C] whitespace-nowrap">
                    {getGrahaName(p.planet, language)}
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    <div className="flex flex-wrap gap-1">
                      {p.signified_houses.map((h) => (
                        <span
                          key={h}
                          className="px-1.5 py-0.5 rounded bg-[#FAF2DE] border border-[#D8BD80] text-[#8C6D23] font-bold text-xs"
                        >
                          {h}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-3 py-2.5 text-xs text-[#475569]">
                    <div className="flex flex-wrap gap-1.5">
                      {p.strength_order.map((s, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded-md bg-[#F1F5F9] border border-[#E2E8F0] text-[11px]"
                        >
                          <strong>{s.type}:</strong> House {s.house}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
