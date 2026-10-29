"use client";

import React, { useState, useMemo } from "react";
import {
  HoroscopeResponse,
  LiveTransitsResponse,
  PlanetInfo,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaName, getGrahaShort, getRasiName } from "@/lib/translations";
import {
  analyzeGkTransits,
  GkTransitAnalysisResult,
  GkPlanetTransitConjunction,
  GkPlanetTransitAspect,
  GK_PLANETARY_ENEMIES,
  ZODIAC_SIGNS_EN,
  ZODIAC_SIGNS_TA,
} from "@/lib/gk-transit-engine";
import {
  Compass,
  Sparkles,
  Calendar,
  Clock,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Info,
  CheckCircle2,
  RefreshCw,
  HeartPulse,
  Activity,
  Award,
  Layers,
  ArrowRight,
  TrendingUp,
  Sliders,
  ChevronDown,
  ChevronUp,
  Search,
} from "lucide-react";

interface GkTransitMatchingCardProps {
  horoscope: HoroscopeResponse;
  liveTransits?: LiveTransitsResponse | null;
  isLoadingTransits?: boolean;
  onRefreshTransits?: () => void;
  dasaLord?: string;
  bukthiLord?: string;
  andharaLord?: string;
  baseScore?: number;
}

export function GkTransitMatchingCard({
  horoscope,
  liveTransits,
  isLoadingTransits = false,
  onRefreshTransits,
  dasaLord,
  bukthiLord,
  andharaLord,
  baseScore = 70,
}: GkTransitMatchingCardProps) {
  const { language } = useLanguage();
  const [filterNature, setFilterNature] = useState<"all" | "benefic" | "caution">("all");
  const [showEnmityMatrix, setShowEnmityMatrix] = useState<boolean>(false);
  const [showAllAspects, setShowAllAspects] = useState<boolean>(false);

  // Compute GK Transit Analysis
  const transitAnalysis: GkTransitAnalysisResult | null = useMemo(() => {
    if (!liveTransits || !liveTransits.planets || liveTransits.planets.length === 0) {
      return null;
    }
    const natalPlanets = horoscope.planets || [];
    return analyzeGkTransits(
      natalPlanets,
      liveTransits.planets,
      dasaLord,
      bukthiLord,
      andharaLord,
      baseScore
    );
  }, [horoscope.planets, liveTransits, dasaLord, bukthiLord, andharaLord, baseScore]);

  // Filtered conjunctions
  const filteredConjunctions = useMemo(() => {
    if (!transitAnalysis) return [];
    if (filterNature === "all") return transitAnalysis.conjunctions;
    return transitAnalysis.conjunctions.filter((c) => c.nature === filterNature);
  }, [transitAnalysis, filterNature]);

  if (!liveTransits && isLoadingTransits) {
    return (
      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-8 shadow-xs text-center space-y-4">
        <div className="inline-flex items-center justify-center p-3 bg-amber-50 rounded-full text-[#B4872B] animate-spin">
          <RefreshCw className="w-6 h-6" />
        </div>
        <h4 className="text-base font-bold text-[#183047]">
          {language === "ta"
            ? "நேரலை கோச்சார நிலைகள் கணக்கிடப்படுகின்றன..."
            : "Calculating Live Ephemeris Transits..."}
        </h4>
        <p className="text-xs text-[#52667E] max-w-md mx-auto">
          {language === "ta"
            ? "சுவிஸ் எபிமெரிஸ் மூலம் தற்போதைய கோச்சார கிரகங்களை உங்கள் ஜனன ஜாதகத்துடன் இணைத்து பகுப்பாய்வு செய்கிறோம்."
            : "Matching real-time Swiss Ephemeris transiting planetary positions against your saved natal chart."}
        </p>
      </div>
    );
  }

  if (!liveTransits && !isLoadingTransits) {
    return (
      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-8 shadow-xs text-center space-y-4">
        <div className="inline-flex items-center justify-center p-3 bg-blue-50 rounded-full text-[#153F6B]">
          <Compass className="w-6 h-6" />
        </div>
        <h4 className="text-base font-bold text-[#183047]">
          {language === "ta"
            ? "கோச்சார விவரங்கள் தயார் நிலையில் இல்லை"
            : "Transit Data Not Yet Loaded"}
        </h4>
        <p className="text-xs text-[#52667E] max-w-md mx-auto">
          {language === "ta"
            ? "திருப்பூர் ஸ்ரீ எஸ். கோபாலகிருஷ்ணன் (ஜிகே) அவர்களின் துல்லிய கோச்சார பலன்களை அறிய நேரலை கோச்சாரத்தை இயக்கவும்."
            : "Load live planetary transits to match against this horoscope using Tirupur S. Gopalakrishnan's accurate rules."}
        </p>
        {onRefreshTransits && (
          <button
            type="button"
            onClick={onRefreshTransits}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#153F6B] hover:bg-[#103053] text-white text-xs font-bold transition-all shadow-xs cursor-pointer"
          >
            <RefreshCw className="w-4 h-4" />
            <span>{language === "ta" ? "நேரலை கோசாரம் ஏற்றுக" : "Load Live Transits"}</span>
          </button>
        )}
      </div>
    );
  }

  if (!transitAnalysis) return null;

  const confluence = transitAnalysis.dasaConfluence;

  return (
    <div className="space-y-6">
      {/* Top Banner: Master Book Reference & Principle */}
      <div className="bg-gradient-to-r from-[#0F2844] via-[#153F6B] to-[#1E4D7F] rounded-2xl p-5 sm:p-6 text-white shadow-md relative overflow-hidden border border-[#2B5D94]/40">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-[#B4872B]/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FAF2DE]/15 border border-[#B4872B]/40 text-[#ECC367] text-xs font-semibold backdrop-blur-xs">
              <Compass className="w-3.5 h-3.5" />
              <span>
                {language === "ta"
                  ? "திருப்பூர் ஸ்ரீ எஸ். கோபாலகிருஷ்ணன் (ஜிகே) சந்திர நாடி கோச்சார முறை"
                  : "Tirupur S. Gopalakrishnan (GK) Chandra Nadi Transit System"}
              </span>
            </div>
            <h3 className="text-lg sm:text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <span>{language === "ta" ? "துல்லிய கோச்சாரப் பலன்கள் & ஜனன ஜாதக ஒப்பீடு" : "Accurate Transit Predictions & Natal Matching"}</span>
            </h3>
            <p className="text-xs text-[#CBD5E1] max-w-2xl leading-relaxed">
              {language === "ta" ? transitAnalysis.gkCoreRuleTa : transitAnalysis.gkCoreRuleEn}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <div className="bg-[#0B1E33]/70 backdrop-blur-xs border border-[#2B5D94]/60 rounded-xl px-4 py-2.5 text-right">
              <div className="text-[10px] text-[#94A3B8] uppercase tracking-wider font-semibold">
                {language === "ta" ? "கணக்கிடப்பட்ட நேரம்" : "Calculated At"}
              </div>
              <div className="text-xs font-mono font-bold text-[#E2E8F0]">
                {new Date(liveTransits?.calculated_at || Date.now()).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                })}
              </div>
            </div>

            {onRefreshTransits && (
              <button
                type="button"
                onClick={onRefreshTransits}
                disabled={isLoadingTransits}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#B4872B] hover:bg-[#976E20] text-white text-xs font-bold transition-all shadow-xs cursor-pointer disabled:opacity-50"
                title={language === "ta" ? "கோச்சாரத்தை புதுப்பி" : "Refresh live transits"}
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoadingTransits ? "animate-spin" : ""}`} />
                <span>{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Dasa-Bukthi-Andhara Transit Confluence Card */}
      {confluence && (
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5 sm:p-6 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#F1F5F9]">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-amber-50 rounded-xl text-[#B4872B] border border-amber-200/50">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-[#183047]">
                  {language === "ta"
                    ? "தசா - புக்தி - கோச்சார ஒருங்கிணைந்த பலன் & சதவீத மாற்றம்"
                    : "Dasa - Bukthi - Transit Confluence Score Modifier"}
                </h4>
                <p className="text-xs text-[#52667E]">
                  {language === "ta"
                    ? `நடப்பு ${confluence.dasaLord} தசை - ${confluence.bukthiLord} புக்தி மீது கோச்சார கிரகங்களின் நேரடி தாக்கம்`
                    : `Direct impact of live transits on running ${confluence.dasaLord} Dasa - ${confluence.bukthiLord} Bukthi`}
                </p>
              </div>
            </div>

            {/* Combined Score Pill */}
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-[10px] text-[#8190A6] uppercase tracking-wider font-semibold">
                  {language === "ta" ? "கோச்சார மாற்றியமைத்த சுப பலன்" : "Transit Adjusted Score"}
                </div>
                <div className="flex items-center gap-1.5 justify-end">
                  <span className="text-2xl font-black text-[#153F6B]">
                    {confluence.combinedAdjustedScore}%
                  </span>
                  <span
                    className={`inline-flex items-center text-xs font-bold px-2 py-0.5 rounded-full ${
                      confluence.transitScoreModifier >= 0
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {confluence.transitScoreModifier >= 0
                      ? `+${confluence.transitScoreModifier}%`
                      : `${confluence.transitScoreModifier}%`}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Progress bar split visual */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-bold">
              <span className="text-emerald-700 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                {language === "ta" ? "சுப கோச்சார ஆதரவு" : "Auspicious Transit Support"}:{" "}
                {confluence.combinedAdjustedScore}%
              </span>
              <span className="text-rose-700 flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                {language === "ta" ? "கவனமும் பொறுமையும்" : "Caution & Patience"}:{" "}
                {100 - confluence.combinedAdjustedScore}%
              </span>
            </div>
            <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden flex shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-700"
                style={{ width: `${confluence.combinedAdjustedScore}%` }}
              />
              <div
                className="h-full bg-gradient-to-r from-rose-400 to-amber-500 transition-all duration-700"
                style={{ width: `${100 - confluence.combinedAdjustedScore}%` }}
              />
            </div>
          </div>

          {/* Confluence summary explanation */}
          <div className="p-3.5 bg-[#FAF2DE]/40 border border-[#B4872B]/30 rounded-xl">
            <p className="text-xs text-[#5F4512] leading-relaxed font-medium">
              {language === "ta"
                ? confluence.transitConfluenceSummaryTa
                : confluence.transitConfluenceSummaryEn}
            </p>
          </div>

          {/* Specific Catalysts */}
          {confluence.keyCatalystsEn.length > 0 && (
            <div className="space-y-2 pt-1">
              <div className="text-xs font-bold text-[#183047] uppercase tracking-wider flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-[#B4872B]" />
                <span>{language === "ta" ? "செயல்பாட்டில் உள்ள கோச்சார தூண்டுதல்கள்" : "Active Transit Catalysts"}</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {(language === "ta" ? confluence.keyCatalystsTa : confluence.keyCatalystsEn).map(
                  (item, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-slate-50 border border-slate-200/80 rounded-xl text-xs text-[#334155] flex items-start gap-2"
                    >
                      <ArrowRight className="w-3.5 h-3.5 text-[#153F6B] shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chapter 3: Medical Astrological Guidance & Surgery Timing */}
      <div className="bg-white rounded-2xl border border-rose-200/80 p-5 sm:p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-rose-50 text-rose-600 rounded-xl border border-rose-200">
              <HeartPulse className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-bold text-[#183047]">
                  {language === "ta"
                    ? "மருத்துவ சிகிச்சை & அறுவை சிகிச்சை கோச்சார வழிகாட்டல் (அத்தியாயம் 3)"
                    : "Medical Treatment & Surgery Timing (GK Chapter 3)"}
                </h4>
                <span className="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[10px] font-bold">
                  {language === "ta"
                    ? `சந்திரன்: ${transitAnalysis.moonMedical.moonSignNameTa}`
                    : `Moon in ${transitAnalysis.moonMedical.moonSignNameEn}`}
                </span>
              </div>
              <p className="text-xs text-[#52667E]">
                {language === "ta"
                  ? "சந்திரன் சஞ்சரிக்கும் காலபுருஷ ராசிக்குரிய உறுப்புகளில் அறுவை சிகிச்சைகளை தவிர்ப்பது நன்று."
                  : "Surgeries must not be scheduled on body parts denoted by the sign through which transit Moon passes."}
              </p>
            </div>
          </div>

          {transitAnalysis.moonMedical.safeHealingWindow && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>{language === "ta" ? "குரு பார்வை: குணமடையும் காலம்" : "Jupiter Glance: Healing Window"}</span>
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-rose-50/50 border border-rose-100 rounded-xl space-y-2">
            <div className="text-xs font-bold text-rose-900 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-rose-600" />
              <span>
                {language === "ta"
                  ? "தற்போது அறுவை சிகிச்சை தவிர்க்க வேண்டிய உடல் பாகங்கள்:"
                  : "Body Parts to Avoid Elective Surgeries Right Now:"}
              </span>
            </div>
            <div className="text-xs font-medium text-rose-950">
              {language === "ta"
                ? transitAnalysis.moonMedical.vulnerableOrganTa
                : transitAnalysis.moonMedical.vulnerableOrganEn}
            </div>
            <ul className="text-xs text-rose-800 space-y-1 list-disc list-inside">
              {(language === "ta"
                ? transitAnalysis.moonMedical.avoidSurgeriesTa
                : transitAnalysis.moonMedical.avoidSurgeriesEn
              ).map((avoid, i) => (
                <li key={i}>{avoid}</li>
              ))}
            </ul>
          </div>

          <div className="p-4 bg-blue-50/50 border border-blue-100 rounded-xl space-y-2">
            <div className="text-xs font-bold text-[#153F6B] flex items-center gap-1.5">
              <Info className="w-4 h-4 text-[#153F6B]" />
              <span>{language === "ta" ? "திருப்பூர் ஜிகே மருத்துவ விதி:" : "Tirupur GK Medical Rule:"}</span>
            </div>
            <p className="text-xs text-[#334155] leading-relaxed">
              {language === "ta"
                ? transitAnalysis.moonMedical.medicalAdviceTa
                : transitAnalysis.moonMedical.medicalAdviceEn}
            </p>
            <p className="text-[11px] text-[#64748B] italic pt-1">
              {language === "ta"
                ? "அவசர உயிர்காக்கும் அறுவை சிகிச்சைகளுக்கு இந்த கோச்சார விதி பொருந்தாது; விருப்பத்தேர்வு சிகிச்சைகளுக்கு மட்டுமே."
                : "Note: Emergency life-saving operations take absolute medical precedence over astrological elective timing."}
            </p>
          </div>
        </div>
      </div>

      {/* Active Conjunctions: Transiting Planets over Natal Planets */}
      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5 sm:p-6 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h4 className="text-base font-bold text-[#183047] flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#B4872B]" />
              <span>
                {language === "ta"
                  ? `ஜனன கிரகங்கள் மீது கோச்சார கிரக சேர்க்கை (${transitAnalysis.conjunctions.length})`
                  : `Transit over Natal Planets Conjunctions (${transitAnalysis.conjunctions.length})`}
              </span>
            </h4>
            <p className="text-xs text-[#52667E]">
              {language === "ta"
                ? "ஜனன ஜாதகத்தில் உள்ள கிரகங்களின் ராசியில் தற்போது சஞ்சரிக்கும் கோச்சார கிரகங்கள் மற்றும் அவற்றின் பலன்கள்."
                : "Real-time transiting planets passing directly through the natal signs of your saved horoscope."}
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl self-start sm:self-auto">
            <button
              type="button"
              onClick={() => setFilterNature("all")}
              className={`px-2.5 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                filterNature === "all" ? "bg-white text-[#153F6B] shadow-2xs" : "text-[#64748B] hover:text-[#183047]"
              }`}
            >
              {language === "ta" ? "அனைத்தும்" : "All"} ({transitAnalysis.conjunctions.length})
            </button>
            <button
              type="button"
              onClick={() => setFilterNature("benefic")}
              className={`px-2.5 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                filterNature === "benefic"
                  ? "bg-emerald-600 text-white shadow-2xs"
                  : "text-emerald-700 hover:text-emerald-900"
              }`}
            >
              {language === "ta" ? "சுப சேர்க்கை" : "Benefic"}
            </button>
            <button
              type="button"
              onClick={() => setFilterNature("caution")}
              className={`px-2.5 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                filterNature === "caution"
                  ? "bg-rose-600 text-white shadow-2xs"
                  : "text-rose-700 hover:text-rose-900"
              }`}
            >
              {language === "ta" ? "எச்சரிக்கை" : "Caution"}
            </button>
          </div>
        </div>

        {/* Conjunction Cards Grid */}
        {filteredConjunctions.length === 0 ? (
          <div className="text-center py-8 text-xs text-[#8190A6]">
            {language === "ta"
              ? "தேர்ந்தெடுக்கப்பட்ட பிரிவில் நேரடி கோச்சார சேர்க்கைகள் இல்லை."
              : "No direct planetary conjunctions match the selected filter."}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredConjunctions.map((conj, idx) => {
              const isBenefic = conj.nature === "benefic";
              const isCaution = conj.nature === "caution";

              return (
                <div
                  key={idx}
                  className={`rounded-2xl border p-4 transition-all duration-200 flex flex-col justify-between space-y-3 ${
                    isBenefic
                      ? "bg-gradient-to-br from-emerald-50/40 via-white to-teal-50/30 border-emerald-200 shadow-2xs"
                      : isCaution
                      ? "bg-gradient-to-br from-rose-50/40 via-white to-amber-50/30 border-rose-200 shadow-2xs"
                      : "bg-slate-50/60 border-slate-200"
                  }`}
                >
                  <div className="space-y-2">
                    {/* Header */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="px-2 py-0.5 rounded-md bg-[#153F6B] text-white text-[11px] font-bold">
                            {language === "ta" ? "கோச்சாரம்:" : "Transit:"} {getGrahaName(conj.transitingPlanet, language)}
                          </span>
                          <span className="text-xs text-[#8190A6] font-bold">+</span>
                          <span className="px-2 py-0.5 rounded-md bg-[#B4872B] text-white text-[11px] font-bold">
                            {language === "ta" ? "ஜனனம்:" : "Natal:"} {getGrahaName(conj.natalPlanet, language)}
                          </span>
                          <span className="text-xs text-[#52667E] font-medium">
                            ({language === "ta" ? conj.signNameTa : conj.signNameEn})
                          </span>
                        </div>
                        <h5 className="text-xs sm:text-sm font-bold text-[#183047] pt-1">
                          {language === "ta" ? conj.predictionTitleTa : conj.predictionTitleEn}
                        </h5>
                      </div>

                      {conj.isExactOrb && (
                        <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-bold border border-amber-300 shrink-0">
                          {language === "ta" ? `துல்லிய பாகை (${conj.degreeOrb}°)` : `Exact Orb (${conj.degreeOrb}°)`}
                        </span>
                      )}
                    </div>

                    {/* Effects List */}
                    <ul className="text-xs text-[#334155] space-y-1.5 pt-1">
                      {(language === "ta" ? conj.effectsTa : conj.effectsEn).map((eff, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span
                            className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${
                              isBenefic ? "bg-emerald-500" : isCaution ? "bg-rose-500" : "bg-slate-400"
                            }`}
                          />
                          <span className="leading-relaxed">{eff}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Tirupur GK Treatise Quote */}
                  <div className="pt-2 border-t border-slate-100">
                    <p className="text-[11px] italic text-[#64748B] flex items-center gap-1">
                      <Sparkles className="w-3 h-3 text-[#B4872B] shrink-0" />
                      <span>{language === "ta" ? conj.gkRuleQuoteTa : conj.gkRuleQuoteEn}</span>
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* GK Planetary Aspects on Natal Chart */}
      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5 sm:p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h4 className="text-base font-bold text-[#183047] flex items-center gap-2">
              <Compass className="w-4 h-4 text-[#153F6B]" />
              <span>
                {language === "ta"
                  ? `கோச்சார கிரகங்களின் சிறப்புப் பார்வைகள் (${transitAnalysis.aspects.length})`
                  : `Tirupur GK Special Transit Aspects (${transitAnalysis.aspects.length})`}
              </span>
            </h4>
            <p className="text-xs text-[#52667E]">
              {language === "ta"
                ? "செவ்வாயின் 4, 7, 8 பார்வைகள்; குருவின் 5, 7, 9 பார்வைகள்; சனியின் 3, 7, 10 பார்வைகள்."
                : "Mars 4,7,8; Jupiter 5,7,9 trinal glances; Saturn 3,7,10 aspects on natal planets."}
            </p>
          </div>

          <button
            type="button"
            onClick={() => setShowAllAspects(!showAllAspects)}
            className="text-xs font-bold text-[#153F6B] hover:text-[#B4872B] flex items-center gap-1 transition-colors cursor-pointer"
          >
            <span>{showAllAspects ? (language === "ta" ? "சுருக்குக" : "Show Less") : (language === "ta" ? "அனைத்தையும் காட்டு" : "View All")}</span>
            {showAllAspects ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {(showAllAspects ? transitAnalysis.aspects : transitAnalysis.aspects.slice(0, 6)).map(
            (asp, idx) => {
              const isBenefic = asp.nature === "benefic";
              const isCaution = asp.nature === "caution";

              return (
                <div
                  key={idx}
                  className={`p-3.5 rounded-xl border text-xs flex items-start gap-3 transition-all ${
                    isBenefic
                      ? "bg-emerald-50/30 border-emerald-200/80"
                      : isCaution
                      ? "bg-rose-50/30 border-rose-200/80"
                      : "bg-slate-50 border-slate-200"
                  }`}
                >
                  <div
                    className={`p-1.5 rounded-lg shrink-0 ${
                      isBenefic
                        ? "bg-emerald-100 text-emerald-800"
                        : isCaution
                        ? "bg-rose-100 text-rose-800"
                        : "bg-slate-200 text-slate-800"
                    }`}
                  >
                    {isBenefic ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : (
                      <AlertTriangle className="w-4 h-4" />
                    )}
                  </div>
                  <div className="space-y-1">
                    <div className="font-bold text-[#183047]">
                      {language === "ta" ? asp.effectTitleTa : asp.effectTitleEn}
                    </div>
                    <div className="text-[#475569] leading-relaxed">
                      {language === "ta" ? asp.descriptionTa : asp.descriptionEn}
                    </div>
                  </div>
                </div>
              );
            }
          )}
        </div>
      </div>

      {/* Collapsible Tirupur GK Enmity & Friendship Matrix */}
      <div className="bg-slate-50 rounded-2xl border border-slate-200 p-4 sm:p-5">
        <button
          type="button"
          onClick={() => setShowEnmityMatrix(!showEnmityMatrix)}
          className="w-full flex items-center justify-between text-left cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4 text-[#153F6B]" />
            <span className="text-xs font-bold text-[#183047]">
              {language === "ta"
                ? "திருப்பூர் ஜிகே அவர்களின் கிரக பகை & நட்பு அட்டவணை"
                : "Tirupur GK Planetary Friendship & Enmity Reference Table"}
            </span>
          </div>
          <span className="text-xs font-bold text-[#153F6B] flex items-center gap-1">
            {showEnmityMatrix ? (language === "ta" ? "மறை" : "Hide") : (language === "ta" ? "காட்டு" : "View")}
            {showEnmityMatrix ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </span>
        </button>

        {showEnmityMatrix && (
          <div className="mt-4 pt-4 border-t border-slate-200 space-y-3">
            <p className="text-xs text-[#52667E]">
              {language === "ta"
                ? "திருப்பூர் ஸ்ரீ எஸ். கோபாலகிருஷ்ணன் அவர்கள் தமது 'Accurate Transit Predictions' நூலில் குறிப்பிட்ட அதிகாரப்பூர்வ பகை கிரகங்கள்:"
                : "Official planetary enemies according to Tirupur S. Gopalakrishnan's treatise:"}
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              {Object.entries(GK_PLANETARY_ENEMIES).map(([planet, enemies]) => (
                <div key={planet} className="p-2.5 bg-white rounded-xl border border-slate-200 text-xs">
                  <span className="font-bold text-[#153F6B] block">
                    {getGrahaName(planet, language)}:
                  </span>
                  <span className="text-rose-700 text-[11px]">
                    {language === "ta" ? "பகை:" : "Enemies:"}{" "}
                    {enemies.map((e) => getGrahaName(e, language)).join(", ")}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
