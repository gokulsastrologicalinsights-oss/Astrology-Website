"use client";

import React, { useState, useMemo } from "react";
import { UnifiedDoshaResponse, DoshaEvaluationItem } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaName, GRAHAS } from "@/lib/translations";
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Info,
  ChevronRight,
  X,
  Search,
  BookOpen,
  Sparkles,
  Orbit,
  HelpCircle,
  Compass,
  Moon,
  Layers,
  HeartHandshake,
} from "lucide-react";

interface DoshaSectionProps {
  doshas?: UnifiedDoshaResponse | null;
  onCalculate?: () => void;
  isCalculating?: boolean;
}

export function DoshaSection({
  doshas,
  onCalculate,
  isCalculating,
}: DoshaSectionProps) {
  const { language, t } = useLanguage();

  const [selectedDosha, setSelectedDosha] = useState<DoshaEvaluationItem | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<
    "all" | "present" | "mitigated" | "absent" | "indeterminate"
  >("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const allDoshas = doshas?.all_doshas || [];
  const summary = doshas?.summary;

  const totalEvaluated = summary?.total_rules_evaluated ?? (summary as any)?.total_evaluated ?? allDoshas.length;
  const presentCount = summary?.total_present ?? (summary as any)?.present_count ?? allDoshas.filter((d) => d.status === "present").length;
  const mitigatedCount = summary?.total_mitigated ?? (summary as any)?.mitigated_count ?? allDoshas.filter((d) => d.status === "mitigated").length;
  const absentCount = summary?.total_absent ?? (summary as any)?.absent_count ?? allDoshas.filter((d) => d.status === "absent").length;
  const indeterminateCount = summary?.total_indeterminate ?? (summary as any)?.indeterminate_count ?? allDoshas.filter((d) => d.status === "indeterminate").length;

  // Filtered doshas
  const filteredDoshas = useMemo(() => {
    return allDoshas.filter((d) => {
      // Category filter
      if (categoryFilter !== "all" && d.category !== categoryFilter) {
        return false;
      }

      // Status filter
      if (statusFilter !== "all" && d.status !== statusFilter) {
        return false;
      }

      // Search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        const matchNameEn = d.name_en.toLowerCase().includes(query);
        const matchNameTa = d.name_ta && d.name_ta.toLowerCase().includes(query);
        const matchCategory = d.category.toLowerCase().includes(query);
        const matchPlanet = d.involved_planets && d.involved_planets.some((p) => p.toLowerCase().includes(query));
        const matchId = d.dosha_id.toLowerCase().includes(query);
        if (!matchNameEn && !matchNameTa && !matchCategory && !matchPlanet && !matchId) {
          return false;
        }
      }

      return true;
    });
  }, [allDoshas, categoryFilter, statusFilter, searchQuery]);

  // Counts by category
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {
      "Planetary Conjunction & Axis": 0,
      "Moon & Nakshatra": 0,
      "Lagna & House Placements": 0,
      "Marriage Compatibility": 0,
      "Transit": 0,
    };
    allDoshas.forEach((d) => {
      if (counts[d.category] !== undefined) {
        counts[d.category]++;
      }
    });
    return counts;
  }, [allDoshas]);

  if (!doshas || (!doshas.all_doshas && !doshas.summary)) {
    return (
      <div className="p-8 rounded-xl border border-[#E2DCD5] bg-white text-center space-y-4 shadow-xs">
        <div className="w-12 h-12 mx-auto rounded-full bg-amber-50 text-[#8C6D23] flex items-center justify-center">
          <ShieldAlert className="w-6 h-6 text-[#B8860B]" />
        </div>
        <div className="space-y-1">
          <h3 className="font-serif text-lg font-bold text-[#0F172A]">
            {t.doshasTitle}
          </h3>
          <p className="text-xs text-[#64748B] max-w-md mx-auto">
            {t.doshasMissingNotice}
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
                <span>{t.doshasCalculating}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>{t.doshasCalculateButton}</span>
              </>
            )}
          </button>
        )}
      </div>
    );
  }

  // Category mapping
  const categoryLabels: Record<string, { en: string; ta: string }> = {
    "Planetary Conjunction & Axis": {
      en: "Planetary Conjunction & Axis",
      ta: "கிரக சேர்க்கை & அச்சு",
    },
    "Moon & Nakshatra": {
      en: "Moon & Nakshatra",
      ta: "சந்திரன் & நட்சத்திரம்",
    },
    "Lagna & House Placements": {
      en: "Lagna & House Placements",
      ta: "லக்னம் & பாவகம்",
    },
    "Marriage Compatibility": {
      en: "Marriage Compatibility",
      ta: "திருமணப் பொருத்தம்",
    },
    "Transit": {
      en: "Transit (Gochara)",
      ta: "கோச்சாரம்",
    },
  };

  const getCategoryName = (cat: string) => {
    const meta = categoryLabels[cat];
    if (!meta) return cat;
    return language === "ta" ? meta.ta : meta.en;
  };

  const getCategoryBadgeClass = (category: string) => {
    switch (category) {
      case "Planetary Conjunction & Axis":
        return "bg-rose-50 text-rose-900 border-rose-200";
      case "Moon & Nakshatra":
        return "bg-sky-50 text-sky-900 border-sky-200";
      case "Lagna & House Placements":
        return "bg-amber-50 text-amber-900 border-amber-200";
      case "Marriage Compatibility":
        return "bg-purple-50 text-purple-900 border-purple-200";
      case "Transit":
        return "bg-indigo-50 text-indigo-900 border-indigo-200";
      default:
        return "bg-slate-50 text-slate-800 border-slate-200";
    }
  };

  const getStatusBadge = (status: DoshaEvaluationItem["status"]) => {
    switch (status) {
      case "present":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-800 border border-rose-300">
            <AlertTriangle className="w-3 h-3 text-rose-600 shrink-0" />
            <span>{language === "ta" ? "உள்ளது" : "Present"}</span>
          </span>
        );
      case "mitigated":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-900 border border-amber-300">
            <ShieldCheck className="w-3 h-3 text-amber-600 shrink-0" />
            <span>{language === "ta" ? "நிவர்த்தி (பங்கம்)" : "Mitigated"}</span>
          </span>
        );
      case "absent":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
            <span>{language === "ta" ? "தோஷமில்லை" : "Absent"}</span>
          </span>
        );
      case "indeterminate":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-purple-50 text-purple-800 border border-purple-200">
            <HelpCircle className="w-3 h-3 text-purple-600 shrink-0" />
            <span>{language === "ta" ? "தரவு தேவை" : "Indeterminate"}</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700 border border-slate-200">
            <Info className="w-3 h-3 text-slate-500 shrink-0" />
            <span>{status}</span>
          </span>
        );
    }
  };

  const formatDegree = (deg: number) => {
    const norm = deg % 30;
    const d = Math.floor(norm);
    const m = Math.floor((norm - d) * 60);
    return `${d}°${m.toString().padStart(2, "0")}'`;
  };



  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <div className="p-4 sm:p-5 rounded-xl border border-[#D8BD80]/80 bg-[#FAF7F0] shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E8DEC8]">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-[#B8860B]" />
            <h3 className="font-serif text-lg font-bold text-[#0F172A]">
              {t.doshasTitle}
            </h3>
          </div>
          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-[11px] font-mono text-[#784E0E] bg-[#FAF2DE] border border-[#D8BD80] px-2.5 py-0.5 rounded-full">
              {language === "ta"
                ? `${presentCount} உள்ளவை • ${mitigatedCount} நிவர்த்தி`
                : `${presentCount} Active • ${mitigatedCount} Mitigated`}
            </span>
            <span className="text-[11px] font-mono text-slate-600 bg-white border border-[#E2DCD5] px-2.5 py-0.5 rounded-full">
              {language === "ta"
                ? `மொத்தம் ${totalEvaluated} விதிகள்`
                : `${totalEvaluated} Rules Evaluated`}
            </span>
          </div>
        </div>
        <p className="text-xs text-[#64748B] mt-2.5 leading-relaxed">
          {t.doshasSubtitle}
        </p>
      </div>

      {/* 2. Five Key Summary Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
            {t.doshasTotalEvaluated}
          </span>
          <div className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A]">
            {totalEvaluated}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-rose-700 flex items-center justify-center gap-1">
            <AlertTriangle className="w-3 h-3 text-rose-600" />
            <span>{t.doshasPresent}</span>
          </span>
          <div className="font-serif text-2xl sm:text-3xl font-bold text-rose-700">
            {presentCount}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 flex items-center justify-center gap-1">
            <ShieldCheck className="w-3 h-3 text-amber-600" />
            <span>{t.doshasMitigated}</span>
          </span>
          <div className="font-serif text-2xl sm:text-3xl font-bold text-amber-700">
            {mitigatedCount}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 flex items-center justify-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
            <span>{t.doshasAbsent}</span>
          </span>
          <div className="font-serif text-2xl sm:text-3xl font-bold text-emerald-700">
            {absentCount}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center space-y-1 col-span-2 sm:col-span-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-purple-800 flex items-center justify-center gap-1">
            <HelpCircle className="w-3 h-3 text-purple-600" />
            <span>{t.doshasIndeterminate}</span>
          </span>
          <div className="font-serif text-2xl sm:text-3xl font-bold text-purple-700">
            {indeterminateCount}
          </div>
        </div>
      </div>

      {/* 3. Filters & Search Control Bar */}
      <div className="rounded-xl border border-[#E2DCD5] bg-white p-4 shadow-2xs space-y-3">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          {/* Category Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5 text-xs font-semibold">
            <button
              type="button"
              onClick={() => setCategoryFilter("all")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "all"
                  ? "bg-[#0F172A] text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {t.doshasFilterAll} ({allDoshas.length})
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("Planetary Conjunction & Axis")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "Planetary Conjunction & Axis"
                  ? "bg-rose-700 text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {language === "ta" ? "கிரக சேர்க்கை & அச்சு" : "Conjunction & Axis"} ({categoryCounts["Planetary Conjunction & Axis"] || 0})
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("Moon & Nakshatra")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "Moon & Nakshatra"
                  ? "bg-sky-700 text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {language === "ta" ? "சந்திரன் & நட்சத்திரம்" : "Moon & Nakshatra"} ({categoryCounts["Moon & Nakshatra"] || 0})
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("Lagna & House Placements")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "Lagna & House Placements"
                  ? "bg-amber-700 text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {language === "ta" ? "லக்னம் & பாவகம்" : "Lagna & House"} ({categoryCounts["Lagna & House Placements"] || 0})
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("Marriage Compatibility")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "Marriage Compatibility"
                  ? "bg-purple-700 text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {language === "ta" ? "திருமணப் பொருத்தம்" : "Compatibility"} ({categoryCounts["Marriage Compatibility"] || 0})
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("Transit")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "Transit"
                  ? "bg-indigo-700 text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {language === "ta" ? "கோச்சாரம்" : "Transit"} ({categoryCounts["Transit"] || 0})
            </button>
          </div>

          {/* Status Qualifier Toggle Buttons */}
          <div className="flex flex-wrap items-center gap-1 bg-[#FAF8F5] p-1 rounded-lg border border-[#E2DCD5] self-start lg:self-auto">
            <button
              type="button"
              onClick={() => setStatusFilter("all")}
              className={`px-2 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                statusFilter === "all"
                  ? "bg-[#0F172A] text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              {t.doshasFilterAll}
            </button>
            <button
              type="button"
              onClick={() => setStatusFilter("present")}
              className={`px-2 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                statusFilter === "present"
                  ? "bg-rose-600 text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              {t.doshasFilterPresent}
            </button>
            <button
              type="button"
              onClick={() => setStatusFilter("mitigated")}
              className={`px-2 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                statusFilter === "mitigated"
                  ? "bg-amber-600 text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              {t.doshasFilterMitigated}
            </button>
            <button
              type="button"
              onClick={() => setStatusFilter("absent")}
              className={`px-2 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                statusFilter === "absent"
                  ? "bg-emerald-600 text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              {t.doshasFilterAbsent}
            </button>
            <button
              type="button"
              onClick={() => setStatusFilter("indeterminate")}
              className={`px-2 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                statusFilter === "indeterminate"
                  ? "bg-purple-600 text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              {t.doshasFilterIndeterminate}
            </button>
          </div>
        </div>

        {/* Search input */}
        <div className="relative">
          <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t.doshasSearchPlaceholder}
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-[#E2DCD5] text-xs bg-[#FAF8F5] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#B8860B] text-[#0F172A]"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* 4. Dosha Results Table */}
      <div className="rounded-xl border border-[#E2DCD5] bg-white overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#FAF7F0] border-b border-[#E2DCD5] text-[11px] font-bold text-[#64748B] uppercase tracking-wider">
                <th className="py-3 px-3.5 w-10 text-center">{t.doshasColSNo}</th>
                <th className="py-3 px-4">{t.doshasColName}</th>
                <th className="py-3 px-3">{t.doshasColCategory}</th>
                <th className="py-3 px-3">{t.doshasColStatus}</th>
                <th className="py-3 px-3">{t.doshasColPlanets}</th>
                <th className="py-3 px-3">{t.doshasColReference}</th>
                <th className="py-3 px-4 min-w-[200px]">{t.doshasColConditions}</th>
                <th className="py-3 px-3 text-right">{t.doshasColAction}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1EBE4]">
              {filteredDoshas.length > 0 ? (
                filteredDoshas.map((dosha, index) => {
                  const displayName = language === "ta" && dosha.name_ta ? dosha.name_ta : dosha.name_en;
                  return (
                    <tr
                      key={dosha.dosha_id}
                      className="hover:bg-[#FAF8F5] transition-colors cursor-pointer group"
                      onClick={() => setSelectedDosha(dosha)}
                    >
                      <td className="py-3 px-3.5 text-center text-slate-400 font-mono text-[11px]">
                        {index + 1}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-serif font-bold text-sm text-[#0F172A] group-hover:text-[#B8860B] transition-colors">
                          {displayName}
                        </div>
                        {language === "ta" && (
                          <div className="text-[10px] text-[#64748B] font-mono">{dosha.name_en}</div>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${getCategoryBadgeClass(
                            dosha.category
                          )}`}
                        >
                          {getCategoryName(dosha.category)}
                        </span>
                      </td>
                      <td className="py-3 px-3">{getStatusBadge(dosha.status)}</td>
                      <td className="py-3 px-3">
                        <div className="flex flex-wrap gap-1">
                          {dosha.involved_planets && dosha.involved_planets.length > 0 ? (
                            dosha.involved_planets.map((planet) => {
                              const graha = GRAHAS[planet];
                              const label = getGrahaName(planet, language);
                              const deg = dosha.degrees && dosha.degrees[planet] !== undefined
                                ? formatDegree(dosha.degrees[planet])
                                : null;
                              return (
                                <span
                                  key={planet}
                                  className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-[#FAF7F0] border border-[#E2DCD5] text-[#0F172A]"
                                  style={{ borderLeftColor: graha?.color || "#B8860B", borderLeftWidth: "2.5px" }}
                                >
                                  <span>{label}</span>
                                  {deg && <span className="font-mono text-[9px] text-[#64748B]">{deg}</span>}
                                </span>
                              );
                            })
                          ) : (
                            <span className="text-slate-400">—</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="inline-block px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px]">
                          {dosha.reference_basis || "Lagna"}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <p className="text-[11px] text-[#334155] line-clamp-2 leading-relaxed">
                          {language === "ta" && dosha.interpretation_ta
                            ? dosha.interpretation_ta
                            : dosha.interpretation}
                        </p>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedDosha(dosha);
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-bold text-[#784E0E] bg-[#FAF2DE] hover:bg-[#FAF4E6] border border-[#D8BD80] shadow-2xs transition-colors cursor-pointer"
                        >
                          <span>{t.doshasColAction}</span>
                          <ChevronRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-xs text-[#64748B]">
                    {language === "ta"
                      ? "தேர்ந்தெடுக்கப்பட்ட வடிகட்டிகளுக்கு தோஷங்கள் எதுவும் கிடைக்கவில்லை."
                      : "No doshas matched your current filter criteria."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Detailed Analytical Inspector Modal */}
      {selectedDosha && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="relative w-full max-w-2xl bg-white rounded-2xl border-2 border-[#D8BD80] shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-[#E2DCD5]">
              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`px-2.5 py-0.5 rounded text-[10px] font-bold border ${getCategoryBadgeClass(
                      selectedDosha.category
                    )}`}
                  >
                    {getCategoryName(selectedDosha.category)}
                  </span>
                  {getStatusBadge(selectedDosha.status)}
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 text-slate-700 border border-slate-200">
                    {language === "ta" ? "ஆதாரம்:" : "Basis:"} {selectedDosha.reference_basis}
                  </span>
                </div>
                <h3 className="font-serif text-2xl font-bold text-[#0F172A] flex items-center gap-2">
                  <span>
                    {language === "ta" && selectedDosha.name_ta ? selectedDosha.name_ta : selectedDosha.name_en}
                  </span>
                </h3>
                {language === "ta" && (
                  <p className="text-xs text-[#64748B] font-mono">{selectedDosha.name_en}</p>
                )}
              </div>
              <button
                type="button"
                onClick={() => setSelectedDosha(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Missing Prerequisite Alert if Indeterminate */}
            {selectedDosha.missing_prerequisites && (
              <div className="p-3.5 rounded-xl bg-purple-50 border border-purple-200 text-purple-900 text-xs space-y-1">
                <div className="font-bold flex items-center gap-1.5 text-purple-950">
                  <HelpCircle className="w-4 h-4 text-purple-600 shrink-0" />
                  <span>{t.doshasModalMissingPrereq}</span>
                </div>
                <p className="leading-relaxed text-[11px] text-purple-800">
                  {selectedDosha.missing_prerequisites}
                </p>
              </div>
            )}

            {/* Planetary Placements & Degrees Detail Chips */}
            {selectedDosha.signs_and_houses && selectedDosha.signs_and_houses.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
                  {language === "ta" ? "கிரக நிலைகள் & பாவகங்கள்" : "Planetary Positions & Signs/Houses"}
                </span>
                <div className="flex flex-wrap gap-2">
                  {selectedDosha.signs_and_houses.map((sh, idx) => {
                    if (typeof sh === "string") {
                      return (
                        <div
                          key={idx}
                          className="px-2.5 py-1.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] text-xs flex items-center gap-1.5 text-[#0F172A] font-medium"
                        >
                          <Compass className="w-3.5 h-3.5 text-[#B8860B]" />
                          <span>{sh}</span>
                        </div>
                      );
                    }
                    const pl = (sh as any)?.planet || "";
                    const graha = GRAHAS[pl];
                    const label = pl ? getGrahaName(pl, language) : "Graha";
                    return (
                      <div
                        key={idx}
                        className="px-2.5 py-1.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] text-xs flex items-center gap-2"
                        style={{ borderLeftColor: graha?.color || "#B8860B", borderLeftWidth: "3px" }}
                      >
                        <span className="font-bold text-[#0F172A]">{label}</span>
                        {(sh as any)?.house && (
                          <span className="px-1.5 py-0.5 rounded bg-slate-200/80 text-slate-800 font-mono text-[10px] font-bold">
                            H{(sh as any).house}
                          </span>
                        )}
                        {(sh as any)?.sign && (
                          <span className="text-[11px] text-[#475569]">{(sh as any).sign}</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Formation Conditions Evaluated Checklist */}
            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#64748B] block">
                {t.doshasModalFormation}
              </span>
              <div className="divide-y divide-[#F1EBE4] border border-[#E2DCD5] rounded-xl overflow-hidden bg-white">
                {selectedDosha.formation_conditions && selectedDosha.formation_conditions.length > 0 ? (
                  selectedDosha.formation_conditions.map((cond, i) => {
                    const isString = typeof cond === "string";
                    const ruleText = isString ? cond : (cond as any)?.rule || "";
                    const isPassed = isString
                      ? selectedDosha.status === "present" || selectedDosha.status === "mitigated"
                      : !!(cond as any)?.passed;
                    const evidence = isString ? null : (cond as any)?.evidence;

                    return (
                      <div key={i} className="p-3 space-y-1">
                        <div className="flex items-start gap-2">
                          {isPassed ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                          ) : (
                            <XCircle className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                          )}
                          <div>
                            <span className="text-xs font-bold text-[#0F172A]">{ruleText}</span>
                            {evidence && (
                              <p className="text-[11px] text-[#475569] mt-0.5">{evidence}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="p-3 text-xs text-[#64748B]">
                    {language === "ta" ? "விதிகள் பதிவு செய்யப்படவில்லை." : "No specific formation conditions recorded."}
                  </div>
                )}
              </div>
            </div>

            {/* Cancellation & Mitigation Analysis */}
            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#64748B] block">
                {t.doshasModalCancellation}
              </span>
              {selectedDosha.cancellation_evidence && selectedDosha.cancellation_evidence.length > 0 ? (
                <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-950 text-xs space-y-1.5">
                  <div className="font-bold flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>{language === "ta" ? "செயலில் உள்ள நிவர்த்திகள் / பங்கங்கள்:" : "Active Mitigations & Cancellations:"}</span>
                  </div>
                  <ul className="list-disc list-inside space-y-1 text-[11px] text-amber-900">
                    {selectedDosha.cancellation_evidence.map((ev, idx) => (
                      <li key={idx} className="leading-relaxed">{ev}</li>
                    ))}
                  </ul>
                </div>
              ) : selectedDosha.cancellation_conditions_checked && selectedDosha.cancellation_conditions_checked.length > 0 ? (
                <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E2DCD5] text-xs text-[#64748B] space-y-1">
                  <p className="text-[11px] font-semibold text-[#475569]">
                    {language === "ta"
                      ? "ஆய்வு செய்யப்பட்ட நிவர்த்தி விதிகள் (எவையும் பொருந்தவில்லை):"
                      : "Mitigation rules checked (none active):"}
                  </p>
                  <ul className="list-disc list-inside text-[10px] space-y-0.5 text-[#64748B]">
                    {selectedDosha.cancellation_conditions_checked.map((cc, idx) => (
                      <li key={idx}>{cc}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E2DCD5] text-xs text-[#64748B]">
                  {language === "ta" ? "குறிப்பிட்ட நிவர்த்தி விதிகள் எதுவும் பொருந்தவில்லை." : "No specific cancellation conditions registered."}
                </div>
              )}
            </div>

            {/* Classical Interpretation (Non-Alarmist) */}
            <div className="space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B]">
                {t.doshasModalInterpretation}
              </span>
              <div className="p-3.5 rounded-xl bg-blue-50/50 border border-blue-200/60 text-xs text-[#1E293B] leading-relaxed">
                <p className="italic">
                  &ldquo;{selectedDosha.interpretation}&rdquo;
                </p>
                {language === "ta" && selectedDosha.interpretation_ta && (
                  <p className="mt-2 pt-2 border-t border-blue-200/40 text-[11px] text-[#334155]">
                    {selectedDosha.interpretation_ta}
                  </p>
                )}
              </div>
            </div>

            {/* Classical Remedies if provided */}
            {selectedDosha.remedies && selectedDosha.remedies.length > 0 && (
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800">
                  {t.doshasModalRemedies}
                </span>
                <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-200/70 text-xs space-y-1.5">
                  <ul className="list-disc list-inside space-y-1 text-[11px] text-emerald-950">
                    {selectedDosha.remedies.map((rem, idx) => (
                      <li key={idx} className="leading-relaxed">{rem}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Metadata Footer: Classical References & Rule-set Version */}
            <div className="pt-3 border-t border-[#E2DCD5] flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#64748B]">
              <div className="flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-[#B8860B]" />
                <span className="font-medium text-[#784E0E]">
                  {Array.isArray(selectedDosha.source_references)
                    ? selectedDosha.source_references.join(", ")
                    : selectedDosha.source_references || "Classical Vedic Authority"}
                </span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                Rule-Set: {selectedDosha.rule_set_version || "v1.0.0"}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
