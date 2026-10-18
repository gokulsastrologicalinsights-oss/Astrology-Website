"use client";

import React, { useState } from "react";
import { NabhashaResponse, NabhashaYogaDetail } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaName, getRasiName, GRAHAS } from "@/lib/translations";
import {
  Compass,
  Sparkles,
  Info,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Layers,
  ShieldCheck,
  Bookmark,
  Orbit,
} from "lucide-react";

interface NabhashaSectionProps {
  nabhasha?: NabhashaResponse | null;
  onCalculate?: () => void;
  isCalculating?: boolean;
}

export function NabhashaSection({
  nabhasha,
  onCalculate,
  isCalculating,
}: NabhashaSectionProps) {
  const { language, t } = useLanguage();
  const [showAllQualifying, setShowAllQualifying] = useState(false);

  if (!nabhasha) {
    return (
      <div className="p-8 rounded-xl border border-[#E2DCD5] bg-white text-center space-y-4 shadow-xs">
        <div className="w-12 h-12 mx-auto rounded-full bg-[#FAF2DE] text-[#8C6D23] flex items-center justify-center">
          <Sparkles className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h3 className="font-serif text-lg font-bold text-[#0F172A]">
            {t.nabhashaTitle}
          </h3>
          <p className="text-xs text-[#64748B] max-w-md mx-auto">
            {language === "ta"
              ? "நபச யோகங்கள் கணக்கீடு முடிவுகள் இன்னும் ஏற்றப்படவில்லை."
              : "Nabhasha Yoga calculations are not yet generated for this horoscope snapshot."}
          </p>
        </div>
        {onCalculate && (
          <button
            type="button"
            onClick={onCalculate}
            disabled={isCalculating}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-sm disabled:opacity-50 transition-all cursor-pointer"
          >
            {isCalculating ? (
              <>
                <Orbit className="w-4 h-4 animate-spin" />
                <span>{language === "ta" ? "கணக்கிடப்படுகிறது..." : "Calculating..."}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>{language === "ta" ? "நபச யோகங்களைக் கணக்கிடு" : "Calculate Nabhasha Yogas"}</span>
              </>
            )}
          </button>
        )}
      </div>
    );
  }

  const { distribution, primary_yoga, all_qualifying_yogas, classical_reference } = nabhasha;

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case "ashraya":
        return "bg-indigo-50 text-indigo-800 border-indigo-200";
      case "dala":
        return "bg-emerald-50 text-emerald-800 border-emerald-200";
      case "aakriti":
        return "bg-amber-50 text-amber-900 border-amber-300";
      case "sankhya":
        return "bg-purple-50 text-purple-800 border-purple-200";
      default:
        return "bg-slate-50 text-slate-800 border-slate-200";
    }
  };

  const getCategoryBadgeName = (category: string) => {
    if (language === "ta") {
      switch (category.toLowerCase()) {
        case "ashraya":
          return "ஆச்ரய யோகம் (அடிப்படைக் கிரக யோகம்)";
        case "dala":
          return "தல யோகம் (சுப/அசுப தள யோகம்)";
        case "aakriti":
          return "ஆக்ருதி யோகம் (வடிவ யோகம்)";
        case "sankhya":
          return "சங்க்யா யோகம் (எண்ணிக்கை யோகம்)";
        default:
          return category;
      }
    }
    return `${category} Classification`;
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <div className="p-4 sm:p-5 rounded-xl border border-[#D8BD80]/80 bg-[#FAF7F0] shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E8DEC8]">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[#B8860B]" />
            <h3 className="font-serif text-lg font-bold text-[#0F172A]">
              {t.nabhashaTitle}
            </h3>
          </div>
          <span className="text-[11px] font-mono text-[#784E0E] bg-[#FAF2DE] border border-[#D8BD80] px-2.5 py-0.5 rounded-full self-start sm:self-auto">
            {language === "ta" ? "32 யோக முறைகள்" : "32 Classical Formations"}
          </span>
        </div>
        <p className="text-xs text-[#64748B] mt-2.5 leading-relaxed">
          {t.nabhashaSubtitle}
        </p>
        <div className="mt-3 pt-2.5 border-t border-[#E8DEC8]/60 flex flex-wrap items-center justify-between text-[11px] text-[#64748B] gap-2">
          <span className="flex items-center gap-1.5 font-medium text-[#784E0E]">
            <Bookmark className="w-3.5 h-3.5 text-[#B8860B]" />
            <span>{classical_reference}</span>
          </span>
          <span className="text-[10px] bg-white px-2 py-0.5 rounded border border-[#E2DCD5] text-[#475569]">
            {t.nabhashaPrecedenceNotice}
          </span>
        </div>
      </div>

      {/* 2. Primary Operative Yoga Hero Card */}
      {primary_yoga ? (
        <div className="p-5 sm:p-6 rounded-xl border-2 border-[#D8BD80] bg-white shadow-sm relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-[#B8860B] text-white text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-bl-lg shadow-2xs">
            {t.nabhashaPrimaryYoga}
          </div>

          <div className="flex flex-wrap items-center gap-2.5 mb-3">
            <h4 className="font-serif text-2xl font-bold text-[#0F172A] tracking-tight">
              {primary_yoga.name} Yoga
            </h4>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${getCategoryColor(
                primary_yoga.category
              )}`}
            >
              {getCategoryBadgeName(primary_yoga.category)}
            </span>
          </div>

          <div className="space-y-4">
            {/* Formation Rule */}
            <div className="p-3.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] space-y-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#8C6D23] flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-[#B8860B]" />
                <span>{t.nabhashaFormationRule}</span>
              </span>
              <p className="text-xs font-semibold text-[#0F172A] leading-relaxed">
                {primary_yoga.formation_rule}
              </p>
            </div>

            {/* Classical Interpretation */}
            <div className="space-y-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#64748B]">
                {t.nabhashaDescription}
              </span>
              <p className="text-xs text-[#334155] leading-relaxed italic bg-blue-50/40 p-3 rounded-lg border border-blue-100">
                &ldquo;{primary_yoga.description}&rdquo;
              </p>
            </div>

            {/* Qualifying details: Houses, Signs, Planets */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              {/* Participating Planets */}
              <div className="p-3 rounded-lg border border-[#E2DCD5] bg-white">
                <span className="text-[10px] font-bold uppercase text-[#64748B] block mb-1.5">
                  {t.nabhashaPlanetsInvolved} ({primary_yoga.planets_involved.length})
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {primary_yoga.planets_involved.map((planet) => {
                    const graha = GRAHAS[planet];
                    const label = getGrahaName(planet, language);
                    return (
                      <span
                        key={planet}
                        className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-[#FAF7F0] border border-[#E2DCD5] text-[#0F172A]"
                        style={{ borderLeftColor: graha?.color || "#B8860B", borderLeftWidth: "3px" }}
                      >
                        {label}
                      </span>
                    );
                  })}
                </div>
              </div>

              {/* Qualifying Houses */}
              <div className="p-3 rounded-lg border border-[#E2DCD5] bg-white">
                <span className="text-[10px] font-bold uppercase text-[#64748B] block mb-1.5">
                  {t.nabhashaQualifyingHouses}
                </span>
                <div className="flex flex-wrap gap-1">
                  {primary_yoga.qualifying_houses && primary_yoga.qualifying_houses.length > 0 ? (
                    primary_yoga.qualifying_houses.map((h) => (
                      <span
                        key={h}
                        className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-mono text-[11px] font-bold"
                      >
                        Bhava {h}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-[#64748B]">—</span>
                  )}
                </div>
              </div>

              {/* Qualifying Signs */}
              <div className="p-3 rounded-lg border border-[#E2DCD5] bg-white">
                <span className="text-[10px] font-bold uppercase text-[#64748B] block mb-1.5">
                  {t.nabhashaQualifyingSigns}
                </span>
                <div className="flex flex-wrap gap-1">
                  {primary_yoga.qualifying_signs && primary_yoga.qualifying_signs.length > 0 ? (
                    primary_yoga.qualifying_signs.map((s) => (
                      <span
                        key={s}
                        className="px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200 text-[11px] font-medium"
                      >
                        {getRasiName(s, language)}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-[#64748B]">—</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 text-center text-xs text-[#64748B]">
          {language === "ta"
            ? "நபச யோகம் கண்டறியப்படவில்லை."
            : "No qualifying Nabhasha Yoga detected for this configuration."}
        </div>
      )}

      {/* 3. Spatial Distribution & Bhava Placement Grid */}
      <div className="rounded-xl border border-[#E2DCD5] bg-white p-5 shadow-2xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#E2DCD5]">
          <h4 className="font-serif text-base font-bold text-[#0F172A] flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#B8860B]" />
            <span>{t.nabhashaDistribution}</span>
          </h4>
          <span className="text-[11px] text-[#64748B]">
            {language === "ta" ? "7 பாரம்பரிய கிரகங்கள் மட்டுமே (சூரியன் முதல் சனி வரை)" : "7 Classical Grahas Exclusively (Sun to Saturn)"}
          </span>
        </div>

        {/* 4 Summary Stat Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] text-center">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
              {t.nabhashaDistinctSigns}
            </span>
            <span className="font-serif text-2xl font-bold text-[#0F172A] mt-1 block">
              {distribution.distinct_signs_count} / 12
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] text-center">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
              {t.nabhashaDistinctHouses}
            </span>
            <span className="font-serif text-2xl font-bold text-[#0F172A] mt-1 block">
              {distribution.distinct_houses_count} / 12
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] text-center">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
              {t.nabhashaKendraPlanets}
            </span>
            <span className="font-serif text-2xl font-bold text-[#784E0E] mt-1 block">
              {distribution.kendra_planets.length}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] text-center">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
              {t.nabhashaTrikonaPlanets}
            </span>
            <span className="font-serif text-2xl font-bold text-[#0F172A] mt-1 block">
              {distribution.trikona_planets.length}
            </span>
          </div>
        </div>

        {/* House Class Details */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2 text-xs">
          {/* Kendras */}
          <div className="p-3 rounded-lg border border-slate-200 bg-white space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#0F172A]">Kendras (1, 4, 7, 10)</span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-900">
                {distribution.kendra_planets.length}
              </span>
            </div>
            <div className="text-[11px] text-[#475569]">
              {distribution.kendra_planets.length > 0
                ? distribution.kendra_planets.map((p) => getGrahaName(p, language)).join(", ")
                : language === "ta" ? "கிரகங்கள் இல்லை" : "None"}
            </div>
          </div>

          {/* Panapharas */}
          <div className="p-3 rounded-lg border border-slate-200 bg-white space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#0F172A]">Panapharas (2, 5, 8, 11)</span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-900">
                {distribution.panaphara_planets.length}
              </span>
            </div>
            <div className="text-[11px] text-[#475569]">
              {distribution.panaphara_planets.length > 0
                ? distribution.panaphara_planets.map((p) => getGrahaName(p, language)).join(", ")
                : language === "ta" ? "கிரகங்கள் இல்லை" : "None"}
            </div>
          </div>

          {/* Apoklimas */}
          <div className="p-3 rounded-lg border border-slate-200 bg-white space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#0F172A]">Apoklimas (3, 6, 9, 12)</span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-purple-100 text-purple-900">
                {distribution.apoklima_planets.length}
              </span>
            </div>
            <div className="text-[11px] text-[#475569]">
              {distribution.apoklima_planets.length > 0
                ? distribution.apoklima_planets.map((p) => getGrahaName(p, language)).join(", ")
                : language === "ta" ? "கிரகங்கள் இல்லை" : "None"}
            </div>
          </div>

          {/* Trikonas */}
          <div className="p-3 rounded-lg border border-slate-200 bg-white space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#0F172A]">Trikonas (1, 5, 9)</span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-900">
                {distribution.trikona_planets.length}
              </span>
            </div>
            <div className="text-[11px] text-[#475569]">
              {distribution.trikona_planets.length > 0
                ? distribution.trikona_planets.map((p) => getGrahaName(p, language)).join(", ")
                : language === "ta" ? "கிரகங்கள் இல்லை" : "None"}
            </div>
          </div>
        </div>
      </div>

      {/* 4. All Qualifying Formations Accordion (if multiple yogas qualify) */}
      {all_qualifying_yogas && all_qualifying_yogas.length > 1 && (
        <div className="rounded-xl border border-[#E2DCD5] bg-white overflow-hidden shadow-2xs">
          <button
            type="button"
            onClick={() => setShowAllQualifying(!showAllQualifying)}
            className="w-full px-5 py-3.5 bg-[#FAF7F0] flex items-center justify-between text-left hover:bg-[#FAF4E6] transition-colors cursor-pointer border-b border-[#E2DCD5]"
          >
            <div className="flex items-center gap-2">
              <span className="font-serif text-sm font-bold text-[#0F172A]">
                {t.nabhashaAllQualifying} ({all_qualifying_yogas.length})
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                {language === "ta" ? "முன்னுரிமை வரிசை" : "Precedence Resolved"}
              </span>
            </div>
            {showAllQualifying ? (
              <ChevronUp className="w-4 h-4 text-[#64748B]" />
            ) : (
              <ChevronDown className="w-4 h-4 text-[#64748B]" />
            )}
          </button>

          {showAllQualifying && (
            <div className="divide-y divide-[#F1EBE4]">
              {all_qualifying_yogas.map((yoga, idx) => (
                <div key={yoga.name + idx} className="p-4 hover:bg-[#FAF8F5] transition-colors space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-serif font-bold text-sm text-[#0F172A]">
                        {yoga.name}
                      </span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${getCategoryColor(
                          yoga.category
                        )}`}
                      >
                        {yoga.category}
                      </span>
                    </div>
                    {yoga.is_primary ? (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>{language === "ta" ? "முதன்மை யோகம்" : "Operative (Primary)"}</span>
                      </span>
                    ) : (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                        {language === "ta" ? "துணை யோகம்" : "Secondary (Subsumed)"}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[#334155]">{yoga.formation_rule}</p>
                  <p className="text-[11px] text-[#64748B] italic">{yoga.description}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
