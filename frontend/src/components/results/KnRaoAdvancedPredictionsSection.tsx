"use client";

import React, { useState } from "react";
import {
  KnRaoAdvancedResearchResponse,
  HoroscopeResponse,
} from "@/lib/types";
import {
  Briefcase,
  Cpu,
  Feather,
  Heart,
  Grid,
  Activity,
  Award,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Layers,
  Sparkles,
  Shield,
  Clock,
  Compass,
} from "lucide-react";

interface KnRaoAdvancedPredictionsSectionProps {
  horoscope?: HoroscopeResponse;
  data?: KnRaoAdvancedResearchResponse | null;
  language?: "en" | "ta";
}

export function KnRaoAdvancedPredictionsSection({
  data,
  language = "en",
}: KnRaoAdvancedPredictionsSectionProps) {
  const [activeTab, setActiveTab] = useState<
    "service_business" | "technical" | "authors" | "marital" | "kakshya" | "medical"
  >("service_business");

  if (!data) {
    return null;
  }

  const {
    service_vs_self_employment: se,
    technical_profession: tech,
    author_vs_journalist: auth,
    marital_discord: marr,
    medical_timing: med,
    jaimini_karakas: karakas,
    karakamsha_sign: kk_sign,
    arudha_lagna: al_sign,
    upapada_lagna: ul_sign,
    darapada: a7_sign,
  } = data;

  const isTa = language === "ta";

  return (
    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden my-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-amber-700 via-orange-800 to-indigo-900 text-white p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-200 border border-amber-400/30 text-xs font-semibold uppercase tracking-wider mb-2">
              <Award className="w-3.5 h-3.5" />
              {isTa ? "கே.என். ராவ் ஆய்வுக் களஞ்சியம்" : "K.N. Rao Research Canon"}
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
              {isTa
                ? "மேம்பட்ட ஜோதிட முன்கணிப்பு முறைகள்"
                : "Advanced Techniques of Astrological Predictions"}
            </h2>
            <p className="text-amber-100/90 text-sm mt-1 max-w-2xl">
              {isTa
                ? "பாரதிய வித்யா பவன் ஆய்வுப் பேராசிரியர்களின் பல ஆண்டு சோதனைகளில் நிரூபிக்கப்பட்ட கணித மாதிரிகள் மற்றும் விதிகள்."
                : "Empirically validated models from the research faculty of Bharatiya Vidya Bhavan (New Delhi), edited by K.N. Rao."}
            </p>
          </div>

          {/* Quick Badges */}
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-white/20">
              AK: <strong>{karakas?.AK || "Sun"}</strong>
            </span>
            <span className="bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-white/20">
              Karakamsha: <strong>{kk_sign}</strong>
            </span>
            <span className="bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-white/20">
              Upapada (UL): <strong>{ul_sign}</strong>
            </span>
            <span className="bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-white/20">
              Arudha (AL): <strong>{al_sign}</strong>
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-none mt-6 pt-4 border-t border-white/10">
          <button
            onClick={() => setActiveTab("service_business")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap transition-all ${
              activeTab === "service_business"
                ? "bg-white text-orange-950 font-bold shadow-md"
                : "bg-white/10 text-white/80 hover:bg-white/20"
            }`}
          >
            <Briefcase className="w-4 h-4" />
            {isTa ? "சுயதொழில் vs உத்தியோகம்" : "Service vs Business"}
          </button>

          <button
            onClick={() => setActiveTab("technical")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap transition-all ${
              activeTab === "technical"
                ? "bg-white text-orange-950 font-bold shadow-md"
                : "bg-white/10 text-white/80 hover:bg-white/20"
            }`}
          >
            <Cpu className="w-4 h-4" />
            {isTa ? "தொழில்நுட்ப மதிப்பீடு" : "Technical Scoring"}
          </button>

          <button
            onClick={() => setActiveTab("authors")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap transition-all ${
              activeTab === "authors"
                ? "bg-white text-orange-950 font-bold shadow-md"
                : "bg-white/10 text-white/80 hover:bg-white/20"
            }`}
          >
            <Feather className="w-4 h-4" />
            {isTa ? "எழுத்தாளர் vs இதழியல்" : "Authors & Media"}
          </button>

          <button
            onClick={() => setActiveTab("marital")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap transition-all ${
              activeTab === "marital"
                ? "bg-white text-orange-950 font-bold shadow-md"
                : "bg-white/10 text-white/80 hover:bg-white/20"
            }`}
          >
            <Heart className="w-4 h-4" />
            {isTa ? "தாம்பத்திய இணக்கம் (உபபதம்)" : "Marital Discord (UL)"}
          </button>

          <button
            onClick={() => setActiveTab("medical")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap transition-all ${
              activeTab === "medical"
                ? "bg-white text-orange-950 font-bold shadow-md"
                : "bg-white/10 text-white/80 hover:bg-white/20"
            }`}
          >
            <Activity className="w-4 h-4" />
            {isTa ? "மருத்துவ முன்னறிவிப்பு & மிருத்யு பாகை" : "Medical Timing & MB"}
          </button>
        </div>
      </div>

      {/* Main Tab Content */}
      <div className="p-6 sm:p-8">
        {/* TAB 1: SERVICE VS SELF-EMPLOYMENT (S.N. KAPOOR) */}
        {activeTab === "service_business" && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between p-6 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-slate-800/60 dark:to-slate-800/20 border border-amber-200 dark:border-slate-700 rounded-xl">
              <div>
                <span className="text-xs font-semibold text-amber-700 dark:text-amber-400 uppercase tracking-wider">
                  {isTa ? "எஸ்.என். கபூர் அனுபவ மாதிரி" : "S.N. Kapoor Empirical Model"}
                </span>
                <h3 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {isTa ? se.verdict_tamil : se.primary_verdict}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Saturn: <span className="font-semibold text-slate-700 dark:text-slate-300">{se.saturn_status}</span> |
                  Lagna Lord: <span className="font-semibold text-slate-700 dark:text-slate-300">{se.lagna_lord_avastha}</span> |
                  10th Lord: <span className="font-semibold text-slate-700 dark:text-slate-300">{se.tenth_lord_avastha}</span>
                </p>
              </div>

              <div className="mt-4 md:mt-0 flex items-center gap-6">
                <div className="text-center">
                  <div className="text-2xl font-extrabold text-orange-600 dark:text-orange-400">
                    {se.self_employment_probability}%
                  </div>
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400">
                    {isTa ? "சுயதொழில் வாய்ப்பு" : "Self-Employment"}
                  </div>
                </div>

                <div className="h-10 w-px bg-slate-300 dark:bg-slate-700" />

                <div className="text-center">
                  <div className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400">
                    {se.service_probability}%
                  </div>
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400">
                    {isTa ? "உத்தியோக வாய்ப்பு" : "Salaried Service"}
                  </div>
                </div>
              </div>
            </div>

            {/* Probability Progress Bar */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-slate-600 dark:text-slate-400">
                <span>{isTa ? "வணிகம் / சுயதொழில்" : "Business / Independent"} ({se.self_employment_probability}%)</span>
                <span>{isTa ? "அரசு / தனியார் உத்தியோகம்" : "Corporate / Govt Service"} ({se.service_probability}%)</span>
              </div>
              <div className="w-full h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden flex">
                <div
                  className="bg-gradient-to-r from-amber-500 to-orange-600 transition-all duration-500"
                  style={{ width: `${se.self_employment_probability}%` }}
                />
                <div
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 transition-all duration-500"
                  style={{ width: `${se.service_probability}%` }}
                />
              </div>
            </div>

            {/* Diagnostic Metrics Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                  <Flame className="w-4 h-4 text-orange-500" />
                  {isTa ? "பரமாத்மாம்ச கிரகங்கள்" : "Poorna Parmatmansha"}
                </div>
                <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {se.poorna_parmatmansha_count} / 4
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa ? "சூரியன், சந்திரன், செவ்வாய், ராகு பார்வை/நிலை" : "Sun, Moon, Mars, Rahu in 7-12 or 10-3"}
                </p>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                  <Layers className="w-4 h-4 text-blue-500" />
                  {isTa ? "பணிவு ஸ்தான கிரகங்கள் (4-6)" : "Subordination Zone (H4-6)"}
                </div>
                <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {se.planets_in_4_to_6}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa ? "4, 5, 6-ம் வீடுகளில் கிரகங்கள் உத்தியோகத்தை வலுப்படுத்தும்" : "Clustering here favors structured service"}
                </p>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                  <Compass className="w-4 h-4 text-emerald-500" />
                  {isTa ? "தத்துவ சமநிலை" : "Tattwa Balance"}
                </div>
                <div className="text-sm font-semibold text-slate-900 dark:text-white mt-1">
                  Agni+Vayu: <strong>{se.agni_vayu_count}</strong> | Prithvi+Jala: <strong>{se.prithvi_jala_count}</strong>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {se.agni_vayu_count >= se.prithvi_jala_count
                    ? (isTa ? "நெருப்பு & காற்று ஆதிக்கம்: வணிக உந்துதல்" : "Fire & Air dominant: Enterprise")
                    : (isTa ? "நிலம் & நீர் ஆதிக்கம்: சேவை ஒழுக்கம்" : "Earth & Water dominant: Service")}
                </p>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                  <Shield className="w-4 h-4 text-purple-500" />
                  {isTa ? "சனி பகவான் நிலை" : "Saturn Transit Dignity"}
                </div>
                <div className="text-sm font-bold text-slate-900 dark:text-white mt-1">
                  {se.saturn_status.split(" ")[0]}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {se.saturn_aspects_career
                    ? (isTa ? "தொழில்/லக்னத்தை நோக்குகிறார்" : "Aspects Career/Lagna")
                    : (isTa ? "நேரடி பார்வை இல்லை" : "No direct aspect")}
                </p>
              </div>
            </div>

            {/* Contributing factors */}
            <div className="p-5 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-slate-200 dark:border-slate-800">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-3">
                {isTa ? "முடிவை நிர்ணயித்த முதன்மைக் காரணிகள்" : "Deciding Research Factors"}
              </h4>
              <ul className="space-y-2 text-xs sm:text-sm text-slate-700 dark:text-slate-300">
                {(isTa ? se.contributing_factors_tamil : se.contributing_factors).map((factor, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-orange-500 shrink-0 mt-0.5" />
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* TAB 2: TECHNICAL VS NON-TECHNICAL SCORING (R.C. SHARMA) */}
        {activeTab === "technical" && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between p-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-slate-800/60 dark:to-slate-800/20 border border-blue-200 dark:border-slate-700 rounded-xl">
              <div>
                <span className="text-xs font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wider">
                  {isTa ? "ஆர்.சி. சர்மா கணித மாதிரி (4-அடுக்கு மதிப்பீடு)" : "R.C. Sharma 4-Fold Scoring Model"}
                </span>
                <h3 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {isTa ? tech.category_tamil : tech.category}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Karakamsha: <strong>{tech.karakamsha_sign}</strong> | Cumulative Score:{" "}
                  <strong className={tech.total_score <= -2 ? "text-blue-600" : "text-emerald-600"}>
                    {tech.total_score}
                  </strong>{" "}
                  (Negative = Technical, Positive = Humanities/Finance)
                </p>
              </div>

              {tech.rahu_engineering_prominence && (
                <div className="mt-4 md:mt-0 px-4 py-2 bg-purple-100 dark:bg-purple-900/40 border border-purple-300 dark:border-purple-700 rounded-xl text-xs font-semibold text-purple-900 dark:text-purple-200 flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                  {isTa ? "ராகு ஆதிக்கம்: கணினி & மென்பொருள் பொறியியல்" : "Rahu Prominence: Computing & High-Tech"}
                </div>
              )}
            </div>

            {/* 4 Score Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                  {isTa ? "1. காரகாம்ச 10-ம் வீடு" : "1. Karakamsha 10th"}
                </div>
                <div className={`text-2xl font-bold mt-1 ${tech.score_karakamsha_10th < 0 ? "text-blue-600" : "text-amber-600"}`}>
                  {tech.score_karakamsha_10th > 0 ? `+${tech.score_karakamsha_10th}` : tech.score_karakamsha_10th}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa ? "ஆத்மகாரகனின் நவாம்ச 10-ம் அதிபதி/கிரகங்கள்" : "Planets aspecting/posited in 10th from AK"}
                </p>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                  {isTa ? "2. ஜென்ம லக்ன 10-ம் வீடு" : "2. Janma Lagna 10th"}
                </div>
                <div className={`text-2xl font-bold mt-1 ${tech.score_lagna_10th < 0 ? "text-blue-600" : "text-amber-600"}`}>
                  {tech.score_lagna_10th > 0 ? `+${tech.score_lagna_10th}` : tech.score_lagna_10th}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa ? "லக்னத்திற்கு 10-ம் அதிபதி & பார்வை" : "10th lord and drishti from natal Lagna"}
                </p>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                  {isTa ? "3. சந்திர லக்ன 10-ம் வீடு" : "3. Chandra Lagna 10th"}
                </div>
                <div className={`text-2xl font-bold mt-1 ${tech.score_moon_10th < 0 ? "text-blue-600" : "text-amber-600"}`}>
                  {tech.score_moon_10th > 0 ? `+${tech.score_moon_10th}` : tech.score_moon_10th}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa ? "சந்திரனுக்கு 10-ம் அதிபதி & பார்வை" : "10th lord and drishti from Moon sign"}
                </p>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                  {isTa ? "4. நட்சத்திர தொடர்பு" : "4. Nakshatra Influences"}
                </div>
                <div className={`text-2xl font-bold mt-1 ${tech.score_nakshatra_10th < 0 ? "text-blue-600" : "text-amber-600"}`}>
                  {tech.score_nakshatra_10th > 0 ? `+${tech.score_nakshatra_10th}` : tech.score_nakshatra_10th}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa ? "10-ம் அதிபதி நின்ற நட்சத்திர நாதனின் தகுதி" : "Nakshatra rulers of 10th lord & house"}
                </p>
              </div>
            </div>

            {/* Interpretation */}
            <div className="p-5 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-slate-200 dark:border-slate-800 text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                {isTa ? "ஆய்வு விளக்கம்" : "Empirical Interpretation"}
              </h4>
              <p>{isTa ? tech.interpretation_tamil : tech.interpretation}</p>
            </div>
          </div>
        )}

        {/* TAB 3: AUTHORS AND JOURNALISTS (COL. A.K. GOUR) */}
        {activeTab === "authors" && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between p-6 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-slate-800/60 dark:to-slate-800/20 border border-emerald-200 dark:border-slate-700 rounded-xl">
              <div>
                <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                  {isTa ? "கர்னல் ஏ.கே. கெளர் இலக்கிய ஆய்வு" : "Col. A.K. Gour Literary Enquiry"}
                </span>
                <h3 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {isTa ? auth.writing_profile_tamil : auth.writing_profile}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {auth.mars_mercury_bond_details}
                </p>
              </div>

              <div className="mt-4 md:mt-0 flex gap-2">
                <span className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${
                  auth.pac_bond_present
                    ? "bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-300"
                    : "bg-slate-100 text-slate-600 border-slate-300 dark:bg-slate-800 dark:text-slate-400"
                }`}>
                  {auth.pac_bond_present ? "PAC Bond Active" : "No PAC Bond"}
                </span>

                <span className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${
                  auth.mars_mercury_bond
                    ? "bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-950/60 dark:text-amber-300"
                    : "bg-slate-100 text-slate-600 border-slate-300 dark:bg-slate-800 dark:text-slate-400"
                }`}>
                  {auth.mars_mercury_bond ? "Mars-Mercury Ink & Paper" : "No Mars-Mercury Link"}
                </span>
              </div>
            </div>

            {/* Literary Synthesis */}
            <div className="p-5 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-slate-200 dark:border-slate-800 text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                {isTa ? "இலக்கிய மற்றும் ஊடகத் திறன் தொகுப்பு" : "Literary & Media Talent Synthesis"}
              </h4>
              <p>{isTa ? auth.synthesis_tamil : auth.synthesis}</p>
            </div>
          </div>
        )}

        {/* TAB 4: MARITAL DISCORD & UPAPADA (SHUNNY NIGAM & SHIV RAJ SHARMA) */}
        {activeTab === "marital" && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between p-6 bg-gradient-to-r from-rose-50 to-pink-50 dark:from-slate-800/60 dark:to-slate-800/20 border border-rose-200 dark:border-slate-700 rounded-xl">
              <div>
                <span className="text-xs font-semibold text-rose-700 dark:text-rose-400 uppercase tracking-wider">
                  {isTa ? "ஷன்னி நிகாம் & சிவராஜ் சர்மா ஆய்வு (4 முதன்மை விதிகள்)" : "Shunny Nigam & Shiv Raj Sharma Research"}
                </span>
                <h3 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {isTa ? marr.discord_intensity_tamil : marr.discord_intensity}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Upapada Lagna (UL): <strong>{marr.upapada_lagna_sign}</strong> | 2nd from UL:{" "}
                  <strong>{marr.second_from_upapada_sign}</strong> | Darakaraka:{" "}
                  <strong>{marr.darakaraka_planet}</strong>
                </p>
              </div>

              <div className="mt-4 md:mt-0 text-center">
                <div className="text-2xl font-extrabold text-rose-600 dark:text-rose-400">
                  {marr.main_rules_matched_count} / 4
                </div>
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400">
                  {isTa ? "விதிகள் பொருத்தம்" : "Main Rules Matched"}
                </div>
              </div>
            </div>

            {/* 4 Main Rules Checklist */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-xl border ${
                marr.rule_a_matched
                  ? "bg-rose-50/60 border-rose-300 dark:bg-rose-950/20 dark:border-rose-800"
                  : "bg-slate-50 border-slate-200 dark:bg-slate-800/30 dark:border-slate-800"
              }`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase text-slate-700 dark:text-slate-300">
                    Rule A (96% Empirical)
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                    marr.rule_a_matched ? "bg-rose-600 text-white" : "bg-emerald-600 text-white"
                  }`}>
                    {marr.rule_a_matched ? "TRIGGERED" : "CLEAR"}
                  </span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5">
                  {isTa
                    ? "உபபத லக்னத்திற்கு 2-ம் வீட்டில் பாபக் கிரகங்கள் அமைதல் அல்லது ஜெமினி பார்வை."
                    : "Malefics in or aspecting (Jaimini) the 2nd house from Upapada Lagna."}
                </p>
              </div>

              <div className={`p-4 rounded-xl border ${
                marr.rule_b_matched
                  ? "bg-rose-50/60 border-rose-300 dark:bg-rose-950/20 dark:border-rose-800"
                  : "bg-slate-50 border-slate-200 dark:bg-slate-800/30 dark:border-slate-800"
              }`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase text-slate-700 dark:text-slate-300">
                    Rule B (64% Empirical)
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                    marr.rule_b_matched ? "bg-rose-600 text-white" : "bg-emerald-600 text-white"
                  }`}>
                    {marr.rule_b_matched ? "TRIGGERED" : "CLEAR"}
                  </span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5">
                  {isTa
                    ? "7-ம் அதிபதி நீசம்/அஸ்தமனம் அல்லது நவாம்சத்தில் (D9) பாப சேர்க்கை."
                    : "Natal 7th lord debilitated, combust, or afflicted in Navamsha (D9)."}
                </p>
              </div>

              <div className={`p-4 rounded-xl border ${
                marr.rule_c_matched
                  ? "bg-rose-50/60 border-rose-300 dark:bg-rose-950/20 dark:border-rose-800"
                  : "bg-slate-50 border-slate-200 dark:bg-slate-800/30 dark:border-slate-800"
              }`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase text-slate-700 dark:text-slate-300">
                    Rule C (64% Empirical)
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                    marr.rule_c_matched ? "bg-rose-600 text-white" : "bg-emerald-600 text-white"
                  }`}>
                    {marr.rule_c_matched ? "TRIGGERED" : "CLEAR"}
                  </span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5">
                  {isTa
                    ? "களத்திரகாரகன் சுக்கிரன் நீசம்/அஸ்தமனம் அல்லது பாபகர்த்தாரி யோகத்தில் சிக்கல்."
                    : "Venus afflicted by malefics, debilitated, or hemmed in Papakartari Yoga."}
                </p>
              </div>

              <div className={`p-4 rounded-xl border ${
                marr.rule_d_matched
                  ? "bg-rose-50/60 border-rose-300 dark:bg-rose-950/20 dark:border-rose-800"
                  : "bg-slate-50 border-slate-200 dark:bg-slate-800/30 dark:border-slate-800"
              }`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase text-slate-700 dark:text-slate-300">
                    Rule D (84% Empirical)
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                    marr.rule_d_matched ? "bg-rose-600 text-white" : "bg-emerald-600 text-white"
                  }`}>
                    {marr.rule_d_matched ? "TRIGGERED" : "CLEAR"}
                  </span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5">
                  {isTa
                    ? "6, 8, 12-ம் மறைவு ஸ்தான அதிபதிகள் 7-ம் வீடு அல்லது 7-ம் அதிபதியுடன் தொடர்பு."
                    : "Dusthana (6/8/12) lords associated with 7th house or 7th lord."}
                </p>
              </div>
            </div>

            {/* Darakaraka Timing */}
            <div className="p-5 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-slate-200 dark:border-slate-800 text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                {isTa ? "தாரகாரகன் விம்சோத்தரி தசா கால ஆய்வு" : "Darakaraka Timing Analysis (Supriya Jagdish)"}
              </h4>
              <p>{marr.darakaraka_dasha_analysis}</p>
            </div>
          </div>
        )}

        {/* TAB 5: MEDICAL TIMING & MRITYU BHAGA (DR. K.S. CHARAK) */}
        {activeTab === "medical" && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between p-6 bg-gradient-to-r from-red-50 to-orange-50 dark:from-slate-800/60 dark:to-slate-800/20 border border-red-200 dark:border-slate-700 rounded-xl">
              <div>
                <span className="text-xs font-semibold text-red-700 dark:text-red-400 uppercase tracking-wider">
                  {isTa ? "டாக்டர் கே.எஸ். சரக் மருத்துவ ஜோதிட மாதிரி" : "Dr. K.S. Charak Medical Astrology Model"}
                </span>
                <h3 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {isTa ? med.prognosis_verdict_tamil : med.prognosis_verdict}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa ? med.subsequent_dasha_prognosis_tamil : med.subsequent_dasha_prognosis}
                </p>
              </div>

              <div className="mt-4 md:mt-0 text-center">
                <div className="text-2xl font-extrabold text-red-600 dark:text-red-400">
                  {med.planets_in_mrityu_bhaga.length}
                </div>
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400">
                  {isTa ? "மிருத்யு பாகை கிரகங்கள்" : "Mrityu Bhaga Planets"}
                </div>
              </div>
            </div>

            {/* Mrityu Bhaga Alerts */}
            {med.planets_in_mrityu_bhaga.length > 0 ? (
              <div className="p-4 bg-red-50 dark:bg-red-950/20 border border-red-300 dark:border-red-800 rounded-xl space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-red-800 dark:text-red-300 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  {isTa ? "மிருத்யு பாகை எச்சரிக்கைகள் (அபாய பாகை)" : "Mrityu Bhaga Fatal Degree Alerts"}
                </h4>
                {med.planets_in_mrityu_bhaga.map((item, idx) => (
                  <p key={idx} className="text-xs text-red-700 dark:text-red-300">
                    <strong>{item.planet}</strong> is placed at {item.degree_in_sign}° in {item.sign} (Exact MB: {item.mrityu_bhaga_degree}°, diff: {item.difference_deg}°).
                  </p>
                ))}
              </div>
            ) : (
              <div className="p-4 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-300 dark:border-emerald-800 rounded-xl text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                {isTa
                  ? "எந்த கிரகமும் மிருத்யு பாகை அபாய பாகையில் அமையவில்லை (இயற்கை உடல் பாதுகாப்பு உறுதி)."
                  : "No planets occupy classical Mrityu Bhaga fatal degrees. Vital baseline is protected."}
              </div>
            )}

            {/* Dasha Health Vulnerabilities */}
            {med.dasha_lords_health_risk.length > 0 && (
              <div className="p-5 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-slate-200 dark:border-slate-800">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                  {isTa ? "தசா நாதர்களின் உடல்நல அழுத்தங்கள்" : "Active Dasha Lords Health Influences"}
                </h4>
                <ul className="space-y-1.5 text-xs text-slate-700 dark:text-slate-300">
                  {med.dasha_lords_health_risk.map((risk, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-amber-500" />
                      <span>{risk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
