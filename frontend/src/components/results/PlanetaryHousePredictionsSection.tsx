"use client";

import React, { useState, useMemo } from "react";
import {
  evaluateHoroscopePlanetarySthanas,
  EvaluatedPlanetSthana,
  BhavaCategory,
} from "@/lib/planetary-sthana-predictions";
import {
  Sparkles,
  BookOpen,
  ShieldCheck,
  AlertCircle,
  Compass,
  Search,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  Briefcase,
  HeartPulse,
  Crown,
  Flame,
  Zap,
  Filter,
  CheckCircle2,
  Layers,
  Star,
  Activity,
  UserCheck,
} from "lucide-react";

interface PlanetaryHousePredictionsSectionProps {
  horoscope: any;
  language?: "en" | "ta";
}

const BHAVA_CATEGORY_LABELS: Record<
  BhavaCategory,
  { ta: string; en: string; badgeClass: string }
> = {
  kendra: {
    ta: "கேந்திரம் (1, 4, 7, 10)",
    en: "Kendra (1, 4, 7, 10)",
    badgeClass: "bg-blue-50 text-blue-800 border-blue-200",
  },
  trikona: {
    ta: "திரிகோணம் (1, 5, 9)",
    en: "Trikona (1, 5, 9)",
    badgeClass: "bg-amber-50 text-amber-800 border-amber-200",
  },
  upachaya: {
    ta: "உபசயம் (3, 6, 10, 11)",
    en: "Upachaya (3, 6, 10, 11)",
    badgeClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
  },
  dusthana: {
    ta: "மறைவு ஸ்தானம் (6, 8, 12)",
    en: "Dusthana (6, 8, 12)",
    badgeClass: "bg-rose-50 text-rose-800 border-rose-200",
  },
  panaphara: {
    ta: "பணபர ஸ்தானம் (2, 5, 8, 11)",
    en: "Panaphara (2, 5, 8, 11)",
    badgeClass: "bg-purple-50 text-purple-800 border-purple-200",
  },
  apoklima: {
    ta: "அபோக்லிம ஸ்தானம் (3, 6, 9, 12)",
    en: "Apoklima (3, 6, 9, 12)",
    badgeClass: "bg-slate-50 text-slate-800 border-slate-200",
  },
};

export function PlanetaryHousePredictionsSection({
  horoscope,
  language = "ta",
}: PlanetaryHousePredictionsSectionProps) {
  const [selectedPlanet, setSelectedPlanet] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [expandedPlanets, setExpandedPlanets] = useState<Record<string, boolean>>({
    Sun: true,
    Moon: true,
    Mars: true,
    Mercury: true,
    Jupiter: true,
    Venus: true,
    Saturn: true,
    Rahu: true,
    Ketu: true,
  });

  // Evaluate the 9 planets' placements and dignities dynamically
  const evaluatedPlanets: EvaluatedPlanetSthana[] = useMemo(() => {
    return evaluateHoroscopePlanetarySthanas(horoscope);
  }, [horoscope]);

  // Filtering based on planet pill, bhava category, and search query
  const filteredPlanets = useMemo(() => {
    return evaluatedPlanets.filter((item) => {
      // Planet filter
      if (selectedPlanet !== "all" && item.planet_name.toLowerCase() !== selectedPlanet.toLowerCase()) {
        return false;
      }

      // Bhava category filter
      if (selectedCategory !== "all") {
        if (selectedCategory === "kendra" && ![1, 4, 7, 10].includes(item.house_number)) return false;
        if (selectedCategory === "trikona" && ![1, 5, 9].includes(item.house_number)) return false;
        if (selectedCategory === "upachaya" && ![3, 6, 10, 11].includes(item.house_number)) return false;
        if (selectedCategory === "dusthana" && ![6, 8, 12].includes(item.house_number)) return false;
      }

      // Search query filter (matches tamil / english text, house title, traits)
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const p = item.prediction;
        const matchTitle =
          item.planet_name.toLowerCase().includes(q) ||
          item.planet_name_ta.toLowerCase().includes(q) ||
          item.house_name_ta.toLowerCase().includes(q) ||
          item.house_name_en.toLowerCase().includes(q) ||
          item.sign_name_ta.toLowerCase().includes(q) ||
          item.sign_name_en.toLowerCase().includes(q);

        const matchTraits =
          p.core_traits_ta.some((t) => t.toLowerCase().includes(q)) ||
          p.core_traits_en.some((t) => t.toLowerCase().includes(q)) ||
          p.strong_placement_ta.some((t) => t.toLowerCase().includes(q)) ||
          p.career_wealth_ta.some((t) => t.toLowerCase().includes(q)) ||
          p.health_precautions_ta.some((t) => t.toLowerCase().includes(q));

        return matchTitle || matchTraits;
      }

      return true;
    });
  }, [evaluatedPlanets, selectedPlanet, selectedCategory, searchQuery]);

  const toggleExpand = (planetName: string) => {
    setExpandedPlanets((prev) => ({
      ...prev,
      [planetName]: !prev[planetName],
    }));
  };

  const expandAll = () => {
    const allExp: Record<string, boolean> = {};
    evaluatedPlanets.forEach((p) => {
      allExp[p.planet_name] = true;
    });
    setExpandedPlanets(allExp);
  };

  const collapseAll = () => {
    setExpandedPlanets({});
  };

  if (!evaluatedPlanets || evaluatedPlanets.length === 0) {
    return null;
  }

  return (
    <div className="w-full bg-white rounded-2xl border border-[#D9DEE7] shadow-sm overflow-hidden my-6">
      {/* Header Banner - Classical Gold & Navy Theme */}
      <div className="bg-gradient-to-r from-[#153F6B] via-[#102d4d] to-[#183047] p-4 sm:p-6 text-white border-b border-[#B4872B]/30">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start sm:items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B4872B] shrink-0 shadow-md">
              <Crown className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="text-base sm:text-lg font-bold text-white tracking-wide">
                  {language === "ta"
                    ? "கிரகங்களின் ஸ்தான பலன்கள் (House Placements)"
                    : "Planetary House Placement Predictions"}
                </h3>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#B4872B] text-white shadow-2xs">
                  {language === "ta" ? "டாக்டர் பி. வி. ராமன் முறை" : "Dr. B. V. Raman Canon"}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-white/15 text-white/90">
                  {language === "ta" ? "சாராவளி & பிருஹத் பராசர ஹோர" : "Saravali & BPHS"}
                </span>
              </div>
              <p className="text-xs text-white/80 mt-1 max-w-3xl leading-relaxed">
                {language === "ta"
                  ? "லக்னத்திலிருந்து ஒன்பது கிரகங்கள் அமர்ந்திருக்கும் ஸ்தானம் (1 முதல் 12 பாவங்கள்) மற்றும் அவற்றின் வலிமை (ஆட்சி, உச்சம், நீசம், திக்பலம், ஷட்பல சதவீதம்) அடிப்படையிலான தனித்துவமான பாயிண்ட் பலன்கள்."
                  : "Authentic, bullet-pointed predictions for all 9 planets based on their house placements from Lagna (Houses 1-12) synthesized with real-time planetary dignity (exalted, own sign, debilitated, digbala) and Shadbala power."}
              </p>
            </div>
          </div>

          {/* Quick Stats Pill */}
          <div className="flex items-center gap-2 self-start md:self-auto shrink-0">
            <button
              type="button"
              onClick={expandAll}
              className="text-[11px] px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 text-white font-medium transition cursor-pointer border border-white/20"
            >
              {language === "ta" ? "அனைத்தும் விரி" : "Expand All"}
            </button>
            <button
              type="button"
              onClick={collapseAll}
              className="text-[11px] px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 text-white font-medium transition cursor-pointer border border-white/20"
            >
              {language === "ta" ? "அனைத்தும் சுருக்கு" : "Collapse All"}
            </button>
          </div>
        </div>

        {/* 9 Grahas Filter Strip */}
        <div className="mt-5 pt-4 border-t border-white/15 flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
          <button
            type="button"
            onClick={() => setSelectedPlanet("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 cursor-pointer ${
              selectedPlanet === "all"
                ? "bg-[#B4872B] text-white shadow-sm"
                : "bg-white/10 text-white/80 hover:bg-white/20"
            }`}
          >
            {language === "ta" ? "அனைத்து 9 கிரகங்கள்" : "All 9 Planets"}
          </button>
          {evaluatedPlanets.map((ep) => (
            <button
              key={ep.planet_name}
              type="button"
              onClick={() => setSelectedPlanet(ep.planet_name)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 cursor-pointer ${
                selectedPlanet.toLowerCase() === ep.planet_name.toLowerCase()
                  ? "bg-[#FAF2DE] text-[#153F6B] font-bold shadow-sm border border-[#D8BD80]"
                  : "bg-white/10 text-white/85 hover:bg-white/20"
              }`}
            >
              <span>{ep.symbol}</span>
              <span>{language === "ta" ? ep.planet_name_ta : ep.planet_name}</span>
              <span className="text-[10px] opacity-75 font-mono">({ep.house_number})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3.5 sm:p-4 bg-[#F8FAFC] border-b border-[#E2E8F0] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Bhava Category Filters */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs font-semibold text-[#52667E] flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" />
            {language === "ta" ? "பாவ வகை:" : "Bhava Class:"}
          </span>
          {[
            { id: "all", ta: "அனைத்தும்", en: "All" },
            { id: "kendra", ta: "கேந்திரங்கள் (1, 4, 7, 10)", en: "Kendras (1, 4, 7, 10)" },
            { id: "trikona", ta: "திரிகோணங்கள் (1, 5, 9)", en: "Trikonas (1, 5, 9)" },
            { id: "upachaya", ta: "உபசயங்கள் (3, 6, 10, 11)", en: "Upachayas (3, 6, 10, 11)" },
            { id: "dusthana", ta: "மறைவு ஸ்தானங்கள் (6, 8, 12)", en: "Dusthanas (6, 8, 12)" },
          ].map((cat) => (
            <button
              key={cat.id}
              type="button"
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition cursor-pointer border ${
                selectedCategory === cat.id
                  ? "bg-[#153F6B] text-white border-[#153F6B] font-bold shadow-2xs"
                  : "bg-white text-[#52667E] border-[#D9DEE7] hover:bg-[#F1F4F9]"
              }`}
            >
              {language === "ta" ? cat.ta : cat.en}
            </button>
          ))}
        </div>

        {/* Keyword Search Input */}
        <div className="relative min-w-[220px]">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-[#8190A6]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={
              language === "ta"
                ? "கோபம், கௌரவம், தொழில், செல்வம்..."
                : "Search temperament, career, health..."
            }
            className="w-full pl-8 pr-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-white text-xs text-[#183047] placeholder-[#8190A6] focus:outline-hidden focus:border-[#B4872B] focus:ring-1 focus:ring-[#B4872B] transition"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-[#8190A6] hover:text-[#183047] cursor-pointer"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Main Predictions Grid / List */}
      <div className="p-3.5 sm:p-6 space-y-4">
        {filteredPlanets.length === 0 ? (
          <div className="py-12 text-center text-sm text-[#8190A6]">
            <BookOpen className="w-8 h-8 mx-auto text-[#B4872B]/60 mb-2" />
            <p>
              {language === "ta"
                ? "வடிகட்டலுக்கு ஏற்ற பலன்கள் ஏதும் கிடைக்கவில்லை."
                : "No planetary placement matches your current search/filter."}
            </p>
          </div>
        ) : (
          filteredPlanets.map((planet) => {
            const isExpanded = Boolean(expandedPlanets[planet.planet_name]);
            const pred = planet.prediction;
            const bhavaCategoryMeta = BHAVA_CATEGORY_LABELS[planet.bhava_category] || {
              ta: "பாவம்",
              en: "Bhava",
              badgeClass: "bg-slate-50 text-slate-700 border-slate-200",
            };

            return (
              <div
                key={planet.planet_name}
                className="bg-white rounded-xl border border-[#D9DEE7] shadow-2xs hover:border-[#B4872B]/60 transition-all overflow-hidden"
              >
                {/* Planet Card Header */}
                <div
                  onClick={() => toggleExpand(planet.planet_name)}
                  className="p-3.5 sm:p-4 bg-gradient-to-r from-[#FAF2DE]/40 via-white to-[#F8FAFC] flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer select-none border-b border-[#F2F3F5] hover:bg-[#FAF2DE]/60 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-white border border-[#D8BD80] flex items-center justify-center text-xl shrink-0 shadow-xs">
                      {planet.symbol}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <h4 className="text-sm sm:text-base font-bold text-[#153F6B]">
                          {language === "ta" ? planet.planet_name_ta : planet.planet_name}
                        </h4>
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[#153F6B] text-white">
                          {language === "ta"
                            ? `${planet.house_number}-ஆம் பாவம் (${planet.sign_name_ta})`
                            : `${planet.house_number}th House (${planet.sign_name_en})`}
                        </span>

                        {/* Dignity Badge */}
                        <span
                          className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${
                            planet.dignity_type === "exalted"
                              ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                              : planet.dignity_type === "own_sign"
                              ? "bg-blue-50 text-blue-800 border-blue-300"
                              : planet.dignity_type === "dikbala"
                              ? "bg-purple-50 text-purple-800 border-purple-300"
                              : planet.dignity_type === "debilitated"
                              ? "bg-rose-50 text-rose-800 border-rose-300"
                              : "bg-slate-50 text-slate-700 border-slate-200"
                          }`}
                        >
                          {language === "ta" ? planet.dignity_label_ta : planet.dignity_label_en}
                        </span>

                        {/* Retrograde indicator */}
                        {planet.is_retrograde && (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-orange-100 text-orange-800 border border-orange-300">
                            {language === "ta" ? "வக்ரம்" : "Retrograde"}
                          </span>
                        )}
                      </div>

                      {/* Sub-header: Bhava Category & Element */}
                      <div className="flex items-center gap-2 mt-1 text-[11px] text-[#52667E] flex-wrap">
                        <span className={`px-2 py-0.2 rounded-full border text-[10px] font-semibold ${bhavaCategoryMeta.badgeClass}`}>
                          {language === "ta" ? bhavaCategoryMeta.ta : bhavaCategoryMeta.en}
                        </span>
                        <span>•</span>
                        <span>{language === "ta" ? `தத்துவம்: ${planet.element}` : `Element: ${planet.element}`}</span>
                        <span>•</span>
                        <span className="font-mono">{planet.degree_in_sign.toFixed(2)}°</span>
                      </div>
                    </div>
                  </div>

                  {/* Right: Shadbala Power Gauge & Expand Chevron */}
                  <div className="flex items-center gap-3 self-end sm:self-auto shrink-0">
                    {planet.shadbala_percentage !== undefined && (
                      <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-white border border-[#D9DEE7] text-[11px]">
                        <Activity className="w-3.5 h-3.5 text-[#B4872B]" />
                        <span className="font-medium text-[#52667E]">
                          {language === "ta" ? "ஷட்பலம்:" : "Shadbala:"}
                        </span>
                        <span
                          className={`font-bold font-mono ${
                            planet.shadbala_percentage >= 100 ? "text-emerald-700" : "text-amber-700"
                          }`}
                        >
                          {planet.shadbala_percentage}%
                        </span>
                        <div className="w-12 h-1.5 rounded-full bg-slate-100 overflow-hidden hidden sm:block">
                          <div
                            className={`h-full ${
                              planet.shadbala_percentage >= 100 ? "bg-emerald-500" : "bg-amber-500"
                            }`}
                            style={{ width: `${Math.min(100, (planet.shadbala_percentage / 150) * 100)}%` }}
                          />
                        </div>
                      </div>
                    )}

                    <div className="w-7 h-7 rounded-full bg-white border border-[#D9DEE7] flex items-center justify-center text-[#52667E]">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                  </div>
                </div>

                {/* Planet Prediction Content - Visible when expanded */}
                {isExpanded && (
                  <div className="p-4 sm:p-6 space-y-5 bg-white">
                    {/* Status Summary Banner */}
                    <div className="p-3 rounded-lg bg-[#FAF2DE]/50 border border-[#D8BD80]/50 text-xs text-[#183047] flex items-start gap-2">
                      <Sparkles className="w-4 h-4 text-[#B4872B] shrink-0 mt-0.5" />
                      <div>
                        <span className="font-bold text-[#8C6D23]">
                          {language === "ta" ? "ஸ்தான தீர்ப்பு: " : "Placement Verdict: "}
                        </span>
                        <span>{language === "ta" ? planet.status_summary_ta : planet.status_summary_en}</span>
                      </div>
                    </div>

                    {/* Section 1: Core Traits & Temperament (User's specific highlight: self-respect, anger, confidence) */}
                    <div>
                      <div className="flex items-center gap-2 mb-2 pb-1 border-b border-slate-100">
                        <Flame className="w-4 h-4 text-amber-600" />
                        <h5 className="text-xs sm:text-sm font-bold text-[#183047]">
                          {language === "ta"
                            ? "பொதுவான குணநலன்கள் & சுபாவம் (சுயகௌரவம், கோபம் & சுபாவம்)"
                            : "General Traits, Temperament & Self-Respect"}
                        </h5>
                      </div>
                      <ul className="space-y-1.5 pl-2">
                        {(language === "ta" ? pred.core_traits_ta : pred.core_traits_en).map((trait, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-xs text-[#2A3B50] leading-relaxed">
                            <span className="text-[#B4872B] font-bold text-sm leading-none mt-0.5">•</span>
                            <span>{trait}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Section 2: Current Dignity Impact (Strong vs Debilitated points tailored to current chart) */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Strong Placement Fruits */}
                      <div
                        className={`p-3.5 rounded-xl border ${
                          planet.is_net_strong
                            ? "bg-emerald-50/50 border-emerald-200 ring-1 ring-emerald-300/40"
                            : "bg-slate-50/70 border-slate-200"
                        }`}
                      >
                        <div className="flex items-center gap-1.5 mb-2">
                          <ShieldCheck
                            className={`w-4 h-4 ${planet.is_net_strong ? "text-emerald-700" : "text-slate-500"}`}
                          />
                          <h6
                            className={`text-xs font-bold ${
                              planet.is_net_strong ? "text-emerald-900" : "text-slate-700"
                            }`}
                          >
                            {language === "ta"
                              ? "வலுவான நிலையில் (ஆட்சி / உச்சம் / திக்பலம் / சுப சேர்க்கை)"
                              : "When Strong (Exalted / Own House / Digbala / Benefic)"}
                          </h6>
                          {planet.is_net_strong && (
                            <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-600 text-white ml-auto">
                              {language === "ta" ? "தற்போதைய நிலை" : "Current State"}
                            </span>
                          )}
                        </div>
                        <ul className="space-y-1.5 pl-1">
                          {(language === "ta" ? pred.strong_placement_ta : pred.strong_placement_en).map((pt, idx) => (
                            <li key={idx} className="flex items-start gap-1.5 text-xs text-slate-700 leading-relaxed">
                              <span className="text-emerald-600 font-bold">✓</span>
                              <span>{pt}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Weak Placement Precautions */}
                      <div
                        className={`p-3.5 rounded-xl border ${
                          planet.dignity_type === "debilitated" || (!planet.is_net_strong && (planet.shadbala_percentage || 100) < 95)
                            ? "bg-rose-50/60 border-rose-200 ring-1 ring-rose-300/40"
                            : "bg-slate-50/70 border-slate-200"
                        }`}
                      >
                        <div className="flex items-center gap-1.5 mb-2">
                          <AlertCircle
                            className={`w-4 h-4 ${
                              planet.dignity_type === "debilitated" ? "text-rose-600" : "text-slate-500"
                            }`}
                          />
                          <h6
                            className={`text-xs font-bold ${
                              planet.dignity_type === "debilitated" ? "text-rose-900" : "text-slate-700"
                            }`}
                          >
                            {language === "ta"
                              ? "பலவீனமான நிலையில் (நீசம் / பகை / குறைந்த பலம்)"
                              : "When Weak (Debilitated / Afflicted / Low Strength)"}
                          </h6>
                          {planet.dignity_type === "debilitated" && (
                            <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-rose-600 text-white ml-auto">
                              {language === "ta" ? "கவனம் தேவை" : "Needs Care"}
                            </span>
                          )}
                        </div>
                        <ul className="space-y-1.5 pl-1">
                          {(language === "ta" ? pred.weak_placement_ta : pred.weak_placement_en).map((pt, idx) => (
                            <li key={idx} className="flex items-start gap-1.5 text-xs text-slate-700 leading-relaxed">
                              <span className="text-rose-500 font-bold">⚠</span>
                              <span>{pt}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Section 3: Career & Wealth Fortunes */}
                    <div>
                      <div className="flex items-center gap-2 mb-2 pb-1 border-b border-slate-100">
                        <Briefcase className="w-4 h-4 text-blue-600" />
                        <h5 className="text-xs sm:text-sm font-bold text-[#183047]">
                          {language === "ta"
                            ? "தொழில், பதவி & பொருளாதார யோகங்கள்"
                            : "Career, Authority & Financial Fortunes"}
                        </h5>
                      </div>
                      <ul className="space-y-1.5 pl-2">
                        {(language === "ta" ? pred.career_wealth_ta : pred.career_wealth_en).map((cw, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-xs text-[#2A3B50] leading-relaxed">
                            <span className="text-blue-500 font-bold text-sm leading-none mt-0.5">•</span>
                            <span>{cw}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Section 4: Health Precautions */}
                    <div>
                      <div className="flex items-center gap-2 mb-2 pb-1 border-b border-slate-100">
                        <HeartPulse className="w-4 h-4 text-emerald-600" />
                        <h5 className="text-xs sm:text-sm font-bold text-[#183047]">
                          {language === "ta"
                            ? "உடல் ஆரோக்கியம் & தற்காப்பு எச்சரிக்கைகள்"
                            : "Health, Vitality & Preventive Precautions"}
                        </h5>
                      </div>
                      <ul className="space-y-1.5 pl-2">
                        {(language === "ta" ? pred.health_precautions_ta : pred.health_precautions_en).map((hp, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-xs text-[#2A3B50] leading-relaxed">
                            <span className="text-emerald-500 font-bold text-sm leading-none mt-0.5">•</span>
                            <span>{hp}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Card Footer: Source Citation */}
                    <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] text-[#8190A6]">
                      <div className="flex items-center gap-1.5">
                        <BookOpen className="w-3.5 h-3.5 text-[#B4872B]" />
                        <span>
                          {language === "ta" ? "சாஸ்திர ஆதாரம்: " : "Classical Authority: "}
                          <strong className="text-[#52667E]">{pred.source_reference}</strong>
                        </span>
                      </div>
                      <div className="text-[10px] text-[#8190A6] italic">
                        {language === "ta"
                          ? "* லக்னத்தை அடிப்படையாகக் கொண்ட ஸ்தான கணிப்பு."
                          : "* Accurate ascendant-relative house calculation."}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Section Footer Banner */}
      <div className="p-3 bg-[#FAF2DE]/30 border-t border-[#D9DEE7] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-[#52667E] px-4 sm:px-6">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[#B4872B]" />
          <span>
            {language === "ta"
              ? "கிரகங்களின் ஸ்தான பலன்கள் லக்னம், நவாம்சம் மற்றும் ஷட்பலத்தின் கூட்டு சக்தியால் மட்டுமே பரிபூரணமாக உணரப்படும்."
              : "Planetary house predictions manifest fully when harmonized with Rasi, Navamsa, and Shadbala strength."}
          </span>
        </div>
        <span className="text-[11px] text-[#8190A6] font-mono">108 Classical Rules Synthesized</span>
      </div>
    </div>
  );
}
