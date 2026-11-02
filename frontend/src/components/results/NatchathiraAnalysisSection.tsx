"use client";

import React, { useState, useMemo } from "react";
import { useLanguage } from "@/lib/i18n";
import {
  NatchathiraDeepAnalysisResult,
  NatchathiraMatchedRule,
  NatchathiraAgeMilestone,
} from "@/lib/types";
import {
  Sparkles,
  AlertTriangle,
  Clock,
  Compass,
  Footprints,
  ShieldCheck,
  Award,
  BookOpen,
  Filter,
  CheckCircle2,
  Calendar,
  Layers,
  Heart,
  Cpu,
  Flame,
  Zap,
  Info,
} from "lucide-react";

interface NatchathiraAnalysisSectionProps {
  analysis: NatchathiraDeepAnalysisResult | null;
  nativeName?: string;
  birthDate?: string;
  isLoading?: boolean;
}

export function NatchathiraAnalysisSection({
  analysis,
  nativeName,
  birthDate,
}: NatchathiraAnalysisSectionProps) {
  const { language } = useLanguage();
  const isTa = language === "ta";

  const [activeFilter, setActiveFilter] = useState<
    "ALL" | "CRITICAL_CAUTION" | "IMPORTANT_MILESTONE" | "LIFE_LESSON" | "POSITIVE_TALENT" | "VASTU_HEALTH"
  >("ALL");

  const [expandedRule, setExpandedRule] = useState<string | null>(null);

  if (!analysis || !analysis.valid) {
    return (
      <div className="rounded-2xl border border-[#D9DEE7] bg-white p-8 text-center space-y-3">
        <Sparkles className="w-8 h-8 text-[#B4872B] mx-auto animate-pulse" />
        <h3 className="text-base font-bold text-[#183047]">
          {isTa ? "நட்சத்திர ஆய்வு கணக்கிடப்படுகிறது..." : "Calculating Natchathira Analysis..."}
        </h3>
        <p className="text-xs text-[#8190A6] max-w-md mx-auto">
          {isTa
            ? "சப்தரிஷி ஜோதிட ஆராய்ச்சி விதிகளின்படி இந்த ஜாதகத்திற்கான நட்சத்திர நுணுக்கங்கள் ஆராயப்படுகின்றன."
            : "Synthesizing deep constellational rules and conditions from Saptarishis research for this chart."}
        </p>
      </div>
    );
  }

  const {
    active_nakshatras_summary = [],
    total_rules_matched = 0,
    critical_cautions_count = 0,
    milestones_count = 0,
    soul_lessons_count = 0,
    matched_rules = [],
    age_milestones = [],
    vastu_advisories = [],
    body_part_alerts = [],
    native_age,
  } = analysis;

  const filteredRules = useMemo(() => {
    if (activeFilter === "ALL") return matched_rules;
    if (activeFilter === "VASTU_HEALTH") {
      return matched_rules.filter(
        (r) =>
          r.category === "VASTU_REMEDY" ||
          r.category === "MEDICAL_VULNERABILITY" ||
          r.category === "DIET_HABITS" ||
          r.category === "DIET_HEALTH"
      );
    }
    return matched_rules.filter((r) => r.severity === activeFilter);
  }, [matched_rules, activeFilter]);

  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <div className="rounded-2xl border border-[#B4872B]/30 bg-gradient-to-r from-[#0F2942] via-[#153F6B] to-[#1E4D80] text-white p-5 sm:p-6 shadow-md relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-48 h-48 rounded-full bg-[#B4872B]/10 blur-2xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-[#B4872B]/20 text-[#EAD08D] border border-[#B4872B]/40">
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isTa ? "சப்தரிஷி நட்சத்திர ஆராய்ச்சி முறை" : "Saptarishis Empirical Nakshatra System"}</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
              {isTa ? "நட்சத்திர ஆழ்ந்த ஆய்வு பலன்கள்" : "In-Depth Natchathira Analysis"}
              {nativeName && <span className="text-[#EAD08D] text-lg font-normal ml-2">({nativeName})</span>}
            </h2>
            <p className="text-xs sm:text-sm text-slate-200/90 max-w-2xl leading-relaxed">
              {isTa ? analysis.summary_ta : analysis.summary_en}
            </p>
          </div>

          {native_age !== undefined && native_age !== null && (
            <div className="shrink-0 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl px-4 py-3 text-center">
              <div className="text-[11px] text-slate-300 uppercase tracking-wider font-semibold">
                {isTa ? "தற்போதைய வயது" : "Current Age"}
              </div>
              <div className="text-2xl font-black text-[#EAD08D]">{native_age}</div>
              <div className="text-[10px] text-slate-300">{isTa ? "ஆண்டுகள்" : "Years"}</div>
            </div>
          )}
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3 mt-5 pt-4 border-t border-white/10">
          <div className="rounded-xl bg-white/5 border border-white/10 p-2.5 text-center">
            <div className="text-xs text-slate-300 font-medium">{isTa ? "மொத்த விதிகள்" : "Active Rules"}</div>
            <div className="text-xl font-bold text-white mt-0.5">{total_rules_matched}</div>
          </div>
          <div className="rounded-xl bg-rose-500/10 border border-rose-400/20 p-2.5 text-center">
            <div className="text-xs text-rose-200 font-medium">{isTa ? "முக்கிய எச்சரிக்கை" : "Key Cautions"}</div>
            <div className="text-xl font-bold text-rose-300 mt-0.5">{critical_cautions_count}</div>
          </div>
          <div className="rounded-xl bg-indigo-500/10 border border-indigo-400/20 p-2.5 text-center">
            <div className="text-xs text-indigo-200 font-medium">{isTa ? "வயது திருப்புமுனை" : "Age Milestones"}</div>
            <div className="text-xl font-bold text-indigo-300 mt-0.5">{milestones_count}</div>
          </div>
          <div className="rounded-xl bg-amber-500/10 border border-amber-400/20 p-2.5 text-center">
            <div className="text-xs text-amber-200 font-medium">{isTa ? "ஆன்ம பாடங்கள்" : "Soul Lessons"}</div>
            <div className="text-xl font-bold text-amber-300 mt-0.5">{soul_lessons_count}</div>
          </div>
        </div>
      </div>

      {/* 2. Active Stars Bar */}
      {active_nakshatras_summary.length > 0 && (
        <div className="rounded-2xl border border-[#D9DEE7] bg-white p-4 sm:p-5 space-y-3 shadow-2xs">
          <div className="flex items-center gap-2 text-xs font-bold text-[#183047] uppercase tracking-wider">
            <Layers className="w-4 h-4 text-[#B4872B]" />
            <span>{isTa ? "ஜாதகத்தில் ஆதிக்கம் செலுத்தும் நட்சத்திரங்கள்" : "Active Nakshatras in Natal Chart"}</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {active_nakshatras_summary.map((item, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-3 flex items-start justify-between gap-2.5 hover:border-[#B4872B]/60 transition-all"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-[#153F6B]">
                      {isTa ? item.name_ta : item.nakshatra}
                    </span>
                    <span className="text-[10px] font-mono font-semibold px-1.5 py-0.2 rounded bg-amber-50 text-amber-800 border border-amber-200">
                      {isTa ? "அதிபதி: " : "Lord: "}{item.lord}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#52667E]">
                    <span className="font-medium text-[#183047]">{isTa ? "அதிதேவதை: " : "Deity: "}</span>
                    {item.deity} • <span className="font-medium text-[#183047]">{isTa ? "சின்னம்: " : "Symbol: "}</span>
                    {item.symbol}
                  </div>
                  <div className="flex flex-wrap gap-1 pt-1">
                    {item.padas.map((pd, pidx) => (
                      <span
                        key={pidx}
                        className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white text-[#153F6B] border border-[#CBD5E1]"
                      >
                        {pd}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. Special Advisory Highlights: Age Milestones, Vastu, & Body Part */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Age Milestones Card */}
        {age_milestones.length > 0 && (
          <div className="rounded-2xl border border-indigo-200 bg-indigo-50/40 p-4 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-indigo-950 uppercase tracking-wider">
              <Clock className="w-4 h-4 text-indigo-700" />
              <span>{isTa ? "வயது திருப்புமுனைகள்" : "Key Age Milestones"}</span>
            </div>
            <div className="space-y-2">
              {age_milestones.map((m, midx) => {
                const isCurrent = m.status === "CURRENT";
                const isPast = m.status === "PAST";
                return (
                  <div
                    key={midx}
                    className={`rounded-xl p-3 border text-xs transition-all ${
                      isCurrent
                        ? "bg-amber-50 border-amber-300 ring-2 ring-amber-400/50"
                        : isPast
                        ? "bg-white/80 border-slate-200 text-slate-600"
                        : "bg-white border-indigo-200 text-indigo-900"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="font-bold text-sm text-[#183047]">
                        {isTa ? `வயது ${m.age}` : `Age ${m.age}`}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          isCurrent
                            ? "bg-amber-500 text-white animate-pulse"
                            : isPast
                            ? "bg-slate-200 text-slate-700"
                            : "bg-indigo-600 text-white"
                        }`}
                      >
                        {isCurrent
                          ? isTa ? "இப்போது நடப்பில்!" : "ACTIVE NOW!"
                          : isPast
                          ? isTa ? "கடந்த நிகழ்வு" : "Past Trigger"
                          : isTa ? "எதிர்காலம்" : "Upcoming"}
                      </span>
                    </div>
                    <div className="text-[11px] font-medium text-slate-700 mb-1">
                      {m.nakshatra} ({m.graha})
                    </div>
                    <p className="text-[11px] leading-relaxed text-[#52667E]">
                      {isTa ? m.event_ta : m.event_en}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Vastu North-East Advisory Card */}
        {vastu_advisories.length > 0 && (
          <div className="rounded-2xl border border-rose-200 bg-rose-50/40 p-4 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-rose-950 uppercase tracking-wider">
              <Compass className="w-4 h-4 text-rose-700" />
              <span>{isTa ? "வடகிழக்கு வாஸ்து வழிகாட்டல்" : "North-East Vastu Advisory"}</span>
            </div>
            {vastu_advisories.map((v, vidx) => (
              <div key={vidx} className="rounded-xl bg-white p-3 border border-rose-200 text-xs space-y-2">
                <div className="flex items-center gap-1.5 font-bold text-rose-900">
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                  <span>{v.direction}</span>
                </div>
                <p className="text-[11px] text-[#52667E] leading-relaxed">
                  <span className="font-semibold text-rose-950">{isTa ? "குறைபாடு: " : "Defect Risk: "}</span>
                  {v.defect_risk}
                </p>
                <div className="pt-1.5 border-t border-rose-100 text-[11px] text-emerald-800 font-medium">
                  <span className="font-bold">{isTa ? "பரிகாரம்: " : "Upaya: "}</span>
                  {v.remedy}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Body Part Vulnerabilities Card */}
        {body_part_alerts.length > 0 && (
          <div className="rounded-2xl border border-amber-200 bg-amber-50/40 p-4 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-amber-950 uppercase tracking-wider">
              <Footprints className="w-4 h-4 text-amber-800" />
              <span>{isTa ? "பாதங்கள் & கணுக்கால் பாதுகாப்பு" : "Foot & Ankle Health Alert"}</span>
            </div>
            <div className="space-y-2">
              {body_part_alerts.map((b, bidx) => (
                <div key={bidx} className="rounded-xl bg-white p-3 border border-amber-200 text-xs space-y-1">
                  <div className="flex items-center justify-between gap-1">
                    <span className="font-bold text-amber-950">
                      {isTa ? b.relative_ta : b.relative_en}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 font-bold">
                      {b.graha} ({b.nakshatra})
                    </span>
                  </div>
                  <p className="text-[11px] text-[#52667E] leading-relaxed">
                    {isTa
                      ? "பரணி நட்சத்திரத்தின் கர்ம உடல் பகுதியான பாதங்கள், குதிகால் அல்லது கணுக்காலில் வலி, சுளுக்கு அல்லது காயங்கள் ஏற்பட வாய்ப்புண்டு."
                      : b.organ}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 4. Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-2">
        <span className="text-xs font-bold text-[#8190A6] shrink-0 mr-1 flex items-center gap-1">
          <Filter className="w-3.5 h-3.5" />
          {isTa ? "வடிகட்ட:" : "Filter:"}
        </span>
        <button
          type="button"
          onClick={() => setActiveFilter("ALL")}
          className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
            activeFilter === "ALL"
              ? "bg-[#153F6B] text-white shadow-2xs"
              : "bg-white border border-[#CBD5E1] text-[#52667E] hover:bg-[#F2F3F5]"
          }`}
        >
          {isTa ? "அனைத்து விதிகள்" : "All Rules"} ({matched_rules.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveFilter("CRITICAL_CAUTION")}
          className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
            activeFilter === "CRITICAL_CAUTION"
              ? "bg-rose-600 text-white shadow-2xs"
              : "bg-white border border-rose-200 text-rose-700 hover:bg-rose-50"
          }`}
        >
          {isTa ? "முக்கிய எச்சரிக்கை" : "Critical Cautions"} ({critical_cautions_count})
        </button>
        <button
          type="button"
          onClick={() => setActiveFilter("IMPORTANT_MILESTONE")}
          className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
            activeFilter === "IMPORTANT_MILESTONE"
              ? "bg-indigo-600 text-white shadow-2xs"
              : "bg-white border border-indigo-200 text-indigo-700 hover:bg-indigo-50"
          }`}
        >
          {isTa ? "வயது திருப்புமுனைகள்" : "Milestones"} ({milestones_count})
        </button>
        <button
          type="button"
          onClick={() => setActiveFilter("LIFE_LESSON")}
          className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
            activeFilter === "LIFE_LESSON"
              ? "bg-amber-600 text-white shadow-2xs"
              : "bg-white border border-amber-200 text-amber-800 hover:bg-amber-50"
          }`}
        >
          {isTa ? "ஆன்ம பாடங்கள்" : "Soul Lessons"} ({soul_lessons_count})
        </button>
        <button
          type="button"
          onClick={() => setActiveFilter("POSITIVE_TALENT")}
          className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
            activeFilter === "POSITIVE_TALENT"
              ? "bg-emerald-600 text-white shadow-2xs"
              : "bg-white border border-emerald-200 text-emerald-800 hover:bg-emerald-50"
          }`}
        >
          {isTa ? "சிறப்பு ஆற்றல்கள்" : "Talents & Gifts"}
        </button>
        <button
          type="button"
          onClick={() => setActiveFilter("VASTU_HEALTH")}
          className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
            activeFilter === "VASTU_HEALTH"
              ? "bg-purple-600 text-white shadow-2xs"
              : "bg-white border border-purple-200 text-purple-800 hover:bg-purple-50"
          }`}
        >
          {isTa ? "வாஸ்து & உடல்நலம்" : "Vastu & Health"}
        </button>
      </div>

      {/* 5. Detailed Matched Rules Cards */}
      <div className="space-y-4">
        {filteredRules.length === 0 ? (
          <div className="p-8 text-center rounded-2xl border border-dashed border-[#CBD5E1] bg-white text-xs text-[#8190A6]">
            {isTa ? "தேர்ந்தெடுக்கப்பட்ட பிரிவில் விதிகள் ஏதுமில்லை." : "No rules found for this category."}
          </div>
        ) : (
          filteredRules.map((rule, ridx) => {
            const isCrit = rule.severity === "CRITICAL_CAUTION";
            const isMile = rule.severity === "IMPORTANT_MILESTONE";
            const isLesson = rule.severity === "LIFE_LESSON";
            const isTalent = rule.severity === "POSITIVE_TALENT";
            const isExpanded = expandedRule === rule.technique_id;

            const badgeBg = isCrit
              ? "bg-rose-50 text-rose-700 border-rose-200"
              : isMile
              ? "bg-indigo-50 text-indigo-700 border-indigo-200"
              : isLesson
              ? "bg-amber-50 text-amber-800 border-amber-200"
              : isTalent
              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
              : "bg-slate-50 text-slate-700 border-slate-200";

            return (
              <div
                key={ridx}
                className={`rounded-2xl border transition-all bg-white p-4 sm:p-5 space-y-3.5 shadow-2xs ${
                  isCrit
                    ? "border-rose-200 hover:border-rose-400"
                    : isMile
                    ? "border-indigo-200 hover:border-indigo-400"
                    : "border-[#D9DEE7] hover:border-[#B4872B]"
                }`}
              >
                {/* Card Top Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#F1F5F9] pb-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-xs font-black px-2.5 py-0.5 rounded-md bg-[#153F6B] text-white">
                      {rule.nakshatra}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${badgeBg}`}>
                      {isCrit
                        ? isTa ? "முக்கிய எச்சரிக்கை ⚠️" : "Critical Caution ⚠️"
                        : isMile
                        ? isTa ? "முக்கிய திருப்புமுனை ⏳" : "Important Milestone ⏳"
                        : isLesson
                        ? isTa ? "ஆன்ம பாடம் 🎯" : "Soul Lesson 🎯"
                        : isTalent
                        ? isTa ? "சிறப்பு ஆற்றல் 🌟" : "Positive Talent 🌟"
                        : isTa ? "சுபாவம் 💡" : "Behavioral Trait 💡"}
                    </span>
                    <span className="text-[11px] font-semibold text-[#8190A6]">
                      {isTa ? "கிரகங்கள்:" : "Grahas:"} {rule.trigger_grahas.join(", ")}
                    </span>
                  </div>

                  <span className="text-[10px] font-mono font-semibold text-slate-400">
                    {rule.technique_id}
                  </span>
                </div>

                {/* Title */}
                <h3 className="font-bold text-sm sm:text-base text-[#183047] leading-snug">
                  {isTa ? rule.title_ta : rule.title_en}
                </h3>

                {/* Explanation */}
                <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
                  {isTa ? rule.details_ta : rule.details_en}
                </p>

                {/* Case Study Parallel */}
                {rule.case_study && (
                  <div className="rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] p-3 text-xs text-[#334155] space-y-1">
                    <div className="flex items-center gap-1.5 font-bold text-[#153F6B]">
                      <BookOpen className="w-3.5 h-3.5 text-[#B4872B]" />
                      <span>{isTa ? "சப்தரிஷி ஜோதிட ஆய்வு சான்று (Research Case Parallel)" : "Empirical Research Parallel"}</span>
                    </div>
                    <p className="text-[11px] leading-relaxed text-[#52667E]">
                      {rule.case_study}
                    </p>
                  </div>
                )}

                {/* Remedy Box */}
                {(rule.remedy_ta || rule.remedy_en) && (
                  <div className="rounded-xl bg-emerald-50/70 border border-emerald-200/80 p-3 text-xs space-y-1">
                    <div className="flex items-center gap-1.5 font-bold text-emerald-900">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{isTa ? "சாஸ்திர பரிகாரம் & வழிகாட்டுதல் (Remedial Upaya)" : "Shastric Upaya & Practical Advice"}</span>
                    </div>
                    <p className="text-[11px] text-emerald-950 leading-relaxed font-medium">
                      {isTa ? rule.remedy_ta : rule.remedy_en}
                    </p>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
