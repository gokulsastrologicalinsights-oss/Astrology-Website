"use client";

import React, { useState } from "react";
import { DirectionMetadata, PadaDeityMetadata } from "@/lib/types";

interface VastuMandalaProps {
  directions?: DirectionMetadata[];
  padas?: PadaDeityMetadata[];
  highlightDirection?: string;
  favorableDirections?: string[];
  className?: string;
}

export function VastuMandala({
  directions: _directions = [],
  padas: _padas = [],
  highlightDirection,
  favorableDirections = [],
  className = "",
}: VastuMandalaProps) {
  const [activeCell, setActiveCell] = useState<{
    title: string;
    sub: string;
    element: string;
    deity: string;
    tip: string;
    status: string;
  } | null>(null);

  // 9 inner zones configuration on a 3x3 layout (scaled to 700x700 viewBox)
  // Grid layout: row 0 (North), row 1 (Mid), row 2 (South); col 0 (West), col 1 (Center), col 2 (East)
  const innerZones = [
    { code: "NW", label: "西北 (Vāyavya)", deity: "Vāyu (風神)", element: "Air", tip: "客房 · 女兒房 · 車庫", r: 0, c: 0, color: "#E0F2FE" },
    { code: "N", label: "北方 (Uttara)", deity: "Kubera (財神)", element: "Water", tip: "財位 · 客廳 · 入口", r: 0, c: 1, color: "#E0F7FA" },
    { code: "NE", label: "東北 (Īśānya)", deity: "Īśāna (濕婆)", element: "Ether", tip: "祈禱 · 冥想 · 水井", r: 0, c: 2, color: "#F3E8FF" },
    { code: "W", label: "西方 (Paścima)", deity: "Varuṇa (水界)", element: "Water", tip: "餐廳 · 次臥 · 學習", r: 1, c: 0, color: "#EDE9FE" },
    { code: "Center", label: "中央 (Brahmasthan)", deity: "Brahmā (梵天)", element: "Ether", tip: "宇宙核心 · 宜開闊潔淨", r: 1, c: 1, color: "#FEF3C7" },
    { code: "E", label: "東方 (Pūrva)", deity: "Indra (帝釋天)", element: "Fire", tip: "主門 · 起居 · 晨曦窗", r: 1, c: 2, color: "#FFEDD5" },
    { code: "SW", label: "西南 (Nairṛtya)", deity: "Nirṛti (羅剎主)", element: "Earth", tip: "家主臥室 · 重物 · 錨定", r: 2, c: 0, color: "#FEE2E2" },
    { code: "S", label: "南方 (Dakṣiṇa)", deity: "Yama (閻摩)", element: "Earth", tip: "臥室 · 儲藏 · 重型壁", r: 2, c: 1, color: "#F5E6D3" },
    { code: "SE", label: "東南 (Āgneya)", deity: "Agni (火神)", element: "Fire", tip: "廚房 · 配電 · 暖氣", r: 2, c: 2, color: "#FEE2E2" },
  ];

  // 32 Outer Padas layout coordinates around the perimeter
  // 9 cells on each border (total 32 cells around perimeter)
  // Grid size: 9x9 cells. Cell size = 60px. Outer ring padding = 80px.
  const cellSize = 60;
  const gridOrigin = 80;

  // Outer padas mapping
  const outerPadaCoords: Array<{ r: number; c: number; index: number; name: string; side: string; nature: string }> = [
    // Top Row (North): Left to Right
    { r: 0, c: 0, index: 1, name: "Roga", side: "North", nature: "inauspicious" },
    { r: 0, c: 1, index: 2, name: "Nāga", side: "North", nature: "inauspicious" },
    { r: 0, c: 2, index: 3, name: "Mukhya", side: "North", nature: "auspicious" },
    { r: 0, c: 3, index: 4, name: "Bhallāṭa", side: "North", nature: "auspicious" },
    { r: 0, c: 4, index: 5, name: "Soma", side: "North", nature: "auspicious" },
    { r: 0, c: 5, index: 6, name: "Bhujaga", side: "North", nature: "inauspicious" },
    { r: 0, c: 6, index: 7, name: "Aditi", side: "North", nature: "auspicious" },
    { r: 0, c: 7, index: 8, name: "Diti", side: "North", nature: "neutral" },
    { r: 0, c: 8, index: 9, name: "Śikhi", side: "East", nature: "neutral" },

    // Right Column (East): Top to Bottom
    { r: 1, c: 8, index: 10, name: "Parjanya", side: "East", nature: "neutral" },
    { r: 2, c: 8, index: 11, name: "Jayanta", side: "East", nature: "auspicious" },
    { r: 3, c: 8, index: 12, name: "Indra", side: "East", nature: "auspicious" },
    { r: 4, c: 8, index: 13, name: "Sūrya", side: "East", nature: "auspicious" },
    { r: 5, c: 8, index: 14, name: "Satya", side: "East", nature: "inauspicious" },
    { r: 6, c: 8, index: 15, name: "Bhṛśa", side: "East", nature: "inauspicious" },
    { r: 7, c: 8, index: 16, name: "Antarikṣa", side: "East", nature: "inauspicious" },
    { r: 8, c: 8, index: 17, name: "Agni", side: "South", nature: "inauspicious" },

    // Bottom Row (South): Right to Left
    { r: 8, c: 7, index: 18, name: "Pūṣan", side: "South", nature: "inauspicious" },
    { r: 8, c: 6, index: 19, name: "Vitatha", side: "South", nature: "inauspicious" },
    { r: 8, c: 5, index: 20, name: "Gṛhakṣata", side: "South", nature: "auspicious" },
    { r: 8, c: 4, index: 21, name: "Yama", side: "South", nature: "inauspicious" },
    { r: 8, c: 3, index: 22, name: "Gandharva", side: "South", nature: "auspicious" },
    { r: 8, c: 2, index: 23, name: "Bhṛṅga", side: "South", nature: "neutral" },
    { r: 8, c: 1, index: 24, name: "Mṛga", side: "South", nature: "inauspicious" },
    { r: 8, c: 0, index: 25, name: "Pitṛ", side: "West", nature: "inauspicious" },

    // Left Column (West): Bottom to Top
    { r: 7, c: 0, index: 26, name: "Dauvārika", side: "West", nature: "inauspicious" },
    { r: 6, c: 0, index: 27, name: "Sugrīva", side: "West", nature: "auspicious" },
    { r: 5, c: 0, index: 28, name: "Puṣpadanta", side: "West", nature: "auspicious" },
    { r: 4, c: 0, index: 29, name: "Varuṇa", side: "West", nature: "auspicious" },
    { r: 3, c: 0, index: 30, name: "Asura", side: "West", nature: "inauspicious" },
    { r: 2, c: 0, index: 31, name: "Śoṣa", side: "West", nature: "inauspicious" },
    { r: 1, c: 0, index: 32, name: "Pāpayakṣmā", side: "West", nature: "inauspicious" },
  ];

  return (
    <div className={`flex flex-col items-center bg-white rounded-2xl border border-slate-200/80 shadow-sm p-4 sm:p-6 ${className}`}>
      {/* Title */}
      <div className="text-center mb-4">
        <h3 className="text-lg font-bold text-slate-800 flex items-center justify-center gap-2">
          <span>🕉️</span> Vastu Purusha Mandala (Paramasayika 9×9)
        </h3>
        <p className="text-xs text-slate-500 mt-0.5">
          9 Inner Energy Zones & 32 Outer Guardian Deity Padas (Mayamata Tradition)
        </p>
      </div>

      {/* SVG Canvas */}
      <div className="relative w-full max-w-[620px] aspect-square flex items-center justify-center">
        <svg
          viewBox="0 0 700 700"
          className="w-full h-full select-none"
          style={{ fontVariantNumeric: "tabular-nums" }}
        >
          {/* Compass labels around outer ring */}
          <text x="350" y="45" textAnchor="middle" className="text-sm font-bold fill-slate-700">⬆ North (北方 · 0°)</text>
          <text x="665" y="355" textAnchor="middle" className="text-sm font-bold fill-slate-700">East (東方 · 90°) ➡</text>
          <text x="350" y="675" textAnchor="middle" className="text-sm font-bold fill-slate-700">⬇ South (南方 · 180°)</text>
          <text x="35" y="355" textAnchor="middle" className="text-sm font-bold fill-slate-700">⬅ West (西方 · 270°)</text>

          {/* Outer Border Box */}
          <rect
            x={gridOrigin - 4}
            y={gridOrigin - 4}
            width={cellSize * 9 + 8}
            height={cellSize * 9 + 8}
            fill="#F8FAFC"
            stroke="#CBD5E1"
            strokeWidth="3"
            rx="12"
          />

          {/* 32 Outer Ring Cells */}
          {outerPadaCoords.map((pada) => {
            const x = gridOrigin + pada.c * cellSize;
            const y = gridOrigin + pada.r * cellSize;
            const isAuspicious = pada.nature === "auspicious";
            const isInauspicious = pada.nature === "inauspicious";
            const bgFill = isAuspicious ? "#DCFCE7" : isInauspicious ? "#FEE2E2" : "#F1F5F9";
            const borderStroke = isAuspicious ? "#86EFAC" : isInauspicious ? "#FCA5A5" : "#CBD5E1";

            return (
              <g
                key={`pada-${pada.index}`}
                className="cursor-pointer transition-transform duration-150 hover:opacity-90"
                onMouseEnter={() =>
                  setActiveCell({
                    title: `${pada.name} (Pada #${pada.index})`,
                    sub: `Perimeter Deity on ${pada.side} Face`,
                    element: "Outer Guardian Ring",
                    deity: pada.name,
                    tip: isAuspicious ? "Auspicious Gate Location (大吉入口)" : isInauspicious ? "Inauspicious Gate (禁開主門)" : "Neutral Location",
                    status: pada.nature,
                  })
                }
              >
                <rect
                  x={x + 1}
                  y={y + 1}
                  width={cellSize - 2}
                  height={cellSize - 2}
                  fill={bgFill}
                  stroke={borderStroke}
                  strokeWidth="1.5"
                  rx="4"
                />
                <text
                  x={x + cellSize / 2}
                  y={y + cellSize / 2 - 2}
                  textAnchor="middle"
                  className="text-[9px] font-bold fill-slate-800"
                >
                  {pada.name}
                </text>
                <text
                  x={x + cellSize / 2}
                  y={y + cellSize / 2 + 10}
                  textAnchor="middle"
                  className="text-[7.5px] fill-slate-500"
                >
                  #{pada.index}
                </text>
              </g>
            );
          })}

          {/* 9 Inner Grid Zones (spanning 7x7 inner space) */}
          {innerZones.map((z) => {
            // Coordinate mapping: r=0 (top inner: rows 1 to 3), r=1 (mid: rows 3 to 6), r=2 (bottom: rows 6 to 8)
            const rowSpans = [
              { start: 1, span: 2.33 },
              { start: 3.33, span: 2.34 },
              { start: 5.67, span: 2.33 },
            ];
            const colSpans = [
              { start: 1, span: 2.33 },
              { start: 3.33, span: 2.34 },
              { start: 5.67, span: 2.33 },
            ];

            const x = gridOrigin + colSpans[z.c].start * cellSize + 2;
            const y = gridOrigin + rowSpans[z.r].start * cellSize + 2;
            const w = colSpans[z.c].span * cellSize - 4;
            const h = rowSpans[z.r].span * cellSize - 4;

            const isHighlighted = highlightDirection === z.code;
            const isFavorable = favorableDirections.includes(z.code);

            return (
              <g
                key={`zone-${z.code}`}
                className="cursor-pointer transition-all duration-200"
                onMouseEnter={() =>
                  setActiveCell({
                    title: `${z.label}`,
                    sub: `Governor: ${z.deity}`,
                    element: z.element,
                    deity: z.deity,
                    tip: z.tip,
                    status: isHighlighted ? "Facing Orientation" : isFavorable ? "Astro-Vastu Favorable" : "Harmonious",
                  })
                }
              >
                <rect
                  x={x}
                  y={y}
                  width={w}
                  height={h}
                  fill={z.color}
                  stroke={isHighlighted ? "#F59E0B" : isFavorable ? "#10B981" : "#E2E8F0"}
                  strokeWidth={isHighlighted || isFavorable ? "3" : "1.5"}
                  rx="8"
                />
                {isHighlighted && (
                  <rect
                    x={x - 2}
                    y={y - 2}
                    width={w + 4}
                    height={h + 4}
                    fill="none"
                    stroke="#D97706"
                    strokeWidth="2"
                    strokeDasharray="4 2"
                    rx="10"
                  />
                )}
                {/* Zone Label */}
                <text
                  x={x + w / 2}
                  y={y + h / 2 - 16}
                  textAnchor="middle"
                  className="text-xs font-bold fill-slate-800"
                >
                  {z.label}
                </text>
                <text
                  x={x + w / 2}
                  y={y + h / 2 + 2}
                  textAnchor="middle"
                  className="text-[10px] font-medium fill-slate-600"
                >
                  {z.deity}
                </text>
                <text
                  x={x + w / 2}
                  y={y + h / 2 + 18}
                  textAnchor="middle"
                  className="text-[9px] fill-slate-500"
                >
                  {z.tip}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Dynamic Hover Detail Card */}
      <div className="w-full mt-4 p-3 bg-slate-50 border border-slate-200/80 rounded-xl min-h-[64px] flex items-center justify-between text-xs">
        {activeCell ? (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between w-full gap-2">
            <div>
              <span className="font-bold text-slate-800">{activeCell.title}</span>
              <span className="text-slate-500 ml-2">({activeCell.sub})</span>
              <p className="text-slate-600 mt-0.5">{activeCell.tip}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-100 text-blue-800">
                {activeCell.element}
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-100 text-amber-800">
                {activeCell.status}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-slate-400 italic text-center w-full">
            Hover over any inner room quadrant or outer perimeter pada to inspect classical deity attributes and traditional recommendations.
          </p>
        )}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center justify-center gap-4 mt-3 text-[11px] text-slate-600">
        <div className="flex items-center gap-1.5">
          <span className="w-3.5 h-3.5 rounded bg-emerald-100 border border-emerald-300" />
          <span>Auspicious Gate (大吉門位)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3.5 h-3.5 rounded bg-rose-100 border border-rose-300" />
          <span>Inauspicious Gate (禁忌門位)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3.5 h-3.5 rounded bg-amber-100 border-2 border-amber-500" />
          <span>Property Facing (所選朝向)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3.5 h-3.5 rounded bg-amber-50 border border-amber-300" />
          <span>Brahmasthan (中央梵天位)</span>
        </div>
      </div>
    </div>
  );
}
