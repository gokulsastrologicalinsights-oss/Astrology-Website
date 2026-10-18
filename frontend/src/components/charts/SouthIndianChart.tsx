"use client";

import React from "react";
import { HoroscopeResponse, PlanetInfo } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { RASIS, getGrahaShort, getRasiName } from "@/lib/translations";

interface SouthIndianChartProps {
  horoscope: HoroscopeResponse;
  title?: string;
  headerTitle?: string;
  centerLabel?: string;
  centerNumber?: string;
  planetsOverride?: PlanetInfo[];
  ascendantOverride?: { sign_index: number; degree_in_sign: number };
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

export function SouthIndianChart({
  horoscope,
  title,
  headerTitle,
  centerLabel,
  centerNumber,
  planetsOverride,
  ascendantOverride,
}: SouthIndianChartProps) {
  const { language } = useLanguage();
  const ascendant = ascendantOverride || horoscope.ascendant;
  const planets = planetsOverride || horoscope.planets;
  const { metadata } = horoscope;

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

  const chartHeader = headerTitle || title;
  const centralText = centerLabel || (language === "ta" ? "ராசி" : "Rasi");
  const centralNum = centerNumber || "(1)";

  return (
    <div className="w-full max-w-sm sm:max-w-md mx-auto select-none flex flex-col items-center">
      {/* Chart Title above chart matching Screenshot 3 */}
      {chartHeader && (
        <div className="text-center font-bold text-xs sm:text-sm text-[#183047] mb-2 font-tamil">
          {chartHeader}
        </div>
      )}

      {/* 4x4 South Indian Grid matching Screenshot 3 */}
      <div className="w-full aspect-square border-2 border-[#183047] bg-white shadow-xs rounded-sm overflow-hidden">
        <div className="grid grid-cols-4 grid-rows-4 w-full h-full">
          {SOUTH_GRID.map((cell) => {
            const isAscendant = ascendant.sign_index === cell.signIndex;
            const cellPlanets = planetsBySign[cell.signIndex] || [];
            const rasi = RASIS[cell.signIndex];

            return (
              <div
                key={`cell-${cell.signIndex}`}
                style={{
                  gridRowStart: cell.row + 1,
                  gridColumnStart: cell.col + 1,
                }}
                className={`border border-[#183047] p-1 sm:p-1.5 flex flex-col justify-between overflow-hidden relative transition-colors ${
                  isAscendant ? "bg-[#FAF2DE]/40" : "bg-white"
                }`}
              >
                {/* Optional subtle corner rasi symbol/indicator */}
                <div className="text-[9px] text-[#8190A6] font-mono leading-none">
                  {rasi?.symbol || ""}
                </div>

                {/* Body: Grahas and Ascendant matching Screenshot 3 (e.g. 21-சனி(வ), 19-ல) */}
                <div className="flex-1 flex flex-col justify-center items-center gap-0.5 py-0.5 overflow-hidden text-center">
                  {isAscendant && (
                    <div className="text-[10px] sm:text-[11px] font-bold text-[#153F6B] leading-tight">
                      <span>{Math.floor(ascendant.degree_in_sign)}</span>
                      <span>-{language === "ta" ? "ல" : "Asc"}</span>
                    </div>
                  )}

                  {cellPlanets.map((p) => {
                    const shortName = getGrahaShort(p.name, language);
                    const degInt = Math.floor(p.degree_in_sign || 0);
                    return (
                      <div
                        key={p.name}
                        className="text-[10px] sm:text-[11px] font-semibold text-[#183047] leading-tight tracking-tight flex items-center justify-center gap-0.5"
                        title={`${p.name} (${p.degree_in_sign.toFixed(2)}°) in ${p.sign_name}`}
                      >
                        {degInt > 0 && <span className="font-mono">{degInt}-</span>}
                        <span>{shortName}</span>
                        {p.is_retrograde && (
                          <span className="text-red-600 font-bold text-[9px]">
                            {language === "ta" ? "(வ)" : "(R)"}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>

                <div className="h-1" />
              </div>
            );
          })}

          {/* Central 2x2 Hub matching Screenshot 3 */}
          <div
            style={{
              gridRow: "2 / span 2",
              gridColumn: "2 / span 2",
            }}
            className="border border-[#183047] bg-white flex flex-col items-center justify-center p-2 text-center"
          >
            <div className="text-sm sm:text-base font-bold text-[#183047] font-tamil">
              {centralText}
            </div>
            {centralNum && (
              <div className="text-xs sm:text-sm font-semibold text-[#183047] font-mono mt-0.5">
                {centralNum}
              </div>
            )}
            <div className="text-[9px] text-[#8190A6] font-mono mt-1">
              {metadata?.ayanamsa_name || "Lahiri"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
