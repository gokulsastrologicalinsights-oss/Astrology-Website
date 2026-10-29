"use client";

import React, { useState, useMemo } from "react";
import {
  HoroscopeResponse,
  DasaResponse,
  LiveTransitsResponse,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getLordName, getGrahaName } from "@/lib/translations";
import {
  analyzeRecent15DayEvents,
  Recent15DayAnalysisResult,
  RecentPastEventPoint,
} from "@/lib/recent-15day-events-engine";
import {
  Sparkles,
  Calendar,
  Clock,
  CheckCircle2,
  HelpCircle,
  XCircle,
  Copy,
  Check,
  TrendingUp,
  HeartPulse,
  Users,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Info,
  Flame,
  Award,
} from "lucide-react";

interface Recent15DayPastEventsCardProps {
  horoscope: HoroscopeResponse;
  dasa?: DasaResponse;
  liveTransits?: LiveTransitsResponse | null;
  className?: string;
  defaultExpanded?: boolean;
}

export function Recent15DayPastEventsCard({
  horoscope,
  dasa,
  liveTransits,
  className = "",
  defaultExpanded = true,
}: Recent15DayPastEventsCardProps) {
  const { language } = useLanguage();
  const isTa = language === "ta";

  const [isExpanded, setIsExpanded] = useState<boolean>(defaultExpanded);
  const [copied, setCopied] = useState<boolean>(false);

  // User client verification state (key: pointId -> 'yes' | 'partial' | 'no')
  const [feedback, setFeedback] = useState<Record<string, "yes" | "partial" | "no">>({});

  // Run the 15-day past events engine
  const analysis: Recent15DayAnalysisResult = useMemo(() => {
    return analyzeRecent15DayEvents(horoscope, dasa, liveTransits, new Date());
  }, [horoscope, dasa, liveTransits]);

  const handleFeedback = (id: string, value: "yes" | "partial" | "no") => {
    setFeedback((prev) => ({
      ...prev,
      [id]: prev[id] === value ? (undefined as any) : value,
    }));
  };

  // Count feedback tally
  const confirmedCount = Object.values(feedback).filter((v) => v === "yes").length;
  const partialCount = Object.values(feedback).filter((v) => v === "partial").length;

  const handleCopySummary = () => {
    const text = isTa
      ? `🔮 வாக்கு பலிதம் - கடந்த 15 நாட்களில் நிகழ்ந்த 3 முக்கிய நிகழ்வுகள் (${analysis.windowFormattedTa}):\n\n` +
        `1. ${analysis.points[0].headlineTa}\n👉 ${analysis.points[0].questionPromptTa}\n\n` +
        `2. ${analysis.points[1].headlineTa}\n👉 ${analysis.points[1].questionPromptTa}\n\n` +
        `3. ${analysis.points[2].headlineTa}\n👉 ${analysis.points[2].questionPromptTa}\n\n` +
        `நடைபெறும் காலம்: ${getLordName(analysis.activeDasaLord, language)} திசை - ${getLordName(analysis.activeBukthiLord, language)} புக்தி - ${getLordName(analysis.activeAndharaLord, language)} அந்திரம்.`
      : `🔮 Astrological Verification - 3 Key Events in Past 15 Days (${analysis.windowFormattedEn}):\n\n` +
        `1. ${analysis.points[0].headlineEn}\n👉 ${analysis.points[0].questionPromptEn}\n\n` +
        `2. ${analysis.points[1].headlineEn}\n👉 ${analysis.points[1].questionPromptEn}\n\n` +
        `3. ${analysis.points[2].headlineEn}\n👉 ${analysis.points[2].questionPromptEn}\n\n` +
        `Active Timing: ${analysis.activeDasaLord} Dasa - ${analysis.activeBukthiLord} Bhukti - ${analysis.activeAndharaLord} Andhara.`;

    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  return (
    <div
      className={`rounded-2xl border border-amber-300/80 bg-gradient-to-br from-amber-50/70 via-white to-orange-50/40 p-5 sm:p-6 shadow-sm space-y-4 transition-all ${className}`}
    >
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-amber-200/80">
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gradient-to-r from-amber-600 to-orange-600 text-white text-xs font-bold shadow-2xs">
              <Sparkles className="w-3.5 h-3.5 animate-spin" />
              <span>{isTa ? "வாக்கு பலிதம் (உடனடி சரிபார்ப்பு)" : "Astrological Flashback Verification"}</span>
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300 text-[11px] font-semibold">
              <Calendar className="w-3 h-3 text-amber-700" />
              <span>{isTa ? analysis.windowFormattedTa : analysis.windowFormattedEn}</span>
            </span>
          </div>

          <h3 className="text-base sm:text-lg font-extrabold text-[#183047] flex items-center gap-2">
            <span>
              {isTa
                ? "கடந்த 15 நாட்களில் நிகழ்ந்த முக்கிய 3 நிகழ்வுகள்"
                : "3 Strong Events Occurred in the Past 15 Days"}
            </span>
          </h3>

          <p className="text-xs text-[#6B511F] leading-relaxed max-w-2xl">
            {isTa
              ? `ஜாதகர் உங்களிடம் வந்ததும், நடப்பு ${getLordName(analysis.activeDasaLord, language)} திசை – ${getLordName(analysis.activeBukthiLord, language)} புக்தி – ${getLordName(analysis.activeAndharaLord, language)} அந்திரம் மற்றும் 15 நாள் சந்திர கோச்சாரத்தின்படி அவரது வாழ்வில் நிகழ்ந்த இந்த 3 சம்பவங்களை கேட்டு உறுதிப்படுத்தவும்.`
              : `Confirm these 3 specific events with the customer from the running ${analysis.activeDasaLord} Dasa – ${analysis.activeBukthiLord} Bhukti – ${analysis.activeAndharaLord} Andhara and fortnightly lunar transits.`}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 self-start sm:self-auto shrink-0">
          <button
            type="button"
            onClick={handleCopySummary}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-amber-200 hover:bg-amber-100/70 text-[#8C6D23] text-xs font-bold transition-all shadow-2xs cursor-pointer"
            title={isTa ? "வாடிக்கையாளருக்கு அனுப்ப நகலெடு" : "Copy for consultation"}
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-emerald-700">{isTa ? "நகலெடுக்கப்பட்டது!" : "Copied!"}</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-[#B4872B]" />
                <span>{isTa ? "நகலெடு" : "Copy"}</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 rounded-xl bg-white border border-amber-200 text-[#8C6D23] hover:bg-amber-100/70 transition-all shadow-2xs cursor-pointer"
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Verification Tally Pill (if user checked items) */}
      {(confirmedCount > 0 || partialCount > 0) && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-emerald-900 font-bold">
            <Award className="w-4 h-4 text-emerald-600" />
            <span>
              {isTa
                ? `வாக்கு பலித சரிபார்ப்பு: ${confirmedCount} முழுமை + ${partialCount} பகுதி பொருத்தம் (${Math.round(
                    ((confirmedCount + partialCount * 0.5) / 3) * 100
                  )}% உறுதி)`
                : `Flashback Verified: ${confirmedCount} Exact + ${partialCount} Partial (${Math.round(
                    ((confirmedCount + partialCount * 0.5) / 3) * 100
                  )}% Match)`}
            </span>
          </div>
          <span className="text-[11px] text-emerald-700 italic">
            {isTa ? "சாஸ்திர கணிப்பு துல்லியம் உறுதியானது" : "Predictive Accuracy Confirmed"}
          </span>
        </div>
      )}

      {/* 3 Points Container */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
          {analysis.points.map((pt) => {
            const currentFeedback = feedback[pt.id];

            const categoryIcon =
              pt.category === "finance_career" ? (
                <TrendingUp className="w-4 h-4 text-amber-700" />
              ) : pt.category === "health_body" ? (
                <HeartPulse className="w-4 h-4 text-rose-600" />
              ) : (
                <Users className="w-4 h-4 text-blue-600" />
              );

            const categoryBg =
              pt.category === "finance_career"
                ? "bg-amber-100/80 text-amber-900 border-amber-200"
                : pt.category === "health_body"
                ? "bg-rose-100/80 text-rose-900 border-rose-200"
                : "bg-blue-100/80 text-blue-900 border-blue-200";

            return (
              <div
                key={pt.id}
                className="rounded-xl border border-amber-200/90 bg-white p-4 flex flex-col justify-between space-y-3 shadow-2xs hover:shadow-xs transition-all relative overflow-hidden"
              >
                <div className="space-y-2">
                  {/* Category Pill & Point Number */}
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${categoryBg}`}
                    >
                      {categoryIcon}
                      <span>{isTa ? pt.categoryLabelTa : pt.categoryLabelEn}</span>
                    </span>

                    <span className="w-5 h-5 rounded-full bg-[#153F6B] text-white text-[10px] font-bold inline-flex items-center justify-center shrink-0">
                      {pt.pointNumber}
                    </span>
                  </div>

                  {/* Headline */}
                  <h4 className="text-xs sm:text-sm font-bold text-[#183047] leading-snug">
                    {isTa ? pt.headlineTa : pt.headlineEn}
                  </h4>

                  {/* Question Prompt */}
                  <div className="p-2.5 bg-amber-50/60 border border-amber-200/60 rounded-lg">
                    <p className="text-xs text-[#5C4314] font-semibold leading-relaxed">
                      👉 "{isTa ? pt.questionPromptTa : pt.questionPromptEn}"
                    </p>
                  </div>

                  {/* Verifiable details */}
                  <ul className="text-[11px] text-[#475569] space-y-1 pt-1">
                    {(isTa ? pt.verifiableIncidentsTa : pt.verifiableIncidentsEn).map((inc, i) => (
                      <li key={i} className="flex items-start gap-1.5 leading-relaxed">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#B4872B] mt-1.5 shrink-0" />
                        <span>{inc}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Footer: Astrological Root & Interactive Verification Pills */}
                <div className="pt-2 border-t border-slate-100 space-y-2.5">
                  <div className="text-[10px] text-[#64748B] italic leading-tight">
                    <span className="font-semibold text-[#153F6B]">
                      {isTa ? "சாஸ்திர காரகம்: " : "Astrological Root: "}
                    </span>
                    {isTa ? pt.astrologicalReasonTa : pt.astrologicalReasonEn}
                  </div>

                  {/* Interactive Verification Buttons */}
                  <div className="space-y-1">
                    <div className="text-[10px] font-bold text-[#8190A6] uppercase tracking-wider">
                      {isTa ? "வாடிக்கையாளர் சரிபார்ப்பு:" : "Client Verification:"}
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <button
                        type="button"
                        onClick={() => handleFeedback(pt.id, "yes")}
                        className={`px-2 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer flex items-center justify-center gap-1 ${
                          currentFeedback === "yes"
                            ? "bg-emerald-600 text-white shadow-2xs"
                            : "bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-200/60"
                        }`}
                      >
                        <CheckCircle2 className="w-3 h-3" />
                        <span>{isTa ? "ஆம்" : "Yes"}</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleFeedback(pt.id, "partial")}
                        className={`px-2 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer flex items-center justify-center gap-1 ${
                          currentFeedback === "partial"
                            ? "bg-amber-600 text-white shadow-2xs"
                            : "bg-amber-50 text-amber-800 hover:bg-amber-100 border border-amber-200/60"
                        }`}
                      >
                        <HelpCircle className="w-3 h-3" />
                        <span>{isTa ? "ஓரளவு" : "Partial"}</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleFeedback(pt.id, "no")}
                        className={`px-2 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer flex items-center justify-center gap-1 ${
                          currentFeedback === "no"
                            ? "bg-rose-600 text-white shadow-2xs"
                            : "bg-rose-50 text-rose-800 hover:bg-rose-100 border border-rose-200/60"
                        }`}
                      >
                        <XCircle className="w-3 h-3" />
                        <span>{isTa ? "இல்லை" : "No"}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Bottom Aphorism */}
      {isExpanded && (
        <div className="pt-2 text-center">
          <p className="text-[11px] text-[#8C6D23] italic font-medium">
            "{isTa ? analysis.summaryAphorismTa : analysis.summaryAphorismEn}"
          </p>
        </div>
      )}
    </div>
  );
}
