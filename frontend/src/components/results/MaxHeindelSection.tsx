"use client";

import React, { useState, useMemo } from "react";
import {
  MaxHeindelCompendium,
  HeindelSignAnatomy,
  HeindelPlanetPhysiology,
  HeindelViciousCircle,
  HeindelNailDiagnosis,
  HeindelPlanetaryAntidote,
  HeindelAphorism,
  HeindelNebularSpot,
  MedicalRule,
} from "@/lib/types";
import {
  Sparkles,
  ShieldAlert,
  HeartPulse,
  Activity,
  Compass,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  Layers,
  Search,
  BookOpen,
  Filter,
  Info,
  Clock,
  Eye,
  Cross,
  Sun,
  Moon,
  Flame,
  Award,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface MaxHeindelSectionProps {
  compendium: MaxHeindelCompendium;
  language: "en" | "ta";
  onSelectRule?: (rule: MedicalRule) => void;
}

export function MaxHeindelSection({
  compendium,
  language,
  onSelectRule,
}: MaxHeindelSectionProps) {
  const [activeTab, setActiveTab] = useState<
    "philosophy" | "anatomy" | "planets" | "circles" | "nails" | "aphorisms"
  >("philosophy");

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedCircle, setSelectedCircle] = useState<string | null>(null);
  const [selectedNailCategory, setSelectedNailCategory] = useState<string>("all");
  const [aphorismCategory, setAphorismCategory] = useState<string>("all");

  const {
    book_title,
    book_title_ta,
    authors,
    historical_foundation,
    core_philosophy_en,
    core_philosophy_ta,
    healer_injunctions = [],
    signs_anatomy = [],
    planets_physiology = [],
    sense_organs_affinities = [],
    vicious_circles = [],
    nail_and_hand_diagnosis = [],
    planetary_antidotes = [],
    nebular_spots = [],
    aphorisms = [],
    chart_evaluation = {},
    matched_rules = [],
  } = compendium;

  // Active chart-matched rules
  const activeMatchedRules = useMemo(() => {
    return matched_rules.filter((r) => r.is_active);
  }, [matched_rules]);

  // Filtered signs
  const filteredSigns = useMemo(() => {
    if (!searchQuery.trim()) return signs_anatomy;
    const q = searchQuery.toLowerCase();
    return signs_anatomy.filter(
      (s) =>
        s.sign_name_en.toLowerCase().includes(q) ||
        s.sign_name_ta.toLowerCase().includes(q) ||
        s.manilius_rulership.toLowerCase().includes(q) ||
        s.heindel_anatomical_systems.some((sys) => sys.toLowerCase().includes(q)) ||
        s.physiological_afflictions.some((aff) => aff.toLowerCase().includes(q))
    );
  }, [signs_anatomy, searchQuery]);

  // Filtered aphorisms
  const filteredAphorisms = useMemo(() => {
    return aphorisms.filter((a) => {
      if (aphorismCategory !== "all" && a.category !== aphorismCategory) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return (
          a.aphorism_en.toLowerCase().includes(q) ||
          a.aphorism_ta.toLowerCase().includes(q) ||
          a.practical_implication.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [aphorisms, aphorismCategory, searchQuery]);

  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-[#1A365D] via-[#2A4365] to-[#2B6CB0] p-5 sm:p-6 text-white shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1 rounded-full bg-white/20 px-2.5 py-0.5 text-xs font-semibold backdrop-blur-xs">
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                {language === "ta" ? "மேக்ஸ் ஹெயிண்டல் ஜோதிட நோய்நிர்ணயம்" : "Max Heindel Astro-Diagnosis"}
              </span>
              <span className="text-xs text-white/75">
                {authors}
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
              {language === "ta" ? book_title_ta : book_title}
            </h2>
            <p className="text-xs sm:text-sm text-white/85 max-w-2xl leading-relaxed">
              {language === "ta"
                ? "ரோசிக்ரூசியன் ஆன்மீக ஜோதிடம் மற்றும் மார்கஸ் மனிலியஸின் (கி.பி. 1-ம் நூற்றாண்டு) காலபுருஷ உடல் உடலியல் அடிப்படையில் தொகுக்கப்பட்ட மேற்கத்திய மருத்துவ ஜோதிடப் பெட்டகம்."
                : "Western Classical & Rosicrucian Esoteric Astro-Diagnosis integrating Marcus Manilius (1st c. AD Astronomica) with constitutional diagnosis, reflex circles, and hand-nail pathology."}
            </p>
          </div>

          <div className="shrink-0 flex items-center gap-3">
            <div className="rounded-xl bg-white/10 border border-white/20 p-3 text-center backdrop-blur-xs">
              <div className="text-xs text-amber-300 font-medium">
                {language === "ta" ? "உங்கள் லக்னம்" : "Native Lagna"}
              </div>
              <div className="text-base font-bold text-white">
                {chart_evaluation.lagna_sign_ta && language === "ta"
                  ? chart_evaluation.lagna_sign_ta
                  : chart_evaluation.lagna_sign || "Evaluated"}
              </div>
            </div>
            <div className="rounded-xl bg-amber-400/20 border border-amber-300/30 p-3 text-center backdrop-blur-xs">
              <div className="text-xl font-bold text-amber-200">
                {activeMatchedRules.length}
              </div>
              <div className="text-2xs font-semibold uppercase tracking-wider text-amber-100">
                {language === "ta" ? "பொருந்திய விதிகள்" : "Matched Rules"}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Sub-Navigation Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto text-xs font-semibold pb-1 border-b border-[#D9DEE7]">
        <button
          type="button"
          onClick={() => setActiveTab("philosophy")}
          className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "philosophy"
              ? "bg-[#1A365D] text-white shadow-xs font-bold"
              : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>{language === "ta" ? "அடிப்படை தத்துவம் & 19 நெறிமுறைகள்" : "Core Philosophy & 19 Injunctions"}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("anatomy")}
          className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "anatomy"
              ? "bg-[#1A365D] text-white shadow-xs font-bold"
              : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
          }`}
        >
          <Compass className="w-3.5 h-3.5" />
          <span>{language === "ta" ? "12 ராசிகள் & மனிலியஸ் உடலியல்" : "12 Signs & Manilius Anatomy"}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("planets")}
          className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "planets"
              ? "bg-[#1A365D] text-white shadow-xs font-bold"
              : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
          }`}
        >
          <Sun className="w-3.5 h-3.5" />
          <span>{language === "ta" ? "கிரக உடலியல் & மாற்று மருந்துகள்" : "Planetary Physiology & Antidotes"}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("circles")}
          className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "circles"
              ? "bg-[#1A365D] text-white shadow-xs font-bold"
              : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>{language === "ta" ? "3 வட்டப் பிணைப்புகள் (Reflex Circles)" : "The 3 Vicious Circles"}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("nails")}
          className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "nails"
              ? "bg-[#1A365D] text-white shadow-xs font-bold"
              : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>{language === "ta" ? "கை & நக நோய்நிர்ணயம்" : "Hand & Nail Astro-Diagnosis"}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("aphorisms")}
          className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "aphorisms"
              ? "bg-[#1A365D] text-white shadow-xs font-bold"
              : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
          }`}
        >
          <Award className="w-3.5 h-3.5" />
          <span>{language === "ta" ? "43 பொன்மொழிகள் & அறுவைசிகிச்சை" : "43 Aphorisms & Surgery"}</span>
        </button>
      </div>

      {/* =================================================================== */}
      {/* TAB 1: CORE PHILOSOPHY & THE 19 INJUNCTIONS FOR THE HEALER          */}
      {/* =================================================================== */}
      {activeTab === "philosophy" && (
        <div className="space-y-6">
          {/* Spiritual Etiology Card */}
          <div className="p-5 rounded-xl border border-blue-200 bg-blue-50/50 space-y-3">
            <div className="flex items-center gap-2 text-blue-900 font-bold text-sm">
              <HeartPulse className="w-4 h-4 text-blue-700" />
              <span>{language === "ta" ? "நோய்க்கான ஆன்மீக மூலக் காரணம்" : "Spiritual Etiology & The Law of Cause and Effect"}</span>
            </div>
            <p className="text-xs text-blue-950 leading-relaxed font-serif">
              "{language === "ta" ? core_philosophy_ta : core_philosophy_en}"
            </p>
            <div className="text-2xs text-blue-800 italic">
              — {authors}, {book_title}
            </div>
          </div>

          {/* Active Chart Rules Alert if any */}
          {activeMatchedRules.length > 0 && (
            <div className="rounded-xl border border-amber-300 bg-amber-50/80 p-4 space-y-3">
              <div className="flex items-center gap-2 text-amber-900 font-bold text-xs uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4 text-amber-700" />
                <span>
                  {language === "ta"
                    ? `இந்த ஜாதகத்தில் பொருந்தும் மேக்ஸ் ஹெயிண்டல் நோய்நிர்ணய விதிகள் (${activeMatchedRules.length})`
                    : `Active Max Heindel Diagnostic Rules for This Chart (${activeMatchedRules.length})`}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {activeMatchedRules.map((rule) => (
                  <div
                    key={rule.id}
                    onClick={() => onSelectRule && onSelectRule(rule)}
                    className="p-3 bg-white rounded-lg border border-amber-200 hover:border-amber-400 cursor-pointer transition-all space-y-1.5 shadow-2xs"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-[#183047]">
                        {language === "ta" ? rule.name_tamil : rule.name}
                      </span>
                      <span className="text-2xs font-mono bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded">
                        Active
                      </span>
                    </div>
                    <p className="text-2xs text-[#52667E] line-clamp-2">
                      {language === "ta" ? rule.interpretation_tamil : rule.traditional_interpretation}
                    </p>
                    {rule.remedy_en && (
                      <div className="text-2xs text-emerald-800 font-medium">
                        ✦ {language === "ta" ? rule.remedy_ta : rule.remedy_en}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 19 Golden Injunctions for the Healer */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-sm font-bold text-[#183047] flex items-center gap-2">
                <Award className="w-4 h-4 text-amber-600" />
                <span>
                  {language === "ta"
                    ? "குணப்படுத்துபவருக்கான 19 பொன்விதிகள் (Hints & Helps for the Healer)"
                    : "The 19 Golden Injunctions for the Healer (Chapter VIII)"}
                </span>
              </h3>
              <span className="text-2xs text-[#8190A6]">Max Heindel, Chapter VIII</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {healer_injunctions.map((inj) => (
                <div
                  key={inj.id}
                  className="p-3.5 rounded-xl border border-[#D9DEE7] bg-white hover:border-[#1A365D]/30 transition-all space-y-1.5 shadow-2xs"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-900 text-xs font-bold flex items-center justify-center shrink-0">
                      {inj.id}
                    </span>
                    <span className="text-xs font-bold text-[#183047]">
                      {language === "ta" ? `விதி #${inj.id}` : `Injunction #${inj.id}`}
                    </span>
                  </div>
                  <p className="text-xs text-[#334E68] leading-relaxed">
                    {language === "ta" ? inj.rule_ta : inj.rule_en}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* TAB 2: 12 ZODIAC SIGNS & MARCUS MANILIUS HEAD-TO-TOE ANATOMY        */}
      {/* =================================================================== */}
      {activeTab === "anatomy" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-3 rounded-xl border border-[#D9DEE7]">
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Search className="w-4 h-4 text-[#8190A6]" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={
                  language === "ta"
                    ? "ராசி, உறுப்பு அல்லது நோயைத் தேடுக..."
                    : "Search sign, organ, or affliction..."
                }
                className="text-xs text-[#183047] placeholder-[#8190A6] focus:outline-hidden w-full sm:w-64"
              />
            </div>
            <div className="text-2xs text-[#52667E]">
              {language === "ta"
                ? "மார்கஸ் மனிலியஸ் (கி.பி. 1-ம் நூற்றாண்டு) 'அஸ்ட்ரோனாமிகா' பாடல் நெறி"
                : "Marcus Manilius (1st c. AD) 'Astronomica' Head-to-Toe Codification"}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredSigns.map((sign) => {
              const isAsc = sign.is_native_ascendant;
              const isSun = sign.is_native_sun_sign;
              const isMoon = sign.is_native_moon_sign;
              return (
                <div
                  key={sign.sign_index}
                  className={`p-4 rounded-xl border transition-all space-y-3 shadow-2xs ${
                    isAsc
                      ? "border-blue-500 bg-blue-50/40 ring-2 ring-blue-400/40"
                      : isSun
                      ? "border-amber-400 bg-amber-50/40"
                      : "border-[#D9DEE7] bg-white hover:border-[#1A365D]/40"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-md bg-[#1A365D] text-white text-xs font-bold flex items-center justify-center">
                        {sign.sign_index}
                      </span>
                      <div>
                        <h4 className="font-bold text-sm text-[#183047]">
                          {language === "ta" ? sign.sign_name_ta : sign.sign_name_en}
                        </h4>
                        <span className="text-2xs text-[#8190A6]">
                          {sign.manilius_rulership}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      {isAsc && (
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-600 text-white">
                          Lagna
                        </span>
                      )}
                      {isSun && (
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-500 text-white">
                          Sun
                        </span>
                      )}
                      {isMoon && (
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-600 text-white">
                          Moon
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Anatomical Systems */}
                  <div className="space-y-1">
                    <span className="text-2xs font-bold uppercase tracking-wider text-[#52667E]">
                      {language === "ta" ? "ஆளும் உடல் உறுப்புகள்:" : "Ruled Organs & Structures:"}
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {sign.heindel_anatomical_systems.map((sys, idx) => (
                        <span
                          key={idx}
                          className="text-2xs bg-slate-100 text-[#334E68] px-2 py-0.5 rounded-md"
                        >
                          {sys}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Physiological Afflictions */}
                  <div className="space-y-1">
                    <span className="text-2xs font-bold uppercase tracking-wider text-rose-700">
                      {language === "ta" ? "இயற்கை நோய் வாய்ப்புகள்:" : "Pathological Afflictions:"}
                    </span>
                    <p className="text-2xs text-[#52667E] leading-relaxed">
                      {sign.physiological_afflictions.join(", ")}
                    </p>
                  </div>

                  {/* Temperament and Healing */}
                  <div className="pt-2 border-t border-slate-100 text-2xs text-[#334E68] italic leading-relaxed">
                    {sign.temperament_and_healing_reaction}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* TAB 3: PLANETARY PHYSIOLOGY & ROSICRUCIAN ANTIDOTES                 */}
      {/* =================================================================== */}
      {activeTab === "planets" && (
        <div className="space-y-6">
          {/* Antidote Polarity Highlight */}
          <div className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-4 space-y-3">
            <div className="flex items-center gap-2 text-indigo-950 font-bold text-sm">
              <Sparkles className="w-4 h-4 text-indigo-700" />
              <span>{language === "ta" ? "ரோசிக்ரூசியன் பிராண மாற்று மருந்துகள் (The Law of Antidotes)" : "The Rosicrucian Law of Planetary Antidotes"}</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {planetary_antidotes.map((ant, idx) => (
                <div key={idx} className="p-3 bg-white rounded-lg border border-indigo-100 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-rose-700">{ant.afflicting_planet}</span>
                    <span className="text-indigo-600 font-bold">⇌</span>
                    <span className="font-bold text-emerald-700">{ant.antidote_planet}</span>
                  </div>
                  <div className="text-2xs text-[#52667E] space-y-1">
                    <div>
                      <strong>Metal Antidote:</strong> {ant.antidote_metal} balances {ant.afflicting_metal}
                    </div>
                    <div>
                      <strong>Color & Gem:</strong> {ant.antidote_color} • {ant.antidote_gem}
                    </div>
                  </div>
                  <p className="text-2xs text-[#334E68] leading-relaxed border-t border-slate-100 pt-1.5">
                    {ant.polarity_law}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Sense Organs Matrix */}
          <div className="space-y-2">
            <h3 className="font-serif text-sm font-bold text-[#183047] flex items-center gap-2">
              <Eye className="w-4 h-4 text-blue-700" />
              <span>{language === "ta" ? "புலன் உறுப்புகளின் ஜோதிட ஆதிக்கம்" : "Astrological Affinities of the Sense Organs"}</span>
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {sense_organs_affinities.map((so, idx) => (
                <div key={idx} className="p-3 rounded-xl border border-[#D9DEE7] bg-white space-y-1.5 shadow-2xs">
                  <div className="font-bold text-xs text-[#183047]">
                    {language === "ta" ? so.organ_ta : so.organ_en}
                  </div>
                  <div className="text-2xs text-indigo-700 font-medium">
                    {so.astrological_rulers}
                  </div>
                  <p className="text-2xs text-[#52667E] leading-relaxed">
                    {language === "ta" ? so.pathological_notes_ta : so.pathological_notes_en}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Planetary Physiology Table */}
          <div className="space-y-3">
            <h3 className="font-serif text-sm font-bold text-[#183047] flex items-center gap-2">
              <Sun className="w-4 h-4 text-amber-600" />
              <span>{language === "ta" ? "கிரகங்களின் உடலியல் மற்றும் நோயியல் தன்மைகள்" : "Anatomy and Physiology Correlated to the Planets"}</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {planets_physiology.map((p) => (
                <div key={p.planet} className="p-3.5 rounded-xl border border-[#D9DEE7] bg-white space-y-2 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-[#183047]">
                        {language === "ta" ? p.planet_ta : p.planet}
                      </span>
                      <span className="text-2xs bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-medium">
                        {p.salient_keyword}
                      </span>
                    </div>
                    <span className="text-2xs font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                      {p.chart_status}
                    </span>
                  </div>

                  <div className="space-y-1 text-xs">
                    <div className="text-2xs font-semibold text-[#52667E]">
                      {language === "ta" ? "ஆளும் உடல் உறுப்புகள் & திரவங்கள்:" : "Anatomical Organs & Systems:"}
                    </div>
                    <p className="text-xs text-[#183047] leading-relaxed font-medium">
                      {p.anatomical_rulership}
                    </p>
                  </div>

                  <div className="text-2xs text-[#52667E] border-t border-slate-100 pt-1.5 space-y-1">
                    <div>
                      <strong className="text-slate-700">Qualities:</strong> {p.pathological_quality}
                    </div>
                    <div>
                      <strong className="text-emerald-700">Healthy Expression:</strong> {p.positive_expression}
                    </div>
                    <div>
                      <strong className="text-rose-700">Afflicted Expression:</strong> {p.afflicted_expression}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* TAB 4: THE THREE VICIOUS CIRCLES (CARDINAL, FIXED, MUTABLE)         */}
      {/* =================================================================== */}
      {activeTab === "circles" && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/60 space-y-2">
            <h3 className="font-bold text-xs text-amber-950 flex items-center gap-2 uppercase tracking-wider">
              <Layers className="w-4 h-4 text-amber-700" />
              <span>{language === "ta" ? "உடல் உறுப்புகளுக்கிடையேயான எதிரொலிப் பிணைப்பு (Reflex Action)" : "The Law of Sympathy, Antipathy & The 3 Vicious Circles"}</span>
            </h3>
            <p className="text-xs text-amber-900 leading-relaxed font-serif">
              "Doctors have for years noted the strange sympathy between distant organs. When they find a disease in one organ,
              the true cause is frequently situated in an organ situated in direct sympathetic reflex with the first.
              In glaucoma or eye trouble, the true seat is frequently in the stomach or kidneys. In throat trouble or goiter,
              a weakened heart is often the true cause." (Max Heindel, Chapter III)
            </p>
          </div>

          <div className="space-y-4">
            {vicious_circles.map((vc, idx) => (
              <div
                key={idx}
                className={`p-5 rounded-xl border transition-all space-y-3 shadow-2xs ${
                  vc.is_native_cross_active
                    ? "border-blue-500 bg-blue-50/30 ring-1 ring-blue-400"
                    : "border-[#D9DEE7] bg-white"
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-2">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-md bg-[#1A365D] text-white text-xs font-bold flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <h4 className="font-bold text-base text-[#183047]">
                      {language === "ta" ? vc.cross_name_ta : vc.cross_name}
                    </h4>
                  </div>
                  {vc.is_native_cross_active && (
                    <span className="inline-flex items-center gap-1 text-2xs font-bold bg-blue-600 text-white px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="w-3 h-3" />
                      {language === "ta" ? "உங்கள் லக்ன வட்டப் பிணைப்பு" : "Native's Ascendant Cross"}
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {vc.signs_involved.map((sgn, sIdx) => (
                    <div key={sIdx} className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-center">
                      <div className="font-bold text-xs text-[#183047]">{sgn}</div>
                    </div>
                  ))}
                </div>

                <div className="space-y-1">
                  <span className="text-2xs font-bold uppercase tracking-wider text-[#52667E]">
                    {language === "ta" ? "உறுப்புகளின் சமச்சீர் பிணைப்பு:" : "Sympathetic Organ Axis:"}
                  </span>
                  <div className="text-xs font-semibold text-[#183047] bg-slate-50 p-2 rounded-lg border border-slate-100">
                    {vc.organ_sympathies}
                  </div>
                </div>

                <p className="text-xs text-[#334E68] leading-relaxed">
                  {vc.clinical_mechanism}
                </p>

                <div className="space-y-1 bg-white p-3 rounded-lg border border-slate-200">
                  <span className="text-2xs font-bold text-slate-700 uppercase tracking-wider">
                    {language === "ta" ? "நடைமுறை மருத்துவ உதாரணங்கள்:" : "Clinical Textbook Examples:"}
                  </span>
                  <ul className="text-2xs text-[#52667E] space-y-1 list-disc list-inside">
                    {vc.clinical_examples.map((ex, eIdx) => (
                      <li key={eIdx}>{ex}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* TAB 5: HAND & NAIL ASTRO-DIAGNOSIS (CHAPTER X)                      */}
      {/* =================================================================== */}
      {activeTab === "nails" && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl border border-purple-200 bg-purple-50/50 space-y-2">
            <h3 className="font-bold text-xs text-purple-950 flex items-center gap-2 uppercase tracking-wider">
              <Activity className="w-4 h-4 text-purple-700" />
              <span>{language === "ta" ? "கைரேகை மற்றும் நக அமைப்பியல் நோய்நிர்ணயம்" : "Diagnosing from the Hands and Finger Nails (Chapter X)"}</span>
            </h3>
            <p className="text-xs text-purple-900 leading-relaxed font-serif">
              "The astrologer is frequently at disadvantage when birth hours are unverified. By examining the 12 types of
              finger nails and hand proportions, the physician gains an infallible physical verification of latent
              constitutional ailments, heart and liver markers, and patient willpower."
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {nail_and_hand_diagnosis.map((nail, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-[#D9DEE7] bg-white space-y-3 shadow-2xs hover:border-purple-300 transition-all"
              >
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <h4 className="font-bold text-sm text-[#183047]">
                    {language === "ta" ? nail.nail_type_ta : nail.nail_type_en}
                  </h4>
                  <span className="text-2xs font-mono text-purple-700 bg-purple-100 px-2 py-0.5 rounded">
                    Diagram #{idx + 1}
                  </span>
                </div>

                <div className="space-y-1 text-xs">
                  <span className="text-2xs font-bold uppercase tracking-wider text-[#52667E]">
                    {language === "ta" ? "உடல் புற அறிகுறிகள்:" : "Physical Indicators:"}
                  </span>
                  <p className="text-xs text-[#334E68] leading-relaxed">
                    {nail.physical_indicators}
                  </p>
                </div>

                <div className="space-y-1 text-xs">
                  <span className="text-2xs font-bold uppercase tracking-wider text-rose-700">
                    {language === "ta" ? "நோயியல் உட்பொருள்:" : "Pathological Significance:"}
                  </span>
                  <p className="text-xs text-[#52667E] leading-relaxed">
                    {nail.pathological_significance}
                  </p>
                </div>

                <div className="space-y-1 text-2xs text-slate-600 border-t border-slate-100 pt-2">
                  <div>
                    <strong>Astrological Correlation:</strong> {nail.constitutional_correlation}
                  </div>
                  <div className="text-emerald-800">
                    <strong>Hygienic Guidance:</strong> {nail.remedial_and_hygiene_guidance}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* TAB 6: 43 GOLDEN APHORISMS & SURGICAL TIMING (CHAPTER IX)           */}
      {/* =================================================================== */}
      {activeTab === "aphorisms" && (
        <div className="space-y-5">
          {/* Nebular Spots Highlight */}
          <div className="p-4 rounded-xl border border-rose-200 bg-rose-50/50 space-y-2">
            <h3 className="font-bold text-xs text-rose-950 flex items-center gap-2 uppercase tracking-wider">
              <Eye className="w-4 h-4 text-rose-700" />
              <span>{language === "ta" ? "பார்வைக்குரிய மூன்று முக்கிய நெபுலா புள்ளிகள் (Aphorism 20, 33)" : "The Three Critical Nebular Spots Affecting Eyesight"}</span>
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
              {nebular_spots.map((ns, idx) => (
                <div key={idx} className="p-3 bg-white rounded-lg border border-rose-100 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-[#183047]">{ns.name}</span>
                    <span className="text-2xs font-mono bg-rose-100 text-rose-900 px-1.5 py-0.5 rounded">
                      {ns.zodiac_degree}
                    </span>
                  </div>
                  <p className="text-2xs text-[#52667E]">{ns.pathological_focus}</p>
                  <p className="text-2xs text-emerald-800 italic">{ns.esoteric_mitigation}</p>
                  {ns.native_chart_proximity && (
                    <div className="text-2xs font-bold text-rose-600 pt-1">
                      ✦ {ns.chart_details}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Ptolemy's Rule Banner */}
          <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50 flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-200 text-blue-900 flex items-center justify-center shrink-0">
              <Clock className="w-4 h-4" />
            </div>
            <div className="space-y-1 text-xs text-blue-950">
              <span className="font-bold uppercase tracking-wider text-2xs text-blue-800">
                {language === "ta" ? "தாலமியின் அறுவைசிகிச்சை பொன்விதி (Aphorism 6)" : "Ptolemy's Golden Surgical Rule (Aphorism 6)"}
              </span>
              <p className="leading-relaxed font-serif">
                "{language === "ta"
                  ? "சந்திரன் நிற்கும் ராசிக்குரிய உடல் உறுப்பை ஒருபோதும் இரும்பால் துளைக்காதே / அறுவை சிகிச்சை செய்யாதே."
                  : "Pierce not with iron that part of the body which may be governed by the sign actually occupied by the Moon."}
                "
              </p>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-3 rounded-xl border border-[#D9DEE7]">
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Search className="w-4 h-4 text-[#8190A6]" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={
                  language === "ta" ? "பொன்மொழிகளைத் தேடுக..." : "Search 43 aphorisms..."
                }
                className="text-xs text-[#183047] placeholder-[#8190A6] focus:outline-hidden w-full sm:w-64"
              />
            </div>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Filter className="w-3.5 h-3.5 text-[#8190A6]" />
              <select
                value={aphorismCategory}
                onChange={(e) => setAphorismCategory(e.target.value)}
                className="text-xs text-[#183047] border border-[#D9DEE7] rounded-lg px-2 py-1 bg-white focus:outline-hidden"
              >
                <option value="all">{language === "ta" ? "அனைத்து பிரிவுகள்" : "All Categories"}</option>
                <option value="Lunar Cycles">Lunar Cycles</option>
                <option value="Surgical Precaution">Surgical Precaution</option>
                <option value="Natal Constitution">Natal Constitution</option>
                <option value="Therapeutic Dosage">Therapeutic Dosage</option>
                <option value="Fixed Stars">Fixed Stars</option>
              </select>
            </div>
          </div>

          {/* Aphorisms List */}
          <div className="space-y-3">
            {filteredAphorisms.map((a) => (
              <div
                key={a.number}
                className="p-3.5 rounded-xl border border-[#D9DEE7] bg-white hover:border-[#1A365D]/40 transition-all space-y-1.5 shadow-2xs"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-md bg-[#1A365D] text-white text-xs font-bold flex items-center justify-center">
                      {a.number}
                    </span>
                    <span className="text-2xs font-mono uppercase bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                      {a.category}
                    </span>
                  </div>
                </div>

                <p className="text-xs font-semibold text-[#183047] leading-relaxed">
                  {language === "ta" ? a.aphorism_ta : a.aphorism_en}
                </p>

                {language === "ta" && (
                  <p className="text-2xs text-[#8190A6] italic leading-relaxed">
                    {a.aphorism_en}
                  </p>
                )}

                <div className="text-2xs text-emerald-800 font-medium border-t border-slate-100 pt-1">
                  ✦ {a.practical_implication}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
