"use client";

import React from "react";
import { HoroscopeResponse, PlanetInfo } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaShort } from "@/lib/translations";

interface SouthIndianChartProps {
  horoscope: HoroscopeResponse;
  title?: string;
  headerTitle?: string;
  centerLabel?: string;
  centerNumber?: string;
  planetsOverride?: PlanetInfo[];
  ascendantOverride?: { sign_index: number; degree_in_sign: number };
  transitPlanets?: PlanetInfo[];
  showTransits?: boolean;
  isSaved?: boolean;
  highlightLagnaBlue?: boolean;
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
  transitPlanets,
  showTransits = false,
  isSaved,
  highlightLagnaBlue,
}: SouthIndianChartProps) {
  const { language } = useLanguage();
  const ascendant = ascendantOverride || horoscope.ascendant;
  const planets = planetsOverride || horoscope.planets;
  const { metadata } = horoscope;

  // Detect whether this chart belongs to a saved horoscope
  const isSavedChart = React.useMemo(() => {
    if (typeof highlightLagnaBlue === "boolean") return highlightLagnaBlue;
    if (typeof isSaved === "boolean") return isSaved;
    if (typeof window !== "undefined") {
      const sp = new URLSearchParams(window.location.search);
      if (sp.has("id") || sp.has("saved_id") || sp.has("horoscope_id")) {
        return true;
      }
    }
    return Boolean(
      (horoscope as any)?.id ||
      (horoscope as any)?.is_saved ||
      (horoscope as any)?.savedId ||
      (horoscope.metadata as any)?.is_saved
    );
  }, [isSaved, highlightLagnaBlue, horoscope]);

  // Group natal planets by sign_index (1 to 12)
  const planetsBySign: Record<number, PlanetInfo[]> = {};
  for (let s = 1; s <= 12; s++) {
    planetsBySign[s] = [];
  }
  for (const p of planets) {
    if (planetsBySign[p.sign_index]) {
      planetsBySign[p.sign_index].push(p);
    }
  }

  // Group transit planets by sign_index (1 to 12)
  const transitsBySign: Record<number, PlanetInfo[]> = {};
  for (let s = 1; s <= 12; s++) {
    transitsBySign[s] = [];
  }
  if (showTransits && transitPlanets) {
    for (const tp of transitPlanets) {
      if (transitsBySign[tp.sign_index]) {
        transitsBySign[tp.sign_index].push(tp);
      }
    }
  }

  const chartHeader = headerTitle || title;
  const centralText = centerLabel || (language === "ta" ? "ராசி" : "Rasi");
  const centralNum = centerNumber || "(1)";

  // Natal 4x4 Grid Content
  const renderNatalGrid = () => (
    <div className="grid grid-cols-4 grid-rows-4 w-full h-full">
      {SOUTH_GRID.map((cell) => {
        const isAscendant = ascendant.sign_index === cell.signIndex;
        const cellPlanets = planetsBySign[cell.signIndex] || [];
        const totalItems = (isAscendant ? 1 : 0) + cellPlanets.length;

        // Determine highlighting:
        // When opening a saved horoscope chart, highlight ONLY the Lagna box in blue.
        // Keep all other boxes in their existing colors (white) and styles.
        // For non-saved charts, Lagna uses the existing subtle cream highlight.
        const isLagnaHighlightedBlue = isSavedChart && isAscendant;

        let cellBgClass = "bg-white border-[#183047]";
        if (isLagnaHighlightedBlue) {
          cellBgClass = "bg-[#D8E8FD] ring-1 ring-inset ring-[#2563EB]/40 border-[#153F6B]";
        } else if (isAscendant) {
          cellBgClass = "bg-[#FAF2DE]/45 border-[#183047]";
        }

        // Scaled typography & layout classes based on item count for optimal readability & zero clipping
        let textClass = "text-sm sm:text-base md:text-[17px]";
        let gapClass = "gap-1";
        const isMultiColumn = totalItems >= 5;

        if (totalItems >= 5) {
          textClass = "text-[9.5px] sm:text-[10.5px] md:text-[11px]";
          gapClass = "gap-x-1 gap-y-0.5";
        } else if (totalItems === 4) {
          textClass = "text-[10.5px] sm:text-[11.5px] md:text-[12.5px]";
          gapClass = "gap-0.5";
        } else if (totalItems === 3) {
          textClass = "text-[11.5px] sm:text-[12.5px] md:text-[13.5px]";
          gapClass = "gap-0.5 sm:gap-1";
        } else if (totalItems === 2) {
          textClass = "text-[12.5px] sm:text-[14px] md:text-[15px]";
          gapClass = "gap-1 sm:gap-1.5";
        } else {
          textClass = "text-sm sm:text-base md:text-[17px]";
          gapClass = "gap-1";
        }

        const ascDeg = Math.floor(ascendant.degree_in_sign || 0);

        return (
          <div
            key={`cell-${cell.signIndex}`}
            style={{
              gridRowStart: cell.row + 1,
              gridColumnStart: cell.col + 1,
            }}
            className={`border p-1 sm:p-1.5 flex flex-col justify-center items-center overflow-hidden relative transition-colors ${cellBgClass}`}
          >
            {/* Body: Grahas and Ascendant */}
            <div
              className={`w-full flex-1 ${
                isMultiColumn
                  ? "grid grid-cols-2 gap-x-1 gap-y-0.5 justify-items-center items-center"
                  : `flex flex-col justify-center items-center ${gapClass}`
              } py-0.5 overflow-hidden text-center`}
            >
              {isAscendant && (
                <div
                  className={`${textClass} font-bold leading-tight tracking-tight flex items-center justify-center gap-0.5 whitespace-nowrap select-none ${
                    isLagnaHighlightedBlue ? "text-[#0C356A]" : "text-[#153F6B]"
                  }`}
                  title={`Lagna / Ascendant (${ascendant.degree_in_sign?.toFixed(2) ?? 0}°) in sign ${cell.signIndex}`}
                >
                  {ascDeg > 0 && <span className="font-mono">{ascDeg}-</span>}
                  <span className={language === "ta" ? "font-tamil" : ""}>
                    {language === "ta" ? "ல" : "Asc"}
                  </span>
                </div>
              )}

              {cellPlanets.map((p) => {
                const shortName = getGrahaShort(p.name, language);
                const degInt = Math.floor(p.degree_in_sign || 0);
                return (
                  <div
                    key={p.name}
                    className={`${textClass} font-semibold text-[#183047] leading-tight tracking-tight flex items-center justify-center gap-0.5 whitespace-nowrap`}
                    title={`${p.name} (${p.degree_in_sign.toFixed(2)}°) in ${p.sign_name}`}
                  >
                    {degInt > 0 && <span className="font-mono">{degInt}-</span>}
                    <span className={language === "ta" ? "font-tamil" : ""}>{shortName}</span>
                    {p.is_retrograde && (
                      <span
                        className="text-red-600 font-bold ml-0.5 text-[0.85em] leading-none"
                        title={language === "ta" ? "வக்ரம் (Retrograde)" : "Retrograde"}
                      >
                        {language === "ta" ? "(வ)" : "(R)"}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* Central 2x2 Hub */}
      <div
        style={{
          gridRow: "2 / span 2",
          gridColumn: "2 / span 2",
        }}
        className="border border-[#183047] bg-[#FDFDFD] flex flex-col items-center justify-center p-2 text-center"
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
  );

  // Helper to render outer transit cell
  const renderTransitCell = (signIndex: number, extraClasses: string = "") => {
    const list = transitsBySign[signIndex] || [];
    return (
      <div
        className={`border border-[#D8BD80] bg-[#FFFDF8] p-0.5 sm:p-1 flex flex-col items-center justify-center gap-0.5 overflow-hidden transition-all ${extraClasses}`}
      >
        {list.length === 0 ? (
          <span className="text-[8px] text-[#C2C9D6] select-none font-mono">·</span>
        ) : (
          list.map((p) => {
            const shortName = getGrahaShort(p.name, language);
            const degInt = Math.floor(p.degree_in_sign || 0);
            return (
              <div
                key={`tr-${p.name}`}
                className="px-1 py-0.5 bg-[#FAF2DE] border border-[#B8862B]/60 rounded-xs text-[8.5px] sm:text-[9.5px] font-bold text-[#8C6D23] leading-none tracking-tight flex items-center justify-center gap-0.5 shadow-2xs font-mono"
                title={`${p.name} (Transit ${p.degree_in_sign.toFixed(2)}°) in ${p.sign_name}`}
              >
                <span className="text-[7px] text-[#B45309] font-sans font-extrabold">TR</span>
                <span>{shortName}</span>
                <span>{degInt}°</span>
                {p.is_retrograde && (
                  <span className="text-red-600 font-bold text-[7.5px]">
                    {language === "ta" ? "(வ)" : "(R)"}
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    );
  };

  return (
    <div className="w-full max-w-md sm:max-w-lg lg:max-w-xl mx-auto select-none flex flex-col items-center">
      {/* Chart Title */}
      {chartHeader && (
        <div className="text-center font-bold text-xs sm:text-sm text-[#183047] mb-2 font-tamil">
          {chartHeader}
        </div>
      )}

      {showTransits ? (
        /* 6x6 Grid with Outer Transit Perimeter Ring */
        <div className="w-full aspect-square border-2 border-[#D8BD80] bg-[#FAF8F2] shadow-xs rounded-sm p-1 overflow-hidden">
          <div className="grid grid-cols-[minmax(38px,12%)_repeat(4,1fr)_minmax(38px,12%)] grid-rows-[minmax(38px,12%)_repeat(4,1fr)_minmax(38px,12%)] w-full h-full gap-0.5">
            {/* Top Outer Perimeter: Row 1 */}
            {/* Top-Left Corner Badge */}
            <div className="border border-[#D8BD80]/60 bg-[#FAF2DE] rounded-tl flex flex-col items-center justify-center p-0.5 text-center">
              <span className="text-[8.5px] font-bold text-[#8C6D23] font-mono leading-none">🪐 TR</span>
              <span className="text-[7px] text-[#A67C1E] font-medium leading-tight mt-0.5">
                {language === "ta" ? "கோசாரம்" : "Transit"}
              </span>
            </div>
            {/* Col 2: Pisces (12) */}
            {renderTransitCell(12, "rounded-none")}
            {/* Col 3: Aries (1) */}
            {renderTransitCell(1, "rounded-none")}
            {/* Col 4: Taurus (2) */}
            {renderTransitCell(2, "rounded-none")}
            {/* Col 5: Gemini (3) */}
            {renderTransitCell(3, "rounded-none")}
            {/* Top-Right Corner */}
            <div className="border border-[#D8BD80]/60 bg-[#FAF2DE] rounded-tr flex items-center justify-center text-[9px] text-[#8C6D23] font-bold">
              ✦
            </div>

            {/* Left Outer Perimeter: Col 1 */}
            {/* Row 2: Spacer */}
            <div className="border border-[#D8BD80]/40 bg-[#FAF7F0] flex items-center justify-center text-[8px] text-[#B8862B]">✦</div>
            {/* Middle 4x4 Natal Grid: Row 2-5, Col 2-5 */}
            <div className="row-start-2 row-span-4 col-start-2 col-span-4 border-2 border-[#183047] bg-white shadow-xs rounded-xs overflow-hidden">
              {renderNatalGrid()}
            </div>
            {/* Right Outer Perimeter: Col 6, Row 2 Spacer */}
            <div className="border border-[#D8BD80]/40 bg-[#FAF7F0] flex items-center justify-center text-[8px] text-[#B8862B]">✦</div>

            {/* Col 1, Row 3: Aquarius (11) */}
            {renderTransitCell(11, "row-start-3 col-start-1")}
            {/* Col 6, Row 3: Cancer (4) */}
            {renderTransitCell(4, "row-start-3 col-start-6")}

            {/* Col 1, Row 4: Capricorn (10) */}
            {renderTransitCell(10, "row-start-4 col-start-1")}
            {/* Col 6, Row 4: Leo (5) */}
            {renderTransitCell(5, "row-start-4 col-start-6")}

            {/* Col 1, Row 5: Spacer */}
            <div className="border border-[#D8BD80]/40 bg-[#FAF7F0] flex items-center justify-center text-[8px] text-[#B8862B] row-start-5 col-start-1">✦</div>
            {/* Col 6, Row 5: Spacer */}
            <div className="border border-[#D8BD80]/40 bg-[#FAF7F0] flex items-center justify-center text-[8px] text-[#B8862B] row-start-5 col-start-6">✦</div>

            {/* Bottom Outer Perimeter: Row 6 */}
            {/* Bottom-Left Corner */}
            <div className="border border-[#D8BD80]/60 bg-[#FAF2DE] rounded-bl flex items-center justify-center text-[9px] text-[#8C6D23] font-bold">
              ✦
            </div>
            {/* Col 2: Sagittarius (9) */}
            {renderTransitCell(9, "rounded-none")}
            {/* Col 3: Scorpio (8) */}
            {renderTransitCell(8, "rounded-none")}
            {/* Col 4: Libra (7) */}
            {renderTransitCell(7, "rounded-none")}
            {/* Col 5: Virgo (6) */}
            {renderTransitCell(6, "rounded-none")}
            {/* Bottom-Right Corner */}
            <div className="border border-[#D8BD80]/60 bg-[#FAF2DE] rounded-br flex items-center justify-center text-[9px] text-[#8C6D23] font-bold">
              ✦
            </div>
          </div>
        </div>
      ) : (
        /* Standard 4x4 South Indian Natal Grid (no outer transits) */
        <div className="w-full aspect-square border-2 border-[#183047] bg-white shadow-xs rounded-sm overflow-hidden">
          {renderNatalGrid()}
        </div>
      )}
    </div>
  );
}
