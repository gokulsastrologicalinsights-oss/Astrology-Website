"use client";

import React, { useState } from "react";
import { LoShuGridResult } from "@/lib/types";
import { Grid3X3, Zap, ShieldAlert, Sparkles, CheckCircle2 } from "lucide-react";

interface Props {
  loShu: LoShuGridResult;
}

export function LoShuGrid({ loShu }: Props) {
  const [activePlane, setActivePlane] = useState<string>("mental");

  // Standard Lo Shu grid arrangement
  // Row 1: 4, 9, 2
  // Row 2: 3, 5, 7
  // Row 3: 8, 1, 6
  const gridCells = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
  ];

  return (
    <div className="rounded-2xl border border-[#E2DCD5] bg-white p-6 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#E2DCD5]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8860B]">
            <Grid3X3 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-serif text-base font-bold text-[#0F172A]">
              3x3 Lo Shu Magic Square & Planes
            </h3>
            <p className="text-[11px] text-[#64748B]">
              Deterministic frequency mapping of digits 1-9 from your birth date.
            </p>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        {/* 3x3 Magic Square Interactive Grid */}
        <div className="max-w-[280px] mx-auto w-full aspect-square grid grid-cols-3 gap-2.5 p-3 rounded-2xl bg-[#FAF8F5] border border-[#E2DCD5]">
          {gridCells.flatMap((row, rIdx) =>
            row.map((num) => {
              const count = loShu.grid_counts[String(num)] || 0;
              const isPresent = count > 0;

              return (
                <div
                  key={num}
                  className={`relative rounded-xl border flex flex-col items-center justify-center transition-all ${
                    isPresent
                      ? "bg-white border-[#B8860B] shadow-2xs text-[#0F172A]"
                      : "bg-[#F1ECE6]/60 border-dashed border-[#CBD5E1] text-[#94A3B8]"
                  }`}
                >
                  <span className="font-serif text-xl sm:text-2xl font-bold">
                    {num}
                  </span>
                  <span
                    className={`text-[10px] font-bold mt-0.5 px-1.5 py-0.2 rounded-full ${
                      isPresent
                        ? "bg-[#FAF2DE] text-[#8C6D23]"
                        : "text-[#94A3B8]"
                    }`}
                  >
                    {isPresent ? `${count}x` : "None"}
                  </span>
                </div>
              );
            })
          )}
        </div>

        {/* Planes Analysis Cards */}
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-1.5 pb-2">
            {Object.entries(loShu.planes).map(([key, plane]) => (
              <button
                key={key}
                type="button"
                onClick={() => setActivePlane(key)}
                className={`px-2 py-1.5 rounded-lg text-[10px] font-bold truncate transition-colors cursor-pointer ${
                  activePlane === key
                    ? "bg-[#0F172A] text-white shadow-xs"
                    : "bg-[#FAF8F5] text-[#475569] hover:bg-[#F1ECE6] border border-[#E2DCD5]"
                }`}
              >
                {key.toUpperCase()}
              </button>
            ))}
          </div>

          {loShu.planes[activePlane] && (
            <div className="p-3.5 rounded-xl border border-[#D8BD80]/60 bg-[#FAF2DE]/40">
              <div className="flex items-center justify-between pb-1.5 border-b border-[#D8BD80]/30">
                <span className="font-bold text-xs text-[#0F172A]">
                  {loShu.planes[activePlane].name}
                </span>
                <span className="text-[10px] font-semibold text-[#8C6D23]">
                  {loShu.planes[activePlane].present_count} Digits Present
                </span>
              </div>
              <p className="mt-2 text-xs text-[#475569] leading-relaxed">
                {loShu.planes[activePlane].description}
              </p>
            </div>
          )}

          {/* Arrows of Strength / Weakness */}
          <div className="space-y-2 pt-2">
            {loShu.arrows_of_strength.length > 0 && (
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold text-emerald-800 flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Active Arrows of Strength:</span>
                </div>
                {loShu.arrows_of_strength.map((arr, i) => (
                  <div
                    key={i}
                    className="p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-950 flex items-start gap-2"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                    <div>
                      <div className="font-bold">{arr.name} ({arr.numbers})</div>
                      <div className="text-[11px] text-emerald-800">{arr.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {loShu.arrows_of_weakness.length > 0 && (
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold text-amber-800 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                  <span>Arrows of Potential Cultivation:</span>
                </div>
                {loShu.arrows_of_weakness.map((arr, i) => (
                  <div
                    key={i}
                    className="p-2 rounded-lg bg-amber-50/70 border border-amber-200 text-xs text-amber-950 flex items-start gap-2"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-amber-600 mt-0.5 shrink-0" />
                    <div>
                      <div className="font-bold">{arr.name} ({arr.numbers})</div>
                      <div className="text-[11px] text-amber-800">{arr.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
