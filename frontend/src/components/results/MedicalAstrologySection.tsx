"use client";

import React, { useState, useMemo } from "react";
import {
  HoroscopeResponse,
  KpResponse,
  DasaResponse,
  LiveTransitsResponse,
  MedicalAstrologyResponse,
  MedicalRule,
  HouseHealthAnalysis,
  AnatomicalSystemMapping,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { evaluateMedicalAstrologyClient } from "@/lib/medical-astrology-evaluator";
import {
  ShieldAlert,
  Activity,
  HeartPulse,
  Info,
  BookOpen,
  Sparkles,
  Clock,
  Compass,
  Filter,
  Search,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Radio,
  Calendar,
  Award,
  X,
  ExternalLink,
  ShieldCheck,
  Check,
} from "lucide-react";

interface MedicalAstrologySectionProps {
  horoscope?: HoroscopeResponse | null;
  kp?: KpResponse | null;
  dasa?: DasaResponse | null;
  liveTransits?: LiveTransitsResponse | null;
  clientInputs?: {
    fullName?: string;
    birthDate?: string;
    birthTime?: string;
    timezone?: string;
  };
  savedHoroscopeId?: string;
}

export function MedicalAstrologySection({
  horoscope,
  kp,
  dasa,
  liveTransits,
  clientInputs,
  savedHoroscopeId,
}: MedicalAstrologySectionProps) {
  const { language } = useLanguage();

  // Internal tab: "birth" | "current" | "historical" | "vedic" | "kp"
  const [activePerspective, setActivePerspective] = useState<
    "birth" | "current" | "historical" | "vedic" | "kp"
  >("birth");

  // Filter and search state for classical rules
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [selectedRule, setSelectedRule] = useState<MedicalRule | null>(null);

  // Compute or use pre-calculated Medical Astrology data
  const medicalData: MedicalAstrologyResponse | null = useMemo(() => {
    if (!horoscope) return null;
    if (horoscope.medical_astrology) {
      return horoscope.medical_astrology;
    }
    try {
      return evaluateMedicalAstrologyClient(horoscope, kp, dasa, liveTransits);
    } catch (err) {
      console.warn("Medical astrology client evaluation error:", err);
      return null;
    }
  }, [horoscope, kp, dasa, liveTransits]);

  if (!horoscope || !medicalData) {
    return (
      <div className="p-8 rounded-xl border border-[#D9DEE7] bg-white text-center space-y-4 shadow-2xs">
        <div className="w-12 h-12 mx-auto rounded-full bg-[#FAF2DE] text-[#B4872B] flex items-center justify-center">
          <HeartPulse className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h3 className="font-serif text-lg font-bold text-[#183047]">
            {language === "ta" ? "மருத்துவ ஜோதிட ஆராய்ச்சி" : "Medical Astrology Research"}
          </h3>
          <p className="text-xs text-[#52667E] max-w-md mx-auto">
            {language === "ta"
              ? "மருத்துவ ஜோதிட பகுப்பாய்விற்கான ஜாதகத் தரவுகள் கிடைக்கவில்லை. தயவுசெய்து ஜாதகத்தை மீண்டும் கணக்கிடவும்."
              : "Horoscope data is not available for Medical Astrology research. Please recalculate or reload the chart."}
          </p>
        </div>
      </div>
    );
  }

  const { vedic_analysis: vedic, kp_analysis: kpData, disclaimer_en, disclaimer_ta, rule_set_version } = medicalData;
  const { birth_chart: birthChart, current_period: currentPeriod, historical_periods: historicalPeriods } = vedic;

  // Filter triggered classical rules
  const filteredRules = useMemo(() => {
    const list = birthChart.triggered_rules || [];
    return list.filter((r) => {
      if (categoryFilter !== "all" && r.category !== categoryFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchName = r.name.toLowerCase().includes(q) || r.name_tamil.toLowerCase().includes(q);
        const matchSource = r.source.toLowerCase().includes(q) || r.chapter_verse.toLowerCase().includes(q);
        const matchSystem = r.anatomical_system.toLowerCase().includes(q);
        if (!matchName && !matchSource && !matchSystem) return false;
      }
      return true;
    });
  }, [birthChart.triggered_rules, categoryFilter, searchQuery]);

  return (
    <div className="space-y-6">
      {/* 1. Mandatory Safety & Ethical Notice Banner (English & Tamil) */}
      <div className="rounded-xl border border-amber-300 bg-amber-50/90 p-4 sm:p-5 shadow-2xs">
        <div className="flex items-start gap-3.5">
          <div className="w-9 h-9 rounded-full bg-amber-200/80 text-amber-900 flex items-center justify-center shrink-0 mt-0.5">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div className="space-y-2 text-xs text-amber-950 flex-1">
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <span className="font-bold uppercase tracking-wider text-[11px] text-amber-800">
                {language === "ta" ? "முக்கிய அறிவிப்பு மற்றும் நெறிமுறை வழிகாட்டுதல்" : "Important Research & Ethical Notice"}
              </span>
              <span className="font-mono text-[10px] text-amber-700 bg-amber-100 px-2 py-0.5 rounded border border-amber-200">
                Registry v{rule_set_version}
              </span>
            </div>
            <p className="leading-relaxed font-medium">
              {language === "ta" ? disclaimer_ta : disclaimer_en}
            </p>
            <p className="text-[11px] text-amber-800 leading-relaxed border-t border-amber-200/60 pt-1.5">
              {language === "ta" ? disclaimer_en : disclaimer_ta}
            </p>
          </div>
        </div>
      </div>

      {/* 2. Primary Navigation Bar */}
      <div className="bg-white rounded-xl border border-[#D9DEE7] p-2 sm:p-3 shadow-2xs">
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs font-semibold pb-1 sm:pb-0">
          {/* Perspective A: Birth Chart */}
          <button
            type="button"
            onClick={() => setActivePerspective("birth")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activePerspective === "birth"
                ? "bg-[#153F6B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "பிறப்பு ஜாதக ஆய்வு" : "Birth-Chart Research"}</span>
          </button>

          {/* Perspective B: Current Period */}
          <button
            type="button"
            onClick={() => setActivePerspective("current")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activePerspective === "current"
                ? "bg-[#153F6B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "நடப்பு தசா ஆய்வு" : "Current Period"}</span>
          </button>

          {/* Perspective C: Historical Periods */}
          <button
            type="button"
            onClick={() => setActivePerspective("historical")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activePerspective === "historical"
                ? "bg-[#153F6B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "வரலாற்று காலக்கோடு" : "Historical Periods"}</span>
          </button>

          <span className="text-[#D9DEE7] hidden sm:inline">|</span>

          {/* Dedicated Vedic Perspective View */}
          <button
            type="button"
            onClick={() => setActivePerspective("vedic")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activePerspective === "vedic"
                ? "bg-[#B4872B] text-white shadow-2xs font-bold"
                : "text-[#8C6D23] hover:text-[#5F4917] hover:bg-[#FAF2DE]/50"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "வேத ஜோதிட முறை" : "Vedic Analysis"}</span>
          </button>

          {/* Dedicated KP Perspective View */}
          <button
            type="button"
            onClick={() => setActivePerspective("kp")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activePerspective === "kp"
                ? "bg-[#153F6B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <Award className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "கே.பி. முறை (CSL)" : "KP Analysis (CSL)"}</span>
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* PERSPECTIVE A: BIRTH-CHART RESEARCH */}
      {/* ------------------------------------------------------------------- */}
      {(activePerspective === "birth" || activePerspective === "vedic") && (
        <div className="space-y-6">
          {/* 4 Key Houses Health Grid */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-base font-bold text-[#183047] flex items-center gap-2">
                <HeartPulse className="w-4 h-4 text-[#B4872B]" />
                <span>
                  {language === "ta"
                    ? "முக்கிய உடல்நல பாவங்கள் (1, 6, 8, 12-ம் வீடுகள்)"
                    : "Primary Health Bhavas (Houses 1, 6, 8, and 12)"}
                </span>
              </h3>
              <span className="text-[11px] text-[#8190A6]">
                {language === "ta" ? "பராசர ஹோரா சாஸ்திர முறை" : "Parashari Canonical Framework"}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[birthChart.lagna_analysis, birthChart.sixth_house_analysis, birthChart.eighth_house_analysis, birthChart.twelfth_house_analysis].map((h) => {
                const isLagna = h.house_number === 1;
                const isRoga = h.house_number === 6;
                const isAyur = h.house_number === 8;
                const titleBadge = isLagna
                  ? (language === "ta" ? "1-ம் பாவம்: லக்னம் (உடலமைப்பு & உயிர் பலம்)" : "House 1: Lagna (Vitality & Constitution)")
                  : isRoga
                  ? (language === "ta" ? "6-ம் பாவம்: ரோக ஸ்தானம் (நோய் எதிர்ப்பு & செரிமானம்)" : "House 6: Roga Bhava (Acute Illness & Immunity)")
                  : isAyur
                  ? (language === "ta" ? "8-ம் பாவம்: ஆயுள் ஸ்தானம் (நீண்டகால சகிப்புத்தன்மை)" : "House 8: Ayur Bhava (Chronic Reserves & Crisis)")
                  : (language === "ta" ? "12-ம் பாவம்: விரய ஸ்தானம் (ஓய்வு, தூக்கம், மருத்துவச் செலவு)" : "House 12: Vyaya Bhava (Recuperation & Sleep)");

                return (
                  <div
                    key={`bhava-card-${h.house_number}`}
                    className="bg-white rounded-xl border border-[#D9DEE7] p-4 shadow-2xs space-y-3 flex flex-col justify-between"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between gap-2 border-b border-[#F2F3F5] pb-2">
                        <span className="font-bold text-xs text-[#153F6B]">{titleBadge}</span>
                        <span className="font-mono text-[11px] text-[#B4872B] font-semibold">
                          {language === "ta" ? h.sign_name_ta : h.sign_name_en}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-[11px]">
                        <div>
                          <span className="text-[#8190A6] block">{language === "ta" ? "அதிபதி:" : "House Lord:"}</span>
                          <span className="font-semibold text-[#183047]">{h.lord} ({h.lord_dignity})</span>
                        </div>
                        <div>
                          <span className="text-[#8190A6] block">{language === "ta" ? "அதிபதி நின்ற பாவம்:" : "Lord Placement:"}</span>
                          <span className="font-mono text-[#183047]">
                            {h.lord_house ? `House ${h.lord_house} (${h.lord_sign || "-"})` : "-"}
                          </span>
                        </div>
                        <div>
                          <span className="text-[#8190A6] block">{language === "ta" ? "நின்ற கிரகங்கள்:" : "Occupants:"}</span>
                          <span className="text-[#183047] font-medium">
                            {h.occupants.length > 0 ? h.occupants.join(", ") : (language === "ta" ? "எதுவுமில்லை" : "None")}
                          </span>
                        </div>
                        <div>
                          <span className="text-[#8190A6] block">{language === "ta" ? "பார்வை செய்யும் கிரகங்கள்:" : "Aspecting Grahas:"}</span>
                          <span className="text-[#183047] font-medium">
                            {h.aspecting_planets.length > 0 ? h.aspecting_planets.join(", ") : (language === "ta" ? "எதுவுமில்லை" : "None")}
                          </span>
                        </div>
                      </div>

                      <div className="bg-[#F8FAFC] rounded-lg p-2.5 border border-[#E2E8F0] text-[11px] space-y-1">
                        <span className="font-bold text-[#153F6B] block">
                          {language === "ta" ? "உடல் உறுப்பு ஆதிக்கம்:" : "Anatomical Rulership:"} {language === "ta" ? h.anatomical_system_ta : h.anatomical_system_en}
                        </span>
                        <p className="text-[#52667E] leading-relaxed">
                          {language === "ta" ? h.traditional_summary_ta : h.traditional_summary_en}
                        </p>
                      </div>
                    </div>

                    {/* Mitigations or Afflictions Badges */}
                    <div className="pt-2 border-t border-[#F2F3F5] flex items-center justify-between gap-2 flex-wrap text-[10px]">
                      {h.mitigations.length > 0 && (
                        <div className="flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>{h.mitigations[0]}</span>
                        </div>
                      )}
                      {h.afflictions.length > 0 && (
                        <div className="flex items-center gap-1 text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                          <AlertTriangle className="w-3 h-3" />
                          <span>{h.afflictions[0]}</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Conflicting Indications & Classical Mitigations Banner */}
          {birthChart.conflicting_indications.length > 0 && (
            <div className="bg-emerald-50/80 rounded-xl border border-emerald-200 p-4 shadow-2xs space-y-2">
              <div className="flex items-center gap-2 text-emerald-900 font-bold text-xs">
                <ShieldCheck className="w-4 h-4 text-emerald-700" />
                <span>
                  {language === "ta"
                    ? "பாரம்பரிய அரிஷ்ட பங்க மற்றும் சமன்செய்யும் விதிகள் (Classical Mitigations)"
                    : "Classical Mitigations & Arishta Bhanga Formations"}
                </span>
              </div>
              <ul className="text-xs text-emerald-950 space-y-1 pl-5 list-disc leading-relaxed">
                {birthChart.conflicting_indications.map((ci, idx) => (
                  <li key={`mitig-ind-${idx}`}>{ci}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Source-Backed Triggered Classical Rules Section */}
          <div className="bg-white rounded-xl border border-[#D9DEE7] p-4 sm:p-5 shadow-2xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#F2F3F5] pb-3">
              <div>
                <h4 className="font-serif text-base font-bold text-[#183047] flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-[#B4872B]" />
                  <span>
                    {language === "ta"
                      ? "சான்றளிக்கப்பட்ட பாரம்பரிய ஜோதிட விதிகள் (Rule Registry)"
                      : "Source-Backed Traditional Rule Library"}
                  </span>
                </h4>
                <p className="text-xs text-[#8190A6]">
                  {language === "ta"
                    ? "பிருஹத் பராசர ஹோரா சாஸ்திரம் அத்தியாயம் 17 மற்றும் பிற மூல நூல்களின் சரிபார்க்கப்பட்ட விதிகள்."
                    : "Verified classical combinations from Brihat Parashara Hora Shastra Ch. 17 and classical texts."}
                </p>
              </div>

              {/* Search & Category Filter */}
              <div className="flex items-center gap-2 flex-wrap">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-[#8190A6] absolute left-2.5 top-2.5" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder={language === "ta" ? "விதியைத் தேடுக…" : "Filter rules…"}
                    className="pl-8 pr-3 py-1.5 rounded-lg border border-[#D9DEE7] text-xs w-36 sm:w-44 focus:outline-hidden focus:border-[#B4872B]"
                  />
                </div>
              </div>
            </div>

            {/* Rules Cards List */}
            {filteredRules.length === 0 ? (
              <div className="p-6 text-center text-xs text-[#8190A6] border border-dashed border-[#D9DEE7] rounded-xl">
                {language === "ta"
                  ? "தேடலுக்குரிய குறிப்பிட்ட பாரம்பரிய விதி எதுவும் கண்டறியப்படவில்லை."
                  : "No classical rules matched the current filter criteria."}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {filteredRules.map((rule) => (
                  <div
                    key={`med-rule-${rule.id}`}
                    onClick={() => setSelectedRule(rule)}
                    className="p-3.5 rounded-xl border border-[#D9DEE7] bg-white hover:border-[#B4872B] hover:shadow-2xs transition-all cursor-pointer space-y-2.5 flex flex-col justify-between"
                  >
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-bold text-xs text-[#153F6B] leading-snug">
                          {language === "ta" ? rule.name_tamil : rule.name}
                        </span>
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-[#FAF2DE] text-[#8C6D23] shrink-0 border border-[#B4872B]/30">
                          {rule.category}
                        </span>
                      </div>

                      <p className="text-[11px] text-[#52667E] line-clamp-2 leading-relaxed">
                        {language === "ta" ? rule.interpretation_tamil : rule.traditional_interpretation}
                      </p>
                    </div>

                    <div className="pt-2 border-t border-[#F2F3F5] flex items-center justify-between gap-2 text-[10px] text-[#8190A6]">
                      <span className="truncate max-w-[200px] font-mono">
                        {rule.source} ({rule.chapter_verse})
                      </span>
                      <span className="text-[#B4872B] font-semibold hover:underline flex items-center gap-0.5">
                        <span>{language === "ta" ? "விவரங்கள்" : "Inspect"}</span>
                        <ChevronRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Kalapurusha 12-Sign Anatomical System Table */}
          <div className="bg-white rounded-xl border border-[#D9DEE7] p-4 sm:p-5 shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-serif text-base font-bold text-[#183047] flex items-center gap-2">
                <Layers className="w-4 h-4 text-[#B4872B]" />
                <span>
                  {language === "ta"
                    ? "காலபுருஷ 12 ராசி உடல் உறுப்பு வரைபடம் (Kalapurusha Anatomy)"
                    : "Kalapurusha 12-Sign Anatomical Correspondence"}
                </span>
              </h4>
              <span className="text-[11px] text-[#8190A6]">
                {language === "ta" ? "12 ராசிகளின் உடல் அமைப்பு" : "12-Sign Zodiac Matrix"}
              </span>
            </div>

            <div className="overflow-x-auto rounded-lg border border-[#E2E8F0]">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#FAF8F2] text-[#8C6D23] font-semibold border-b border-[#E2E8F0]">
                  <tr>
                    <th className="p-2 sm:p-2.5">{language === "ta" ? "ராசி / மண்டலம்" : "Zodiac Sign / System"}</th>
                    <th className="p-2 sm:p-2.5">{language === "ta" ? "உடல் உறுப்புகள்" : "Governed Organs"}</th>
                    <th className="p-2 sm:p-2.5">{language === "ta" ? "ஆளும் கிரகம்" : "Ruler"}</th>
                    <th className="p-2 sm:p-2.5">{language === "ta" ? "ஜாதக நிலை" : "Status in Chart"}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F2F3F5]">
                  {birthChart.anatomical_mappings.map((m, idx) => (
                    <tr key={`anat-row-${idx}`} className="hover:bg-[#FAF8F2]/30">
                      <td className="p-2 sm:p-2.5 font-semibold text-[#183047]">
                        <span>{language === "ta" ? m.system_name_ta : m.system_name_en}</span>
                        <span className="block text-[10px] text-[#8190A6] font-normal">{m.sign_governance}</span>
                      </td>
                      <td className="p-2 sm:p-2.5 text-[#52667E] max-w-xs text-[11px]">
                        {language === "ta" ? m.organs_ta : m.organs_en}
                      </td>
                      <td className="p-2 sm:p-2.5 text-[11px] text-[#183047] font-mono">
                        {m.planetary_governance}
                      </td>
                      <td className="p-2 sm:p-2.5 text-[11px]">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold ${
                            m.status === "Mitigated"
                              ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                              : m.status === "Afflicted"
                              ? "bg-amber-50 text-amber-900 border border-amber-200"
                              : m.status === "Balanced"
                              ? "bg-blue-50 text-blue-900 border border-blue-200"
                              : "bg-slate-100 text-slate-700"
                          }`}
                        >
                          {m.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* PERSPECTIVE B: CURRENT PERIOD RESEARCH */}
      {/* ------------------------------------------------------------------- */}
      {activePerspective === "current" && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#F2F3F5] pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#153F6B]/10 flex items-center justify-center text-[#153F6B] shrink-0">
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-serif text-base font-bold text-[#183047]">
                    {language === "ta" ? "நடப்பு தசா–புத்தி–அந்தர கால ஆய்வு" : "Active Dasa–Bhukti–Antara Period"}
                  </h4>
                  <p className="text-xs text-[#8190A6]">
                    {language === "ta"
                      ? "விம்சோத்தரி தசா கணிப்பு முறையின்படி தற்போது செயல்படும் கிரக கால கட்டம்."
                      : "Verified temporal window based on the project's Vimshottari calculation engine."}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold bg-[#FAF2DE] text-[#8C6D23] px-3 py-1.5 rounded-lg border border-[#B4872B]/30">
                  {currentPeriod.mahadasha} - {currentPeriod.bhukti || "Dasa"} - {currentPeriod.antara || "Antara"}
                </span>
              </div>
            </div>

            {/* Non-Diagnostic Educational Synthesis */}
            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2">
              <span className="font-bold text-xs text-[#153F6B] block">
                {language === "ta" ? "காலக்கட்ட ஜோதிட விளக்கம்:" : "Astrological Period Synthesis:"}
              </span>
              <p className="text-xs text-[#52667E] leading-relaxed">
                {language === "ta" ? currentPeriod.traditional_synthesis_ta : currentPeriod.traditional_synthesis_en}
              </p>
            </div>

            {/* Matching Rules for Active Period */}
            {currentPeriod.matching_rules.length > 0 && (
              <div className="space-y-3 pt-2">
                <h5 className="font-bold text-xs text-[#183047]">
                  {language === "ta"
                    ? "நடப்பு தசா நாதர்களுக்கான பாரம்பரிய உடலமைப்பு விதிகள்"
                    : "Classical Health Governance of Active Period Rulers"}
                </h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {currentPeriod.matching_rules.map((rule) => (
                    <div
                      key={`curr-rule-${rule.id}`}
                      className="p-3.5 rounded-lg border border-[#D9DEE7] bg-white space-y-2"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-bold text-xs text-[#153F6B]">{language === "ta" ? rule.name_tamil : rule.name}</span>
                        <span className="text-[10px] text-[#B4872B] font-mono">{rule.source}</span>
                      </div>
                      <p className="text-[11px] text-[#52667E] leading-relaxed">
                        {language === "ta" ? rule.interpretation_tamil : rule.traditional_interpretation}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Verified Live Transits Overlay (if liveTransits is loaded) */}
            {currentPeriod.transits.length > 0 && (
              <div className="space-y-3 pt-3 border-t border-[#F2F3F5]">
                <div className="flex items-center justify-between">
                  <h5 className="font-bold text-xs text-[#183047] flex items-center gap-1.5">
                    <Radio className="w-3.5 h-3.5 text-[#B4872B] animate-pulse" />
                    <span>{language === "ta" ? "நேரலை கோசார கிரக நிலைகள் (லக்னத்திலிருந்து)" : "Verified Live Transits Relative to Natal Lagna"}</span>
                  </h5>
                  <span className="text-[10px] text-[#8190A6]">{language === "ta" ? "கோசாரம்" : "Ephemeris Live Data"}</span>
                </div>

                <div className="overflow-x-auto rounded-lg border border-[#E2E8F0]">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#FAF8F2] text-[#8C6D23] font-semibold border-b border-[#E2E8F0]">
                      <tr>
                        <th className="p-2">{language === "ta" ? "கிரகம்" : "Planet"}</th>
                        <th className="p-2">{language === "ta" ? "கோசார ராசி" : "Transit Sign"}</th>
                        <th className="p-2">{language === "ta" ? "லக்னத்திலிருந்து பாவம்" : "House from Lagna"}</th>
                        <th className="p-2 font-mono">{language === "ta" ? "பாகை" : "Degree"}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#F2F3F5]">
                      {currentPeriod.transits.map((t) => (
                        <tr key={`transit-row-${t.planet}`} className="hover:bg-[#FAF8F2]/30">
                          <td className="p-2 font-semibold text-[#183047] flex items-center gap-1">
                            <span>{t.planet}</span>
                            {t.is_retrograde && <span className="text-red-600 font-mono text-[9px] font-bold">(R)</span>}
                          </td>
                          <td className="p-2 text-[#52667E]">{language === "ta" ? t.sign_name_ta : t.sign_name_en}</td>
                          <td className="p-2 font-semibold text-[#8C6D23] font-mono">H{t.house_from_lagna}</td>
                          <td className="p-2 font-mono text-[#52667E]">{t.degree}°</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* PERSPECTIVE C: HISTORICAL PERIODS */}
      {/* ------------------------------------------------------------------- */}
      {activePerspective === "historical" && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-4">
            <div className="flex items-center gap-3 border-b border-[#F2F3F5] pb-4">
              <div className="w-10 h-10 rounded-full bg-[#153F6B]/10 flex items-center justify-center text-[#153F6B] shrink-0">
                <Calendar className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-serif text-base font-bold text-[#183047]">
                  {language === "ta" ? "வரலாற்று தசா காலக்கோடு ஆய்வு" : "Historical Astrological Period Research"}
                </h4>
                <p className="text-xs text-[#8190A6]">
                  {language === "ta"
                    ? "கடந்த கால மற்றும் நடப்பு விம்சோத்தரி தசா காலங்களின் பாரம்பரிய ஜோதிடக் குறிப்புகள் (நோய்களை உருவாக்காது)."
                    : "Traditional health-related planetary notes across past and present Vimshottari periods without illness inference."}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {historicalPeriods.periods.map((hp, idx) => (
                <div
                  key={`hist-period-${idx}`}
                  className="p-4 rounded-xl border border-[#D9DEE7] bg-white hover:border-[#B4872B] transition-all space-y-2"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-[#F2F3F5] pb-2">
                    <span className="font-bold text-xs text-[#153F6B] flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-[#B4872B]" />
                      <span>{hp.period_name}</span>
                    </span>
                    <span className="font-mono text-[11px] text-[#8190A6]">
                      {hp.age_range} • {hp.start_date_iso.slice(0, 10)} to {hp.end_date_iso.slice(0, 10)}
                    </span>
                  </div>

                  <p className="text-xs text-[#52667E] leading-relaxed">
                    {language === "ta" ? hp.traditional_notes_ta : hp.traditional_notes_en}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* KP ANALYTICAL SYSTEM VIEW */}
      {/* ------------------------------------------------------------------- */}
      {activePerspective === "kp" && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#F2F3F5] pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#153F6B]/10 flex items-center justify-center text-[#153F6B] shrink-0">
                  <Award className="w-5 h-5 text-[#B4872B]" />
                </div>
                <div>
                  <h4 className="font-serif text-base font-bold text-[#183047]">
                    {language === "ta" ? "கே.பி. மருத்துவ ஜோதிட ஆய்வு (KP Medical Astrology)" : "Krishnamurti Paddhati (KP) Medical System"}
                  </h4>
                  <p className="text-xs text-[#8190A6]">
                    {language === "ta"
                      ? "6-ம் பாவ உப அதிபதி (6th CSL), நட்சத்திர நாதர் மற்றும் 4 அடுக்கு காரகத்துவங்களின் அடிப்படையில்."
                      : "Based on KP 6th Cusp Sub-Lord (CSL), Star-Lord, and 4-tier house significators."}
                  </p>
                </div>
              </div>

              <span className="text-xs font-semibold text-[#153F6B] bg-[#F8FAFC] px-3 py-1.5 rounded-lg border border-[#D9DEE7] flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-[#B4872B]" />
                <span>{language === "ta" ? "KP Reader IV குறிப்பு கட்டமைப்பு" : "KP Reader IV reference framework"}</span>
              </span>
            </div>

            {kpData ? (
              <div className="space-y-5">
                {/* 6th CSL Highlight Box */}
                {(() => {
                  const c6 = kpData.sixth_csl;
                  return (
                    <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-r from-[#FAF8F2] to-white border border-[#D8BD80] space-y-4">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#EADBB8] pb-3">
                        <div>
                          <span className="font-bold text-xs text-[#8C6D23] uppercase tracking-wider block">
                            {language === "ta" ? "6-ம் பாவ உப அதிபதி (6th CSL) ஆய்வு" : "6th Cusp Sub-Lord (Primary Health Significator)"}
                          </span>
                          <span className="text-[11px] text-[#52667E]">
                            {language === "ta"
                              ? `6-ம் பாவ ஆரம்பம்: ${c6.cusp_degree ? `${c6.cusp_degree.toFixed(2)}°` : ""} ${c6.sign_name || ""} • 6-ம் பாவ நட்சத்திர நாதர்: ${c6.cusp_star_lord || "—"}`
                              : `Cusp 6: ${c6.cusp_degree ? `${c6.cusp_degree.toFixed(2)}°` : ""} ${c6.sign_name || ""} • Cusp 6 Star Lord: ${c6.cusp_star_lord || "—"}`}
                          </span>
                        </div>

                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono text-xs font-bold text-[#153F6B] bg-white px-2.5 py-1 rounded border border-[#D9DEE7]" title={language === "ta" ? "6-ம் பாவ உப அதிபதி" : "6th Cusp Sub-Lord"}>
                            {language === "ta" ? "6-ம் CSL:" : "6th CSL:"} <span className="text-[#102A4C]">{c6.csl_planet}</span>
                          </span>
                          <span className="font-mono text-xs font-bold text-[#B4872B] bg-white px-2.5 py-1 rounded border border-[#D9DEE7]" title={language === "ta" ? "CSL கிரகத்தின் நட்சத்திர நாதர்" : "Star Lord of CSL Planet"}>
                            {language === "ta" ? "CSL நட்சத்திர நாதர்:" : "CSL Star Lord:"} <span className="text-[#8C6D23]">{c6.csl_star_lord || c6.star_lord}</span>
                          </span>
                        </div>
                      </div>

                      {/* Missing data alert if calculation is incomplete */}
                      {!c6.is_data_available && (
                        <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                          <span>
                            {language === "ta"
                              ? `கணிப்புத் தரவு கிடைக்கவில்லை: ${c6.missing_data_reason || "தேவையான காரகத்துவ விவரங்கள் இல்லை"}`
                              : `Calculation data unavailable: ${c6.missing_data_reason || "Required significator inputs missing"}`}
                          </span>
                        </div>
                      )}

                      {/* Data-driven explanation with strict unresolved-placeholder defense */}
                      {(() => {
                        const rawExplanation = language === "ta" ? c6.primary_signification_ta : c6.primary_signification_en;
                        const cleanExplanation = (rawExplanation || "")
                          .replace(/\{csl\}/gi, c6.csl_planet || "CSL")
                          .replace(/\{csl_star_lord\}/gi, c6.csl_star_lord || c6.star_lord || "")
                          .replace(/\{cslStarL\}/gi, c6.csl_star_lord || c6.star_lord || "")
                          .replace(/\{star_lord\}/gi, c6.csl_star_lord || c6.star_lord || "")
                          .replace(/\{starLord\}/gi, c6.csl_star_lord || c6.star_lord || "")
                          .replace(/\{housesStr\}/gi, c6.signified_houses?.join(", ") || "");

                        return (
                          <p className="text-xs text-[#183047] leading-relaxed bg-white/70 p-3 rounded-lg border border-[#EADBB8]/50">
                            {cleanExplanation}
                          </p>
                        );
                      })()}

                      {/* 4 Category Status Evaluation Grid */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1 text-xs">
                        {/* 1. Recovery (1, 5, 11) */}
                        <div className={`p-3 rounded-xl border transition-all ${
                          c6.recovery_status === "present"
                            ? "bg-emerald-50/70 border-emerald-200 text-emerald-950"
                            : c6.recovery_status === "data_unavailable"
                            ? "bg-slate-50 border-slate-200 text-slate-600"
                            : "bg-white border-[#E2E8F0] text-slate-600"
                        }`}>
                          <div className="flex items-center justify-between pb-1 border-b border-black/5">
                            <span className="font-bold text-[11px] text-[#153F6B]">
                              {language === "ta" ? "குணமடைதல் (1, 5, 11)" : "Recovery (1, 5, 11)"}
                            </span>
                            {c6.recovery_status === "present" ? (
                              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                            ) : c6.recovery_status === "data_unavailable" ? (
                              <Info className="w-4 h-4 text-slate-400 shrink-0" />
                            ) : null}
                          </div>
                          <div className="mt-2 space-y-1">
                            <span className={`inline-block font-bold text-xs ${
                              c6.recovery_status === "present"
                                ? "text-emerald-700"
                                : c6.recovery_status === "data_unavailable"
                                ? "text-amber-700"
                                : "text-slate-500"
                            }`}>
                              {c6.recovery_status === "present"
                                ? (language === "ta" ? "காரகத்துவங்களில் உள்ளது" : "Present in calculated significations")
                                : c6.recovery_status === "data_unavailable"
                                ? (language === "ta" ? "கணிப்புத் தரவு கிடைக்கவில்லை" : "Calculation data unavailable")
                                : (language === "ta" ? "காரகத்துவங்களில் இல்லை" : "Not found in calculated significations")}
                            </span>
                            <span className="block text-[11px] text-[#52667E]">
                              {c6.recovery_status === "present"
                                ? (language === "ta" ? `குறிக்கப்படும் பாவங்கள்: [${c6.recovery_houses?.join(", ") || ""}]` : `Houses present: [${c6.recovery_houses?.join(", ") || ""}]`)
                                : c6.recovery_status === "data_unavailable"
                                ? (language === "ta" ? (c6.missing_data_reason || "விவரம் இல்லை") : (c6.missing_data_reason || "Missing inputs"))
                                : (language === "ta" ? "1, 5, 11 தொடர்பு அமையவில்லை" : "No 1, 5, 11 link in CSL dynamics")}
                            </span>
                          </div>
                        </div>

                        {/* 2. Disease / Acute Roga (6) */}
                        <div className={`p-3 rounded-xl border transition-all ${
                          c6.disease_status === "present"
                            ? "bg-amber-50/70 border-amber-200 text-amber-950"
                            : c6.disease_status === "data_unavailable"
                            ? "bg-slate-50 border-slate-200 text-slate-600"
                            : "bg-white border-[#E2E8F0] text-slate-600"
                        }`}>
                          <div className="flex items-center justify-between pb-1 border-b border-black/5">
                            <span className="font-bold text-[11px] text-[#153F6B]">
                              {language === "ta" ? "நோய் காரகம் (6)" : "Acute Roga (6)"}
                            </span>
                            {c6.disease_status === "present" ? (
                              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                            ) : c6.disease_status === "data_unavailable" ? (
                              <Info className="w-4 h-4 text-slate-400 shrink-0" />
                            ) : null}
                          </div>
                          <div className="mt-2 space-y-1">
                            <span className={`inline-block font-bold text-xs ${
                              c6.disease_status === "present"
                                ? "text-amber-700"
                                : c6.disease_status === "data_unavailable"
                                ? "text-amber-700"
                                : "text-slate-500"
                            }`}>
                              {c6.disease_status === "present"
                                ? (language === "ta" ? "காரகத்துவங்களில் உள்ளது" : "Present in calculated significations")
                                : c6.disease_status === "data_unavailable"
                                ? (language === "ta" ? "கணிப்புத் தரவு கிடைக்கவில்லை" : "Calculation data unavailable")
                                : (language === "ta" ? "காரகத்துவங்களில் இல்லை" : "Not found in calculated significations")}
                            </span>
                            <span className="block text-[11px] text-[#52667E]">
                              {c6.disease_status === "present"
                                ? (language === "ta" ? "6-ம் பாவம் குறிக்கப்படுகிறது (கவனம் தேவை)" : "House 6 signified (acute indication)")
                                : c6.disease_status === "data_unavailable"
                                ? (language === "ta" ? (c6.missing_data_reason || "விவரம் இல்லை") : (c6.missing_data_reason || "Missing inputs"))
                                : (language === "ta" ? "6-ம் பாவம் தொடர்பு இல்லை" : "House 6 not signified by CSL")}
                            </span>
                          </div>
                        </div>

                        {/* 3. Chronic / Surgical (8) */}
                        <div className={`p-3 rounded-xl border transition-all ${
                          c6.chronic_status === "present"
                            ? "bg-rose-50/70 border-rose-200 text-rose-950"
                            : c6.chronic_status === "data_unavailable"
                            ? "bg-slate-50 border-slate-200 text-slate-600"
                            : "bg-white border-[#E2E8F0] text-slate-600"
                        }`}>
                          <div className="flex items-center justify-between pb-1 border-b border-black/5">
                            <span className="font-bold text-[11px] text-[#153F6B]">
                              {language === "ta" ? "நீண்டகால / அறுவை (8)" : "Chronic / Surgical (8)"}
                            </span>
                            {c6.chronic_status === "present" ? (
                              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                            ) : c6.chronic_status === "data_unavailable" ? (
                              <Info className="w-4 h-4 text-slate-400 shrink-0" />
                            ) : null}
                          </div>
                          <div className="mt-2 space-y-1">
                            <span className={`inline-block font-bold text-xs ${
                              c6.chronic_status === "present"
                                ? "text-rose-700"
                                : c6.chronic_status === "data_unavailable"
                                ? "text-amber-700"
                                : "text-slate-500"
                            }`}>
                              {c6.chronic_status === "present"
                                ? (language === "ta" ? "காரகத்துவங்களில் உள்ளது" : "Present in calculated significations")
                                : c6.chronic_status === "data_unavailable"
                                ? (language === "ta" ? "கணிப்புத் தரவு கிடைக்கவில்லை" : "Calculation data unavailable")
                                : (language === "ta" ? "காரகத்துவங்களில் இல்லை" : "Not found in calculated significations")}
                            </span>
                            <span className="block text-[11px] text-[#52667E]">
                              {c6.chronic_status === "present"
                                ? (language === "ta" ? "8-ம் பாவம் குறிக்கப்படுகிறது (சகிப்புத்தன்மை தேவை)" : "House 8 signified (chronic factor)")
                                : c6.chronic_status === "data_unavailable"
                                ? (language === "ta" ? (c6.missing_data_reason || "விவரம் இல்லை") : (c6.missing_data_reason || "Missing inputs"))
                                : (language === "ta" ? "8-ம் பாவம் தொடர்பு இல்லை" : "House 8 not signified by CSL")}
                            </span>
                          </div>
                        </div>

                        {/* 4. Hospitalization (12) */}
                        <div className={`p-3 rounded-xl border transition-all ${
                          c6.hospitalization_status === "present"
                            ? "bg-purple-50/70 border-purple-200 text-purple-950"
                            : c6.hospitalization_status === "data_unavailable"
                            ? "bg-slate-50 border-slate-200 text-slate-600"
                            : "bg-white border-[#E2E8F0] text-slate-600"
                        }`}>
                          <div className="flex items-center justify-between pb-1 border-b border-black/5">
                            <span className="font-bold text-[11px] text-[#153F6B]">
                              {language === "ta" ? "மருத்துவமனை / ஓய்வு (12)" : "Hospitalization (12)"}
                            </span>
                            {c6.hospitalization_status === "present" ? (
                              <AlertTriangle className="w-4 h-4 text-purple-600 shrink-0" />
                            ) : c6.hospitalization_status === "data_unavailable" ? (
                              <Info className="w-4 h-4 text-slate-400 shrink-0" />
                            ) : null}
                          </div>
                          <div className="mt-2 space-y-1">
                            <span className={`inline-block font-bold text-xs ${
                              c6.hospitalization_status === "present"
                                ? "text-purple-700"
                                : c6.hospitalization_status === "data_unavailable"
                                ? "text-amber-700"
                                : "text-slate-500"
                            }`}>
                              {c6.hospitalization_status === "present"
                                ? (language === "ta" ? "காரகத்துவங்களில் உள்ளது" : "Present in calculated significations")
                                : c6.hospitalization_status === "data_unavailable"
                                ? (language === "ta" ? "கணிப்புத் தரவு கிடைக்கவில்லை" : "Calculation data unavailable")
                                : (language === "ta" ? "காரகத்துவங்களில் இல்லை" : "Not found in calculated significations")}
                            </span>
                            <span className="block text-[11px] text-[#52667E]">
                              {c6.hospitalization_status === "present"
                                ? (language === "ta" ? "12-ம் பாவம் குறிக்கப்படுகிறது (படுக்கை ஓய்வு)" : "House 12 signified (clinical care / rest)")
                                : c6.hospitalization_status === "data_unavailable"
                                ? (language === "ta" ? (c6.missing_data_reason || "விவரம் இல்லை") : (c6.missing_data_reason || "Missing inputs"))
                                : (language === "ta" ? "12-ம் பாவம் தொடர்பு இல்லை" : "House 12 not signified by CSL")}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Significator Sources Provenance Table */}
                      {c6.signification_details && c6.signification_details.length > 0 && (
                        <div className="space-y-2 pt-2 border-t border-[#EADBB8]/60">
                          <span className="font-bold text-[11px] text-[#183047] flex items-center gap-1.5">
                            <Layers className="w-3.5 h-3.5 text-[#B4872B]" />
                            <span>
                              {language === "ta"
                                ? `6-ம் CSL ${c6.csl_planet} குறிக்கும் பாவங்களின் ஆதாரம் மற்றும் நிலை விவரம்`
                                : `Calculated House Significations & Derivation for 6th CSL (${c6.csl_planet})`}
                            </span>
                          </span>

                          <div className="overflow-x-auto rounded-lg border border-[#E2E8F0]">
                            <table className="w-full text-left text-xs">
                              <thead className="bg-[#FAF8F2] text-[#8C6D23] font-semibold border-b border-[#E2E8F0]">
                                <tr>
                                  <th className="p-2 w-16">{language === "ta" ? "பாவம்" : "House"}</th>
                                  <th className="p-2 w-28">{language === "ta" ? "காரக முறை" : "Mechanism"}</th>
                                  <th className="p-2 w-36">{language === "ta" ? "கிரக வழிமுறை" : "Planet Agency"}</th>
                                  <th className="p-2">{language === "ta" ? "காரக நிலை & விளக்கம்" : "Significator Level & Derivation"}</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-[#F2F3F5] bg-white">
                                {c6.signification_details.map((d, dIdx) => (
                                  <tr key={`sig-detail-${dIdx}`} className="hover:bg-[#FAF8F2]/30">
                                    <td className="p-2 font-mono font-bold text-[#153F6B]">H{d.house}</td>
                                    <td className="p-2">
                                      <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-100 text-slate-700">
                                        {d.source_type}
                                      </span>
                                    </td>
                                    <td className="p-2">
                                      <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-mono bg-amber-50 text-amber-800 border border-amber-200">
                                        {d.planet_channel || c6.csl_planet}
                                      </span>
                                    </td>
                                    <td className="p-2 text-[#52667E]">
                                      <span className="font-semibold text-[#183047] block text-[11px]">
                                        {language === "ta" ? d.level_name_ta : d.level_name_en}
                                      </span>
                                      <span className="text-[10px] text-slate-500">
                                        {language === "ta" ? d.description_ta : d.description_en}
                                      </span>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>

                          <p className="text-[10px] text-[#8190A6] italic leading-normal">
                            {language === "ta"
                              ? `* குறிப்பு: ஒரே பாவம் பல நிலைகளில் (எ.கா. நேரடி பாவக அமர்வு மற்றும் நட்சத்திர நாதர் தொடர்பு) குறிக்கப்படும் போது, முழுமையான ஆய்வு ஆதாரத்திற்காக ஒவ்வொரு நிலையும் தனித்தனியாக அட்டவணையில் காட்டப்பட்டுள்ளது; காரக பாவங்களின் தொகுப்பில் [${c6.signified_houses?.join(", ") || ""}] என ஒருங்கிணைக்கப்பட்டுள்ளது.`
                              : `* Note: When a house is signified through multiple distinct mechanisms (e.g., direct placement and star lord agency), each channel is preserved individually in this provenance table, while consolidated as deduplicated houses [${c6.signified_houses?.join(", ") || ""}] in the analytical summary.`}
                          </p>
                        </div>
                      )}

                      <div className="text-[10px] text-[#8190A6] flex items-center justify-between pt-1">
                        <span>{c6.calculation_provenance}</span>
                        <span className="font-mono">{language === "ta" ? "ஆய்வு நோக்கம் மட்டுமே" : "Educational Research Model"}</span>
                      </div>
                    </div>
                  );
                })()}

                {/* KP Rules Triggered */}
                <div className="space-y-3">
                  <h5 className="font-bold text-xs text-[#183047] flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#B4872B]" />
                    <span>{language === "ta" ? "கே.பி. வாசகர் IV குறிப்பு விதிகளின் நிலை" : "KP Reader IV Reference Rules Evaluated"}</span>
                  </h5>
                  <div className="space-y-2.5">
                    {kpData.kp_rules.map((rule) => (
                      <div
                        key={`kp-rule-${rule.id}`}
                        className="p-3.5 rounded-lg border border-[#D9DEE7] bg-white space-y-1.5"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-bold text-xs text-[#153F6B]">{language === "ta" ? rule.name_tamil : rule.name}</span>
                          <span className="text-[10px] text-[#B4872B] font-mono">{rule.source}</span>
                        </div>
                        <p className="text-xs text-[#52667E] leading-relaxed">
                          {language === "ta" ? rule.interpretation_tamil : rule.traditional_interpretation}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-[#8190A6]">
                {language === "ta"
                  ? "கே.பி. கணிப்பு முடிவுகள் கிடைக்கவில்லை."
                  : "KP calculations are not available for this record."}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Rule Detail Inspection Modal */}
      {selectedRule && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-5 sm:p-6 shadow-xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between gap-3 border-b border-[#F2F3F5] pb-3">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#B4872B] block">
                  {selectedRule.category} • {selectedRule.system.toUpperCase()}
                </span>
                <h3 className="font-serif text-base sm:text-lg font-bold text-[#183047] mt-0.5">
                  {language === "ta" ? selectedRule.name_tamil : selectedRule.name}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedRule(null)}
                className="w-8 h-8 rounded-full bg-[#F2F3F5] hover:bg-[#E2E8F0] flex items-center justify-center text-[#52667E] transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[#8190A6] font-semibold block">{language === "ta" ? "மூல நூல் ஆதாரம்:" : "Classical Authority:"}</span>
                <span className="font-mono text-[#183047] font-bold">{selectedRule.source} ({selectedRule.chapter_verse})</span>
              </div>

              <div>
                <span className="text-[#8190A6] font-semibold block">{language === "ta" ? "பாரம்பரிய விளக்கம்:" : "Traditional Interpretation:"}</span>
                <p className="text-[#183047] leading-relaxed mt-0.5">
                  {language === "ta" ? selectedRule.interpretation_tamil : selectedRule.traditional_interpretation}
                </p>
              </div>

              <div>
                <span className="text-[#8190A6] font-semibold block">{language === "ta" ? "உடல் உறுப்பு மண்டலம்:" : "Anatomical Rulership:"}</span>
                <span className="text-[#153F6B] font-medium">{selectedRule.anatomical_system}</span>
              </div>

              <div>
                <span className="text-[#8190A6] font-semibold block">{language === "ta" ? "தூண்டிய கிரக நிலை:" : "Triggered Placement in Chart:"}</span>
                <ul className="list-disc pl-5 text-[#52667E] space-y-0.5">
                  {selectedRule.triggered_positions.map((tp, idx) => (
                    <li key={`trig-pos-${idx}`}>{tp}</li>
                  ))}
                </ul>
              </div>

              {selectedRule.conflicting_indications && (
                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-950 text-[11px] space-y-1">
                  <span className="font-bold block">{language === "ta" ? "சமன்செய்யும் விதி / பாதுகாப்பு:" : "Classical Mitigation / Arishta Bhanga:"}</span>
                  <p>{selectedRule.conflicting_indications}</p>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-[#F2F3F5] flex justify-end">
              <button
                type="button"
                onClick={() => setSelectedRule(null)}
                className="px-4 py-2 rounded-lg bg-[#153F6B] text-white font-bold text-xs hover:bg-[#0F3155] transition-colors cursor-pointer"
              >
                {language === "ta" ? "மூடுக" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
