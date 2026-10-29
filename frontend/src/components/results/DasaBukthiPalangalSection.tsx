"use client";

import React, { useState, useMemo, useEffect } from "react";
import {
  HoroscopeResponse,
  DasaResponse,
  ShadbalaResponse,
  AshtakavargaResponse,
  FullHoroscopeResult,
  LiveTransitsResponse,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getLordName, getGrahaShort } from "@/lib/translations";
import {
  analyzeDasaBukthiPalangal,
  DasaBukthiAnalysis,
  ZODIAC_SIGNS_EN,
  ZODIAC_SIGNS_TA,
} from "@/lib/dasa-bukthi-palangal";
import {
  analyzeGkTransits,
  GkTransitAnalysisResult,
} from "@/lib/gk-transit-engine";
import { GkTransitMatchingCard } from "@/components/results/GkTransitMatchingCard";
import { Recent15DayPastEventsCard } from "@/components/results/Recent15DayPastEventsCard";
import { MarcBoneyMilestonesCard } from "@/components/results/MarcBoneyMilestonesCard";
import {
  Sparkles,
  Calendar,
  Clock,
  Compass,
  Award,
  ShieldAlert,
  ShieldCheck,
  Briefcase,
  Coins,
  Heart,
  Baby,
  Sun,
  Moon,
  ChevronRight,
  Flame,
  CheckCircle2,
  AlertTriangle,
  Info,
  Layers,
  ArrowRight,
  Filter,
  Check,
  RefreshCw,
  BookOpen,
  TrendingUp,
  ThumbsUp,
  Activity,
  Radio,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface DasaBukthiPalangalSectionProps {
  horoscope: HoroscopeResponse;
  dasa?: DasaResponse;
  shadbala?: ShadbalaResponse;
  ashtakavarga?: AshtakavargaResponse;
  birthDate?: string;
  birthTime?: string;
  timezone?: string;
  onNavigateToTab?: (tab: string) => void;
  liveTransits?: LiveTransitsResponse | null;
  isLoadingTransits?: boolean;
  onFetchTransits?: () => void;
}

const MAHADASHAS_ORDER = [
  "Ketu",
  "Venus",
  "Sun",
  "Moon",
  "Mars",
  "Rahu",
  "Jupiter",
  "Saturn",
  "Mercury",
];

export function DasaBukthiPalangalSection({
  horoscope,
  dasa,
  shadbala,
  ashtakavarga,
  birthDate,
  birthTime,
  timezone,
  onNavigateToTab,
  liveTransits,
  isLoadingTransits = false,
  onFetchTransits,
}: DasaBukthiPalangalSectionProps) {
  const { language } = useLanguage();
  const isTa = language === "ta";
  const [showTransitMatching, setShowTransitMatching] = useState<boolean>(false);
  const [showMilestones, setShowMilestones] = useState<boolean>(false);

  // Active Dasha, Bhukti, and Andhara detection
  const nowJd = useMemo(() => Date.now() / 86400000 + 2440587.5, []);

  const activePeriods = useMemo(() => {
    if (!dasa?.dasa_tree) return { maha: "Sun", antar: "Sun", andhar: "Sun" };

    const activeMaha =
      dasa.dasa_tree.find((m) => m.start_jd <= nowJd && nowJd < m.end_jd) ||
      dasa.dasa_tree[0];
    const mahaLord = activeMaha?.lord || "Sun";

    let antarLord = mahaLord;
    let activeAntar = null;
    if (activeMaha?.sub_periods && activeMaha.sub_periods.length > 0) {
      activeAntar =
        activeMaha.sub_periods.find(
          (b) => b.start_jd <= nowJd && nowJd < b.end_jd
        ) || activeMaha.sub_periods[0];
      if (activeAntar) antarLord = activeAntar.lord;
    }

    let andharLord = antarLord;
    if (activeAntar?.sub_periods && activeAntar.sub_periods.length > 0) {
      const activeAndhar =
        activeAntar.sub_periods.find(
          (a) => a.start_jd <= nowJd && nowJd < a.end_jd
        ) || activeAntar.sub_periods[0];
      if (activeAndhar) andharLord = activeAndhar.lord;
    }

    return { maha: mahaLord, antar: antarLord, andhar: andharLord };
  }, [dasa, nowJd]);

  // Selected state for browsing 3 levels: Mahadasha, Bhukti, and Andhara
  const [selectedMaha, setSelectedMaha] = useState<string>(activePeriods.maha);
  const [selectedAntar, setSelectedAntar] = useState<string>(activePeriods.antar);
  const [selectedAndhar, setSelectedAndhar] = useState<string>(activePeriods.andhar);
  const [levelMode, setLevelMode] = useState<"dasa-bukthi" | "dasa-bukthi-andhara">("dasa-bukthi-andhara");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  // Keep in sync with active periods when dasa changes
  useEffect(() => {
    if (activePeriods.maha) {
      setSelectedMaha(activePeriods.maha);
      setSelectedAntar(activePeriods.antar);
      setSelectedAndhar(activePeriods.andhar);
    }
  }, [activePeriods.maha, activePeriods.antar, activePeriods.andhar]);

  // Antardashas available under selected Mahadasha
  const availableBhuktis = useMemo(() => {
    if (!selectedMaha) return MAHADASHAS_ORDER;
    const sIdx = MAHADASHAS_ORDER.indexOf(selectedMaha);
    if (sIdx === -1) return MAHADASHAS_ORDER;
    const ordered: string[] = [];
    for (let i = 0; i < 9; i++) {
      ordered.push(MAHADASHAS_ORDER[(sIdx + i) % 9]);
    }
    return ordered;
  }, [selectedMaha]);

  // Full Analysis Result (with 3-tier Andhara analysis)
  const analysis: DasaBukthiAnalysis | null = useMemo(() => {
    if (!dasa || !horoscope) return null;
    return analyzeDasaBukthiPalangal(
      horoscope,
      dasa,
      selectedMaha,
      selectedAntar,
      selectedAndhar,
      shadbala,
      ashtakavarga,
      birthDate,
      birthTime,
      timezone
    );
  }, [
    horoscope,
    dasa,
    selectedMaha,
    selectedAntar,
    selectedAndhar,
    shadbala,
    ashtakavarga,
    birthDate,
    birthTime,
    timezone,
  ]);

  if (!dasa || !horoscope || !analysis) {
    return (
      <div className="p-8 rounded-xl border border-amber-200 bg-amber-50/50 text-center space-y-3">
        <Sparkles className="w-8 h-8 text-amber-600 mx-auto animate-pulse" />
        <h3 className="text-base font-bold text-[#183047]">
          {isTa
            ? "தசா புத்தி கணிப்புகள் ஏற்றப்படுகின்றன..."
            : "Calculating Dasa Bukthi Predictions..."}
        </h3>
        <p className="text-xs text-[#52667E]">
          {isTa
            ? "ஜாதகத்தின் தசா புத்தி அமைப்புகள் சாஸ்திர விதிகளின்படி பகுப்பாய்வு செய்யப்படுகின்றன."
            : "Vedic planetary positions and Dasa hierarchies are being aligned according to classical rules."}
        </p>
      </div>
    );
  }

  const isCurrentActive =
    selectedMaha === activePeriods.maha &&
    selectedAntar === activePeriods.antar &&
    selectedAndhar === activePeriods.andhar;

  const currentPositiveScore =
    levelMode === "dasa-bukthi"
      ? analysis.dasaBukthiPositiveScore
      : analysis.andharaPositiveScore;

  const currentCautionScore = 100 - currentPositiveScore;

  // Tirupur GK Live Transit Analysis matched with this saved horoscope
  const transitAnalysis: GkTransitAnalysisResult | null = useMemo(() => {
    if (!liveTransits?.planets || liveTransits.planets.length === 0) return null;
    return analyzeGkTransits(
      horoscope.planets || [],
      liveTransits.planets,
      selectedMaha,
      selectedAntar,
      levelMode === "dasa-bukthi-andhara" ? selectedAndhar : undefined,
      currentPositiveScore
    );
  }, [
    liveTransits,
    horoscope.planets,
    selectedMaha,
    selectedAntar,
    selectedAndhar,
    levelMode,
    currentPositiveScore,
  ]);

  const dasaConfluence = transitAnalysis?.dasaConfluence;
  const confluencePositiveScore = dasaConfluence
    ? dasaConfluence.combinedAdjustedScore
    : currentPositiveScore;

  return (
    <div className="space-y-6">
      {/* 1. Header Banner with Attribution to Mantreswara & Krishan Kant Bhardwaj */}
      <div className="relative overflow-hidden rounded-2xl border border-[#B4872B]/30 bg-gradient-to-r from-[#153F6B] via-[#102d4d] to-[#183047] text-white p-6 shadow-sm">
        <div className="absolute top-0 right-0 -mt-4 -mr-4 w-40 h-40 bg-[#B4872B]/10 rounded-full blur-2xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#B4872B]/20 border border-[#B4872B]/40 text-[#f5d78a] text-[11px] font-bold tracking-wide">
              <Sparkles className="w-3.5 h-3.5" />
              <span>
                {isTa
                  ? "மந்த்ரேஸ்வரரின் பலதீபிகை & விம்சோத்தரி தசா முறை"
                  : "Mantreswara's Phaladeepika & Vimshottari Dasha System"}
              </span>
            </div>
            <h2 className="text-xl md:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <span>{isTa ? "தசா புத்தி பலன்கள்" : "Dasa Bukthi Palangal"}</span>
              <span className="text-xs px-2.5 py-0.5 rounded bg-white/10 text-amber-200 border border-white/20 font-medium">
                {levelMode === "dasa-bukthi"
                  ? isTa
                    ? "2 அடுக்கு: மகா திசை – புக்தி"
                    : "2-Tier: Mahadasha – Bhukti"
                  : isTa
                  ? "3 அடுக்கு: மகா திசை – புக்தி – அந்திரம்"
                  : "3-Tier: Dasa – Bhukti – Andhara"}
              </span>
            </h2>
            <p className="text-xs text-white/80 max-w-2xl leading-relaxed">
              {isTa
                ? "மகா திசா நாதன், புக்தி நாதன் மற்றும் அந்திர நாதனின் ஷட்பலம், அஷ்டகவர்க்க பரல்கள், தார பலம், கிரக அச்சு மற்றும் சூரிய பெயர்ச்சி கால நிர்ணயத்துடன் கூடிய துல்லியமான சாஸ்திர பலன்கள்."
                : "Precise classical timing evaluating Mahadasha, Antardasha (Bhukti), and Pratyantardasha (Andhara) lord strengths, Shadbala, Ashtakavarga bindus, mutual distance, and Sun transit manifestations."}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row md:flex-col items-start md:items-end gap-2 shrink-0">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 border border-white/15 backdrop-blur-sm text-xs">
              <span className="text-amber-200 font-medium">
                {isTa ? "இப்போது நடக்கும் காலம்:" : "Currently Running:"}
              </span>
              <span className="font-bold text-white">
                {getLordName(activePeriods.maha, language)} –{" "}
                {getLordName(activePeriods.antar, language)}
                {levelMode === "dasa-bukthi-andhara" && (
                  <span> – {getLordName(activePeriods.andhar, language)}</span>
                )}
              </span>
            </div>

            {!isCurrentActive && (
              <button
                type="button"
                onClick={() => {
                  setSelectedMaha(activePeriods.maha);
                  setSelectedAntar(activePeriods.antar);
                  setSelectedAndhar(activePeriods.andhar);
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white text-xs font-bold transition-all shadow-xs cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>
                  {isTa ? "தற்போதைய காலத்திற்கு செல்ல" : "Jump to Active Period"}
                </span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 1b. Recent 15-Day Past Events Flashback & Client Verification */}
      <Recent15DayPastEventsCard
        horoscope={horoscope}
        dasa={dasa}
        liveTransits={liveTransits}
        defaultExpanded={true}
      />

      {/* 2. Interactive Navigator with Level Mode Switcher */}
      <div className="rounded-xl border border-[#D9DEE7] bg-white p-4 shadow-2xs space-y-4">
        {/* Level Mode Switcher */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#D9DEE7]">
          <div>
            <div className="text-xs font-bold text-[#183047] uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-[#B4872B]" />
              <span>{isTa ? "கணிப்பு அடுக்கு நிலை (Depth Level)" : "Calculation Depth Level"}</span>
            </div>
            <div className="text-[11px] text-[#52667E]">
              {isTa
                ? "2 அடுக்கு (திசா-புக்தி) அல்லது 3 அடுக்கு (அந்திரம் வரை) தேர்வு செய்து சுப சதவீதத்தைக் காண்க"
                : "Select 2-Tier (Dasa-Bhukti) or 3-Tier (Till Andhara) to view positive percentage"}
            </div>
          </div>

          <div className="inline-flex rounded-xl p-1 bg-[#F1F5F9] border border-[#E2E8F0]">
            <button
              type="button"
              onClick={() => setLevelMode("dasa-bukthi")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                levelMode === "dasa-bukthi"
                  ? "bg-[#153F6B] text-white shadow-xs"
                  : "text-[#52667E] hover:text-[#183047]"
              }`}
            >
              {isTa ? "1. திசா + புக்தி (2 நிலைகள்)" : "1. Dasa + Bhukti (2 Levels)"}
            </button>
            <button
              type="button"
              onClick={() => setLevelMode("dasa-bukthi-andhara")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                levelMode === "dasa-bukthi-andhara"
                  ? "bg-[#B4872B] text-white shadow-xs"
                  : "text-[#52667E] hover:text-[#183047]"
              }`}
            >
              {isTa ? "2. திசா + புக்தி + அந்திரம் (3 நிலைகள்)" : "2. Dasa + Bhukti + Andhara (3 Levels)"}
            </button>
          </div>
        </div>

        {/* Step A: Select Mahadasha */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-bold text-[#183047] uppercase tracking-wider flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full bg-[#153F6B] text-white text-[10px] inline-flex items-center justify-center font-bold">1</span>
              <span>{isTa ? "மகா திசை தேர்வு செய்க" : "Select Mahadasha"}</span>
            </label>
            <span className="text-[11px] text-[#52667E]">
              {isTa ? "விம்சோத்தரி 9 திசைகள்" : "9 Vimshottari Lords"}
            </span>
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-1.5">
            {MAHADASHAS_ORDER.map((lord) => {
              const isSelected = selectedMaha === lord;
              const isRunning = activePeriods.maha === lord;
              return (
                <button
                  key={lord}
                  type="button"
                  onClick={() => {
                    setSelectedMaha(lord);
                    setSelectedAntar(lord);
                    setSelectedAndhar(lord);
                  }}
                  className={`p-2 rounded-lg border text-center transition-all cursor-pointer relative ${
                    isSelected
                      ? "border-[#153F6B] bg-[#153F6B] text-white shadow-xs font-bold"
                      : isRunning
                      ? "border-amber-400 bg-amber-50 text-[#153F6B] font-semibold hover:bg-amber-100"
                      : "border-[#D9DEE7] bg-[#F8FAFC] hover:bg-white text-[#183047]"
                  }`}
                >
                  <div className="text-xs truncate">{getLordName(lord, language)}</div>
                  <div className="text-[10px] opacity-75">{getGrahaShort(lord, language)}</div>
                  {isRunning && (
                    <span
                      className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full ${
                        isSelected ? "bg-amber-400" : "bg-emerald-500 animate-pulse"
                      }`}
                      title={isTa ? "தற்போது நடக்கும் திசை" : "Currently Active"}
                    />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Step B: Select Antardasha (Bhukti) */}
        <div className="pt-2 border-t border-[#D9DEE7]/70">
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-bold text-[#183047] uppercase tracking-wider flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full bg-[#B4872B] text-white text-[10px] inline-flex items-center justify-center font-bold">2</span>
              <span>
                {isTa
                  ? `${getLordName(selectedMaha, language)} மகா திசையில் புக்தி தேர்வு செய்க`
                  : `Select Antardasha (Bhukti) under ${selectedMaha}`}
              </span>
            </label>
            <span className="text-[11px] text-[#52667E]">
              {isTa ? "9 உப காலங்கள்" : "9 Sub-periods"}
            </span>
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-1.5">
            {availableBhuktis.map((bLord) => {
              const isSelected = selectedAntar === bLord;
              const isRunning =
                activePeriods.maha === selectedMaha && activePeriods.antar === bLord;
              return (
                <button
                  key={bLord}
                  type="button"
                  onClick={() => {
                    setSelectedAntar(bLord);
                    setSelectedAndhar(bLord);
                  }}
                  className={`p-2 rounded-lg border text-center transition-all cursor-pointer relative ${
                    isSelected
                      ? "border-[#B4872B] bg-[#B4872B] text-white shadow-xs font-bold"
                      : isRunning
                      ? "border-emerald-500 bg-emerald-50 text-emerald-900 font-semibold hover:bg-emerald-100"
                      : "border-[#D9DEE7] bg-[#F8FAFC] hover:bg-white text-[#183047]"
                  }`}
                >
                  <div className="text-xs truncate">{getLordName(bLord, language)}</div>
                  <div className="text-[10px] opacity-75">{isTa ? "புக்தி" : "Bhukti"}</div>
                  {isRunning && (
                    <span
                      className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full ${
                        isSelected ? "bg-white" : "bg-emerald-500 animate-pulse"
                      }`}
                      title={isTa ? "தற்போது நடக்கும் புக்தி" : "Currently Active"}
                    />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Step C: Select Pratyantardasha (Andhara) - shown in 3-tier mode */}
        {levelMode === "dasa-bukthi-andhara" ? (
          <div className="pt-2 border-t border-[#D9DEE7]/70">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold text-[#183047] uppercase tracking-wider flex items-center gap-1.5">
                <span className="w-4 h-4 rounded-full bg-amber-700 text-white text-[10px] inline-flex items-center justify-center font-bold">3</span>
                <span>
                  {isTa
                    ? `${getLordName(selectedAntar, language)} புக்தியில் அந்திரம் (Pratyantar) தேர்வு செய்க`
                    : `Select Andhara (Pratyantardasha) under ${selectedAntar}`}
                </span>
              </label>
              <span className="text-[11px] text-[#52667E]">
                {isTa ? "9 அந்திர காலங்கள் (3-ஆம் அடுக்கு)" : "9 Andhara Periods (Level 3)"}
              </span>
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-1.5">
              {analysis.availableAndharas.map((aItem) => {
                const isSelected = selectedAndhar === aItem.lord;
                const isRunning =
                  activePeriods.maha === selectedMaha &&
                  activePeriods.antar === selectedAntar &&
                  activePeriods.andhar === aItem.lord;
                return (
                  <button
                    key={aItem.lord}
                    type="button"
                    onClick={() => setSelectedAndhar(aItem.lord)}
                    className={`p-2 rounded-lg border text-center transition-all cursor-pointer relative ${
                      isSelected
                        ? "border-amber-700 bg-amber-700 text-white shadow-xs font-bold"
                        : isRunning
                        ? "border-emerald-500 bg-emerald-50 text-emerald-900 font-semibold hover:bg-emerald-100"
                        : "border-[#D9DEE7] bg-[#F8FAFC] hover:bg-white text-[#183047]"
                    }`}
                  >
                    <div className="text-xs truncate">{getLordName(aItem.lord, language)}</div>
                    <div className="text-[10px] opacity-75">{isTa ? "அந்திரம்" : "Andhara"}</div>
                    {isRunning && (
                      <span
                        className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full ${
                          isSelected ? "bg-white" : "bg-emerald-500 animate-pulse"
                        }`}
                        title={isTa ? "தற்போது நடக்கும் அந்திரம்" : "Currently Active"}
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="pt-2 border-t border-[#D9DEE7]/70 flex items-center justify-between text-xs text-[#52667E]">
            <span>
              {isTa
                ? `தற்போது 2 அடுக்கு திசா-புக்தி பலன் கணக்கிடப்படுகிறது.`
                : `Currently showing 2-tier Dasa-Bhukti baseline calculation.`}
            </span>
            <button
              type="button"
              onClick={() => setLevelMode("dasa-bukthi-andhara")}
              className="text-[#B4872B] hover:text-[#8C6D23] font-bold inline-flex items-center gap-1 cursor-pointer"
            >
              <span>{isTa ? "3-ஆம் அடுக்கு அந்திரம் பலன் சேர்க்க ➔" : "Add 3-Tier Andhara Level ➔"}</span>
            </button>
          </div>
        )}
      </div>

      {/* 3. Overview Card of Currently Selected Dasha-Bhukti-Andhara */}
      <div className="rounded-2xl border border-[#D9DEE7] bg-white p-5 shadow-2xs space-y-4">
        {/* Title Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#D9DEE7]">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-lg font-bold text-[#153F6B]">
                {getLordName(analysis.mahadashaLord, language)} {isTa ? "மகா திசை" : "Mahadasha"}
              </span>
              <span className="text-gray-400 font-bold">/</span>
              <span className="text-lg font-bold text-[#B4872B]">
                {getLordName(analysis.antardashaLord, language)} {isTa ? "புக்தி" : "Bhukti"}
              </span>
              {levelMode === "dasa-bukthi-andhara" && (
                <>
                  <span className="text-gray-400 font-bold">/</span>
                  <span className="text-lg font-bold text-amber-700">
                    {getLordName(analysis.pratyantardashaLord, language)} {isTa ? "அந்திரம்" : "Andhara"}
                  </span>
                </>
              )}
              {analysis.isActiveNow && (
                <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 text-[11px] font-bold inline-flex items-center gap-1 animate-pulse">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                  {isTa ? "இப்போது நடப்பில் உள்ளது" : "Active Period Now"}
                </span>
              )}
            </div>
            <p className="text-xs text-[#52667E] italic">"{analysis.summaryQuoteTa || analysis.summaryQuoteEn}"</p>
          </div>

          <div className="flex items-center gap-2">
            <span className={`px-3 py-1.5 rounded-lg border text-xs font-bold ${analysis.verdictBadgeClass}`}>
              {isTa ? analysis.verdictLabelTa : analysis.verdictLabelEn}
            </span>
          </div>
        </div>

        {/* Dynamic Positive % Gauge Card */}
        <div className="p-4 rounded-xl border border-emerald-200 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50/70 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-emerald-600 text-white shadow-2xs">
                  <TrendingUp className="w-4 h-4" />
                </span>
                <span className="text-xs font-bold text-emerald-950 uppercase tracking-wide">
                  {levelMode === "dasa-bukthi"
                    ? isTa
                      ? "திசா - புக்தி சுப பலன் சதவீதம் (Dasa-Bhukti Positive %)"
                      : "Dasa + Bhukti Net Positive Ratio"
                    : isTa
                    ? "3-அடுக்கு கூட்டு சுப பலன் சதவீதம் (Dasa-Bhukti-Andhara Positive %)"
                    : "3-Tier (Till Andhara) Net Positive Ratio"}
                </span>
              </div>
              <p className="text-xs text-emerald-800/90 mt-1">
                {levelMode === "dasa-bukthi"
                  ? isTa
                    ? `${getLordName(analysis.mahadashaLord, language)} திசா நாதன் மற்றும் ${getLordName(analysis.antardashaLord, language)} புக்தி நாதனின் ஷட்பலம், அஷ்டகவர்க்கம், அவஸ்தை & கிரக அச்சு அடிப்படையில் கணக்கிடப்பட்டது.`
                    : `Evaluated strictly from ${analysis.mahadashaLord} Dasa & ${analysis.antardashaLord} Bhukti lord strengths, Shadbala, Ashtakavarga, and mutual axis.`
                  : isTa
                  ? `${getLordName(analysis.pratyantardashaLord, language)} அந்திர தூண்டுதல் சேர்க்கப்பட்டு கணக்கிடப்பட்ட துல்லியமான கூட்டு பலன்.`
                  : `Combined 3-tier matrix incorporating the specific Pratyantar catalyst of ${analysis.pratyantardashaLord}.`}
              </p>
            </div>

            <div className="flex items-baseline gap-3 shrink-0">
              <div className="text-right">
                <div className="text-2xl sm:text-3xl font-extrabold text-emerald-700">
                  {currentPositiveScore}%
                </div>
                <div className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider">
                  {isTa ? "நற்பலன் (Positive)" : "Positive Ratio"}
                </div>
              </div>
              <div className="h-8 w-[1px] bg-emerald-200" />
              <div className="text-right">
                <div className="text-xl sm:text-2xl font-bold text-amber-700">
                  {currentCautionScore}%
                </div>
                <div className="text-[10px] font-bold text-amber-800 uppercase tracking-wider">
                  {isTa ? "கவனம் (Caution)" : "Caution / Alerts"}
                </div>
              </div>
            </div>
          </div>

          {/* Dual-color Progress Split Bar */}
          <div className="space-y-1">
            <div className="w-full h-3 rounded-full bg-amber-200/80 overflow-hidden flex shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-emerald-600 via-teal-500 to-emerald-500 transition-all duration-700"
                style={{ width: `${currentPositiveScore}%` }}
                title={`${isTa ? "சுபத்தன்மை:" : "Positive:"} ${currentPositiveScore}%`}
              />
              <div
                className="h-full bg-gradient-to-r from-amber-400 to-rose-400 transition-all duration-700"
                style={{ width: `${currentCautionScore}%` }}
                title={`${isTa ? "கவனிக்க வேண்டியவை:" : "Caution:"} ${currentCautionScore}%`}
              />
            </div>
            <div className="flex justify-between text-[10px] text-[#52667E] font-medium">
              <span className="text-emerald-700 font-bold">● {isTa ? "சுப யோக வாய்ப்புகள்:" : "Auspicious Opportunities:"} {currentPositiveScore}%</span>
              {levelMode === "dasa-bukthi-andhara" && (
                <span className="text-[#153F6B] font-semibold">
                  ({isTa ? "அடிப்படை திசா-புக்தி பலன்:" : "Baseline Dasa-Bhukti:"} {analysis.dasaBukthiPositiveScore}%)
                </span>
              )}
              <span className="text-amber-800 font-bold">● {isTa ? "கவனிக்க வேண்டியவை:" : "Care Required:"} {currentCautionScore}%</span>
            </div>
          </div>

          {/* Live Transit (Gochara) Confluence Pill & Toggle */}
          {dasaConfluence ? (
            <div className="pt-3 border-t border-emerald-200/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#153F6B] text-white text-[10px] font-bold">
                    <Radio className="w-3 h-3 text-amber-400 animate-pulse" />
                    <span>{isTa ? "நேரலை கோச்சார சங்கமம்" : "Live Transit Confluence"}</span>
                  </span>
                  <span
                    className={`text-xs font-bold px-2 py-0.5 rounded-md ${
                      dasaConfluence.transitScoreModifier >= 0
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {dasaConfluence.transitScoreModifier >= 0
                      ? `+${dasaConfluence.transitScoreModifier}%`
                      : `${dasaConfluence.transitScoreModifier}%`}{" "}
                    {isTa ? "கோச்சார மாற்றம்" : "Transit Impact"}
                  </span>
                  <span className="text-xs font-extrabold text-[#153F6B]">
                    = {confluencePositiveScore}% {isTa ? "கூட்டு சுப பலன்" : "Combined Score"}
                  </span>
                </div>
                <p className="text-[11px] text-emerald-950 font-medium">
                  {isTa
                    ? dasaConfluence.transitConfluenceSummaryTa
                    : dasaConfluence.transitConfluenceSummaryEn}
                </p>
              </div>

              <div className="flex items-center gap-2 flex-wrap self-start sm:self-auto">
                <button
                  type="button"
                  onClick={() => setShowTransitMatching(!showTransitMatching)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#B4872B]/50 hover:bg-[#FAF2DE] text-[#8C6D23] text-xs font-bold transition-all shadow-2xs shrink-0 cursor-pointer"
                >
                  <Compass className="w-3.5 h-3.5 text-[#B4872B]" />
                  <span>
                    {showTransitMatching
                      ? isTa
                        ? "கோச்சாரத்தை மறை"
                        : "Hide Transit Details"
                      : isTa
                      ? "துல்லிய கோச்சார பலன்கள் (ஜிகே முறை) ▾"
                      : "View GK Transit Matching ▾"}
                  </span>
                  {showTransitMatching ? (
                    <ChevronUp className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5" />
                  )}
                </button>

                <button
                  type="button"
                  onClick={() => setShowMilestones(!showMilestones)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-indigo-300 hover:bg-indigo-50 text-indigo-700 text-xs font-bold transition-all shadow-2xs shrink-0 cursor-pointer"
                >
                  <Award className="w-3.5 h-3.5 text-indigo-600" />
                  <span>
                    {showMilestones
                      ? isTa
                        ? "மைல்கற்களை மறை"
                        : "Hide Life Milestones"
                      : isTa
                      ? "8 முக்கிய மைல்கற்கள் (Marc Boney) ▾"
                      : "8 Life Milestones (Marc Boney) ▾"}
                  </span>
                  {showMilestones ? (
                    <ChevronUp className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>
          ) : (
            <div className="pt-2 border-t border-emerald-200/50 flex items-center justify-between gap-2 text-xs">
              <span className="text-emerald-900/80 text-[11px]">
                {isTa
                  ? "நேரலை கோச்சார நிலைகளை இணைத்து இந்த தசா-புக்திக்கான கூட்டு பலனை அறியலாம்."
                  : "Connect live planetary transits to see the combined Gochara impact on this period."}
              </span>
              {onFetchTransits && (
                <button
                  type="button"
                  onClick={onFetchTransits}
                  disabled={isLoadingTransits}
                  className="inline-flex items-center gap-1 text-[11px] font-bold text-[#153F6B] hover:text-[#B4872B] underline cursor-pointer disabled:opacity-50"
                >
                  <RefreshCw className={`w-3 h-3 ${isLoadingTransits ? "animate-spin" : ""}`} />
                  <span>{isTa ? "கோசாரம் இணைக்க" : "Match Transits"}</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Embedded GK Transit Matching View (when toggled open) */}
        {showTransitMatching && liveTransits && (
          <div className="pt-2 pb-2">
            <GkTransitMatchingCard
              horoscope={horoscope}
              liveTransits={liveTransits}
              isLoadingTransits={isLoadingTransits}
              onRefreshTransits={onFetchTransits}
              dasaLord={selectedMaha}
              bukthiLord={selectedAntar}
              andharaLord={levelMode === "dasa-bukthi-andhara" ? selectedAndhar : undefined}
              baseScore={currentPositiveScore}
            />
          </div>
        )}

        {/* Embedded Marc Boney Life Milestones View (when toggled open) */}
        {showMilestones && (
          <div className="pt-2 pb-2">
            <MarcBoneyMilestonesCard
              horoscope={horoscope}
              dasa={dasa}
              liveTransits={liveTransits}
            />
          </div>
        )}

        {/* Positive Factors & Cautions Split Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 text-xs">
          {/* Positive Manifestations */}
          <div className="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-200 space-y-2">
            <div className="flex items-center gap-1.5 font-bold text-emerald-900 pb-1.5 border-b border-emerald-200/70">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>{isTa ? "இக்காலத்தின் முக்கிய நற்பலன்கள் (Positive Factors)" : "Key Auspicious Manifestations"}</span>
            </div>
            <ul className="space-y-1.5">
              {(isTa ? analysis.keyPositivePointsTa : analysis.keyPositivePointsEn).map((pt, idx) => (
                <li key={idx} className="flex items-start gap-1.5 text-emerald-950 text-[11px] leading-relaxed">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{pt}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Cautions & Safeguards */}
          <div className="p-3.5 rounded-xl bg-amber-50/50 border border-amber-200 space-y-2">
            <div className="flex items-center gap-1.5 font-bold text-amber-900 pb-1.5 border-b border-amber-200/70">
              <ShieldAlert className="w-4 h-4 text-amber-600" />
              <span>{isTa ? "கவனிக்க வேண்டியவை & சாந்திகள் (Cautionary Alerts)" : "Areas Requiring Vigilance"}</span>
            </div>
            <ul className="space-y-1.5">
              {(isTa ? analysis.keyCautionPointsTa : analysis.keyCautionPointsEn).map((pt, idx) => (
                <li key={idx} className="flex items-start gap-1.5 text-amber-950 text-[11px] leading-relaxed">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                  <span>{pt}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Mantreswara's Phaladeepika (Ch. 20) Bhava Lord Influence */}
        {analysis.bhavaSignificationsTa.length > 0 && (
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#D9DEE7] space-y-2">
            <div className="flex items-center gap-1.5 font-bold text-[#153F6B] text-xs pb-1.5 border-b border-gray-200">
              <BookOpen className="w-3.5 h-3.5 text-[#B4872B]" />
              <span>
                {isTa
                  ? `பலதீபிகை விதி (அத்தியாயம் 20): ${getLordName(analysis.antardashaLord, language)} புக்தி நாதன் பாவக பலன்கள்`
                  : `Phaladeepika (Ch. 20): ${analysis.antardashaLord} Bhukti House Lordship Effects`}
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
              {(isTa ? analysis.bhavaSignificationsTa : analysis.bhavaSignificationsEn).map((sig, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-white border border-gray-200/80 text-[#183047] leading-relaxed flex items-start gap-1.5">
                  <Sparkles className="w-3 h-3 text-[#B4872B] shrink-0 mt-0.5" />
                  <span>{sig}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timing Metrics & Progress Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-[#F8FAFC] p-3 rounded-xl border border-[#E2E8F0] text-xs">
          <div>
            <div className="text-[#52667E] text-[11px]">{isTa ? "புக்தி ஆரம்பம்" : "Bhukti Start"}</div>
            <div className="font-bold text-[#183047]">{analysis.startDateFormatted}</div>
            <div className="text-[10px] text-gray-500">{analysis.ageAtStartFormatted}</div>
          </div>
          <div>
            <div className="text-[#52667E] text-[11px]">{isTa ? "புக்தி முடிவு" : "Bhukti End"}</div>
            <div className="font-bold text-[#183047]">{analysis.endDateFormatted}</div>
            <div className="text-[10px] text-gray-500">{analysis.ageAtEndFormatted}</div>
          </div>
          <div>
            <div className="text-[#52667E] text-[11px]">{isTa ? "கால அளவு" : "Duration"}</div>
            <div className="font-bold text-[#183047]">{analysis.durationYearsFormatted}</div>
          </div>
          <div>
            <div className="text-[#52667E] text-[11px]">{isTa ? "நிகழ்வு நிலை" : "Timeline Status"}</div>
            <div className="font-bold text-[#183047]">
              {analysis.isActiveNow
                ? isTa
                  ? `நடப்பில் உள்ளது (${analysis.progressPercent}%)`
                  : `In Progress (${analysis.progressPercent}%)`
                : analysis.isPast
                ? isTa
                  ? "கடந்துவிட்டது (Past)"
                  : "Completed (Past)"
                : isTa
                ? "எதிர்காலம் (Upcoming)"
                : "Upcoming (Future)"}
            </div>
          </div>
        </div>

        {/* Progress Bar for Active Period */}
        {analysis.isActiveNow && (
          <div className="space-y-1">
            <div className="flex justify-between text-[11px] text-[#52667E] font-medium">
              <span>{isTa ? "கால நிறைவு விகிதம்" : "Period Progress"}</span>
              <span>{analysis.progressPercent}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-[#E2E8F0] overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#153F6B] to-[#B4872B] rounded-full transition-all duration-500"
                style={{ width: `${analysis.progressPercent}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* 4. Andhara Level Event Catalyst (3rd-tier Pratyantardasha Manifestation) */}
      <div className="rounded-2xl border border-amber-300/80 bg-gradient-to-br from-amber-50/70 via-orange-50/40 to-yellow-50/60 p-5 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-amber-200">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-[#B4872B] text-white shadow-xs">
                <Sparkles className="w-4 h-4" />
              </span>
              <h3 className="text-base font-bold text-[#183047] flex items-center gap-2">
                <span>
                  {isTa
                    ? `${getLordName(analysis.pratyantardashaLord, language)} அந்திர பலன் & நிகழ்வு தூண்டுதல்`
                    : `${analysis.pratyantardashaLord} Andhara (Pratyantar) Event Catalyst`}
                </span>
                {analysis.andhara.timing.isActiveNow && (
                  <span className="px-2 py-0.5 rounded-full bg-emerald-600 text-white text-[10px] font-bold">
                    {isTa ? "இப்போது நடப்பில்" : "Active Now"}
                  </span>
                )}
              </h3>
            </div>
            <p className="text-xs text-[#8C6D23] font-medium">
              {isTa ? analysis.andhara.catalystThemeTa : analysis.andhara.catalystThemeEn}
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs bg-white/90 border border-amber-200 px-3 py-1.5 rounded-xl text-[#183047] shadow-2xs">
            <Calendar className="w-3.5 h-3.5 text-[#B4872B]" />
            <span className="font-semibold">{analysis.andhara.timing.startDateFormatted} — {analysis.andhara.timing.endDateFormatted}</span>
            <span className="text-gray-300">|</span>
            <span className="text-amber-800 font-bold">{analysis.andhara.timing.durationFormatted}</span>
          </div>
        </div>

        {/* Andhara 9-Period Timeline Quick Picker Bar */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-[11px] text-[#52667E]">
            <span className="font-semibold">{isTa ? "புக்திக்குள் 9 அந்திர கால அட்டவணை (கிளிக் செய்து பலன்களைக் காண்க):" : "9 Andhara Periods within this Bhukti (click to inspect):"}</span>
            <span className="text-xs text-[#153F6B] font-bold">{isTa ? "3-ஆம் அடுக்கு விம்சோத்தரி" : "Level 3 Vimshottari"}</span>
          </div>
          <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-1.5">
            {analysis.availableAndharas.map((item) => {
              const isSelected = item.lord === selectedAndhar;
              const isNow =
                activePeriods.maha === selectedMaha &&
                activePeriods.antar === selectedAntar &&
                activePeriods.andhar === item.lord;
              return (
                <button
                  key={item.lord}
                  type="button"
                  onClick={() => setSelectedAndhar(item.lord)}
                  className={`p-2 rounded-lg border text-left transition-all cursor-pointer relative ${
                    isSelected
                      ? "border-amber-700 bg-amber-700 text-white shadow-xs"
                      : isNow
                      ? "border-emerald-500 bg-emerald-50 text-emerald-950 font-semibold hover:bg-emerald-100"
                      : "border-amber-200/80 bg-white hover:bg-amber-50/60 text-[#183047]"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold truncate">{getLordName(item.lord, language)}</span>
                    {isNow && (
                      <span className={`w-1.5 h-1.5 rounded-full ${isSelected ? "bg-white" : "bg-emerald-500"}`} />
                    )}
                  </div>
                  <div className={`text-[10px] truncate ${isSelected ? "text-amber-100" : "text-[#52667E]"}`}>
                    {item.startDateFormatted.split(" ")[0]}
                  </div>
                  <div className={`text-[9px] font-medium ${isSelected ? "text-white" : "text-amber-800"}`}>
                    {item.durationFormatted}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Andhara Analytical Findings */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs pt-1">
          {/* Card 1: Specific Event Catalyst */}
          <div className="p-3.5 rounded-xl bg-white border border-amber-200 shadow-2xs space-y-1.5 md:col-span-2">
            <div className="text-[11px] font-bold text-[#B4872B] uppercase tracking-wider flex items-center gap-1.5">
              <Flame className="w-3.5 h-3.5 text-amber-600" />
              <span>{isTa ? "நிகழ்வு தூண்டுதல் பலன் (Trigger Prediction)" : "Event Manifestation & Trigger"}</span>
            </div>
            <p className="text-xs text-[#183047] leading-relaxed font-medium">
              {isTa ? analysis.andhara.predictionTa : analysis.andhara.predictionEn}
            </p>
            <div className="pt-2 border-t border-gray-100 flex items-start gap-1.5 text-[11px] text-[#52667E]">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#B4872B] shrink-0 mt-0.5" />
              <span>
                <strong className="text-[#183047]">{isTa ? "செயல்பாட்டு களம்:" : "Trigger Focus:"} </strong>
                {isTa ? analysis.andhara.eventTriggerFocusTa : analysis.andhara.eventTriggerFocusEn}
              </span>
            </div>
          </div>

          {/* Card 2: Relationship with Bhukti Lord & Dignity */}
          <div className="p-3.5 rounded-xl bg-white border border-amber-200 shadow-2xs space-y-2">
            <div className="text-[11px] font-bold text-[#153F6B] uppercase tracking-wider flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5" />
              <span>{isTa ? "புக்தி நாதனுடன் தொடர்பு" : "Disposition from Bhukti"}</span>
            </div>

            <div className="space-y-1 text-[11px]">
              <div className="flex justify-between text-[#52667E]">
                <span>{isTa ? "தூர அச்சு:" : "Axis:"}</span>
                <span className="font-bold text-[#183047]">
                  {isTa ? analysis.andhara.relationshipFromBhukti.axisNameTa : analysis.andhara.relationshipFromBhukti.axisNameEn}
                </span>
              </div>
              <div className="flex justify-between text-[#52667E]">
                <span>{isTa ? "அமர்வு:" : "Position:"}</span>
                <span className="font-semibold text-[#183047]">
                  {analysis.andhara.strength.signName} (H{analysis.andhara.strength.houseOccupied})
                </span>
              </div>
              <div className="flex justify-between text-[#52667E]">
                <span>{isTa ? "ஷட்பல தேர்ச்சி:" : "Shadbala:"}</span>
                <span className={analysis.andhara.strength.shadbalaPass ? "text-emerald-700 font-bold" : "text-amber-700 font-semibold"}>
                  {analysis.andhara.strength.shadbalaPass ? (isTa ? "தேர்ச்சி" : "Adequate") : (isTa ? "குறைவு" : "Sub-optimal")}
                </span>
              </div>
              <div className="flex justify-between text-[#52667E]">
                <span>{isTa ? "அஷ்டகவர்க பரல்:" : "Ashtakavarga:"}</span>
                <span className="font-bold text-[#183047]">
                  {analysis.andhara.strength.ashtakavargaBindus} bindus
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Classical Analytical Deep Dive: Sambandha & Strength Profile */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Card 4A: Distance & Sambandha (Chapter 1, Rules 12-16) */}
        <div className="rounded-xl border border-[#D9DEE7] bg-white p-5 shadow-2xs space-y-3.5">
          <div className="flex items-center gap-2 pb-2 border-b border-[#E2E8F0]">
            <Compass className="w-4 h-4 text-[#B4872B]" />
            <h3 className="text-sm font-bold text-[#183047]">
              {isTa ? "1. பாவ தூரம் & கிரக சம்பந்தம்" : "1. Mutual Distance & Sambandha"}
            </h3>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
              <span className="text-[#52667E]">
                {isTa ? "திசா நாதனிடமிருந்து புக்தி நாதன் தூரம்:" : "Distance from Maha Lord:"}
              </span>
              <span className="font-bold text-[#153F6B]">
                {isTa ? analysis.relationship.axisNameTa : analysis.relationship.axisNameEn}
              </span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
              <span className="text-[#52667E]">
                {isTa ? "லக்னத்திலிருந்து வெளிப்படும் பாவகம்:" : "Manifesting House from Lagna:"}
              </span>
              <span className="font-bold text-[#B4872B]">
                {isTa
                  ? `லக்னத்திலிருந்து ${analysis.relationship.derivedHouseFromLagna}-ஆம் இடம்`
                  : `House ${analysis.relationship.derivedHouseFromLagna} from Ascendant`}
              </span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
              <span className="text-[#52667E]">
                {isTa ? "கிரக சேர்க்கை / பார்வை நிலை:" : "Sambandha Connection:"}
              </span>
              <span className="font-bold text-[#183047]">
                {isTa ? analysis.relationship.sambandhaTextTa : analysis.relationship.sambandhaTextEn}
              </span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
              <span className="text-[#52667E]">
                {isTa ? "இயற்கை மற்றும் தற்காலிக நட்பு:" : "Planetary Disposition:"}
              </span>
              <span className="font-bold text-[#183047]">
                {isTa ? analysis.relationship.relationshipNatureTextTa : analysis.relationship.relationshipNatureTextEn}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-amber-50/70 border border-amber-200/80 text-[#8C6D23] space-y-1">
              <div className="font-bold flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5" />
                <span>{isTa ? "பலன்கள் வெளிப்படும் காலப்பகுதி (விதி 1):" : "Timing of Manifestation:"}</span>
              </div>
              <p className="text-[11px] leading-relaxed">
                {isTa ? analysis.relationship.deliveryWindowTextTa : analysis.relationship.deliveryWindowTextEn}
              </p>
            </div>
          </div>
        </div>

        {/* Card 4B: Strength & Dignity Audit (Chapter 1, Rules 1-5 & Chapter 3) */}
        <div className="rounded-xl border border-[#D9DEE7] bg-white p-5 shadow-2xs space-y-3.5">
          <div className="flex items-center gap-2 pb-2 border-b border-[#E2E8F0]">
            <Award className="w-4 h-4 text-[#153F6B]" />
            <h3 className="text-sm font-bold text-[#183047]">
              {isTa ? "2. கிரக பலம் & அஷ்டகவர்க நிர்ணயம்" : "2. Planetary Strength & Ashtakavarga"}
            </h3>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            {/* Mahadasha Lord Strength */}
            <div className="p-3 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] space-y-1.5">
              <div className="font-bold text-[#153F6B] flex items-center justify-between">
                <span>{getLordName(analysis.mahaStrength.planet, language)}</span>
                <span className="text-[10px] text-gray-500 uppercase">{isTa ? "மகா திசா நாதன்" : "Maha Lord"}</span>
              </div>
              <div className="text-[11px] text-[#52667E]">
                {isTa ? "அமர்வு:" : "Position:"}{" "}
                <strong className="text-[#183047]">{analysis.mahaStrength.signName} (பாவம் {analysis.mahaStrength.houseOccupied})</strong>
              </div>
              <div className="text-[11px] text-[#52667E]">
                {isTa ? "அவஸ்தை:" : "Avastha:"}{" "}
                <strong className="text-[#183047]">{isTa ? analysis.mahaStrength.avasthaNameTa : analysis.mahaStrength.avasthaNameEn}</strong>
              </div>
              <div className="text-[11px] text-[#52667E] flex items-center justify-between">
                <span>{isTa ? "ஷட்பல தேர்ச்சி:" : "Shadbala Status:"}</span>
                <strong className={analysis.mahaStrength.shadbalaPass ? "text-emerald-700" : "text-amber-700"}>
                  {analysis.mahaStrength.shadbalaPass ? (isTa ? "பலம் உள்ளது" : "Adequate") : (isTa ? "குறைவு" : "Sub-optimal")}
                </strong>
              </div>
              <div className="text-[11px] text-[#52667E] flex items-center justify-between">
                <span>{isTa ? "அஷ்டகவர்க பரல்கள்:" : "Ashtakavarga:"}</span>
                <strong className="text-[#183047]">{analysis.mahaStrength.ashtakavargaBindus} bindus</strong>
              </div>
            </div>

            {/* Antardasha Lord Strength */}
            <div className="p-3 rounded-lg border border-amber-200 bg-amber-50/40 space-y-1.5">
              <div className="font-bold text-[#B4872B] flex items-center justify-between">
                <span>{getLordName(analysis.antarStrength.planet, language)}</span>
                <span className="text-[10px] text-gray-500 uppercase">{isTa ? "புக்தி நாதன்" : "Bhukti Lord"}</span>
              </div>
              <div className="text-[11px] text-[#52667E]">
                {isTa ? "அமர்வு:" : "Position:"}{" "}
                <strong className="text-[#183047]">{analysis.antarStrength.signName} (பாவம் {analysis.antarStrength.houseOccupied})</strong>
              </div>
              <div className="text-[11px] text-[#52667E]">
                {isTa ? "அவஸ்தை:" : "Avastha:"}{" "}
                <strong className="text-[#183047]">{isTa ? analysis.antarStrength.avasthaNameTa : analysis.antarStrength.avasthaNameEn}</strong>
              </div>
              <div className="text-[11px] text-[#52667E] flex items-center justify-between">
                <span>{isTa ? "தார பலம்:" : "Tara Bala:"}</span>
                <strong className={analysis.antarStrength.taraBala.isAuspicious ? "text-emerald-700" : "text-rose-700"}>
                  {isTa ? analysis.antarStrength.taraBala.nameTa : analysis.antarStrength.taraBala.nameEn}
                </strong>
              </div>
              <div className="text-[11px] text-[#52667E] flex items-center justify-between">
                <span>{isTa ? "அஷ்டகவர்க பரல்கள்:" : "Ashtakavarga:"}</span>
                <strong className={analysis.antarStrength.ashtakavargaBindus >= 5 ? "text-emerald-700 font-bold" : "text-[#183047]"}>
                  {analysis.antarStrength.ashtakavargaBindus} bindus ({analysis.antarStrength.ashtakavargaStatus})
                </strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Life Domain Predictions (Categories & Classical Explanations) */}
      <div className="rounded-xl border border-[#D9DEE7] bg-white p-5 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E2E8F0]">
          <div>
            <h3 className="text-base font-bold text-[#183047] flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-[#B4872B]" />
              <span>{isTa ? "வாழ்க்கை விவகாரங்களில் பலன்கள்" : "Life Domain Predictions & Outcomes"}</span>
            </h3>
            <p className="text-xs text-[#52667E]">
              {isTa
                ? "சாஸ்திர விதிகளின்படி இந்த தசா-புக்தியில் தொழில், தனம், இல்லறம் மற்றும் ஆரோக்கியத்தில் நிகழும் பலன்கள்."
                : "Actionable forecasts for Career, Wealth, Marriage, Education, and Health for this period."}
            </p>
          </div>

          {/* Quick Filters */}
          <div className="flex items-center gap-1 overflow-x-auto pb-1 text-xs">
            {[
              { id: "all", en: "All Domains", ta: "அனைத்தும்" },
              { id: "career", en: "Career & Status", ta: "தொழில் & வேலை" },
              { id: "wealth", en: "Wealth & Property", ta: "தனம் & சொத்து" },
              { id: "marriage", en: "Marriage & Family", ta: "திருமணம் & குடும்பம்" },
              { id: "educationChildren", en: "Intellect & Children", ta: "கல்வி & புத்திரர்" },
              { id: "healthMaraka", en: "Health & Alerts", ta: "ஆரோக்கியம் & எச்சரிக்கை" },
            ].map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setCategoryFilter(f.id)}
                className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer whitespace-nowrap font-medium ${
                  categoryFilter === f.id
                    ? "bg-[#153F6B] text-white"
                    : "bg-[#F1F5F9] text-[#52667E] hover:bg-[#E2E8F0]"
                }`}
              >
                {isTa ? f.ta : f.en}
              </button>
            ))}
          </div>
        </div>

        {/* Prediction Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(categoryFilter === "all" || categoryFilter === "general") && (
            <PredictionBlockView block={analysis.categories.general} isTa={isTa} />
          )}
          {(categoryFilter === "all" || categoryFilter === "career") && (
            <PredictionBlockView block={analysis.categories.career} isTa={isTa} />
          )}
          {(categoryFilter === "all" || categoryFilter === "wealth") && (
            <PredictionBlockView block={analysis.categories.wealth} isTa={isTa} />
          )}
          {(categoryFilter === "all" || categoryFilter === "marriage") && (
            <PredictionBlockView block={analysis.categories.marriage} isTa={isTa} />
          )}
          {(categoryFilter === "all" || categoryFilter === "educationChildren") && (
            <PredictionBlockView block={analysis.categories.educationChildren} isTa={isTa} />
          )}
          {(categoryFilter === "all" || categoryFilter === "healthMaraka") && (
            <PredictionBlockView block={analysis.categories.healthMaraka} isTa={isTa} />
          )}
        </div>
      </div>

      {/* 6. Sun Transit Manifestation Window (Chapter 2, Rule 9) */}
      <div className="rounded-xl border border-amber-300 bg-gradient-to-r from-amber-50/80 via-orange-50/60 to-yellow-50/80 p-5 shadow-2xs space-y-3">
        <div className="flex items-center gap-2 text-amber-900">
          <Sun className="w-5 h-5 text-amber-600 animate-spin-slow" />
          <h4 className="text-sm font-bold">
            {isTa ? "சூரிய பெயர்ச்சி உச்ச பலன் காலம் (சாஸ்திர விதி 9)" : "Sun Transit Manifestation Window (Rule 9)"}
          </h4>
        </div>
        <p className="text-xs text-[#8C6D23] leading-relaxed">
          {isTa ? analysis.sunTransit.descriptionTa : analysis.sunTransit.descriptionEn}
        </p>
        <div className="p-3 rounded-lg bg-white/90 border border-amber-200 text-xs text-[#183047] font-semibold flex items-center gap-2">
          <Clock className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{isTa ? analysis.sunTransit.manifestationWindowTa : analysis.sunTransit.manifestationWindowEn}</span>
        </div>
      </div>

      {/* 7. Classical Vedic Remedies & Propitiation */}
      <div className="rounded-xl border border-[#D9DEE7] bg-white p-5 shadow-2xs space-y-4">
        <div className="flex items-center gap-2 pb-2 border-b border-[#E2E8F0]">
          <Sparkles className="w-4 h-4 text-[#B4872B]" />
          <h4 className="text-sm font-bold text-[#183047]">
            {isTa
              ? `${getLordName(analysis.antardashaLord, language)} புக்திக்கான சாஸ்திர பரிகாரங்கள் & சாந்தி`
              : `Classical Vedic Remedies & Propitiation for ${analysis.antardashaLord} Bhukti`}
          </h4>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
            <div className="text-[#52667E] font-medium">{isTa ? "உபாசனை தெய்வம் (Deity)" : "Sacred Deity"}</div>
            <div className="font-bold text-[#153F6B]">{isTa ? analysis.remedies.deityTa : analysis.remedies.deityEn}</div>
          </div>

          <div className="p-3 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
            <div className="text-[#52667E] font-medium">{isTa ? "அதிர்ஷ்ட ரத்தினம் & நிறம்" : "Gemstone & Auspicious Colors"}</div>
            <div className="font-bold text-[#183047]">
              {isTa ? analysis.remedies.gemstoneTa : analysis.remedies.gemstoneEn} — {isTa ? analysis.remedies.colorTa : analysis.remedies.colorEn}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] space-y-1 md:col-span-2">
            <div className="text-[#52667E] font-medium">{isTa ? "ஜெப மந்திரம் (Sacred Mantra)" : "Sacred Mantra"}</div>
            <div className="font-bold text-[#B4872B]">{isTa ? analysis.remedies.mantraTa : analysis.remedies.mantraEn}</div>
          </div>

          <div className="p-3 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] space-y-1 md:col-span-2">
            <div className="text-[#52667E] font-medium">{isTa ? "தானம் & அறப்பணி" : "Charity & Righteous Conduct"}</div>
            <div className="text-[#183047] leading-relaxed">{isTa ? analysis.remedies.charityTa : analysis.remedies.charityEn}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Sub-component for rendering each category block
function PredictionBlockView({
  block,
  isTa,
}: {
  block: {
    titleEn: string;
    titleTa: string;
    favorableScore: number;
    summaryEn: string;
    summaryTa: string;
    pointsEn: string[];
    pointsTa: string[];
  };
  isTa: boolean;
}) {
  return (
    <div className="p-4 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] hover:bg-white transition-all space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-[#E2E8F0]">
        <h4 className="text-xs font-bold text-[#153F6B] flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
          <span>{isTa ? block.titleTa : block.titleEn}</span>
        </h4>
        <div className="flex items-center gap-1.5 text-[11px] font-bold">
          <span className="text-[#52667E]">{isTa ? "சுப பலன்:" : "Favorable:"}</span>
          <span
            className={
              block.favorableScore >= 70
                ? "text-emerald-700"
                : block.favorableScore >= 45
                ? "text-amber-700"
                : "text-rose-700"
            }
          >
            {block.favorableScore}%
          </span>
        </div>
      </div>

      <p className="text-xs text-[#183047] font-medium leading-relaxed">
        {isTa ? block.summaryTa : block.summaryEn}
      </p>

      <ul className="space-y-1.5 pt-1">
        {(isTa ? block.pointsTa : block.pointsEn).map((pt, idx) => (
          <li key={idx} className="text-[11px] text-[#52667E] flex items-start gap-1.5 leading-relaxed">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#B4872B] shrink-0 mt-0.5" />
            <span>{pt}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
