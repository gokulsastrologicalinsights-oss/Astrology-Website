"use client";

import React, { useState, useMemo } from "react";
import {
  HoroscopeResponse,
  DasaResponse,
  LiveTransitsResponse,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getLordName, getGrahaName, getRasiName } from "@/lib/translations";
import {
  analyzeMarcBoneyComposite,
  MarcBoneyAnalysisResult,
  LifeMilestonePrediction,
  CharaKarakaItem,
  MilestoneDomainKey,
} from "@/lib/marc-boney-composite-engine";
import {
  Compass,
  Sparkles,
  Award,
  Layers,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  TrendingUp,
  Briefcase,
  Coins,
  Heart,
  Baby,
  GraduationCap,
  Home,
  Globe2,
  Flame,
  ChevronDown,
  Clock,
  ChevronUp,
  Copy,
  Check,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  Info,
  Calendar,
  BookOpen,
} from "lucide-react";

interface MarcBoneyMilestonesCardProps {
  horoscope: HoroscopeResponse;
  dasa?: DasaResponse;
  liveTransits?: LiveTransitsResponse | null;
  className?: string;
  defaultTab?: "milestones" | "double_transit" | "chara_karakas" | "beeja_kshetra";
}

export function MarcBoneyMilestonesCard({
  horoscope,
  dasa,
  liveTransits,
  className = "",
  defaultTab = "milestones",
}: MarcBoneyMilestonesCardProps) {
  const { language } = useLanguage();
  const isTa = language === "ta";

  const [activeTab, setActiveTab] = useState<
    "milestones" | "double_transit" | "chara_karakas" | "beeja_kshetra"
  >(defaultTab);

  const [expandedMilestone, setExpandedMilestone] = useState<string | null>("career");
  const [selectedFilter, setSelectedFilter] = useState<string>("all");
  const [copied, setCopied] = useState<boolean>(false);

  // Compute analysis
  const analysis: MarcBoneyAnalysisResult = useMemo(() => {
    return analyzeMarcBoneyComposite(horoscope, dasa, liveTransits);
  }, [horoscope, dasa, liveTransits]);

  const toggleExpand = (id: string) => {
    setExpandedMilestone((prev) => (prev === id ? null : id));
  };

  const getMilestoneIcon = (id: MilestoneDomainKey) => {
    switch (id) {
      case "career":
        return <Briefcase className="w-5 h-5 text-indigo-600" />;
      case "wealth":
        return <Coins className="w-5 h-5 text-emerald-600" />;
      case "marriage":
        return <Heart className="w-5 h-5 text-rose-600" />;
      case "childbirth":
        return <Baby className="w-5 h-5 text-pink-600" />;
      case "education":
        return <GraduationCap className="w-5 h-5 text-amber-600" />;
      case "property":
        return <Home className="w-5 h-5 text-cyan-600" />;
      case "foreign":
        return <Globe2 className="w-5 h-5 text-blue-600" />;
      case "spirituality":
        return <Flame className="w-5 h-5 text-purple-600" />;
      default:
        return <Sparkles className="w-5 h-5 text-amber-600" />;
    }
  };

  const filteredMilestones = useMemo(() => {
    if (selectedFilter === "all") return analysis.milestones;
    if (selectedFilter === "high") {
      return analysis.milestones.filter(
        (m) => m.status === "high_imminent" || m.status === "favorable"
      );
    }
    if (selectedFilter === "double_transit") {
      return analysis.milestones.filter((m) => m.doubleTransit.isFulfilled);
    }
    return analysis.milestones;
  }, [analysis.milestones, selectedFilter]);

  const handleCopySummary = () => {
    const lines: string[] = [];
    if (isTa) {
      lines.push(
        `🏛️ மார்க் போனி & கே.என். ராவ் வாழ்க்கை மைல்கற்கள் பலன் (நடப்பு காலம்: ${getLordName(
          analysis.activeDasaLord,
          language
        )} தசை - ${getLordName(analysis.activeBukthiLord, language)} புக்தி):`
      );
      analysis.milestones.slice(0, 4).forEach((m, idx) => {
        lines.push(
          `${idx + 1}. ${m.domainNameTa}: ${m.readinessScore}% (${m.statusBadgeTa}) - ${
            m.doubleTransit.isFulfilled ? "இரட்டைப் பெயர்ச்சி பூர்த்தி" : "கோச்சார ஆதரவு"
          }`
        );
      });
      lines.push(`\nஆத்ம காரகன்: ${getGrahaName(analysis.charaKarakas[0].planet, language)} (${analysis.charaKarakas[0].formattedDegree})`);
      lines.push(`அமாத்திய காரகன் (தொழில்): ${getGrahaName(analysis.charaKarakas[1].planet, language)}`);
    } else {
      lines.push(
        `🏛️ Marc Boney & K.N. Rao Major Life Milestones (Period: ${analysis.activeDasaLord} Dasa - ${analysis.activeBukthiLord} Bhukti):`
      );
      analysis.milestones.slice(0, 4).forEach((m, idx) => {
        lines.push(
          `${idx + 1}. ${m.domainNameEn}: ${m.readinessScore}% (${m.statusBadgeEn}) - Double Transit: ${
            m.doubleTransit.isFulfilled ? "Sanctioned" : "Partial"
          }`
        );
      });
      lines.push(`\nAtma Karaka (Soul): ${analysis.charaKarakas[0].planet} (${analysis.charaKarakas[0].formattedDegree})`);
      lines.push(`Amatya Karaka (Career): ${analysis.charaKarakas[1].planet}`);
    }

    if (navigator.clipboard) {
      navigator.clipboard.writeText(lines.join("\n"));
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  return (
    <div
      className={`rounded-2xl border border-indigo-200/90 bg-gradient-to-br from-indigo-50/40 via-white to-amber-50/30 p-5 sm:p-7 shadow-sm space-y-6 transition-all ${className}`}
    >
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-indigo-100">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-600 via-purple-600 to-amber-600 text-white text-xs font-bold shadow-xs">
              <Award className="w-3.5 h-3.5" />
              <span>{isTa ? "மார்க் போனி & கே.என். ராவ் கூட்டு முறை" : "Marc Boney & K.N. Rao Composite System"}</span>
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-900 border border-indigo-200 text-xs font-semibold">
              <Compass className="w-3 h-3 text-indigo-700" />
              <span>
                {isTa
                  ? `தசா லக்னம்: ${analysis.dasaLagnaSignNameTa}`
                  : `Dasa Lagna: ${analysis.dasaLagnaSignNameEn}`}
              </span>
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-900 border border-purple-200 text-xs font-semibold">
              <Flame className="w-3 h-3 text-purple-700" />
              <span>
                {isTa
                  ? `காரகாம்சம்: ${analysis.karakamshaSignNameTa}`
                  : `Karakamsha: ${analysis.karakamshaSignNameEn}`}
              </span>
            </span>
          </div>

          <h3 className="text-lg sm:text-xl font-extrabold text-[#183047] flex items-center gap-2">
            <span>
              {isTa
                ? "8 முக்கிய வாழ்க்கை நிகழ்வுகள் முன்கணிப்பு (Major Life Events)"
                : "Predicting 8 Major Life Events & Milestones"}
            </span>
          </h3>
          <p className="text-xs text-[#52667E] max-w-2xl leading-relaxed">
            {isTa
              ? "விம்சForms மகா தசா-புக்தி, தசா லக்னம், கே.என். ராவ் இரட்டைப் பெயர்ச்சி (Saturn & Jupiter Double Transit வக்ர விதி உட்பட) மற்றும் ஜைமினி காரகங்களை இணைக்கும் துல்லிய கணிப்பு."
              : "Composite timing synthesis combining Vimshottari Dasa-Bhukti, Dasa Lagna, K.N. Rao's Double Transit principle (with the Retrograde previous-sign rule), and Jaimini Chara Karakas."}
          </p>
        </div>

        {/* Action button */}
        <div className="flex items-center gap-2 self-start md:self-center">
          <button
            onClick={handleCopySummary}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-indigo-200 bg-white hover:bg-indigo-50 text-indigo-700 text-xs font-semibold shadow-2xs transition-all"
            title="Copy prediction summary"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-emerald-700">{isTa ? "நகலெடுக்கப்பட்டது" : "Copied"}</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>{isTa ? "பகிர்வுக்கு நகலெடு" : "Copy Summary"}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Classical Quote Alert Banner */}
      <div className="rounded-xl border border-amber-200/90 bg-amber-50/70 p-3.5 flex items-start gap-3">
        <BookOpen className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
        <p className="text-xs text-amber-950 italic leading-relaxed">
          {isTa ? analysis.marcBoneyCoreQuoteTa : analysis.marcBoneyCoreQuoteEn}
        </p>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-2 border-b border-indigo-100 overflow-x-auto pb-1 text-xs sm:text-sm font-semibold">
        <button
          onClick={() => setActiveTab("milestones")}
          className={`pb-2.5 px-3.5 rounded-t-lg transition-all whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "milestones"
              ? "border-b-2 border-indigo-600 text-indigo-700 font-bold bg-indigo-50/60"
              : "text-[#52667E] hover:text-[#183047] hover:bg-gray-50"
          }`}
        >
          <Award className="w-4 h-4" />
          <span>{isTa ? "8 முக்கிய மைல்கற்கள்" : "8 Life Milestones"}</span>
        </button>

        <button
          onClick={() => setActiveTab("double_transit")}
          className={`pb-2.5 px-3.5 rounded-t-lg transition-all whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "double_transit"
              ? "border-b-2 border-indigo-600 text-indigo-700 font-bold bg-indigo-50/60"
              : "text-[#52667E] hover:text-[#183047] hover:bg-gray-50"
          }`}
        >
          <Compass className="w-4 h-4" />
          <span>{isTa ? "கே.என். ராவ் இரட்டைப் பெயர்ச்சி ரேடார்" : "Double Transit Radar"}</span>
        </button>

        <button
          onClick={() => setActiveTab("chara_karakas")}
          className={`pb-2.5 px-3.5 rounded-t-lg transition-all whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "chara_karakas"
              ? "border-b-2 border-indigo-600 text-indigo-700 font-bold bg-indigo-50/60"
              : "text-[#52667E] hover:text-[#183047] hover:bg-gray-50"
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>{isTa ? "ஜைமினி 7 சர காரகங்கள்" : "7 Chara Karakas (Jaimini)"}</span>
        </button>

        <button
          onClick={() => setActiveTab("beeja_kshetra")}
          className={`pb-2.5 px-3.5 rounded-t-lg transition-all whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "beeja_kshetra"
              ? "border-b-2 border-indigo-600 text-indigo-700 font-bold bg-indigo-50/60"
              : "text-[#52667E] hover:text-[#183047] hover:bg-gray-50"
          }`}
        >
          <Baby className="w-4 h-4" />
          <span>{isTa ? "பீஜ & ஷேத்ர ஸ்புடம் (சந்ததி பலம்)" : "Beeja & Kshetra Sphuta"}</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: 8 LIFE MILESTONES */}
      {/* ========================================================================= */}
      {activeTab === "milestones" && (
        <div className="space-y-4">
          {/* Filter Pills */}
          <div className="flex items-center justify-between flex-wrap gap-2 text-xs">
            <span className="text-[#52667E] font-medium">
              {isTa ? "வடிகட்டி:" : "Filter by readiness:"}
            </span>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setSelectedFilter("all")}
                className={`px-2.5 py-1 rounded-full font-medium transition-all ${
                  selectedFilter === "all"
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-100 text-[#52667E] hover:bg-gray-200"
                }`}
              >
                {isTa ? "அனைத்தும் (8)" : "All (8)"}
              </button>
              <button
                onClick={() => setSelectedFilter("high")}
                className={`px-2.5 py-1 rounded-full font-medium transition-all ${
                  selectedFilter === "high"
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-100 text-[#52667E] hover:bg-gray-200"
                }`}
              >
                {isTa ? "உயர் வாய்ப்பு (High/Favorable)" : "High / Favorable"}
              </button>
              <button
                onClick={() => setSelectedFilter("double_transit")}
                className={`px-2.5 py-1 rounded-full font-medium transition-all ${
                  selectedFilter === "double_transit"
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-100 text-[#52667E] hover:bg-gray-200"
                }`}
              >
                {isTa ? "இரட்டைப் பெயர்ச்சி பூர்த்தியானது" : "Double Transit Active"}
              </button>
            </div>
          </div>

          {/* Milestones Accordion Grid */}
          <div className="grid grid-cols-1 gap-3.5">
            {filteredMilestones.map((milestone) => {
              const isExp = expandedMilestone === milestone.id;
              const isHigh = milestone.readinessScore >= 80;
              const isFavorable = milestone.readinessScore >= 68 && milestone.readinessScore < 80;

              return (
                <div
                  key={milestone.id}
                  className={`rounded-xl border transition-all ${
                    isExp
                      ? "border-indigo-400 bg-white shadow-md ring-1 ring-indigo-200"
                      : "border-gray-200 bg-white hover:border-indigo-200 hover:shadow-xs"
                  }`}
                >
                  {/* Summary Bar */}
                  <div
                    onClick={() => toggleExpand(milestone.id)}
                    className="p-4 sm:p-4.5 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 select-none"
                  >
                    <div className="flex items-start gap-3.5">
                      <div className="p-2.5 rounded-xl bg-indigo-50/80 border border-indigo-100 shrink-0 mt-0.5">
                        {getMilestoneIcon(milestone.id)}
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4 className="text-sm sm:text-base font-bold text-[#183047]">
                            {isTa ? milestone.domainNameTa : milestone.domainNameEn}
                          </h4>
                          <span className="text-[11px] px-2 py-0.5 rounded-md bg-gray-100 text-gray-700 font-medium">
                            {isTa ? milestone.sanskritTermTa : milestone.sanskritTermEn}
                          </span>
                        </div>

                        <div className="flex items-center gap-2 text-xs text-[#52667E] flex-wrap">
                          <span>
                            {isTa ? "காரக கிரகம்:" : "Karaka:"}{" "}
                            <strong className="text-indigo-900">
                              {milestone.karakasInvolved.jaimini} (
                              {milestone.karakasInvolved.charaRole})
                            </strong>
                          </span>
                          <span>•</span>
                          <span>
                            {isTa ? "தசா-புக்தி:" : "Period:"}{" "}
                            <span
                              className={
                                milestone.dasaBhuktiAlignment.isAligned
                                  ? "text-emerald-700 font-semibold"
                                  : "text-gray-600"
                              }
                            >
                              {milestone.dasaBhuktiAlignment.dasaLord}-
                              {milestone.dasaBhuktiAlignment.bukthiLord}
                            </span>
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Readiness score & status badge */}
                    <div className="flex items-center justify-between sm:justify-end gap-3 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-gray-100">
                      <div className="text-right">
                        <div className="flex items-center gap-2">
                          <span
                            className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
                              isHigh
                                ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                                : isFavorable
                                ? "bg-blue-50 text-blue-800 border-blue-300"
                                : "bg-amber-50 text-amber-800 border-amber-300"
                            }`}
                          >
                            {isTa ? milestone.statusBadgeTa : milestone.statusBadgeEn}
                          </span>
                          <span className="text-sm font-extrabold text-[#183047]">
                            {milestone.readinessScore}%
                          </span>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-28 sm:w-32 bg-gray-100 h-1.5 rounded-full mt-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              isHigh
                                ? "bg-emerald-500"
                                : isFavorable
                                ? "bg-blue-500"
                                : "bg-amber-500"
                            }`}
                            style={{ width: `${milestone.readinessScore}%` }}
                          />
                        </div>
                      </div>

                      <div className="p-1 rounded-full text-gray-400 hover:text-gray-600">
                        {isExp ? (
                          <ChevronUp className="w-5 h-5 text-indigo-600" />
                        ) : (
                          <ChevronDown className="w-5 h-5" />
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Breakdown */}
                  {isExp && (
                    <div className="px-4 pb-5 pt-2 border-t border-indigo-100 space-y-4 text-xs sm:text-sm bg-gradient-to-b from-indigo-50/20 to-white rounded-b-xl">
                      {/* Grid of Key Drivers */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        {/* 1. Dasa-Bhukti Connection */}
                        <div className="rounded-lg border border-indigo-100 bg-white p-3 space-y-1">
                          <div className="flex items-center gap-1.5 text-indigo-800 font-semibold text-xs">
                            <Clock className="w-3.5 h-3.5 text-indigo-600" />
                            <span>{isTa ? "விம்சForms தசா இணைப்பு" : "Vimshottari Dasa-Bhukti"}</span>
                          </div>
                          <p className="text-xs text-[#52667E] leading-relaxed">
                            {isTa
                              ? milestone.dasaBhuktiAlignment.descriptionTa
                              : milestone.dasaBhuktiAlignment.descriptionEn}
                          </p>
                        </div>

                        {/* 2. Double Transit Sanction */}
                        <div
                          className={`rounded-lg border p-3 space-y-1 ${
                            milestone.doubleTransit.isFulfilled
                              ? "border-emerald-200 bg-emerald-50/40"
                              : "border-amber-200 bg-amber-50/40"
                          }`}
                        >
                          <div className="flex items-center gap-1.5 font-semibold text-xs">
                            {milestone.doubleTransit.isFulfilled ? (
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            ) : (
                              <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                            )}
                            <span
                              className={
                                milestone.doubleTransit.isFulfilled
                                  ? "text-emerald-800"
                                  : "text-amber-800"
                              }
                            >
                              {isTa ? "இரட்டைப் பெயர்ச்சி அங்கீகாரம்" : "Double Transit Rule"}
                            </span>
                          </div>
                          <p className="text-xs text-[#52667E] leading-relaxed">
                            {isTa
                              ? milestone.doubleTransit.summaryTa
                              : milestone.doubleTransit.summaryEn}
                          </p>
                        </div>

                        {/* 3. Dasa Lagna Insight */}
                        <div className="rounded-lg border border-indigo-100 bg-white p-3 space-y-1">
                          <div className="flex items-center gap-1.5 text-indigo-800 font-semibold text-xs">
                            <Compass className="w-3.5 h-3.5 text-indigo-600" />
                            <span>{isTa ? "தசா லக்ன ஆய்வு" : "Dasa Lagna Perspective"}</span>
                          </div>
                          <p className="text-xs text-[#52667E] leading-relaxed">
                            {isTa
                              ? milestone.dasaLagnaInsight.insightTa
                              : milestone.dasaLagnaInsight.insightEn}
                          </p>
                        </div>
                      </div>

                      {/* Divisional Chart (Varga) Confirmation */}
                      <div className="rounded-lg border border-purple-100 bg-purple-50/40 p-3 flex items-start gap-2.5">
                        <Layers className="w-4 h-4 text-purple-700 shrink-0 mt-0.5" />
                        <div className="space-y-0.5">
                          <span className="text-xs font-bold text-purple-900">
                            {isTa
                              ? `${milestone.divisionalCheck.vargaNameTa} சரிபார்ப்பு`
                              : `${milestone.divisionalCheck.vargaNameEn} Cross-Verification`}
                          </span>
                          <p className="text-xs text-purple-950 leading-relaxed">
                            {isTa
                              ? milestone.divisionalCheck.focalPointTa
                              : milestone.divisionalCheck.focalPointEn}
                          </p>
                        </div>
                      </div>

                      {/* Classical Rules Cited from Marc Boney & K.N. Rao */}
                      <div className="space-y-1.5">
                        <span className="text-[11px] font-bold text-[#183047] uppercase tracking-wide">
                          {isTa ? "நூலின் மூல விதிகள் (Classical Citations):" : "Classical Principles Applied:"}
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                          {(isTa
                            ? milestone.classicalRulesCitedTa
                            : milestone.classicalRulesCitedEn
                          ).map((rule, idx) => (
                            <div
                              key={idx}
                              className="rounded-md bg-gray-50 border border-gray-200/80 p-2.5 text-[#52667E] italic flex items-start gap-2"
                            >
                              <span className="text-indigo-600 font-bold shrink-0">§</span>
                              <span>{rule}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Actionable Predictive Guidance */}
                      <div className="rounded-xl border border-indigo-200 bg-gradient-to-r from-indigo-50/80 to-blue-50/60 p-3.5 flex items-start gap-3">
                        <Sparkles className="w-4 h-4 text-indigo-700 shrink-0 mt-0.5" />
                        <div className="space-y-0.5">
                          <span className="text-xs font-bold text-indigo-950">
                            {isTa ? "செயல்முறை வழிகாட்டல் (Actionable Guidance):" : "Predictive Timing Guidance:"}
                          </span>
                          <p className="text-xs text-indigo-900 font-medium leading-relaxed">
                            {isTa ? milestone.predictiveGuidanceTa : milestone.predictiveGuidanceEn}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: K.N. RAO DOUBLE TRANSIT RADAR */}
      {/* ========================================================================= */}
      {activeTab === "double_transit" && (
        <div className="space-y-5">
          <div className="rounded-xl border border-blue-200 bg-blue-50/60 p-4 space-y-2">
            <h4 className="text-sm font-bold text-blue-950 flex items-center gap-2">
              <Compass className="w-4 h-4 text-blue-700" />
              <span>
                {isTa
                  ? "கே.என். ராவ் இரட்டைப் பெயர்ச்சி கோட்பாடு (Double Transit Principle)"
                  : "K.N. Rao's Golden Double Transit Axiom"}
              </span>
            </h4>
            <p className="text-xs text-blue-900 leading-relaxed">
              {isTa
                ? "எந்தவொரு முக்கிய நிகழ்வும் பௌதீகமாக நடைபெற வேண்டுமெனில், சனியும் குருவும் ஒரே நேரத்தில் அந்த வீட்டை அல்லது வீட்டின் அதிபதியை தங்கள் நேரடி பார்வை அல்லது வக்ர பார்வையால் தொட வேண்டும். வக்ரமான கிரகம் தான் இருக்கும் ராசியிலிருந்தும், தனக்கு முந்தைய ராசியிலிருந்தும் (Retrograde Preceding Sign) பார்வைகளை வீசும் என்ற கே.என். ராவ் அவர்களின் வரலாற்றுச் சிறப்புமிக்க கண்டுபிடிப்பு இங்கு துல்லியமாக இணைக்கப்பட்டுள்ளது."
                : "No major event manifests in concrete reality unless both Saturn and Jupiter concurrently cast their influence upon the relevant house or house lord. Crucially, as discovered and taught by Shri K.N. Rao, when Saturn or Jupiter is retrograde in transit, it casts its potent aspects not only from its transit sign, but also from the preceding sign (1 sign backward)!"}
            </p>
          </div>

          {/* Saturn & Jupiter live transit aspect grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Saturn Transit */}
            <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3 shadow-2xs">
              <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-blue-50 text-blue-700 font-bold text-xs">
                    ♄
                  </span>
                  <div>
                    <h5 className="text-sm font-bold text-[#183047]">
                      {isTa ? "கோச்சார சனி பகவான்" : "Transiting Saturn"}
                    </h5>
                    <span className="text-xs text-[#52667E]">
                      {isTa ? "கர்ம முத்திரை & கட்டமைப்பு" : "Karmic Seal & Manifestation"}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="inline-block px-2 py-0.5 rounded-md text-xs font-bold bg-blue-100 text-blue-900">
                    {isTa
                      ? analysis.saturnTransitDetail.currentSignNameTa
                      : analysis.saturnTransitDetail.currentSignNameEn}
                  </span>
                  {analysis.saturnTransitDetail.isRetrograde && (
                    <span className="block text-[11px] text-amber-600 font-semibold">
                      {isTa ? "வக்ரம் (Retrograde)" : "Retrograde (Rx)"}
                    </span>
                  )}
                </div>
              </div>

              <div className="space-y-1.5 text-xs">
                <span className="text-[11px] font-bold text-gray-500 uppercase">
                  {isTa ? "சனி பார்வை படும் ராசிகள்:" : "Signs Influenced by Saturn's Aspects:"}
                </span>
                <div className="space-y-1">
                  {analysis.saturnTransitDetail.aspectsCastingOnSigns.map((asp, i) => (
                    <div
                      key={i}
                      className={`flex items-center justify-between p-2 rounded-lg text-xs ${
                        asp.isFromRetrogradePrecedingSign
                          ? "bg-amber-50/70 border border-amber-200 text-amber-900"
                          : "bg-gray-50 text-gray-800"
                      }`}
                    >
                      <span className="font-semibold">{asp.signNameEn}</span>
                      <span className="text-[11px] text-[#52667E]">{asp.aspectType}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Jupiter Transit */}
            <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3 shadow-2xs">
              <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-amber-50 text-amber-700 font-bold text-xs">
                    ♃
                  </span>
                  <div>
                    <h5 className="text-sm font-bold text-[#183047]">
                      {isTa ? "கோச்சார குரு பகவான்" : "Transiting Jupiter"}
                    </h5>
                    <span className="text-xs text-[#52667E]">
                      {isTa ? "தெய்வீக ஆசி & அருள்" : "Divine Grace & Protection"}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="inline-block px-2 py-0.5 rounded-md text-xs font-bold bg-amber-100 text-amber-900">
                    {isTa
                      ? analysis.jupiterTransitDetail.currentSignNameTa
                      : analysis.jupiterTransitDetail.currentSignNameEn}
                  </span>
                  {analysis.jupiterTransitDetail.isRetrograde && (
                    <span className="block text-[11px] text-amber-600 font-semibold">
                      {isTa ? "வக்ரம் (Retrograde)" : "Retrograde (Rx)"}
                    </span>
                  )}
                </div>
              </div>

              <div className="space-y-1.5 text-xs">
                <span className="text-[11px] font-bold text-gray-500 uppercase">
                  {isTa ? "குரு பார்வை படும் ராசிகள்:" : "Signs Influenced by Jupiter's Aspects:"}
                </span>
                <div className="space-y-1">
                  {analysis.jupiterTransitDetail.aspectsCastingOnSigns.map((asp, i) => (
                    <div
                      key={i}
                      className={`flex items-center justify-between p-2 rounded-lg text-xs ${
                        asp.isFromRetrogradePrecedingSign
                          ? "bg-amber-50/70 border border-amber-200 text-amber-900"
                          : "bg-gray-50 text-gray-800"
                      }`}
                    >
                      <span className="font-semibold">{asp.signNameEn}</span>
                      <span className="text-[11px] text-[#52667E]">{asp.aspectType}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: JAIMINI 7 CHARA KARAKAS */}
      {/* ========================================================================= */}
      {activeTab === "chara_karakas" && (
        <div className="space-y-4">
          <div className="rounded-xl border border-purple-200 bg-purple-50/50 p-4 space-y-1.5">
            <h4 className="text-sm font-bold text-purple-950 flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-700" />
              <span>
                {isTa
                  ? "ஜைமினி 7 சர காரகங்கள் & காரகாம்சம்"
                  : "Jaimini 7 Chara Karakas Hierarchy"}
              </span>
            </h4>
            <p className="text-xs text-purple-900 leading-relaxed">
              {isTa
                ? "சூரியன் முதல் சனி வரையிலான 7 பௌதீக கிரகங்களின் பாகை அளவுகளை இறங்குமுக வரிசையில் அமைத்து, ஆத்ம காரகன் முதல் தார காரகன் வரையிலான வாழ்க்கை வழிகாட்டிகளை மார்க் போனி முறையில் பகுப்பாய்வு செய்கிறோம்."
                : "The 7 physical planets (Sun through Saturn) ordered by descending degrees within their respective signs. Atma Karaka (AK) rules the soul, Amatya Karaka (AmK) commands the career, and Dara Karaka (DK) designates the marriage partner."}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {analysis.charaKarakas.map((karaka) => (
              <div
                key={karaka.role}
                className="rounded-xl border border-gray-200 bg-white p-3.5 space-y-2 hover:border-purple-300 hover:shadow-xs transition-all"
              >
                <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                  <span className="px-2 py-0.5 rounded-md bg-purple-100 text-purple-900 font-extrabold text-xs">
                    {karaka.role}
                  </span>
                  <span className="text-xs font-bold text-[#183047]">
                    {getGrahaName(karaka.planet, language)}
                  </span>
                </div>

                <div className="space-y-1">
                  <h5 className="text-xs font-bold text-indigo-950">
                    {isTa ? karaka.roleNameTa : karaka.roleNameEn}
                  </h5>
                  <div className="flex items-center justify-between text-xs text-[#52667E]">
                    <span>
                      {isTa ? karaka.signNameTa : karaka.signNameEn} ({karaka.house}-ம் வீடு)
                    </span>
                    <span className="font-mono font-semibold text-gray-700">
                      {karaka.formattedDegree}
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-600 pt-1 leading-snug">
                    {isTa ? karaka.significationTa : karaka.significationEn}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Special Composite Yogas Highlight */}
          <div className="rounded-xl border border-indigo-100 bg-white p-4 space-y-3">
            <h5 className="text-xs font-bold text-[#183047] uppercase tracking-wide">
              {isTa ? "கூட்டு யோகங்கள் & ஆருட பாதங்கள்:" : "Special Yogas & Arudha Padas:"}
            </h5>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg border border-gray-100 bg-gray-50/60 space-y-1">
                <span className="font-bold text-indigo-900 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                  <span>{isTa ? "உபபத லக்னம் (UL)" : "Upapada Lagna (UL / Marriage Arudha)"}</span>
                </span>
                <p className="text-gray-700">
                  {isTa
                    ? `${analysis.specialYogas.upapadaLagna.signNameTa} ராசி (${analysis.specialYogas.upapadaLagna.houseNumber}-ம் வீடு)`
                    : `${analysis.specialYogas.upapadaLagna.signNameEn} (House ${analysis.specialYogas.upapadaLagna.houseNumber})`}
                </p>
              </div>

              <div className="p-3 rounded-lg border border-gray-100 bg-gray-50/60 space-y-1">
                <span className="font-bold text-indigo-900 flex items-center gap-1.5">
                  <Coins className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{isTa ? "லாப ஆருடம் (A11 / தன பாதம்)" : "Arudha Pada 11 (A11 / Wealth Gains)"}</span>
                </span>
                <p className="text-gray-700">
                  {isTa
                    ? `${analysis.specialYogas.arudhaPada11.signNameTa} ராசி (${analysis.specialYogas.arudhaPada11.houseNumber}-ம் வீடு)`
                    : `${analysis.specialYogas.arudhaPada11.signNameEn} (House ${analysis.specialYogas.arudhaPada11.houseNumber})`}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: BEEJA & KSHETRA SPHUTA */}
      {/* ========================================================================= */}
      {activeTab === "beeja_kshetra" && (
        <div className="space-y-4">
          <div className="rounded-xl border border-pink-200 bg-pink-50/50 p-4 space-y-1.5">
            <h4 className="text-sm font-bold text-pink-950 flex items-center gap-2">
              <Baby className="w-4 h-4 text-pink-700" />
              <span>
                {isTa
                  ? "பீஜ & ஷேத்ர ஸ்புடம்: சந்தான வீரியம் மற்றும் கருப்பை ஏற்புத்திறன்"
                  : "Beeja & Kshetra Sphuta: Classical Fertility Mechanics"}
              </span>
            </h4>
            <p className="text-xs text-pink-900 leading-relaxed">
              {isTa
                ? "பராசர மகரிஷி மற்றும் மார்க் போனி நூலின்படி, விந்து வீரியத்தை நிர்ணயிக்க பீஜ ஸ்புடமும் (சூரியன் + சுக்கிரன் + குரு), கருப்பை ஏற்புத்திறனை கணிக்க ஷேத்ர ஸ்புடமும் (சந்திரன் + செவ்வாய் + குரு) பயன்படுத்தப்படுகின்றன. ஒற்றை/இரட்டை ராசி மற்றும் நவாம்சப் பொருத்தங்கள் இங்கே கணக்கிடப்பட்டுள்ளன."
                : "According to Maharishi Parashara and detailed in Marc Boney's work, Beeja Sphuta (Sun + Venus + Jupiter) measures male procreative vitality, while Kshetra Sphuta (Moon + Mars + Jupiter) calculates female procreative receptivity. Odd/Even sign and Navamsha harmonics reveal natural fertility readiness."}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Beeja Sphuta Card */}
            <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3 shadow-2xs">
              <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                <span className="font-bold text-sm text-[#183047] flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-amber-600" />
                  <span>{isTa ? "பீஜ ஸ்புடம் (Beeja Sphuta)" : "Beeja Sphuta (Male Potency)"}</span>
                </span>
                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
                  {analysis.beejaKshetra.beejaSphuta.vitalityScore}%
                </span>
              </div>

              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between text-[#52667E]">
                  <span>{isTa ? "ராசி நிலை:" : "Zodiac Sign:"}</span>
                  <strong className="text-gray-900">
                    {isTa
                      ? analysis.beejaKshetra.beejaSphuta.signNameTa
                      : analysis.beejaKshetra.beejaSphuta.signNameEn}{" "}
                    ({analysis.beejaKshetra.beejaSphuta.formattedDegree})
                  </strong>
                </div>

                <div className="flex justify-between text-[#52667E]">
                  <span>{isTa ? "நவாம்ச ராசி:" : "Navamsha Sign:"}</span>
                  <strong className="text-gray-900">
                    {isTa
                      ? analysis.beejaKshetra.beejaSphuta.navamshaSignNameTa
                      : analysis.beejaKshetra.beejaSphuta.navamshaSignNameEn}
                  </strong>
                </div>

                <div className="flex justify-between text-[#52667E]">
                  <span>{isTa ? "ராசி/நவாம்ச இயல்பு:" : "Sign / Navamsha Nature:"}</span>
                  <span className="font-semibold text-indigo-700">
                    {analysis.beejaKshetra.beejaSphuta.isSignOdd ? "Odd (ஆண்)" : "Even (பெண்)"} /{" "}
                    {analysis.beejaKshetra.beejaSphuta.isNavamshaOdd ? "Odd (ஆண்)" : "Even (பெண்)"}
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-amber-50/70 border border-amber-200/80 text-[#183047] text-xs leading-relaxed mt-2">
                  {isTa
                    ? analysis.beejaKshetra.beejaSphuta.potencyVerdictTa
                    : analysis.beejaKshetra.beejaSphuta.potencyVerdictEn}
                </div>
              </div>
            </div>

            {/* Kshetra Sphuta Card */}
            <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3 shadow-2xs">
              <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                <span className="font-bold text-sm text-[#183047] flex items-center gap-1.5">
                  <Baby className="w-4 h-4 text-pink-600" />
                  <span>{isTa ? "ஷேத்ர ஸ்புடம் (Kshetra Sphuta)" : "Kshetra Sphuta (Female Soil)"}</span>
                </span>
                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-pink-100 text-pink-800">
                  {analysis.beejaKshetra.kshetraSphuta.vitalityScore}%
                </span>
              </div>

              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between text-[#52667E]">
                  <span>{isTa ? "ராசி நிலை:" : "Zodiac Sign:"}</span>
                  <strong className="text-gray-900">
                    {isTa
                      ? analysis.beejaKshetra.kshetraSphuta.signNameTa
                      : analysis.beejaKshetra.kshetraSphuta.signNameEn}{" "}
                    ({analysis.beejaKshetra.kshetraSphuta.formattedDegree})
                  </strong>
                </div>

                <div className="flex justify-between text-[#52667E]">
                  <span>{isTa ? "நவாம்ச ராசி:" : "Navamsha Sign:"}</span>
                  <strong className="text-gray-900">
                    {isTa
                      ? analysis.beejaKshetra.kshetraSphuta.navamshaSignNameTa
                      : analysis.beejaKshetra.kshetraSphuta.navamshaSignNameEn}
                  </strong>
                </div>

                <div className="flex justify-between text-[#52667E]">
                  <span>{isTa ? "ராசி/நவாம்ச இயல்பு:" : "Sign / Navamsha Nature:"}</span>
                  <span className="font-semibold text-pink-700">
                    {analysis.beejaKshetra.kshetraSphuta.isSignEven ? "Even (பெண்)" : "Odd (ஆண்)"} /{" "}
                    {analysis.beejaKshetra.kshetraSphuta.isNavamshaEven ? "Even (பெண்)" : "Odd (ஆண்)"}
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-pink-50/70 border border-pink-200/80 text-[#183047] text-xs leading-relaxed mt-2">
                  {isTa
                    ? analysis.beejaKshetra.kshetraSphuta.receptivityVerdictTa
                    : analysis.beejaKshetra.kshetraSphuta.receptivityVerdictEn}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
