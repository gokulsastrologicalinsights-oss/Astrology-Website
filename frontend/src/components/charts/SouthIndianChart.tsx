"use client";

import React from "react";
import { HoroscopeResponse, PlanetInfo } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { RASIS, getGrahaShort, getRasiName } from "@/lib/translations";
import { formatDm } from "@/lib/formatters";

interface SouthIndianChartProps {
  horoscope: HoroscopeResponse;
  title?: string;
}

// Fixed mapping of 4x4 grid cells to Zodiac Sign indices (1-12)
// Row 0: Meenam (12), Mesham (1), Rishabam (2), Mithunam (3)
// Row 1: Kumbham (11), [CENTER 2x2], Katakam (4)
// Row 2: Makaram (10), [CENTER 2x2], Simham (5)
// Row 3: Dhanusu (9), Vrischigam (8), Thulam (7), Kanni (6)

interface CellCoord {
  row: number;
  col: number;
  signIndex: number;
}

const SOUTH_GRID: CellCoord[] = [
  { row: 0, col: 0, signIndex: 12 }, // Pisces
  { row: 0, col: 1, signIndex: 1 },  // Aries
  { row: 0, col: 2, signIndex: 2 },  // Taurus
  { row: 0, col: 3, signIndex: 3 },  // Gemini

  { row: 1, col: 3, signIndex: 4 },  // Cancer
  { row: 2, col: 3, signIndex: 5 },  // Leo

  { row: 3, col: 3, signIndex: 6 },  // Virgo
  { row: 3, col: 2, signIndex: 7 },  // Libra
  { row: 3, col: 1, signIndex: 8 },  // Scorpio
  { row: 3, col: 0, signIndex: 9 },  // Sagittarius

  { row: 2, col: 0, signIndex: 10 }, // Capricorn
  { row: 1, col: 0, signIndex: 11 }, // Aquarius
];

export function SouthIndianChart({ horoscope, title }: SouthIndianChartProps) {
  const { language } = useLanguage();
  const { ascendant, planets, metadata } = horoscope;

  // Group planets by sign_index (1 to 12)
  const planetsBySign: Record<number, PlanetInfo[]> = {};
  for (let s = 1; s <= 12; s++) {
    planetsBySign[s] = [];
  }

  for (const p of planets) {
    if (planetsBySign[p.sign_index]) {
      planetsBySign[p.sign_index].push(p);
    }
  }

  return (
    <div className="w-full max-w-xl mx-auto select-none">
      <div className="border-2 border-[#B8860B]/70 bg-[#FAF7F0] rounded-lg shadow-sm p-2 sm:p-3 overflow-hidden">
        {/* 4x4 Grid Container */}
        <div className="grid grid-cols-4 grid-rows-4 aspect-square border border-[#B8860B]/60 bg-[#FFFDF9] rounded">
          {SOUTH_GRID.map((cell) => {
            const rasi = RASIS[cell.signIndex];
            const isAscendant = ascendant.sign_index === cell.signIndex;
            const cellPlanets = planetsBySign[cell.signIndex] || [];
            const rasiName = getRasiName(cell.signIndex, language);

            return (
              <div
                key={`cell-${cell.signIndex}`}
                style={{
                  gridRowStart: cell.row + 1,
                  gridColumnStart: cell.col + 1,
                }}
                className={`border border-[#D8BD80]/80 p-1.5 flex flex-col justify-between overflow-hidden relative transition-colors ${
                  isAscendant ? "bg-[#FAF2DE]/50" : "hover:bg-[#FAF6EC]/60"
                }`}
              >
                {/* Header: Rasi name & symbol */}
                <div className="flex items-center justify-between border-b border-[#E8DEC8] pb-0.5 text-[10px] sm:text-[11px] leading-tight text-[#475569]">
                  <span className="font-semibold truncate text-[#1E293B]">
                    {rasiName}
                  </span>
                  <span className="text-[#8C6D23] font-serif text-xs opacity-75">
                    {rasi?.symbol}
                  </span>
                </div>

                {/* Body: Grahas and Ascendant */}
                <div
                  className={`flex-1 flex flex-col ${
                    cellPlanets.length + (isAscendant ? 1 : 0) > 2
                      ? "justify-start overflow-y-auto"
                      : "justify-center"
                  } space-y-0.5 py-0.5`}
                >
                  {isAscendant && (
                    <div className="flex items-center justify-between bg-[#B8860B]/15 text-[#784E0E] px-1 py-0.5 rounded text-[10px] sm:text-[11px] font-bold shrink-0">
                      <span>{language === "ta" ? "லக்னம்" : "ASC"}</span>
                      <span className="font-mono text-[9px] font-normal">
                        {formatDm(ascendant.degree_in_sign)}
                      </span>
                    </div>
                  )}

                  {cellPlanets.map((p) => {
                    const shortName = getGrahaShort(p.name, language);
                    return (
                      <div
                        key={p.name}
                        className="flex items-center justify-between text-[10px] sm:text-[11px] leading-tight text-[#0F172A] px-0.5 hover:bg-[#F3EBD6]/50 rounded shrink-0"
                        title={`${p.name} (${p.degree_in_sign.toFixed(2)}°) in ${p.sign_name}`}
                      >
                        <span className="font-medium flex items-center gap-0.5">
                          <span>{shortName}</span>
                          {p.is_retrograde && (
                            <span className="text-red-700 font-bold text-[9px]">
                              {language === "ta" ? "(வ)" : "(R)"}
                            </span>
                          )}
                        </span>
                        <span className="font-mono text-[9px] text-[#64748B]">
                          {formatDm(p.degree_in_sign)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {/* Central 2x2 Hub (Row 2-3, Col 2-3) */}
          <div
            style={{
              gridRow: "2 / span 2",
              gridColumn: "2 / span 2",
            }}
            className="border border-[#D8BD80] bg-[#FAF6EC]/80 flex flex-col items-center justify-center p-3 text-center"
          >
            <div className="text-xs uppercase tracking-widest text-[#8C6D23] font-bold">
              {title || (language === "ta" ? "ராசி சக்கரம்" : "Rasi Chakra")}
            </div>
            <div className="text-[11px] font-serif text-[#1E293B] mt-1 font-semibold">
              {metadata.ayanamsa_name}
            </div>
            <div className="text-[9px] text-[#64748B] mt-0.5 font-mono">
              Ayanamsa: {metadata.ayanamsa_deg.toFixed(4)}°
            </div>
            <div className="mt-2 text-[10px] text-[#475569] border-t border-[#E8DEC8] pt-1">
              <span>{language === "ta" ? "லக்னம்" : "Ascendant"}: </span>
              <span className="font-semibold text-[#0F172A]">
                {getRasiName(ascendant.sign_index, language)}
              </span>
              <span className="font-mono text-[9px] ml-1">
                ({formatDm(ascendant.degree_in_sign)})
              </span>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-2 flex items-center justify-between text-[11px] text-[#64748B] px-1">
        <span>
          {language === "ta"
            ? "தென்னிந்திய நிராயன முறை (கடிகாரச் சுற்று)"
            : "South Indian Sidereal Format (Clockwise)"}
        </span>
        <span className="text-[#8C6D23] font-medium">
          {language === "ta" ? "நிலையான ராசிகள்" : "Fixed Sign Grid"}
        </span>
      </div>
    </div>
  );
}
