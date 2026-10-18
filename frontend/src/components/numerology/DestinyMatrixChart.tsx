"use client";

import React, { useState } from "react";
import { DestinyMatrixResponse, MatrixNodeDetail } from "@/lib/types";
import { Sparkles, Info, X, Shield, Heart, DollarSign } from "lucide-react";

interface Props {
  matrix: DestinyMatrixResponse;
}

export function DestinyMatrixChart({ matrix }: Props) {
  const [selectedNode, setSelectedNode] = useState<MatrixNodeDetail | null>(
    matrix.comfort_zone
  );

  // Octagram node definitions on a 500x500 canvas
  const nodes = [
    {
      id: "month",
      cx: 250,
      cy: 65,
      data: matrix.month_arcana,
      color: "#8B5CF6", // Violet (Spiritual)
      labelPos: { x: 250, y: 38 },
      tag: "Month / Spiritual",
    },
    {
      id: "day",
      cx: 65,
      cy: 250,
      data: matrix.day_arcana,
      color: "#3B82F6", // Blue (Personal / Identity)
      labelPos: { x: 40, y: 285 },
      tag: "Day / Youth",
    },
    {
      id: "year",
      cx: 435,
      cy: 250,
      data: matrix.year_arcana,
      color: "#EAB308", // Gold (Material / Wealth)
      labelPos: { x: 460, y: 285 },
      tag: "Year / Material",
    },
    {
      id: "karmic_tail",
      cx: 250,
      cy: 435,
      data: matrix.karmic_tail_base,
      color: "#EF4444", // Red (Karmic Tail / Past Life)
      labelPos: { x: 250, y: 470 },
      tag: "Karmic Tail",
    },
    {
      id: "father_spirit",
      cx: 120,
      cy: 120,
      data: matrix.father_spirit,
      color: "#06B6D4", // Cyan
      labelPos: { x: 80, y: 105 },
      tag: "Father Spirit",
    },
    {
      id: "mother_spirit",
      cx: 380,
      cy: 120,
      data: matrix.mother_spirit,
      color: "#EC4899", // Pink
      labelPos: { x: 420, y: 105 },
      tag: "Mother Spirit",
    },
    {
      id: "father_matter",
      cx: 120,
      cy: 380,
      data: matrix.father_matter,
      color: "#10B981", // Emerald
      labelPos: { x: 80, y: 410 },
      tag: "Father Matter",
    },
    {
      id: "mother_matter",
      cx: 380,
      cy: 380,
      data: matrix.mother_matter,
      color: "#F97316", // Orange
      labelPos: { x: 420, y: 410 },
      tag: "Mother Matter",
    },
    {
      id: "comfort",
      cx: 250,
      cy: 250,
      data: matrix.comfort_zone,
      color: "#B8860B", // Primary Gold
      labelPos: { x: 250, y: 215 },
      tag: "Comfort Zone",
    },
  ];

  // Age timeline labels around perimeter
  const ageLabels = [
    { text: "0 / 80y", x: 25, y: 255 },
    { text: "10y", x: 90, y: 95 },
    { text: "20y", x: 250, y: 20 },
    { text: "30y", x: 410, y: 95 },
    { text: "40y", x: 475, y: 255 },
    { text: "50y", x: 410, y: 415 },
    { text: "60y", x: 250, y: 490 },
    { text: "70y", x: 90, y: 415 },
  ];

  return (
    <div className="flex flex-col lg:flex-row gap-6 items-start">
      {/* SVG Octagram Chart Visualization */}
      <div className="w-full lg:w-3/5 rounded-2xl border border-[#E2DCD5] bg-[#FAF8F5] p-4 sm:p-6 shadow-xs flex flex-col items-center">
        <div className="w-full flex items-center justify-between pb-3 border-b border-[#E2DCD5]">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#B8860B]" />
            <h3 className="font-serif text-sm font-bold text-[#0F172A]">
              Interactive 22-Arcana Octagram Chart
            </h3>
          </div>
          <span className="text-[11px] text-[#64748B] font-medium">
            Click any node to inspect energy
          </span>
        </div>

        <div className="relative w-full max-w-[480px] aspect-square my-2">
          <svg
            viewBox="0 0 500 500"
            className="w-full h-full select-none"
            aria-label="Destiny Matrix Chart"
          >
            <defs>
              {/* Radial gradient for chart background */}
              <radialGradient id="matrixGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#FAF2DE" stopOpacity="0.8" />
                <stop offset="60%" stopColor="#FAF8F5" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#FAF8F5" stopOpacity="0" />
              </radialGradient>

              {/* Node glow filter */}
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Background circular glow */}
            <circle cx="250" cy="250" r="220" fill="url(#matrixGlow)" />

            {/* Outer Age Timeline Ring */}
            <circle
              cx="250"
              cy="250"
              r="225"
              fill="none"
              stroke="#D8BD80"
              strokeWidth="1.5"
              strokeDasharray="4 4"
              opacity="0.7"
            />

            {/* Age Timeline Milestones */}
            {ageLabels.map((item, idx) => (
              <text
                key={idx}
                x={item.x}
                y={item.y}
                textAnchor="middle"
                fontSize="11"
                fontWeight="700"
                fill="#8C6D23"
              >
                {item.text}
              </text>
            ))}

            {/* 1. Orthogonal Personal Square (Straight) */}
            <polygon
              points="250,65 435,250 250,435 65,250"
              fill="rgba(255, 255, 255, 0.7)"
              stroke="#0F172A"
              strokeWidth="2"
              strokeLinejoin="round"
            />

            {/* 2. Diagonal Ancestral Square (45° Rotated Diamond) */}
            <polygon
              points="120,120 380,120 380,380 120,380"
              fill="rgba(250, 242, 222, 0.4)"
              stroke="#B8860B"
              strokeWidth="1.8"
              strokeLinejoin="round"
            />

            {/* 3. Axial Energy Lines */}
            {/* Sky Line (Vertical) */}
            <line
              x1="250"
              y1="65"
              x2="250"
              y2="435"
              stroke="#8B5CF6"
              strokeWidth="1.5"
              strokeDasharray="3 3"
              opacity="0.8"
            />
            {/* Earth Line (Horizontal) */}
            <line
              x1="65"
              y1="250"
              x2="435"
              y2="250"
              stroke="#3B82F6"
              strokeWidth="1.5"
              strokeDasharray="3 3"
              opacity="0.8"
            />
            {/* Father Diagonal */}
            <line
              x1="120"
              y1="120"
              x2="380"
              y2="380"
              stroke="#06B6D4"
              strokeWidth="1.2"
              strokeDasharray="3 3"
              opacity="0.7"
            />
            {/* Mother Diagonal */}
            <line
              x1="380"
              y1="120"
              x2="120"
              y2="380"
              stroke="#EC4899"
              strokeWidth="1.2"
              strokeDasharray="3 3"
              opacity="0.7"
            />

            {/* Karmic Tail Triad connecting line */}
            <line
              x1="250"
              y1="250"
              x2="250"
              y2="435"
              stroke="#EF4444"
              strokeWidth="2.5"
              opacity="0.85"
            />

            {/* Love & Money Channel Lines in Bottom-Right Quadrant */}
            <line
              x1="250"
              y1="250"
              x2="380"
              y2="380"
              stroke="#B8860B"
              strokeWidth="2"
              opacity="0.7"
            />

            {/* Matrix Nodes (Clickable Badges) */}
            {nodes.map((node) => {
              const isSelected = selectedNode?.node_id === node.data.node_id;
              const isCenter = node.id === "comfort";
              const radius = isCenter ? 26 : 21;

              return (
                <g
                  key={node.id}
                  onClick={() => setSelectedNode(node.data)}
                  className="cursor-pointer transition-transform hover:scale-110"
                  style={{ transformOrigin: `${node.cx}px ${node.cy}px` }}
                >
                  {/* Outer halo if selected */}
                  {isSelected && (
                    <circle
                      cx={node.cx}
                      cy={node.cy}
                      r={radius + 6}
                      fill="none"
                      stroke={node.color}
                      strokeWidth="2.5"
                      strokeDasharray="3 2"
                      className="animate-spin"
                      style={{ transformOrigin: `${node.cx}px ${node.cy}px` }}
                    />
                  )}

                  {/* Node Circle */}
                  <circle
                    cx={node.cx}
                    cy={node.cy}
                    r={radius}
                    fill={node.color}
                    stroke="#FFFFFF"
                    strokeWidth="2.5"
                    filter="url(#glow)"
                  />

                  {/* Arcana Number Value */}
                  <text
                    x={node.cx}
                    y={node.cy + 5}
                    textAnchor="middle"
                    fill="#FFFFFF"
                    fontSize={isCenter ? "14" : "12"}
                    fontWeight="800"
                    fontFamily="sans-serif"
                  >
                    {node.data.arcana_number}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Legend */}
        <div className="w-full mt-2 pt-3 border-t border-[#E2DCD5] flex flex-wrap items-center justify-center gap-3 text-[10px] text-[#475569]">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#3B82F6]" />
            Personal (Day)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#8B5CF6]" />
            Spiritual (Month)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#EAB308]" />
            Material (Year)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" />
            Karmic Tail (Base)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#B8860B]" />
            Comfort Zone (Center)
          </span>
        </div>
      </div>

      {/* Node Inspector Drawer */}
      <div className="w-full lg:w-2/5 rounded-2xl border border-[#E2DCD5] bg-white p-5 sm:p-6 shadow-xs">
        {selectedNode ? (
          <div>
            <div className="flex items-start justify-between pb-3 border-b border-[#E2DCD5]">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#B8860B] bg-[#FAF2DE] px-2 py-0.5 rounded-full">
                  {selectedNode.label}
                </span>
                <h4 className="mt-2 font-serif text-lg font-bold text-[#0F172A]">
                  Arcana {selectedNode.arcana_number}: {selectedNode.arcana_name}
                </h4>
              </div>
              <div className="w-10 h-10 rounded-full bg-[#0F172A] text-white flex items-center justify-center font-bold text-sm shadow-xs">
                {selectedNode.arcana_number}
              </div>
            </div>

            <div className="mt-4 space-y-4 text-xs leading-relaxed text-[#334155]">
              <div>
                <div className="font-bold text-[#0F172A] mb-1 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-[#B8860B]" />
                  <span>Core Meaning & Energy:</span>
                </div>
                <p className="bg-[#FAF8F5] p-2.5 rounded-xl border border-[#E2DCD5]">
                  {selectedNode.meaning}
                </p>
              </div>

              <div>
                <div className="font-bold text-emerald-700 mb-1 flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5" />
                  <span>Positive Manifestation:</span>
                </div>
                <p className="bg-emerald-50/60 p-2.5 rounded-xl border border-emerald-200/60 text-emerald-900">
                  {selectedNode.positive_traits}
                </p>
              </div>

              <div>
                <div className="font-bold text-rose-700 mb-1 flex items-center gap-1.5">
                  <X className="w-3.5 h-3.5" />
                  <span>Karmic Shadow / Traps:</span>
                </div>
                <p className="bg-rose-50/60 p-2.5 rounded-xl border border-rose-200/60 text-rose-900">
                  {selectedNode.negative_traps}
                </p>
              </div>

              <div>
                <div className="font-bold text-[#B8860B] mb-1 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Soul Recommendation:</span>
                </div>
                <p className="bg-[#FAF2DE]/50 p-2.5 rounded-xl border border-[#D8BD80]/50 text-[#784E0E]">
                  {selectedNode.recommendations}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="py-12 text-center text-[#64748B] text-xs">
            <Info className="w-6 h-6 mx-auto mb-2 text-[#CBD5E1]" />
            <p>Click any node on the octagram chart to inspect its 22-Arcana energy.</p>
          </div>
        )}
      </div>
    </div>
  );
}
