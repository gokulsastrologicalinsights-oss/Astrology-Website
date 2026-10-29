"use client";

import React from "react";
import { HoroscopeResponse, PlanetInfo } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaShort } from "@/lib/translations";
import { formatDm } from "@/lib/formatters";
import { getGrahaDignity } from "@/lib/dignity";
import { DignityLegend } from "@/components/charts/DignityLegend";

interface NorthIndianChartProps {
  horoscope: HoroscopeResponse;
  transitPlanets?: PlanetInfo[];
  showTransits?: boolean;
  isSaved?: boolean;
  highlightLagnaBlue?: boolean;
  showDignityLegend?: boolean;
}

interface HouseLayout {
  houseNumber: number;
  signIndex: number;
  labelX: number;
  labelY: number;
  planetsX: number;
  planetsY: number;
}

// Outer perimeter coordinates for 12 houses when transits are enabled
const NORTH_TRANSIT_ANCHORS: Record<number, { x: number; y: number }> = {
  1: { x: 200, y: -26 },   // Top apex (House 1)
  2: { x: 90, y: -26 },    // Top left (House 2)
  3: { x: -26, y: 90 },    // Left upper (House 3)
  4: { x: -26, y: 200 },   // Left apex (House 4)
  5: { x: -26, y: 310 },   // Left lower (House 5)
  6: { x: 90, y: 426 },    // Bottom left (House 6)
  7: { x: 200, y: 426 },   // Bottom apex (House 7)
  8: { x: 310, y: 426 },   // Bottom right (House 8)
  9: { x: 426, y: 310 },   // Right lower (House 9)
  10: { x: 426, y: 200 },  // Right apex (House 10)
  11: { x: 426, y: 90 },   // Right upper (House 11)
  12: { x: 310, y: -26 },  // Top right (House 12)
};

export function NorthIndianChart({
  horoscope,
  transitPlanets,
  showTransits = false,
  isSaved,
  highlightLagnaBlue,
  showDignityLegend = true,
}: NorthIndianChartProps) {
  const { language } = useLanguage();
  const { ascendant, planets, metadata } = horoscope;

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

  const ascSign = ascendant.sign_index;

  // Calculate sign index for each house (1 to 12)
  const getHouseSign = (h: number): number => {
    return ((ascSign - 1 + (h - 1)) % 12) + 1;
  };

  // Group natal planets by sign_index
  const planetsBySign: Record<number, PlanetInfo[]> = {};
  for (let s = 1; s <= 12; s++) {
    planetsBySign[s] = [];
  }
  for (const p of planets) {
    if (planetsBySign[p.sign_index]) {
      planetsBySign[p.sign_index].push(p);
    }
  }

  // Group transit planets by sign_index
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

  // Exact coordinates for SVG (400x400 viewBox)
  const houses: HouseLayout[] = [
    { houseNumber: 1, signIndex: getHouseSign(1), labelX: 200, labelY: 175, planetsX: 200, planetsY: 105 },
    { houseNumber: 2, signIndex: getHouseSign(2), labelX: 140, labelY: 80, planetsX: 100, planetsY: 45 },
    { houseNumber: 3, signIndex: getHouseSign(3), labelX: 75, labelY: 140, planetsX: 45, planetsY: 100 },
    { houseNumber: 4, signIndex: getHouseSign(4), labelX: 175, labelY: 200, planetsX: 105, planetsY: 200 },
    { houseNumber: 5, signIndex: getHouseSign(5), labelX: 75, labelY: 260, planetsX: 45, planetsY: 300 },
    { houseNumber: 6, signIndex: getHouseSign(6), labelX: 140, labelY: 320, planetsX: 100, planetsY: 355 },
    { houseNumber: 7, signIndex: getHouseSign(7), labelX: 200, labelY: 230, planetsX: 200, planetsY: 295 },
    { houseNumber: 8, signIndex: getHouseSign(8), labelX: 260, labelY: 320, planetsX: 300, planetsY: 355 },
    { houseNumber: 9, signIndex: getHouseSign(9), labelX: 325, labelY: 260, planetsX: 355, planetsY: 300 },
    { houseNumber: 10, signIndex: getHouseSign(10), labelX: 225, labelY: 200, planetsX: 295, planetsY: 200 },
    { houseNumber: 11, signIndex: getHouseSign(11), labelX: 325, labelY: 140, planetsX: 355, planetsY: 100 },
    { houseNumber: 12, signIndex: getHouseSign(12), labelX: 260, labelY: 80, planetsX: 300, planetsY: 45 },
  ];

  const viewBox = showTransits ? "-55 -55 510 510" : "0 0 400 400";

  return (
    <div className="w-full max-w-md sm:max-w-lg lg:max-w-xl mx-auto select-none">
      <div className="border-2 border-[#B8860B]/70 bg-[#FAF7F0] rounded-lg shadow-sm p-2 sm:p-3 overflow-hidden">
        <div className="aspect-square w-full relative bg-[#FFFDF9] border border-[#B8860B]/60 rounded overflow-hidden">
          <svg
            viewBox={viewBox}
            className="w-full h-full"
            style={{ fontVariantNumeric: "tabular-nums" }}
          >
            {showTransits && (
              <>
                {/* Outer Perimeter Ring for Live Transits */}
                <rect
                  x="-50"
                  y="-50"
                  width="500"
                  height="500"
                  rx="10"
                  fill="#FAF8F2"
                  stroke="#D8BD80"
                  strokeWidth="1.5"
                  strokeDasharray="3 3"
                />
                {/* Outer Corner Badges */}
                <text
                  x="-42"
                  y="-36"
                  fill="#8C6D23"
                  fontSize="8"
                  fontWeight="bold"
                  className="font-mono select-none"
                >
                  🪐 TR
                </text>
              </>
            )}

            {/* Natal Chart Background */}
            <rect x="0" y="0" width="400" height="400" fill="#FFFDF9" />

            {/* When saved chart is opened, highlight only Lagna (House 1 top diamond) in blue */}
            {isSavedChart && (
              <polygon
                points="200,0 300,100 200,200 100,100"
                fill="#D8E8FD"
                opacity="0.85"
              />
            )}

            {/* Geometric Lines */}
            {/* Outer Box */}
            <rect
              x="0"
              y="0"
              width="400"
              height="400"
              fill="none"
              stroke="#B8860B"
              strokeWidth="2"
            />
            {/* Diagonals */}
            <line x1="0" y1="0" x2="400" y2="400" stroke="#D8BD80" strokeWidth="1.5" />
            <line x1="400" y1="0" x2="0" y2="400" stroke="#D8BD80" strokeWidth="1.5" />
            {/* Inner Rhombus Diamond */}
            <polygon
              points="200,0 400,200 200,400 0,200"
              fill="none"
              stroke="#B8860B"
              strokeWidth="1.5"
            />

            {/* Render Each Natal House Content */}
            {houses.map((h) => {
              const occupants = planetsBySign[h.signIndex] || [];
              const isH1 = h.houseNumber === 1;

              return (
                <g key={`h-${h.houseNumber}`}>
                  {/* Sign Index Number (e.g. 1 for Aries, 4 for Cancer) */}
                  <text
                    x={h.labelX}
                    y={h.labelY}
                    textAnchor="middle"
                    dominantBaseline="central"
                    fill="#8C6D23"
                    fontSize="10"
                    fontWeight="bold"
                    className="select-none font-mono opacity-80"
                  >
                    {h.signIndex}
                  </text>

                  {/* House 1 Ascendant Marker */}
                  {isH1 && (
                    <text
                      x={h.planetsX}
                      y={h.planetsY - (occupants.length > 0 ? occupants.length * 6 + 12 : 0)}
                      textAnchor="middle"
                      fill="#784E0E"
                      fontSize="9.5"
                      fontWeight="bold"
                      className="select-none"
                    >
                      {language === "ta" ? "லக்னம்" : "Asc"} ({formatDm(ascendant.degree_in_sign)})
                    </text>
                  )}

                  {/* Occupant Natal Planets */}
                  {occupants.map((p, idx) => {
                    const shortName = getGrahaShort(p.name, language);
                    const dignity = getGrahaDignity(
                      p.name,
                      h.signIndex,
                      ascendant.sign_index,
                      p.degree_in_sign,
                      h.houseNumber
                    );
                    const retro = p.is_retrograde
                      ? language === "ta"
                        ? "(வ)"
                        : "(R)"
                      : "";
                    const lineHeight = occupants.length > 3 ? 10.5 : 12;
                    const yOffset = (idx - (occupants.length - 1) / 2) * lineHeight + (isH1 ? 8 : 0);

                    return (
                      <text
                        key={p.name}
                        x={h.planetsX}
                        y={h.planetsY + yOffset}
                        textAnchor="middle"
                        dominantBaseline="central"
                        fill={dignity.colorHex}
                        fontSize={occupants.length > 3 ? "9.5" : occupants.length > 1 ? "11" : "12.5"}
                        fontWeight={dignity.status !== "none" ? "700" : occupants.length <= 2 ? "600" : "500"}
                        className="select-none"
                      >
                        <title>{language === "ta" ? dignity.tooltipTa : dignity.tooltipEn}</title>
                        {shortName}
                        {(dignity.status === "ucham_dikbala" || dignity.status === "neecham_dikbala") && "⚡"}
                        {retro ? ` ${retro}` : ""}{" "}
                        <tspan fill="#64748B" fontSize={occupants.length > 3 ? "8" : "9"} className="font-mono">
                          {formatDm(p.degree_in_sign)}
                        </tspan>
                      </text>
                    );
                  })}
                </g>
              );
            })}

            {/* Render Outer Transit Overlays */}
            {showTransits &&
              houses.map((h) => {
                const transits = transitsBySign[h.signIndex] || [];
                const anchor = NORTH_TRANSIT_ANCHORS[h.houseNumber];
                if (!anchor) return null;

                if (transits.length === 0) {
                  return (
                    <circle
                      key={`tr-empty-${h.houseNumber}`}
                      cx={anchor.x}
                      cy={anchor.y}
                      r="1.8"
                      fill="#D8BD80"
                      opacity="0.6"
                    />
                  );
                }

                return (
                  <g key={`tr-group-${h.houseNumber}`}>
                    {transits.map((p, idx) => {
                      const shortName = getGrahaShort(p.name, language);
                      const degInt = Math.floor(p.degree_in_sign || 0);
                      const retro = p.is_retrograde
                        ? language === "ta"
                          ? "(வ)"
                          : "(R)"
                        : "";
                      const yOffset = (idx - (transits.length - 1) / 2) * 14;
                      return (
                        <g key={`tr-p-${p.name}`}>
                          <rect
                            x={anchor.x - 32}
                            y={anchor.y + yOffset - 7.5}
                            width="64"
                            height="15"
                            rx="3"
                            fill="#FAF2DE"
                            stroke="#B8862B"
                            strokeWidth="0.8"
                          />
                          <text
                            x={anchor.x}
                            y={anchor.y + yOffset}
                            textAnchor="middle"
                            dominantBaseline="central"
                            fill="#8C6D23"
                            fontSize="8"
                            fontWeight="bold"
                            className="font-mono select-none"
                          >
                            TR {shortName} {degInt}° {retro}
                          </text>
                        </g>
                      );
                    })}
                  </g>
                );
              })}
          </svg>
        </div>
      </div>

      <div className="mt-2 flex items-center justify-between text-[11px] text-[#64748B] px-1">
        <span>
          {language === "ta"
            ? "வடஇந்திய குண்டலி முறை (வைர வடிவம்)"
            : "North Indian Kundali Format (Fixed-House Diamond)"}
        </span>
        <span className="text-[#8C6D23] font-medium font-mono text-[10px]">
          {metadata.ayanamsa_name}
        </span>
      </div>

      {/* Navagraha Dignity & Directional Strength (Dik Balam) Color Legend */}
      {showDignityLegend && <DignityLegend className="mt-2.5 w-full" />}
    </div>
  );
}
