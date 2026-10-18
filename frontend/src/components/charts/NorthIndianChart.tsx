"use client";

import React from "react";
import { HoroscopeResponse, PlanetInfo } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaShort } from "@/lib/translations";
import { formatDm } from "@/lib/formatters";

interface NorthIndianChartProps {
  horoscope: HoroscopeResponse;
}

interface HouseLayout {
  houseNumber: number;
  signIndex: number;
  labelX: number;
  labelY: number;
  planetsX: number;
  planetsY: number;
}

export function NorthIndianChart({ horoscope }: NorthIndianChartProps) {
  const { language } = useLanguage();
  const { ascendant, planets, metadata } = horoscope;

  const ascSign = ascendant.sign_index;

  // Calculate sign index for each house (1 to 12)
  const getHouseSign = (h: number): number => {
    return ((ascSign - 1 + (h - 1)) % 12) + 1;
  };

  // Group planets by sign_index
  const planetsBySign: Record<number, PlanetInfo[]> = {};
  for (let s = 1; s <= 12; s++) {
    planetsBySign[s] = [];
  }
  for (const p of planets) {
    if (planetsBySign[p.sign_index]) {
      planetsBySign[p.sign_index].push(p);
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

  return (
    <div className="w-full max-w-xl mx-auto select-none">
      <div className="border-2 border-[#B8860B]/70 bg-[#FAF7F0] rounded-lg shadow-sm p-2 sm:p-3 overflow-hidden">
        <div className="aspect-square w-full relative bg-[#FFFDF9] border border-[#B8860B]/60 rounded">
          <svg
            viewBox="0 0 400 400"
            className="w-full h-full"
            style={{ fontVariantNumeric: "tabular-nums" }}
          >
            {/* Background */}
            <rect x="0" y="0" width="400" height="400" fill="#FFFDF9" />

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

            {/* Render Each House Content */}
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

                  {/* Occupant Planets */}
                  {occupants.map((p, idx) => {
                    const shortName = getGrahaShort(p.name, language);
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
                        fill="#0F172A"
                        fontSize={occupants.length > 3 ? "8.5" : "9.5"}
                        fontWeight="500"
                        className="select-none"
                      >
                        {shortName} {retro}{" "}
                        <tspan fill="#64748B" fontSize={occupants.length > 3 ? "7.5" : "8"} className="font-mono">
                          {formatDm(p.degree_in_sign)}
                        </tspan>
                      </text>
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
    </div>
  );
}
