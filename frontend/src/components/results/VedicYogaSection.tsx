"use client";

import React, { useState, useMemo } from "react";
import { VedicYogaResponse, YogaDetail } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaName, GRAHAS } from "@/lib/translations";
import {
  Sparkles,
  ShieldCheck,
  Crown,
  Coins,
  Star,
  Layers,
  Search,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Info,
  ChevronRight,
  X,
  Orbit,
  ExternalLink,
  BookOpen,
  Filter,
} from "lucide-react";

interface VedicYogaSectionProps {
  vedicYogas?: VedicYogaResponse | null;
  onCalculate?: () => void;
  isCalculating?: boolean;
}

export function VedicYogaSection({
  vedicYogas,
  onCalculate,
  isCalculating,
}: VedicYogaSectionProps) {
  const { language, t } = useLanguage();

  const [selectedYoga, setSelectedYoga] = useState<YogaDetail | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<"qualifying" | "all" | "non-qualifying">("qualifying");
  const [searchQuery, setSearchQuery] = useState<string>("");

  if (!vedicYogas) {
    return (
      <div className="p-8 rounded-xl border border-[#E2DCD5] bg-white text-center space-y-4 shadow-xs">
        <div className="w-12 h-12 mx-auto rounded-full bg-[#FAF2DE] text-[#8C6D23] flex items-center justify-center">
          <Sparkles className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h3 className="font-serif text-lg font-bold text-[#0F172A]">
            {t.vedicYogasTitle}
          </h3>
          <p className="text-xs text-[#64748B] max-w-md mx-auto">
            {language === "ta"
              ? "வேத யோகக் கணக்கீட்டு முடிவுகள் இன்னும் ஏற்றப்படவில்லை."
              : "Vedic Yoga calculations are not yet generated for this horoscope snapshot."}
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
                <span>{language === "ta" ? "வேத யோகங்களைக் கணக்கிடு" : "Calculate Vedic Yogas"}</span>
              </>
            )}
          </button>
        )}
      </div>
    );
  }

  const { summary, yogas } = vedicYogas;

  // Filter logic
  const filteredYogas = useMemo(() => {
    return yogas.filter((y) => {
      // Category filter
      if (categoryFilter !== "all") {
        if (categoryFilter === "raja" && y.category !== "Raja Yoga") return false;
        if (categoryFilter === "dhana" && y.category !== "Dhana Yoga") return false;
        if (categoryFilter === "mahapurusha" && y.category !== "Panch Mahapurusha") return false;
        if (categoryFilter === "vipareeta" && y.category !== "Vipareeta Raja") return false;
        if (categoryFilter === "other" && ["Raja Yoga", "Dhana Yoga", "Panch Mahapurusha", "Vipareeta Raja"].includes(y.category)) return false;
      }

      // Status filter
      if (statusFilter === "qualifying" && !y.is_qualifying) return false;
      if (statusFilter === "non-qualifying" && y.is_qualifying) return false;

      // Search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        const matchName = y.name.toLowerCase().includes(query) || (y.name_tamil && y.name_tamil.toLowerCase().includes(query));
        const matchCategory = y.category.toLowerCase().includes(query);
        const matchPlanet = y.planets_involved.some((p) => p.toLowerCase().includes(query));
        if (!matchName && !matchCategory && !matchPlanet) return false;
      }

      return true;
    });
  }, [yogas, categoryFilter, statusFilter, searchQuery]);

  const getStatusBadge = (yoga: YogaDetail) => {
    if (yoga.status === "Qualifying") {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-300">
          <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
          <span>{language === "ta" ? "பொருந்துகிறது" : "Qualifying"}</span>
        </span>
      );
    }
    if (yoga.status === "Cancelled") {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-900 border border-amber-300">
          <AlertTriangle className="w-3 h-3 text-amber-600 shrink-0" />
          <span>{language === "ta" ? "ரத்தானது (பங்கம்)" : "Cancelled (Bhanga)"}</span>
        </span>
      );
    }
    if (yoga.status === "Partially Qualifying") {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-50 text-blue-900 border border-blue-300">
          <Info className="w-3 h-3 text-blue-600 shrink-0" />
          <span>{language === "ta" ? "பகுதிப் பொருத்தம்" : "Partial"}</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
        <XCircle className="w-3 h-3 text-slate-400 shrink-0" />
        <span>{language === "ta" ? "பொருந்தவில்லை" : "Not Qualifying"}</span>
      </span>
    );
  };

  const getCategoryBadge = (category: string) => {
    switch (category) {
      case "Raja Yoga":
        return "bg-amber-50 text-amber-900 border-amber-300";
      case "Dhana Yoga":
        return "bg-emerald-50 text-emerald-900 border-emerald-300";
      case "Panch Mahapurusha":
        return "bg-purple-50 text-purple-900 border-purple-300";
      case "Vipareeta Raja":
        return "bg-indigo-50 text-indigo-900 border-indigo-300";
      case "Major Classical":
        return "bg-blue-50 text-blue-900 border-blue-300";
      case "Avayoga":
        return "bg-rose-50 text-rose-900 border-rose-300";
      default:
        return "bg-slate-50 text-slate-800 border-slate-200";
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <div className="p-4 sm:p-5 rounded-xl border border-[#D8BD80]/80 bg-[#FAF7F0] shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E8DEC8]">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[#B8860B]" />
            <h3 className="font-serif text-lg font-bold text-[#0F172A]">
              {t.vedicYogasTitle}
            </h3>
          </div>
          <span className="text-[11px] font-mono text-[#784E0E] bg-[#FAF2DE] border border-[#D8BD80] px-2.5 py-0.5 rounded-full self-start sm:self-auto">
            {language === "ta"
              ? `${summary.total_qualifying} யோகங்கள் பொருந்தின`
              : `${summary.total_qualifying} Active Yogas Formed`}
          </span>
        </div>
        <p className="text-xs text-[#64748B] mt-2.5 leading-relaxed">
          {t.vedicYogasSubtitle}
        </p>
      </div>

      {/* 2. Four Key Summary Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
            {t.vedicYogasTotalQualifying}
          </span>
          <div className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A]">
            {summary.total_qualifying}
            <span className="text-xs font-normal text-[#94A3B8] ml-1">/ {summary.total_evaluated}</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#8C6D23] flex items-center justify-center gap-1">
            <Crown className="w-3 h-3 text-[#B8860B]" />
            <span>{t.vedicYogasRajaYogas}</span>
          </span>
          <div className="font-serif text-2xl sm:text-3xl font-bold text-[#B8860B]">
            {summary.raja_yogas_count}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 flex items-center justify-center gap-1">
            <Coins className="w-3 h-3 text-emerald-600" />
            <span>{t.vedicYogasDhanaYogas}</span>
          </span>
          <div className="font-serif text-2xl sm:text-3xl font-bold text-emerald-700">
            {summary.dhana_yogas_count}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-purple-800 flex items-center justify-center gap-1">
            <Star className="w-3 h-3 text-purple-600" />
            <span>{t.vedicYogasMahapurusha}</span>
          </span>
          <div className="font-serif text-2xl sm:text-3xl font-bold text-purple-700">
            {summary.mahapurusha_yogas_count}
          </div>
        </div>
      </div>

      {/* 3. Filters & Search Control Bar */}
      <div className="rounded-xl border border-[#E2DCD5] bg-white p-4 shadow-2xs space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
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
              {t.vedicYogasFilterAll}
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("raja")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "raja"
                  ? "bg-[#B8860B] text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {t.vedicYogasRajaYogas} ({summary.raja_yogas_count})
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("dhana")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "dhana"
                  ? "bg-emerald-700 text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {t.vedicYogasDhanaYogas} ({summary.dhana_yogas_count})
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("mahapurusha")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "mahapurusha"
                  ? "bg-purple-700 text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {t.vedicYogasMahapurusha} ({summary.mahapurusha_yogas_count})
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("vipareeta")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "vipareeta"
                  ? "bg-indigo-700 text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {t.vedicYogasVipareeta} ({summary.vipareeta_yogas_count})
            </button>
            <button
              type="button"
              onClick={() => setCategoryFilter("other")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                categoryFilter === "other"
                  ? "bg-slate-700 text-white shadow-2xs"
                  : "bg-[#FAF8F5] text-[#475569] hover:bg-[#FAF2DE] hover:text-[#0F172A] border border-[#E2DCD5]"
              }`}
            >
              {t.vedicYogasOtherClassical} ({summary.other_classical_count})
            </button>
          </div>

          {/* Status Qualifier Toggle */}
          <div className="flex items-center gap-1 bg-[#FAF8F5] p-1 rounded-lg border border-[#E2DCD5] self-start md:self-auto">
            <button
              type="button"
              onClick={() => setStatusFilter("qualifying")}
              className={`px-2.5 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                statusFilter === "qualifying"
                  ? "bg-emerald-600 text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              {t.vedicYogasFilterQualifying}
            </button>
            <button
              type="button"
              onClick={() => setStatusFilter("all")}
              className={`px-2.5 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                statusFilter === "all"
                  ? "bg-[#0F172A] text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              {t.vedicYogasFilterAll}
            </button>
            <button
              type="button"
              onClick={() => setStatusFilter("non-qualifying")}
              className={`px-2.5 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                statusFilter === "non-qualifying"
                  ? "bg-slate-700 text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              {t.vedicYogasFilterNonQualifying}
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
            placeholder={t.vedicYogasSearchPlaceholder}
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-[#E2DCD5] text-xs bg-[#FAF8F5] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#B8860B] text-[#0F172A]"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* 4. Yoga Results Table */}
      <div className="rounded-xl border border-[#E2DCD5] bg-white overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#FAF7F0] border-b border-[#E2DCD5] text-[11px] font-bold text-[#64748B] uppercase tracking-wider">
                <th className="py-3 px-3.5 w-10 text-center">{t.vedicYogasColSNo}</th>
                <th className="py-3 px-4">{t.vedicYogasColName}</th>
                <th className="py-3 px-3">{t.vedicYogasColCategory}</th>
                <th className="py-3 px-3">{t.vedicYogasColStatus}</th>
                <th className="py-3 px-3">{t.vedicYogasColPlanets}</th>
                <th className="py-3 px-3">{t.vedicYogasColHouses}</th>
                <th className="py-3 px-4 min-w-[200px]">{t.vedicYogasColConditions}</th>
                <th className="py-3 px-3 text-right">{t.vedicYogasColAction}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1EBE4]">
              {filteredYogas.length > 0 ? (
                filteredYogas.map((yoga, index) => {
                  const displayName = language === "ta" && yoga.name_tamil ? yoga.name_tamil : yoga.name;
                  return (
                    <tr
                      key={yoga.id}
                      className="hover:bg-[#FAF8F5] transition-colors cursor-pointer group"
                      onClick={() => setSelectedYoga(yoga)}
                    >
                      <td className="py-3 px-3.5 text-center text-slate-400 font-mono text-[11px]">
                        {index + 1}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-serif font-bold text-sm text-[#0F172A] group-hover:text-[#B8860B] transition-colors flex items-center gap-1.5">
                          <span>{displayName}</span>
                        </div>
                        {language === "ta" && (
                          <div className="text-[10px] text-[#64748B] font-mono">{yoga.name}</div>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${getCategoryBadge(
                            yoga.category
                          )}`}
                        >
                          {yoga.category}
                        </span>
                      </td>
                      <td className="py-3 px-3">{getStatusBadge(yoga)}</td>
                      <td className="py-3 px-3">
                        <div className="flex flex-wrap gap-1">
                          {yoga.planets_involved.map((planet) => {
                            const graha = GRAHAS[planet];
                            const label = getGrahaName(planet, language);
                            return (
                              <span
                                key={planet}
                                className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-[#FAF7F0] border border-[#E2DCD5] text-[#0F172A]"
                                style={{ borderLeftColor: graha?.color || "#B8860B", borderLeftWidth: "2.5px" }}
                              >
                                {label}
                              </span>
                            );
                          })}
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <div className="flex flex-wrap gap-1">
                          {yoga.relevant_houses.length > 0 ? (
                            yoga.relevant_houses.map((h, hIdx) => (
                              <span
                                key={`${h}-${hIdx}`}
                                className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 font-mono text-[10px] font-bold"
                              >
                                H{h}
                              </span>
                            ))
                          ) : (
                            <span className="text-slate-400">—</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <p className="text-[11px] text-[#334155] line-clamp-2 leading-relaxed">
                          {yoga.short_interpretation}
                        </p>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedYoga(yoga);
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-bold text-[#784E0E] bg-[#FAF2DE] hover:bg-[#FAF4E6] border border-[#D8BD80] shadow-2xs transition-colors cursor-pointer"
                        >
                          <span>{t.vedicYogasColAction}</span>
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
                      ? "தேர்ந்தெடுக்கப்பட்ட வடிகட்டிகளுக்கு யோகங்கள் எதுவும் கிடைக்கவில்லை."
                      : "No yogas matched your current filter criteria."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Detailed Inspection Modal / Inspector Drawer */}
      {selectedYoga && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="relative w-full max-w-3xl bg-white rounded-2xl border-2 border-[#D8BD80] shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-[#E2DCD5]">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2.5 py-0.5 rounded text-[10px] font-bold border ${getCategoryBadge(
                      selectedYoga.category
                    )}`}
                  >
                    {selectedYoga.category}
                  </span>
                  {getStatusBadge(selectedYoga)}
                </div>
                <h3 className="font-serif text-2xl font-bold text-[#0F172A] flex items-center gap-2">
                  <span>
                    {language === "ta" && selectedYoga.name_tamil ? selectedYoga.name_tamil : selectedYoga.name}
                  </span>
                </h3>
                {language === "ta" && (
                  <p className="text-xs text-[#64748B] font-mono">{selectedYoga.name}</p>
                )}
              </div>
              <button
                type="button"
                onClick={() => setSelectedYoga(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Classical Definition */}
            <div className="p-3.5 rounded-xl bg-[#FAF7F0] border border-[#E8DEC8] space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#8C6D23] flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-[#B8860B]" />
                <span>{t.vedicYogasModalDefinition}</span>
              </span>
              <p className="text-xs font-semibold text-[#0F172A] leading-relaxed">
                {selectedYoga.classical_definition}
              </p>
            </div>

            {/* Detailed Conditions Evaluated Checklist */}
            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#64748B] block">
                {t.vedicYogasModalConditionsEval}
              </span>
              <div className="divide-y divide-[#F1EBE4] border border-[#E2DCD5] rounded-xl overflow-hidden bg-white">
                {selectedYoga.conditions.map((cond, i) => (
                  <div key={i} className="p-3 space-y-1">
                    <div className="flex items-start gap-2">
                      {cond.passed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                      )}
                      <div>
                        <span className="text-xs font-bold text-[#0F172A]">{cond.condition}</span>
                        <p className="text-[11px] text-[#475569] mt-0.5">{cond.detail}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Cancellation Notice if Cancelled */}
            {selectedYoga.cancellation_reason && (
              <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1">
                <span className="font-bold flex items-center gap-1 text-amber-950">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>{t.vedicYogasModalCancellation}</span>
                </span>
                <p className="leading-relaxed">{selectedYoga.cancellation_reason}</p>
              </div>
            )}

            {/* Classical Interpretation */}
            <div className="space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B]">
                {t.vedicYogasModalInterpretation}
              </span>
              <div className="p-3.5 rounded-xl bg-blue-50/50 border border-blue-200/60 text-xs text-[#1E293B] italic leading-relaxed">
                &ldquo;{selectedYoga.short_interpretation}&rdquo;
              </div>
            </div>

            {/* Metadata Footer: Classical Reference and Verification Status */}
            <div className="pt-3 border-t border-[#E2DCD5] flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#64748B]">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-[#B8860B]" />
                <span className="font-medium text-[#784E0E]">{selectedYoga.classical_reference}</span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                {selectedYoga.verification_status}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
