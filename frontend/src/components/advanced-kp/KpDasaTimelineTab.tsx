"use client";

import React, { useState } from "react";
import { KpDasaBalance, KpDasaPeriod } from "@/lib/types";
import { getLordName } from "@/lib/translations";
import { Calendar, ChevronDown, ChevronRight, Clock, Layers } from "lucide-react";

interface KpDasaTimelineTabProps {
  dasaHierarchy?: KpDasaBalance;
  language: "en" | "ta";
}

function formatDate(isoStr?: string): string {
  if (!isoStr) return "—";
  return isoStr.split("T")[0];
}

export function KpDasaTimelineTab({ dasaHierarchy, language }: KpDasaTimelineTabProps) {
  const [expandedMds, setExpandedMds] = useState<Record<string, boolean>>({});

  if (!dasaHierarchy) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-[#E2DCD5] text-[#64748B]">
        {language === "ta" ? "தசா-புக்தி தகவல்கள் கிடைக்கவில்லை." : "Dasa-Bhukti timeline not available."}
      </div>
    );
  }

  const toggleMd = (lord: string) => {
    setExpandedMds((prev) => ({
      ...prev,
      [lord]: !prev[lord],
    }));
  };

  return (
    <div className="space-y-6">
      {/* 5-Level Active Hierarchy Card */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#B8862B]" />
            <h3 className="font-serif text-base font-bold text-[#102A4C]">
              {language === "ta"
                ? "5-அடுக்கு விம்சோத்தரி தசா இருப்பு (Five-Level Dasa Hierarchy)"
                : "Five-Level Vimshottari Dasa Hierarchy"}
            </h3>
          </div>
          <span className="text-xs text-[#64748B] font-mono">
            Epoch: {formatDate(dasaHierarchy.birth_epoch)}
          </span>
        </div>

        {/* 5-Tier Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
          {dasaHierarchy.current_periods.map((p) => {
            const levelColors = [
              "bg-[#FAF2DE] border-[#D8BD80] text-[#8C6D23]",
              "bg-[#EBF2FE] border-[#BFDBFE] text-[#2563EB]",
              "bg-purple-50 border-purple-200 text-purple-700",
              "bg-emerald-50 border-emerald-200 text-emerald-700",
              "bg-rose-50 border-rose-200 text-rose-700",
            ];
            const colorClass = levelColors[(p.level - 1) % levelColors.length];

            return (
              <div
                key={p.level}
                className={`p-3.5 rounded-xl border ${colorClass} space-y-1.5 transition-transform hover:-translate-y-0.5`}
              >
                <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider opacity-80">
                  <span>Level {p.level}</span>
                  <span>{p.vedic_name}</span>
                </div>
                <div className="text-base font-bold font-serif">
                  {getLordName(p.lord, language)}
                </div>
                <div className="text-[11px] opacity-90">{p.level_name}</div>
                <div className="pt-1 text-[10px] opacity-80 space-y-0.5 border-t border-current/20">
                  <div>From: {formatDate(p.start_date)}</div>
                  <div>To: {formatDate(p.end_date)}</div>
                  <div>Duration: {p.duration_days.toFixed(1)} d</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Balance Description */}
        <div className="p-3 rounded-xl bg-[#FAF6EC] border border-[#D8BD80] text-xs text-[#102A4C] flex flex-wrap items-center justify-between gap-2">
          <div>
            <strong>{language === "ta" ? "பிறப்பு தசா இருப்பு:" : "Birth Dasa Balance:"}</strong>{" "}
            {getLordName(dasaHierarchy.mahadasha_lord, language)} Mahadasha —{" "}
            {dasaHierarchy.mahadasha_balance_years.toFixed(2)} years ({dasaHierarchy.mahadasha_balance_days.toFixed(1)} days)
          </div>
          <div className="text-[11px] text-[#8C6D23]">
            120-Year Vimshottari Cycle (Pure Proportional Math)
          </div>
        </div>
      </div>

      {/* Mahadasha Complete 120-Year Timeline */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-[#3478F6]" />
            <h3 className="font-serif text-base font-bold text-[#102A4C]">
              {language === "ta" ? "முழு மகா தசா காலவரிசை (120 ஆண்டுகள்)" : "Complete Mahadasha Timeline (120 Years)"}
            </h3>
          </div>
          <span className="text-xs text-[#64748B]">9 Planetary Cycles</span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-[#E2DCD5]">
          <table className="min-w-full divide-y divide-[#E2DCD5] text-xs sm:text-sm">
            <thead className="bg-[#F8FAFC] text-[#475569] font-semibold">
              <tr>
                <th className="px-3 py-2.5 text-left w-12">#</th>
                <th className="px-3 py-2.5 text-left">
                  {language === "ta" ? "மகா தசா அதிபதி" : "Mahadasha Lord"}
                </th>
                <th className="px-3 py-2.5 text-left">
                  {language === "ta" ? "துவக்க தேதி" : "Start Date"}
                </th>
                <th className="px-3 py-2.5 text-left">
                  {language === "ta" ? "முடிவு தேதி" : "End Date"}
                </th>
                <th className="px-3 py-2.5 text-right">
                  {language === "ta" ? "நாட்கள்" : "Days"}
                </th>
                <th className="px-3 py-2.5 text-right">
                  {language === "ta" ? "ஆண்டுகள்" : "Years"}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9] text-[#1E293B]">
              {dasaHierarchy.mahadashas.map((md, idx) => {
                const todayIso = new Date().toISOString().split("T")[0];
                const sDate = (md.start_date || "").split("T")[0];
                const eDate = (md.end_date || "").split("T")[0];
                const isCurrent = sDate && eDate && todayIso >= sDate && todayIso < eDate;

                return (
                  <tr
                    key={idx}
                    className={`transition-colors ${
                      isCurrent
                        ? "bg-[#FAF2DE] font-bold text-[#102A4C] border-l-4 border-l-[#B8862B]"
                        : "hover:bg-[#FAF6EC]/60"
                    }`}
                  >
                    <td className="px-3 py-2 text-xs font-mono text-[#64748B]">{idx + 1}</td>
                    <td className="px-3 py-2 font-bold text-[#102A4C] whitespace-nowrap">
                      <span>{getLordName(md.lord, language)}</span>
                      {isCurrent && (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-400 text-slate-900 tracking-wide ml-2 shadow-2xs whitespace-nowrap">
                          <span className="w-1.5 h-1.5 rounded-full bg-slate-900 animate-pulse" />
                          {language === "ta" ? "நடப்பு தசா" : "Active Dasa"}
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap font-mono text-xs">
                      {formatDate(md.start_date)}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap font-mono text-xs">
                      {formatDate(md.end_date)}
                    </td>
                    <td className="px-3 py-2 text-right font-mono text-xs text-[#475569]">
                      {md.duration_days.toFixed(1)}
                    </td>
                    <td className="px-3 py-2 text-right font-bold text-[#102A4C] font-mono text-xs">
                      {(md.duration_days / 365.25).toFixed(2)} y
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
