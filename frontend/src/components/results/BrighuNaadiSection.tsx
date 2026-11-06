"use client";

import React, { useMemo, useState } from "react";
import {
  BrighuNaadiResponse,
  HoroscopeResponse,
} from "@/lib/types";
import { evaluateBrighuNaadiClient } from "@/lib/brighu-naadi-data";
import { getBrighuPrashnaAnalysis } from "@/lib/api";
import { BrighuPrashnaResponse } from "@/lib/types";
import {
  Compass,
  BookOpen,
  MapPin,
  Home,
  Navigation,
  Briefcase,
  Sparkles,
  Calendar,
  AlertTriangle,
  Heart,
  TrendingUp,
  Shield,
  Clock,
  Layers,
  ChevronRight,
  Globe,
  Award,
  CheckCircle2,
  HelpCircle,
  Flame,
} from "lucide-react";

interface BrighuNaadiSectionProps {
  horoscope?: HoroscopeResponse;
  data?: BrighuNaadiResponse | null;
  gender?: string;
  language?: "en" | "ta";
}

export function BrighuNaadiSection({
  horoscope,
  data,
  gender = "male",
  language = "en",
}: BrighuNaadiSectionProps) {
  const [activeTab, setActiveTab] = useState<
    "overview" | "vastu" | "karakas" | "directions" | "milestones" | "rules" | "bnn_rules" | "pankajj_duaa" | "prashna"
  >("overview");
  const [prashnaAge, setPrashnaAge] = useState<number>(30);
  const [prashnaCategory, setPrashnaCategory] = useState<string>("general");
  const [prashnaResult, setPrashnaResult] = useState<BrighuPrashnaResponse | null>(null);
  const [isPrashnaLoading, setIsPrashnaLoading] = useState<boolean>(false);

  const handleFetchPrashna = async (ageVal: number, catVal: string) => {
    setIsPrashnaLoading(true);
    try {
      const res = await getBrighuPrashnaAnalysis({
        completed_age: Number(ageVal),
        query_category: catVal,
      });
      setPrashnaResult(res);
    } catch (e) {
      console.error("Prashna error:", e);
    } finally {
      setIsPrashnaLoading(false);
    }
  };


  // Derive Brighu Naadi analysis: use prop data if provided, else compute offline
  const analysis: BrighuNaadiResponse | null = useMemo(() => {
    if (data) return data;
    if (horoscope?.planets && horoscope.planets.length > 0) {
      return evaluateBrighuNaadiClient(horoscope.planets, horoscope.ascendant, gender);
    }
    return null;
  }, [data, horoscope, gender]);

  if (!analysis) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
        <Compass className="w-10 h-10 text-slate-400 mx-auto mb-3 animate-spin" />
        <p className="text-slate-600 dark:text-slate-400 text-sm">
          {language === "ta"
            ? "பிருகு நாடி பகுப்பாய்வு கணக்கிடப்படுகிறது..."
            : "Calculating Brighu Naadi Sangraha analysis..."}
        </p>
      </div>
    );
  }

  const {
    treatise_metadata,
    bnn_research_metadata,
    birth_environment,
    jeeva_karaka,
    karma_karaka,
    timing_milestones,
    physical_health_markers,
    matched_rules,
    bnn_directional_groups,
    bnn_20_rules_evaluations = [],
    rahu_ketu_axis_career_outside,
    pankajj_duaa_compendium,
  } = analysis;

  const pkd = pankajj_duaa_compendium;

  const isTa = language === "ta";

  return (
    <div className="space-y-6">
      {/* 1. TREATISE & RESEARCH BANNER */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-amber-900 via-orange-950 to-stone-900 text-white p-6 md:p-8 shadow-xl border border-amber-600/30">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 text-xs font-semibold tracking-wide border border-amber-500/30">
              <Compass className="w-3.5 h-3.5 text-amber-400" />
              <span>{isTa ? "பிருகு நாடி & பிருகு நந்தி நாடி ஆய்வகம்" : "Brighu Naadi & Bhrigu Nandi Nadi Compendium"}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-amber-200/80 bg-black/30 px-3 py-1 rounded-md border border-white/10 font-mono">
                {treatise_metadata.author}
              </span>
              <span className="text-xs text-amber-300/90 bg-amber-950/60 px-3 py-1 rounded-md border border-amber-500/30 font-mono">
                R. G. Rao System • IJCRME 2022
              </span>
            </div>
          </div>

          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white mb-2">
            {isTa
              ? "பிருகு நாடி சங்கிரகம் & பிருகு நந்தி நாடி 20 விதிகள்"
              : "Brighu Naadi Sangraha & Bhrigu Nandi Nadi (20 Golden Rules)"}
          </h2>

          <p className="text-sm md:text-base text-amber-100/90 leading-relaxed max-w-4xl">
            {isTa ? treatise_metadata.philosophy_ta : treatise_metadata.philosophy_en}
          </p>

          <div className="mt-4 pt-4 border-t border-white/10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
            <div className="flex items-start gap-2 bg-white/5 p-3 rounded-lg border border-white/5">
              <Sparkles className="w-4 h-4 text-amber-300 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-amber-200">
                  {isTa ? `ஜீவ காரகர் (${jeeva_karaka.primary_karaka_planet || "குரு"}): ` : `Jeeva Karaka (${jeeva_karaka.primary_karaka_planet || "Jupiter"}): `}
                </span>
                <span className="text-amber-100/80">
                  {isTa
                    ? jeeva_karaka.gender_applied === "female"
                      ? "பெண் ஜாதகத்தில் சுக்கிரனே ஜீவ காரகர் (R.G. Rao விதி)."
                      : "ஆண் ஜாதகத்தில் குருவே ஜீவ காரகர்."
                    : jeeva_karaka.gender_applied === "female"
                      ? "Venus acts as Jeeva Karaka in female horoscopes (R.G. Rao rule)."
                      : "Jupiter acts as Jeeva Karaka in male horoscopes."}
                </span>
              </div>
            </div>

            <div className="flex items-start gap-2 bg-white/5 p-3 rounded-lg border border-white/5">
              <Briefcase className="w-4 h-4 text-orange-300 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-orange-200">
                  {isTa ? "கர்ம காரகர் (சனி): " : "Karma Karaka (Saturn): "}
                </span>
                <span className="text-amber-100/80">{treatise_metadata.karma_karaka_role}</span>
              </div>
            </div>

            <div className="flex items-start gap-2 bg-white/5 p-3 rounded-lg border border-white/5 sm:col-span-2 lg:col-span-1">
              <Award className="w-4 h-4 text-yellow-300 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-yellow-200">
                  {isTa ? "ஆய்வு ஆதாரம்: " : "Academic Authority: "}
                </span>
                <span className="text-amber-100/80">
                  {bnn_research_metadata?.authors[0]} & {bnn_research_metadata?.authors[1]} (Vels University, IJCRME 2022).
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. SUB-NAVIGATION PILLS */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {[
          { id: "overview", label_en: "Overview & Synthesis", label_ta: "சுருக்கம்", icon: Sparkles },
          { id: "karakas", label_en: "Jeeva & Karma Karakas", label_ta: "ஜீவன் & கர்ம காரகங்கள்", icon: Layers },
          { id: "directions", label_en: "Directional Trines (1-5-9)", label_ta: "திசை சேர்க்கைகள் (1-5-9)", icon: Compass },
          { id: "bnn_rules", label_en: `BNN 20 Golden Rules (${bnn_20_rules_evaluations.length})`, label_ta: `BNN 20 விதிகள் (${bnn_20_rules_evaluations.length})`, icon: BookOpen },
          { id: "vastu", label_en: "Birth Vastu & Environment", label_ta: "பிறந்த வாஸ்து & சூழல்", icon: Home },
          { id: "milestones", label_en: "Event Timing Milestones", label_ta: "நிகழ்வு காலக் கணிப்பு", icon: Calendar },
          { id: "rules", label_en: `Classical Yogas (${matched_rules.length})`, label_ta: `நாடி யோகங்கள் (${matched_rules.length})`, icon: Award },
          { id: "pankajj_duaa", label_en: "Pankajj Duaa BNN Notes", label_ta: "பங்கஜ் துவா BNN சாஸ்திரம்", icon: Shield },
          { id: "prashna", label_en: "Brighu Prashna Oracle (107)", label_ta: "பிருகு பிரசன்னம் (107 வாக்குகள்)", icon: Flame },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all shadow-sm ${
                isActive
                  ? "bg-amber-800 text-white shadow-amber-900/20"
                  : "bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-amber-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{isTa ? tab.label_ta : tab.label_en}</span>
            </button>
          );
        })}
      </div>

      {/* 3. TAB 1: OVERVIEW & SYNTHESIS */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Spotlight: Rule 10 Rahu-Ketu Axis Career Outside */}
          {rahu_ketu_axis_career_outside && (
            <div
              className={`p-5 rounded-2xl border transition-all ${
                rahu_ketu_axis_career_outside.is_triggered
                  ? "bg-gradient-to-r from-blue-50 via-indigo-50 to-indigo-100/60 dark:from-blue-950/30 dark:to-indigo-950/40 border-indigo-300 dark:border-indigo-800 text-indigo-950 dark:text-indigo-200"
                  : "bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300"
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
                <div className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-indigo-600" />
                  <h3 className="font-extrabold text-sm sm:text-base">
                    {isTa
                      ? rahu_ketu_axis_career_outside.rule_title_ta
                      : rahu_ketu_axis_career_outside.rule_title_en}
                  </h3>
                </div>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                    rahu_ketu_axis_career_outside.is_triggered
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200"
                  }`}
                >
                  {rahu_ketu_axis_career_outside.is_triggered
                    ? isTa
                      ? "வெளியூர்/வெளிநாட்டு வேலை உறுதியாகிறது"
                      : "Triggered: Career Set Outside / Overseas"
                    : isTa
                      ? "உள்ளூர் தொழில் அமைப்பு"
                      : "Regional / Native Alignment"}
                </span>
              </div>
              <p className="text-xs sm:text-sm leading-relaxed opacity-90">
                {isTa
                  ? rahu_ketu_axis_career_outside.explanation_ta
                  : rahu_ketu_axis_career_outside.explanation_en}
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Karma Karaka Summary Card */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2 text-base">
                  <Briefcase className="w-4 h-4 text-orange-600" />
                  {isTa ? "கர்ம காரகர் (சனி) தொழில் ஆளுமை" : "Karma Karaka (Saturn) Livelihood"}
                </h3>
                <span className="text-xs bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300 px-2.5 py-0.5 rounded-full font-medium">
                  {karma_karaka.direction || "East"} • {isTa ? karma_karaka.sign_ta : karma_karaka.sign}
                </span>
              </div>

              {karma_karaka.saturn_sign_career_en && (
                <div className="p-3 bg-amber-50/70 dark:bg-amber-950/20 rounded-xl border border-amber-200 dark:border-amber-800/40 text-xs text-amber-950 dark:text-amber-200">
                  <span className="font-bold block mb-1">
                    {isTa ? "ராசி வழி தொழில் பலன் (BNN ஆய்வு):" : "Saturn in Sign Career (BNN Paper):"}
                  </span>
                  <span>{isTa ? karma_karaka.saturn_sign_career_ta : karma_karaka.saturn_sign_career_en}</span>
                </div>
              )}

              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-slate-200/60 dark:border-slate-700/60">
                {isTa ? karma_karaka.career_status_ta : karma_karaka.career_status_en}
              </p>

              <div>
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-2">
                  {isTa ? "சுட்டிக்காட்டப்படும் தொழில் துறைகள்:" : "Indicated Professional Trades:"}
                </span>
                <div className="flex flex-wrap gap-2">
                  {(isTa ? karma_karaka.career_fields_ta : karma_karaka.career_fields_en).map((f, i) => (
                    <span
                      key={i}
                      className="text-xs px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-medium border border-slate-200 dark:border-slate-700"
                    >
                      {f}
                    </span>
                  ))}
                </div>
              </div>

              {karma_karaka.career_start_age_approx && (
                <div className="p-3 bg-orange-50 dark:bg-orange-950/20 rounded-lg border border-orange-200/50 dark:border-orange-800/50 flex items-center justify-between text-xs">
                  <span className="text-orange-900 dark:text-orange-200 font-medium flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-orange-600" />
                    {isTa ? "சுய தொழில் / உத்தியோக ஆரம்ப வயது:" : "Approximate Career Start Age:"}
                  </span>
                  <span className="font-extrabold text-orange-800 dark:text-orange-300 text-sm">
                    {karma_karaka.career_start_age_approx} {isTa ? "வயது" : "Years"}
                  </span>
                </div>
              )}
            </div>

            {/* Jeeva Karaka Vitality Card */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2 text-base">
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  {isTa ? `ஜீவ காரகர் (${jeeva_karaka.primary_karaka_planet || "குரு"}) நல்வாழ்வு` : `Jeeva Karaka (${jeeva_karaka.primary_karaka_planet || "Jupiter"}) Vitality`}
                </h3>
                <span className="text-xs bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 px-2.5 py-0.5 rounded-full font-medium">
                  {isTa ? `${jeeva_karaka.sign_ta} (பாவம் ${jeeva_karaka.house_from_lagna})` : `${jeeva_karaka.sign} (House ${jeeva_karaka.house_from_lagna})`}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 text-xs">
                <span className="font-semibold text-slate-500 block mb-1">
                  {isTa ? "பாலின ரீதியான ஜீவ காரகர் (R.G. Rao விதி):" : "Gender Principle (R. G. Rao):"}
                </span>
                <span className="text-slate-800 dark:text-slate-200 font-medium">
                  {isTa
                    ? jeeva_karaka.gender_applied === "female"
                      ? "பெண் ஜாதகத்தில் சுக்கிரனே ஜீவ காரகராக விளங்கி பெண்மையின் நல்வாழ்வு, ஆரோக்கியம், மற்றும் ஆத்ம சக்தியை ஆளுகிறார்."
                      : "ஆண் ஜாதகத்தில் குருவே ஜீவ காரகராக விளங்கி வாழ்வின் உயிர் ஆற்றலையும் தர்ம நெறியையும் வழிநடத்துகிறார்."
                    : jeeva_karaka.gender_applied === "female"
                      ? "In female horoscopes, Venus governs as the primary Jeeva Karaka representing life force, health, and conscious self."
                      : "In male horoscopes, Jupiter governs as the primary Jeeva Karaka representing life force, wisdom, and moral destiny."}
                </span>
              </div>

              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                {isTa ? jeeva_karaka.lifestyle_profile_ta : jeeva_karaka.lifestyle_profile_en}
              </p>

              {jeeva_karaka.prosperity_after_41 && (
                <div className="p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/50 text-xs text-emerald-900 dark:text-emerald-200">
                  <span className="font-bold block mb-1">
                    {isTa ? "41 வயதுக்கு பின் பெரும் மேன்மை:" : "Special Brighu Rule: Prosperity after 41:"}
                  </span>
                  <span>
                    {isTa
                      ? "குரு மிதுனம், தனுசு அல்லது மீனத்தில் இருப்பதால் 41 வயதுக்கு பின் ஜாதகருக்கு சிறப்பான செல்வமும் மன நிம்மதியும் கிட்டும்."
                      : "Jupiter in Gemini, Sagittarius, or Pisces triggers notable life prosperity and wisdom consolidation after the age of 41."}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 4. TAB 2: JEEVA & KARMA KARAKAS */}
      {activeTab === "karakas" && (
        <div className="space-y-6">
          {/* Saturn Karma Analysis Grid */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-orange-600" />
              {isTa ? "கர்ம காரகர் (சனி) அண்டை மற்றும் எதிரெதிர் கிரகங்களின் ஆய்வு" : "Saturn (Karma Karaka) Aspect & Flanking Matrix"}
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1">
                <span className="font-bold text-slate-500 uppercase text-[10px]">
                  {isTa ? "ஒரே திசை திரிகோண கிரகங்கள் (1-5-9)" : "Same Direction Trines (1-5-9)"}
                </span>
                <div className="font-bold text-sm text-slate-900 dark:text-white">
                  {karma_karaka.planets_in_same_direction?.length
                    ? karma_karaka.planets_in_same_direction.join(", ")
                    : isTa ? "எதுவுமில்லை" : "None"}
                </div>
                <p className="text-[11px] text-slate-500">
                  {isTa ? "சனியுடன் இணைந்து தொழில் பாக்கியத்தை உருவாக்கும் கிரகங்கள்." : "Planets cooperating in the same direction."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1">
                <span className="font-bold text-slate-500 uppercase text-[10px]">
                  {isTa ? "7-ஆம் வீட்டு நேரடி பார்வை (Opposite)" : "Direct 7th House Aspect"}
                </span>
                <div className="font-bold text-sm text-slate-900 dark:text-white">
                  {karma_karaka.planets_in_opposite_direction?.length
                    ? karma_karaka.planets_in_opposite_direction.join(", ")
                    : isTa ? "கிரகங்கள் இல்லை" : "Unoccupied"}
                </div>
                <p className="text-[11px] text-slate-500">
                  {isTa ? "விதி 3: 7-ஆம் வீட்டு கிரகமே சனியை மிகத் தீவிரமாகப் பாதிக்கும்." : "Rule 3: 7th sign planet impacts karaka most."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1">
                <span className="font-bold text-slate-500 uppercase text-[10px]">
                  {isTa ? "முன் நிற்கும் கிரகம் (2-ஆம் வீடு)" : "Front Planet (2nd House)"}
                </span>
                <div className="font-bold text-sm text-slate-900 dark:text-white">
                  {karma_karaka.planets_in_2nd?.length ? karma_karaka.planets_in_2nd.join(", ") : isTa ? "எதுவுமில்லை" : "Empty"}
                </div>
                <p className="text-[11px] text-slate-500">
                  {isTa ? "விதி 4: சனியின் முன்னே செல்லும் கிரகங்கள்." : "Rule 4: Planets directly in front of Saturn."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1">
                <span className="font-bold text-slate-500 uppercase text-[10px]">
                  {isTa ? "பின் நிற்கும் கிரகம் (12-ஆம் வீடு)" : "Rear Planet (12th House)"}
                </span>
                <div className="font-bold text-sm text-slate-900 dark:text-white">
                  {karma_karaka.planets_in_12th?.length ? karma_karaka.planets_in_12th.join(", ") : isTa ? "எதுவுமில்லை" : "Empty"}
                </div>
                <p className="text-[11px] text-slate-500">
                  {isTa ? "விதி 4: சனியை நோக்கி முன்னேறும் கிரகங்கள்." : "Rule 4: Planets advancing toward Saturn."}
                </p>
              </div>
            </div>

            {karma_karaka.is_retrograde && karma_karaka.retrograde_backward_house_influence_en && (
              <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/60 text-xs text-amber-900 dark:text-amber-200">
                <span className="font-bold block mb-1 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  {isTa ? "விதி 14: வக்ர சனியின் பின்னோக்கிய பார்வை:" : "Rule 14: Retrograde Saturn Backward Energy Vector:"}
                </span>
                <p>{isTa ? karma_karaka.retrograde_backward_house_influence_ta : karma_karaka.retrograde_backward_house_influence_en}</p>
              </div>
            )}
          </div>

          {/* 12 Bhavas from Jupiter Matrix */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-amber-600" />
                {isTa ? "குருவிலிருந்து 12 பாவங்களின் கிரக அமைவு" : "12 Bhavas Counted from Jupiter (Jeeva Karaka)"}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {isTa
                  ? "பிருகு நாடியில் லக்னத்திற்கு பதிலாக குருவே 1-ஆம் பாவமாக பாவிக்கப்பட்டு, அனைத்து 12 பாவங்களும் குருவிலிருந்து கணக்கிடப்படுகின்றன."
                  : "In Sage Brighu's system, Jupiter is treated as the primary 1st Bhava, and all 12 houses are reckoned from Jupiter's sign."}
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((bhava) => {
                const occupants = jeeva_karaka.planets_in_bhavas_from_jupiter[bhava] || [];
                const hasPlanets = occupants.length > 0;
                return (
                  <div
                    key={bhava}
                    className={`p-3 rounded-xl border text-xs transition-all ${
                      hasPlanets
                        ? "bg-amber-50/70 dark:bg-amber-950/20 border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-200 shadow-sm"
                        : "bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700/60 text-slate-500 dark:text-slate-400"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5 font-bold">
                      <span>{isTa ? `${bhava}-ஆம் பாவம்` : `Bhava ${bhava}`}</span>
                      {bhava === 1 && (
                        <span className="text-[10px] bg-amber-200 dark:bg-amber-800 px-1.5 py-0.5 rounded text-amber-900 dark:text-amber-100">
                          {isTa ? "ஜீவன்" : "Jeeva"}
                        </span>
                      )}
                    </div>
                    {hasPlanets ? (
                      <div className="space-y-1">
                        {occupants.map((p, idx) => (
                          <div key={idx} className="font-semibold text-slate-800 dark:text-slate-200">
                            • {p}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-[11px] italic opacity-60">
                        {isTa ? "கிரகங்கள் இல்லை" : "Empty"}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* 5. TAB 3: DIRECTIONAL TRINES (1-5-9) */}
      {activeTab === "directions" && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Compass className="w-5 h-5 text-amber-600" />
              {isTa ? "பிருகு நந்தி நாடி திசை திரிகோணங்கள் (1-5-9)" : "Bhrigu Nandi Nadi Directional Trines (1-5-9)"}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {isTa
                ? "விதி 1 & விதி 2-ன் படி, ஒரே திசையில் நிற்கும் கிரகங்கள் (1, 5, 9) ஒன்றாக இணைந்து பலன் தரும் கூட்டு அணியாகச் செயல்படுகின்றன."
                : "According to Rules 1 & 2 of Bhrigu Nandi Nadi, planets in the same directional trines operate together as an intimate team."}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {bnn_directional_groups &&
              Object.entries(bnn_directional_groups).map(([dirName, dirPlanets]) => (
                <div
                  key={dirName}
                  className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-800/40 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-slate-900 dark:text-white">{dirName}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-200">
                      {dirPlanets.length} {isTa ? "கிரகங்கள்" : "Planets"}
                    </span>
                  </div>
                  {dirPlanets.length > 0 ? (
                    <div className="space-y-1">
                      {dirPlanets.map((p, idx) => (
                        <div key={idx} className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                          • {p}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <span className="text-xs italic text-slate-400">{isTa ? "கிரகங்கள் இல்லை" : "None"}</span>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}

      {/* 6. TAB 4: BNN 20 GOLDEN RULES */}
      {activeTab === "bnn_rules" && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-amber-600" />
                {isTa
                  ? "பிருகு நந்தி நாடி 20 அடிப்படைக் கணிப்பு விதிகள் (R. G. Rao முறை)"
                  : "Bhrigu Nandi Nadi 20 Golden Rules (Mr. R. G. Rao System)"}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {isTa
                  ? "ஆராய்ச்சியாளர் A. ஜெகதீசன் & முனைவர் K. ஜோதிமணி (வேல்ஸ் பல்கலைக்கழகம், IJCRME 2022) ஆய்வுக் கட்டுரையின் அடிப்படையில் சரிபார்க்கப்பட்ட முடிவுகள்."
                  : "Verified predictive rules from A. Jagadeesan & Dr. K. Jothimani, School of Vedic Astrology, VISTAS, Chennai (IJCRME 2022)."}
              </p>
            </div>
            <span className="text-xs px-3 py-1 rounded-full bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-200 font-bold">
              20 {isTa ? "விதிகள் ஆய்வு" : "Rules Catalogued"}
            </span>
          </div>

          <div className="space-y-4">
            {bnn_20_rules_evaluations.map((rule) => (
              <div
                key={rule.rule_number}
                className={`p-4 rounded-xl border transition-all ${
                  rule.is_active
                    ? "bg-amber-50/50 dark:bg-amber-950/20 border-amber-300 dark:border-amber-800/60 shadow-xs"
                    : "bg-slate-50/50 dark:bg-slate-800/30 border-slate-200 dark:border-slate-800 opacity-80"
                }`}
              >
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded ${
                        rule.is_active ? "bg-amber-600 text-white" : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      Rule {rule.rule_number}
                    </span>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                      {isTa ? rule.title_ta : rule.title_en}
                    </h4>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">{rule.source_ref}</span>
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-300 mb-2 leading-relaxed">
                  {isTa ? rule.principle_ta : rule.principle_en}
                </p>

                <div className="p-2.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-700/80 text-xs flex items-start gap-2">
                  <CheckCircle2
                    className={`w-4 h-4 shrink-0 mt-0.5 ${
                      rule.is_active ? "text-emerald-600" : "text-slate-400"
                    }`}
                  />
                  <div>
                    <span className="font-bold text-slate-700 dark:text-slate-300 mr-1.5">
                      {isTa ? "ஜாதக பொருத்தம்:" : "Natal Chart Verification:"}
                    </span>
                    <span className={rule.is_active ? "text-amber-900 dark:text-amber-200 font-medium" : "text-slate-500"}>
                      {isTa ? rule.chart_evidence_ta : rule.chart_evidence_en}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 7. TAB 5: VASTU & BIRTH ENVIRONMENT */}
      {activeTab === "vastu" && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Compass className="w-5 h-5 text-amber-600" />
              {isTa ? "பிறந்த இடம், மனை வாஸ்து மற்றும் சூழல் நிர்ணயம்" : "Birth Environment & Vastu Verification"}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {isTa
                ? "பிருகு நாடி சங்கிரகத்தின் 10 முதல் 18-ஆம் பக்கங்களின் விதிகளின்படி, ஜாதகரின் பிறந்த வீட்டின் சாலை, தலைவாசல், மற்றும் அருகில் அமைந்த ஆலயம் ஆகியவை ராகு, கேது மற்றும் சூரியனின் நிலைகளால் நிர்ணயிக்கப்படுகின்றன."
                : "According to pages 10-18 of Brighu Naadi Sangraha, the direction of the road in front of the birth house, entrance door, city sector, and local temple are calculated through Rahu, Ketu, and Sun signs."}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 space-y-2">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <Navigation className="w-3.5 h-3.5 text-amber-600" />
                {isTa ? "வீட்டின் முன் சாலை (Rahu Sign)" : "Road in Front of House (Rahu Sign)"}
              </span>
              <div className="text-sm font-bold text-slate-900 dark:text-white">
                {isTa ? birth_environment.road_direction_ta : birth_environment.road_direction_en}
              </div>
              <p className="text-[11px] text-slate-500">
                {isTa
                  ? "விதி: ராகு ஒற்றை ராசியில் இருந்தால் கிழக்கு-மேற்கு; இரட்டை ராசியில் இருந்தால் தெற்கு-வடக்கு."
                  : "Rule: Rahu in odd signs = East to West; even signs = South to North."}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 space-y-2">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <Home className="w-3.5 h-3.5 text-blue-600" />
                {isTa ? "தலைவாசல் நோக்கிய திசை (Rahu Element)" : "Main Door Facing (Rahu Element)"}
              </span>
              <div className="text-sm font-bold text-slate-900 dark:text-white">
                {isTa ? birth_environment.door_facing_ta : birth_environment.door_facing_en}
              </div>
              <p className="text-[11px] text-slate-500">
                {isTa
                  ? "விதி: நெருப்பு ராசி = கிழக்கு, நில ராசி = தெற்கு, காற்று ராசி = மேற்கு, நீர் ராசி = வடக்கு."
                  : "Rule: Fire = East, Earth = South, Air = West, Water = North."}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 space-y-2">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-rose-600" />
                {isTa ? "பிறந்த ஊரின் பகுதி (City Sector)" : "Part of Town / Village (City Sector)"}
              </span>
              <div className="text-sm font-bold text-slate-900 dark:text-white">
                {isTa ? birth_environment.city_sector_ta : birth_environment.city_sector_en}
              </div>
              <p className="text-[11px] text-slate-500">
                {isTa ? "ராகுவின் ராசிக்குரிய ஊர்ப் பகுதி பிரிவு." : "Quadrant of city determined by Rahu's sign."}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 space-y-2">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                {isTa ? "அருகிலுள்ள ஆலயம் (Sun Sign Deity)" : "Nearby Temple (Sun Sign Deity)"}
              </span>
              <div className="text-sm font-bold text-amber-700 dark:text-amber-400">
                {isTa ? birth_environment.temple_near_birth_ta : birth_environment.temple_near_birth_en}
              </div>
              <p className="text-[11px] text-slate-500">
                {isTa ? `சூரியன் அமைந்த ${birth_environment.sun_sign} ராசிக்குரிய ஆலயம்.` : `Governed by Sun in ${birth_environment.sun_sign}.`}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 space-y-2">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <Heart className="w-3.5 h-3.5 text-pink-600" />
                {isTa ? "துணைவர் வரும் திசை" : "Spouse Arrival Direction"}
              </span>
              <div className="text-sm font-bold text-slate-900 dark:text-white">
                {isTa ? birth_environment.spouse_direction_ta : birth_environment.spouse_direction_en}
              </div>
              <p className="text-[11px] text-slate-500">
                {isTa
                  ? "ஆண்களுக்கு சுக்கிரன், பெண்களுக்கு செவ்வாய் அமைந்த ராசியின் திசை."
                  : "Venus sign for male charts, Mars sign for female charts."}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 8. TAB 6: EVENT TIMING MILESTONES */}
      {activeTab === "milestones" && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-indigo-600" />
              {isTa ? "பிருகு நாடி துல்லிய நிகழ்வு காலக் கணிப்பு" : "Brighu Naadi Event Timing Milestones"}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {isTa
                ? "குருவிலிருந்து பிற கிரகங்கள் அமைந்துள்ள தூரம் மற்றும் குருவின் 12 ஆண்டு சுற்றுவட்டத்தின் அடிப்படையில் நிர்ணயிக்கப்பட்ட முக்கிய வாழ்க்கை மைல்கற்கள்."
                : "Exact age windows calculated through planetary distances from Jupiter across 12-year progression cycles."}
            </p>
          </div>

          <div className="space-y-4">
            {timing_milestones.map((m, idx) => {
              const categoryColorMap: Record<string, string> = {
                marriage: "border-pink-300 dark:border-pink-800 bg-pink-50/50 dark:bg-pink-950/20 text-pink-900 dark:text-pink-200",
                fame: "border-amber-300 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/20 text-amber-900 dark:text-amber-200",
                property: "border-emerald-300 dark:border-emerald-800 bg-emerald-50/50 dark:bg-emerald-950/20 text-emerald-900 dark:text-emerald-200",
                career: "border-blue-300 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-950/20 text-blue-900 dark:text-blue-200",
                caution: "border-rose-300 dark:border-rose-800 bg-rose-50/50 dark:bg-rose-950/20 text-rose-900 dark:text-rose-200",
              };
              const colorCls = categoryColorMap[m.category] || "border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 text-slate-800 dark:text-slate-200";

              return (
                <div
                  key={idx}
                  className={`p-4 rounded-xl border transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${colorCls}`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-black/10 dark:bg-white/10">
                        {m.category}
                      </span>
                      <h4 className="font-bold text-sm">
                        {isTa ? m.event_ta : m.event_en}
                      </h4>
                    </div>
                    <p className="text-xs opacity-80">
                      {isTa ? m.basis_ta : m.basis_en}
                    </p>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className="text-xs font-semibold mr-1">{isTa ? "வயது:" : "Ages:"}</span>
                    {m.age_years.map((age, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 rounded-lg bg-white dark:bg-slate-900 font-extrabold text-xs shadow-sm border border-black/10 dark:border-white/10"
                      >
                        {age}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 9. TAB 7: MATCHED CLASSICAL YOGAS */}
      {activeTab === "rules" && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Award className="w-5 h-5 text-amber-600" />
                {isTa ? "ஜாதகத்தில் பொருந்தும் பிருகு நாடி யோகங்கள்" : "Matched Brighu Naadi Classical Yogas"}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {isTa
                  ? "டாக்டர் என். சீனிவாசன் சாஸ்திரியின் 'பிருகு நாடி சங்கிரகம்' நூலில் உள்ள அசல் விதிகளுடன் ஒப்பிட்டு பெறப்பட்ட முடிவுகள்."
                  : "Verified combinations directly matching Dr. N. Srinivasan Shastry's classical compendium."}
              </p>
            </div>
            <span className="text-xs bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 px-3 py-1 rounded-full font-bold">
              {matched_rules.length} {isTa ? "யோகங்கள்" : "Yogas"}
            </span>
          </div>

          {matched_rules.length === 0 ? (
            <div className="p-8 text-center bg-slate-50 dark:bg-slate-800/40 rounded-xl text-slate-500 text-xs">
              {isTa
                ? "இந்த ஜாதகத்தில் நேரடி கிரக சேர்க்கை யோகங்கள் இல்லை; பொதுவான நாடி சுழற்சிகள் பொருந்தும்."
                : "No strict single-sign conjunction yogas matched; general progressive orb rules apply."}
            </div>
          ) : (
            <div className="space-y-4">
              {matched_rules.map((rule, idx) => (
                <div
                  key={idx}
                  className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 space-y-2 hover:border-amber-300 dark:hover:border-amber-700 transition-all"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-amber-600" />
                      {isTa ? rule.title_ta : rule.title_en}
                    </h4>
                    <span className="text-[11px] font-mono text-slate-500 bg-white dark:bg-slate-900 px-2.5 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                      {rule.source_page}
                    </span>
                  </div>

                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                    {isTa ? rule.interpretation_ta : rule.interpretation_en}
                  </p>

                  <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-500">
                    <span className="font-medium">{isTa ? "இணைந்த கிரகங்கள்:" : "Planets Involved:"}</span>
                    <span className="font-bold text-amber-700 dark:text-amber-400">
                      {rule.planets_involved.join(" + ")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 10. TAB 8: PANKAJJ K DUAA BNN COMPENDIUM */}
      {activeTab === "pankajj_duaa" && pkd && (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-amber-900/40 via-orange-950/40 to-stone-900/50 border border-amber-500/30">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-extrabold text-amber-100">
                  {isTa ? pkd.metadata.title_ta : pkd.metadata.title}
                </h3>
              </div>
              <span className="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30 px-3 py-1 rounded-full font-mono">
                {pkd.metadata.author}
              </span>
            </div>
            <p className="text-xs text-amber-200/90 leading-relaxed mb-4">
              {isTa ? pkd.metadata.summary_ta : pkd.metadata.summary_en}
            </p>
            <div className="flex flex-wrap gap-2">
              {pkd.metadata.traditions.map((t, i) => (
                <span key={i} className="text-[11px] bg-black/40 text-amber-300/80 px-2.5 py-0.5 rounded border border-white/10 font-medium">
                  {t}
                </span>
              ))}
            </div>
          </div>

          {/* Rashi Mobility (Gati) Breakdown */}
          <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-3">
            <div className="flex items-center gap-2">
              <Compass className="w-4 h-4 text-amber-600" />
              <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                {isTa ? "ராசி இயக்கத் தத்துவப் பகுப்பாய்வு (Char, Sthir, Upaye)" : "Zodiac Mobility & Movement Tatva (Char, Sthir, Upaye)"}
              </h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3.5 rounded-lg border border-red-200 dark:border-red-900/40 bg-red-50/50 dark:bg-red-950/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-red-800 dark:text-red-300">
                    {isTa ? "சர ராசிகள் (1, 4, 7, 10)" : "Char / Movable Signs (1, 4, 7, 10)"}
                  </span>
                  <span className="text-xs font-extrabold bg-red-200 dark:bg-red-900/60 text-red-900 dark:text-red-200 px-2 py-0.5 rounded">
                    {pkd.rashi_mobility_summary.char_movable_count}
                  </span>
                </div>
                <p className="text-[11px] text-red-700 dark:text-red-400">
                  {pkd.rashi_mobility_summary.char_planets.join(", ") || (isTa ? "கிரகங்கள் இல்லை" : "None")}
                </p>
              </div>

              <div className="p-3.5 rounded-lg border border-blue-200 dark:border-blue-900/40 bg-blue-50/50 dark:bg-blue-950/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-blue-800 dark:text-blue-300">
                    {isTa ? "ஸ்திர ராசிகள் (2, 5, 8, 11)" : "Sthir / Fixed Signs (2, 5, 8, 11)"}
                  </span>
                  <span className="text-xs font-extrabold bg-blue-200 dark:bg-blue-900/60 text-blue-900 dark:text-blue-200 px-2 py-0.5 rounded">
                    {pkd.rashi_mobility_summary.sthir_fixed_count}
                  </span>
                </div>
                <p className="text-[11px] text-blue-700 dark:text-blue-400">
                  {pkd.rashi_mobility_summary.sthir_planets.join(", ") || (isTa ? "கிரகங்கள் இல்லை" : "None")}
                </p>
              </div>

              <div className="p-3.5 rounded-lg border border-purple-200 dark:border-purple-900/40 bg-purple-50/50 dark:bg-purple-950/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-purple-800 dark:text-purple-300">
                    {isTa ? "உபய ராசிகள் (3, 6, 9, 12)" : "Upaye / Dual Signs (3, 6, 9, 12)"}
                  </span>
                  <span className="text-xs font-extrabold bg-purple-200 dark:bg-purple-900/60 text-purple-900 dark:text-purple-200 px-2 py-0.5 rounded">
                    {pkd.rashi_mobility_summary.upaye_dual_count}
                  </span>
                </div>
                <p className="text-[11px] text-purple-700 dark:text-purple-400">
                  {pkd.rashi_mobility_summary.upaye_planets.join(", ") || (isTa ? "கிரகங்கள் இல்லை" : "None")}
                </p>
              </div>
            </div>
          </div>

          {/* Naadi House Quality Table */}
          <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-amber-600" />
                <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                  {isTa ? "நாடி பாவ நிலை பலன் (ராசி சாரா நன்மை/தீமை அட்டவணை)" : "Naadi House Quality Pattern (Irrespective of Rashi)"}
                </h4>
              </div>
              <span className="text-[11px] text-slate-500">
                {isTa ? "லக்னத்திலிருந்து பாவ நிலை" : "House reckoned from Lagna"}
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2.5">
              {Object.entries(pkd.naadi_house_qualities).map(([planet, q]: [string, any]) => {
                const isGood = q.status.includes("Good");
                const isBad = q.status.includes("Very Bad");
                return (
                  <div
                    key={planet}
                    className={`p-3 rounded-lg border text-center transition-all ${
                      isGood
                        ? "border-emerald-200 dark:border-emerald-800/40 bg-emerald-50/50 dark:bg-emerald-950/20"
                        : isBad
                        ? "border-rose-200 dark:border-rose-800/40 bg-rose-50/50 dark:bg-rose-950/20"
                        : "border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20"
                    }`}
                  >
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">
                      {planet}
                    </span>
                    <span className="text-[11px] text-slate-500 block">
                      {isTa ? `${q.house}-ஆம் பாவம்` : `House ${q.house}`}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded mt-1 inline-block ${
                        isGood
                          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200"
                          : isBad
                          ? "bg-rose-100 text-rose-800 dark:bg-rose-900/60 dark:text-rose-200"
                          : "bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200"
                      }`}
                    >
                      {isTa ? q.status_ta : q.status}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Medical Astrology & Cancer Yoga */}
          <div className="p-5 rounded-xl border border-rose-200 dark:border-rose-900/40 bg-rose-50/30 dark:bg-rose-950/10 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <Heart className="w-4 h-4 text-rose-600" />
              <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                {isTa ? "BNN மருத்துவ ஜோதிடம் & ஆரோக்கிய ஆய்வு" : "BNN Medical Astrology & Vitality Assessment"}
              </h4>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {/* Life Significator */}
              <div className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide block mb-1">
                  {isTa ? "ஜீவ காரகர் ஆரோக்கிய நிலை" : "Prime Life Force Karaka"}
                </span>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-sm text-slate-900 dark:text-white">
                    {pkd.medical_astrology.life_significator.prime_planet} ({isTa ? (gender.toLowerCase() === "female" ? "பெண்களுக்கு சுக்கிரன்" : "ஆண்களுக்கு குரு") : (gender.toLowerCase() === "female" ? "Venus for Females" : "Jupiter for Males")})
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      pkd.medical_astrology.life_significator.is_afflicted
                        ? "bg-rose-100 text-rose-800 dark:bg-rose-900/60 dark:text-rose-200"
                        : "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200"
                    }`}
                  >
                    {pkd.medical_astrology.life_significator.is_afflicted ? (isTa ? "பாதிக்கப்பட்டுள்ளது" : "Afflicted") : (isTa ? "ஆரோக்கிய சுபம்" : "Healthy & Dignified")}
                  </span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  {isTa ? pkd.medical_astrology.life_significator.evaluation_ta : pkd.medical_astrology.life_significator.evaluation_en}
                </p>
              </div>

              {/* Cancer Yoga */}
              <div
                className={`p-3.5 rounded-lg border ${
                  pkd.medical_astrology.cancer_yoga.is_active
                    ? "border-red-300 dark:border-red-800 bg-red-50/70 dark:bg-red-950/30"
                    : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                    {isTa ? "சனி - ராகு புற்றுநோய் யோக ஆய்வு" : "Saturn-Rahu Cancer Yoga Check"}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      pkd.medical_astrology.cancer_yoga.is_active
                        ? "bg-red-600 text-white animate-pulse"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                    }`}
                  >
                    {pkd.medical_astrology.cancer_yoga.is_active ? (isTa ? "இணைந்துள்ளது" : "Active Link") : (isTa ? "இல்லை" : "Neutral")}
                  </span>
                </div>
                <h5 className="font-bold text-xs text-slate-900 dark:text-white mb-1">
                  {isTa ? pkd.medical_astrology.cancer_yoga.title_ta : pkd.medical_astrology.cancer_yoga.title_en}
                </h5>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  {isTa ? pkd.medical_astrology.cancer_yoga.explanation_ta : pkd.medical_astrology.cancer_yoga.explanation_en}
                </p>
              </div>
            </div>

            {/* Organ Afflictions by 2+ Enemy Planets */}
            {pkd.medical_astrology.organ_afflictions.length > 0 && (
              <div className="space-y-2 pt-2">
                <span className="text-xs font-bold text-rose-800 dark:text-rose-300 block">
                  {isTa ? "பகை கிரகங்கள் இணைந்த பாவங்களும் உறுப்பு எச்சரிக்கைகளும் (2+ Enemy Rule):" : "Organ Vulnerability Alerts (2+ Enemy Planets in Single House):"}
                </span>
                <div className="space-y-2">
                  {pkd.medical_astrology.organ_afflictions.map((aff, i) => (
                    <div key={i} className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-900/50 flex items-start gap-2.5">
                      <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                      <div>
                        <span className="text-xs font-bold text-slate-900 dark:text-white block">
                          {isTa ? `${aff.house}-ஆம் பாவம்: ${aff.organ_ta}` : `House ${aff.house}: ${aff.organ_en}`}
                        </span>
                        <p className="text-xs text-rose-700 dark:text-rose-400 mt-0.5">
                          {isTa ? aff.warning_ta : aff.warning_en}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Matched Yogas & Injunctions */}
          {pkd.matched_yogas.length > 0 && (
            <div className="p-5 rounded-xl border border-amber-200 dark:border-amber-900/40 bg-amber-50/20 dark:bg-amber-950/10 shadow-sm space-y-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-600" />
                <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                  {isTa ? `பங்கஜ் துவா BNN யோகங்கள் & விதிகள் (${pkd.matched_yogas.length})` : `Pankajj Duaa Matched Yogas & Principles (${pkd.matched_yogas.length})`}
                </h4>
              </div>
              <div className="space-y-2.5">
                {pkd.matched_yogas.map((y, i) => (
                  <div
                    key={i}
                    className={`p-3.5 rounded-lg border ${
                      y.is_favorable
                        ? "border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/40 dark:bg-emerald-950/20"
                        : "border-amber-200 dark:border-amber-900/40 bg-amber-50/40 dark:bg-amber-950/20"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <h5 className="font-bold text-xs text-slate-900 dark:text-white">
                        {isTa ? y.yoga_name_ta : y.yoga_name}
                      </h5>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                          y.is_favorable
                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200"
                            : "bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200"
                        }`}
                      >
                        {y.is_favorable ? (isTa ? "சுப யோகம்" : "Favorable Yoga") : (isTa ? "எச்சரிக்கை / விதி" : "Caution / Injunction")}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                      {isTa ? y.description_ta : y.description_en}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Degree Border Alerts */}
          {pkd.degree_border_alerts.length > 0 && (
            <div className="p-5 rounded-xl border border-indigo-200 dark:border-indigo-900/40 bg-indigo-50/20 dark:bg-indigo-950/10 shadow-sm space-y-3">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-indigo-600" />
                <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                  {isTa ? "பாகை விளிம்பு கிரக மாற்றங்கள் (27°-30° & 0°-3°)" : "Degree Border Shifts (27°-30° & 0°-3°)"}
                </h4>
              </div>
              <div className="space-y-2">
                {pkd.degree_border_alerts.map((alert, i) => (
                  <div key={i} className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-indigo-100 dark:border-indigo-900/50 flex items-start gap-2.5">
                    <Navigation className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="text-xs font-bold text-slate-900 dark:text-white block">
                        {alert.planet} ({alert.degree.toFixed(2)}°)
                      </span>
                      <p className="text-xs text-indigo-900 dark:text-indigo-300 mt-0.5">
                        {isTa ? alert.shift_ta : alert.shift_en}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prescribed Remedies & Taboos */}
          <div className="p-5 rounded-xl border border-amber-300 dark:border-amber-700/60 bg-gradient-to-br from-amber-50 to-orange-50/60 dark:from-slate-900 dark:to-amber-950/20 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-amber-700 dark:text-amber-400" />
                <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                  {isTa ? "பங்கஜ் துவா BNN பரிகாரங்கள், ருத்ராட்சம் & எச்சரிக்கைகள்" : "BNN Prescribed Remedies, Rudrakshas & Sacred Taboos"}
                </h4>
              </div>
            </div>

            {/* Planet-specific remedies */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {pkd.prescribed_remedies.map((rem, i) => (
                <div key={i} className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-extrabold text-sm text-amber-800 dark:text-amber-400">
                      {rem.planet} {isTa ? "பரிகாரங்கள்" : "Remedies"}
                    </span>
                    <span className="text-[11px] font-semibold bg-amber-100 dark:bg-amber-900/50 text-amber-900 dark:text-amber-200 px-2.5 py-0.5 rounded-full">
                      {rem.rudraksha}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500">
                    <span className="font-medium text-slate-700 dark:text-slate-300">{isTa ? "தெய்வம்: " : "Deity: "}</span>
                    {rem.deities}
                  </div>
                  <div className="text-[11px] font-mono text-amber-700 dark:text-amber-300 bg-amber-50/50 dark:bg-amber-950/30 p-2 rounded border border-amber-200/50 dark:border-amber-900/40">
                    {rem.mantra}
                  </div>
                  <ul className="space-y-1 pt-1">
                    {rem.key_remedies.map((kr, ki) => (
                      <li key={ki} className="text-xs text-slate-700 dark:text-slate-300 flex items-start gap-1.5">
                        <span className="text-amber-600 font-bold">•</span>
                        <span>{kr}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            {/* General Life Maxims */}
            <div className="p-4 rounded-xl bg-white/80 dark:bg-slate-900/80 border border-amber-200 dark:border-amber-900/40 space-y-2 mt-3">
              <span className="text-xs font-bold text-amber-900 dark:text-amber-300 block">
                {isTa ? "வாழ்வியல் பொன்விதிகள் & எச்சரிக்கைகள் (Universal Life Maxims):" : "BNN Universal Life Maxims & Sacred Taboos:"}
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {pkd.general_life_maxims.map((glm, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-amber-50/40 dark:bg-slate-800/40 border border-amber-100 dark:border-slate-700">
                    <span className="text-[11px] font-bold text-amber-800 dark:text-amber-300 block">
                      {glm.rule}
                    </span>
                    <span className="text-xs text-slate-600 dark:text-slate-400 mt-0.5 block leading-relaxed">
                      {glm.maxim}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

            {/* 9. TAB 9: BRIGHU PRASHNA NADI ORACLE */}
      {activeTab === "prashna" && (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-red-950/60 via-amber-950/50 to-stone-900/60 border border-red-500/30 text-white shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 -mt-6 -mr-6 w-48 h-48 bg-red-500/10 rounded-full blur-2xl pointer-events-none" />
            <div className="relative z-10 flex flex-wrap items-center justify-between gap-4">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/20 text-red-300 text-xs font-semibold border border-red-500/30 mb-2">
                  <Flame className="w-3.5 h-3.5 text-red-400" />
                  <span>{isTa ? "பிருகு பிரசன்ன நாடி வாக்கு ரகசியம்" : "R. G. Rao's Bhrigu Prashna Nadi Oracle"}</span>
                </div>
                <h3 className="text-xl font-bold tracking-tight text-amber-100">
                  {isTa ? "107 புனித பிரசன்ன கணிப்புகள் (Brighu Prashna Nadi)" : "The 107 Classical Horary Predictions"}
                </h3>
                <p className="text-xs text-amber-200/80 mt-1 max-w-2xl leading-relaxed">
                  {isTa
                    ? "ஆர். ஜி. ராவ் அவர்களின் 'பிருகு பிரசன்ன நாடி' (1994) முறைப்படி ஜாதகரின் பூர்த்தியான வயதை 107 இலிருந்து கழித்து வரும் ரகசிய எண்ணைக் கொண்டு உடனடி கர்ம வினை, தீர்வு மற்றும் சுப பலன் காலம் அறியப்படுகிறது."
                    : "Per R. G. Rao's foundational treatise (1994), subtracting the completed age from 107 unlocks the native's exact classical prophecy, past life karmic causes, deity remedies, and precision timing of relief."}
                </p>
              </div>
              <div className="text-right">
                <span className="text-[11px] text-amber-300/80 bg-black/40 px-3 py-1.5 rounded-lg border border-white/10 font-mono block">
                  Formula: 107 - Completed Age = Remainder
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Author: R. G. Rao (Sagar Publications)
                </span>
              </div>
            </div>
          </div>

          {/* Interactive Calculation Card */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block mb-1.5">
                  {isTa ? "ஜாதகரின் பூர்த்தியான வயது (Completed Age):" : "Querent's Completed Age (Years):"}
                </label>
                <input
                  type="number"
                  min="0"
                  max="107"
                  value={prashnaAge}
                  onChange={(e) => setPrashnaAge(Number(e.target.value))}
                  className="w-full px-3.5 py-2 rounded-xl text-sm border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-semibold focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
                <span className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 block">
                  {isTa ? "107 - வயது = பிரசன்ன எண்: " : "Prediction Remainder: "}
                  <strong className="text-amber-600 dark:text-amber-400">
                    {prashnaAge === 0 ? 107 : Math.max(0, 107 - prashnaAge)}
                  </strong>
                </span>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block mb-1.5">
                  {isTa ? "கேள்விப் பிரிவு (Query Category):" : "Query Category:"}
                </label>
                <select
                  value={prashnaCategory}
                  onChange={(e) => setPrashnaCategory(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl text-sm border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium focus:ring-2 focus:ring-amber-500 focus:outline-none"
                >
                  <option value="general">{isTa ? "பொதுவான வாழ்வு பலன் (General)" : "General Life & Fortune"}</option>
                  <option value="career">{isTa ? "உத்தியோகம் / தொழில் (Career / Job)" : "Career & Profession"}</option>
                  <option value="business">{isTa ? "வியாபாரம் / வர்த்தகம் (Commercial Trade)" : "Business & Trade"}</option>
                  <option value="marriage">{isTa ? "திருமணம் / இல்லறம் (Marriage & Spouse)" : "Marriage & Relationships"}</option>
                  <option value="health">{isTa ? "உடல் நலம் / நோய் தீர்வு (Health & Cures)" : "Health & Medical Relief"}</option>
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={() => handleFetchPrashna(prashnaAge, prashnaCategory)}
                  disabled={isPrashnaLoading}
                  className="w-full py-2.5 px-4 rounded-xl text-sm font-bold text-white bg-gradient-to-r from-amber-700 to-orange-700 hover:from-amber-800 hover:to-orange-800 transition-all shadow-md flex items-center justify-center gap-2 disabled:opacity-60"
                >
                  {isPrashnaLoading ? (
                    <span>{isTa ? "கணக்கிடப்படுகிறது..." : "Consulting Oracle..."}</span>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-amber-200" />
                      <span>{isTa ? "நாடி வாக்கு பெறுக" : "Reveal Oracle Prophecy"}</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Results Box */}
          {prashnaResult && (
            <div className="space-y-4">
              {/* Sacred Invocations */}
              <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 text-center">
                <span className="text-xs font-mono font-bold tracking-wider text-amber-800 dark:text-amber-300 uppercase block">
                  {prashnaResult.guru_mantra}
                </span>
                {prashnaResult.sanskrit_sloka && (
                  <span className="text-sm font-semibold text-amber-900 dark:text-amber-200 italic mt-1 block">
                    "{prashnaResult.sanskrit_sloka}"
                  </span>
                )}
              </div>

              {/* Central Prophecy Card */}
              <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
                  <div>
                    <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                      {isTa ? "இயங்கும் யோகம் / அம்சம்:" : "Active Yoga / Amsha:"}
                    </span>
                    <h4 className="text-lg font-bold text-amber-800 dark:text-amber-300">
                      {isTa ? prashnaResult.yoga_name_ta : prashnaResult.yoga_name_en}
                    </h4>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 rounded-full bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-300 text-xs font-bold border border-amber-200 dark:border-amber-800 font-mono">
                      Prediction #{prashnaResult.prediction_number}
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                      {prashnaResult.formula_applied}
                    </span>
                  </div>
                </div>

                {/* Core Prophecy Text */}
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block mb-1">
                    {isTa ? "பிரசன்ன நாடி வாக்கு (Core Oracle Prophecy):" : "Core Oracle Prophecy:"}
                  </span>
                  <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed font-serif">
                    {isTa ? prashnaResult.core_prophecy_ta : prashnaResult.core_prophecy_en}
                  </p>
                </div>

                {/* 3 Pillars Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Career & Finance */}
                  <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/30 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-blue-800 dark:text-blue-300 font-bold text-xs">
                      <Briefcase className="w-3.5 h-3.5" />
                      <span>{isTa ? "தொழில் & தன யோகம்" : "Career & Finance"}</span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      {isTa ? prashnaResult.career_and_finance_ta : prashnaResult.career_and_finance_en}
                    </p>
                  </div>

                  {/* Family & Relationships */}
                  <div className="p-4 rounded-xl bg-pink-50/50 dark:bg-pink-950/20 border border-pink-100 dark:border-pink-900/30 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-pink-800 dark:text-pink-300 font-bold text-xs">
                      <Heart className="w-3.5 h-3.5" />
                      <span>{isTa ? "குடும்பம் & இல்லறம்" : "Family & Household"}</span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      {isTa ? prashnaResult.family_and_relationships_ta : prashnaResult.family_and_relationships_en}
                    </p>
                  </div>

                  {/* Health & Cautions */}
                  <div className="p-4 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/30 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-emerald-800 dark:text-emerald-300 font-bold text-xs">
                      <Shield className="w-3.5 h-3.5" />
                      <span>{isTa ? "உடல் நலம் & தீர்வு" : "Health & Cures"}</span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      {isTa ? prashnaResult.health_and_cautions_ta : prashnaResult.health_and_cautions_en}
                    </p>
                  </div>
                </div>

                {/* Karmic Cause & Remedy Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  {/* Past Karma Cause */}
                  {prashnaResult.past_karma_cause_en && (
                    <div className="p-4 rounded-xl bg-purple-50/60 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-900/40 space-y-1.5">
                      <div className="flex items-center gap-1.5 text-purple-800 dark:text-purple-300 font-bold text-xs">
                        <Flame className="w-3.5 h-3.5 text-purple-500" />
                        <span>{isTa ? "பூர்வ கர்ம வினை (Poorva Karma Cause):" : "Past Life Karmic Root Cause:"}</span>
                      </div>
                      <p className="text-xs text-purple-950 dark:text-purple-200 leading-relaxed">
                        {isTa ? prashnaResult.past_karma_cause_ta : prashnaResult.past_karma_cause_en}
                      </p>
                    </div>
                  )}

                  {/* Prescribed Remedy */}
                  <div className="p-4 rounded-xl bg-amber-50/60 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-amber-800 dark:text-amber-300 font-bold text-xs">
                      <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                      <span>{isTa ? "பரிகார தெய்வம் & பூஜை (Prescribed Remedy):" : "Prescribed Remedy & Deity:"}</span>
                    </div>
                    <p className="text-xs text-amber-950 dark:text-amber-200 leading-relaxed font-semibold">
                      {isTa ? prashnaResult.prescribed_remedy_ta : prashnaResult.prescribed_remedy_en}
                    </p>
                  </div>
                </div>

                {/* Timeline Banner */}
                <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-900/20 via-teal-900/20 to-slate-900/20 border border-emerald-500/30 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-emerald-500 shrink-0" />
                    <div>
                      <span className="text-[11px] font-bold text-emerald-800 dark:text-emerald-300 block">
                        {isTa ? "துன்பங்கள் நீங்கி சுப பலன்கள் தொடங்கும் காலம்:" : "Precise Relief & Prosperity Timeline:"}
                      </span>
                      <span className="text-xs text-slate-700 dark:text-slate-200 font-medium">
                        {isTa ? prashnaResult.relief_timeline_ta : prashnaResult.relief_timeline_en}
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                    Bhrigu Prashna Nadi
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

    </div>
  );
}
