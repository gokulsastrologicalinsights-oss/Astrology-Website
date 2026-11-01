"use client";

import React, { useState, useMemo } from "react";
import {
  DrKrishnaKumarCompendium,
  NakshatraMedicalDetail,
  GestationalMonthDetail,
  ProgenyShapaDetail,
  TatwaNavadwaraDetail,
  ClinicalCaseStudy,
  MedicalRule,
} from "@/lib/types";
import {
  Stethoscope,
  BookOpen,
  Baby,
  Sparkles,
  Layers,
  FileText,
  Search,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  HeartPulse,
  Compass,
  ShieldCheck,
  Calendar,
  Brain,
  Activity,
  Flame,
} from "lucide-react";

interface DrKrishnaKumarSectionProps {
  compendium: DrKrishnaKumarCompendium;
  language: "en" | "ta";
  onSelectRule?: (rule: MedicalRule) => void;
}

export function DrKrishnaKumarSection({
  compendium,
  language,
  onSelectRule,
}: DrKrishnaKumarSectionProps) {
  const [activeTab, setActiveTab] = useState<
    "native" | "curses" | "pregnancy" | "nakshatras" | "tatwas" | "cases"
  >("native");

  const [starSearch, setStarSearch] = useState<string>("");
  const [expandedCase, setExpandedCase] = useState<string | null>(null);
  const [expandedCurse, setExpandedCurse] = useState<string | null>(null);

  const {
    book_title,
    book_title_ta,
    author,
    publisher,
    salient_features,
    native_moon_star,
    native_lagna_star,
    all_27_nakshatras = [],
    gestational_months = [],
    progeny_shapas = [],
    case_studies = [],
    tatwas_and_senses = [],
    manasika_buddhi_yogas = [],
    organ_specific_yogas = [],
    caesarean_vs_normal_delivery_observation,
    sperm_potency_observation,
  } = compendium;

  // Active progeny curses
  const activeCurses = useMemo(() => {
    return (progeny_shapas || []).filter((s: ProgenyShapaDetail) => s.is_indicated);
  }, [progeny_shapas]);

  // Combined evaluated rules
  const allTriggeredRules = useMemo(() => {
    return [...(manasika_buddhi_yogas || []), ...(organ_specific_yogas || [])];
  }, [manasika_buddhi_yogas, organ_specific_yogas]);

  // Filtered stars
  const filteredStars = useMemo(() => {
    if (!starSearch.trim()) return all_27_nakshatras || [];
    const q = starSearch.toLowerCase();
    return (all_27_nakshatras || []).filter(
      (s: NakshatraMedicalDetail) =>
        s.name.toLowerCase().includes(q) ||
        s.name_ta.toLowerCase().includes(q) ||
        s.devata.toLowerCase().includes(q) ||
        s.body_part_en.toLowerCase().includes(q) ||
        s.body_part_ta.toLowerCase().includes(q) ||
        s.disease_tendency_en.toLowerCase().includes(q) ||
        s.disease_tendency_ta.toLowerCase().includes(q)
    );
  }, [all_27_nakshatras, starSearch]);

  return (
    <div className="space-y-6">
      {/* 1. Treatise Header Banner */}
      <div className="rounded-xl border border-purple-300 bg-gradient-to-br from-purple-50 via-white to-pink-50 p-5 shadow-2xs">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-2 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-[#69235B] text-white">
                <Stethoscope className="w-3.5 h-3.5" />
                {language === "ta" ? "மருத்துவ ஜோதிட நூல் தொகுதி" : "Medical Astrology Treatise"}
              </span>
              <span className="text-[11px] font-mono text-[#69235B] bg-purple-100 px-2 py-0.5 rounded border border-purple-200">
                Dr. S. Krishna Kumar, ICAS Bangalore
              </span>
            </div>
            <h2 className="font-serif text-lg sm:text-xl font-bold text-[#183047]">
              {language === "ta" ? book_title_ta : book_title}
            </h2>
            <p className="text-xs text-[#52667E] leading-relaxed max-w-3xl">
              {language === "ta"
                ? "டாக்டர் எஸ். கிருஷ்ண குமார் அவர்களின் புகழ்பெற்ற ஆய்வு நூல்: ஜாதகமா அல்லது ஸ்டெதாஸ்கோப்பா? - நோய்கள் கண்டறிதல், புத்திர தோஷங்கள் மற்றும் அவற்றின் பரிகாரங்கள் (பராசர ஹோரா சாஸ்திர நெறிகள், பிரசவ தத்துவங்கள், 27 நட்சத்திர நோய்க் கூறுகள்)."
                : "A seminal classical compendium by Dr. S. Krishna Kumar synthesizing Parashari principles, Ayurvedic Tridosha humours, 27 Nakshatras pathology, the 10 gestational months of embryology, and the 9 progeny curses with remedial measures."}
            </p>
          </div>
          <div className="p-3 rounded-lg border border-purple-200 bg-white/80 shrink-0 text-right space-y-1 hidden sm:block">
            <span className="text-[10px] uppercase font-bold text-[#69235B] block">
              {language === "ta" ? "ஆசிரியர் & பதிப்பகம்" : "Author & Publisher"}
            </span>
            <p className="text-xs font-semibold text-[#183047]">{author}</p>
            <p className="text-[10px] text-[#8190A6]">{publisher}</p>
          </div>
        </div>
      </div>

      {/* 2. Sub-Navigation Tabs */}
      <div className="bg-white rounded-xl border border-[#D9DEE7] p-2 shadow-2xs">
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs font-semibold pb-1 sm:pb-0">
          <button
            type="button"
            onClick={() => setActiveTab("native")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === "native"
                ? "bg-[#69235B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "ஜாதகரின் மருத்துவ விவரம்" : "Native's Health Profile"}</span>
            {allTriggeredRules.length > 0 && (
              <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-white/20 text-white font-mono">
                {allTriggeredRules.length}
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("curses")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === "curses"
                ? "bg-[#69235B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <Baby className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "புத்திர தோஷங்கள் & 9 சாபங்கள்" : "Progeny & 9 Curses"}</span>
            {activeCurses.length > 0 && (
              <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-rose-500 text-white font-mono">
                {activeCurses.length}
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("pregnancy")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === "pregnancy"
                ? "bg-[#69235B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "கர்ப்ப கால 10 மாதங்கள்" : "10 Gestational Months"}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("nakshatras")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === "nakshatras"
                ? "bg-[#69235B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "27 நட்சத்திர அட்டவணை" : "27 Nakshatras Matrix"}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("tatwas")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === "tatwas"
                ? "bg-[#69235B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "தத்துவங்கள் & நவதுவாரங்கள்" : "Tatwas & Navadwaras"}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("cases")}
            className={`px-3.5 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === "cases"
                ? "bg-[#69235B] text-white shadow-2xs font-bold"
                : "text-[#52667E] hover:text-[#183047] hover:bg-[#F8FAFC]"
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "12 மருத்துவ ஆய்வு வழக்குகள்" : "12 Case Histories"}</span>
            <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-purple-100 text-[#69235B] font-mono">
              {case_studies.length}
            </span>
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* TAB 1: NATIVE'S HEALTH PROFILE & EVALUATED YOGAS */}
      {/* ------------------------------------------------------------------ */}
      {activeTab === "native" && (
        <div className="space-y-6">
          {/* Star Analysis Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Janma Nakshatra Card */}
            {native_moon_star && (
              <div className="p-4 sm:p-5 rounded-xl border border-purple-200 bg-white space-y-3 shadow-2xs">
                <div className="flex items-center justify-between border-b border-purple-100 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="w-7 h-7 rounded-full bg-purple-100 text-[#69235B] flex items-center justify-center font-bold text-xs">
                      {native_moon_star.number}
                    </span>
                    <div>
                      <span className="text-[10px] uppercase font-bold text-[#8190A6] block">
                        {language === "ta" ? "ஜென்ம நட்சத்திரம் (சந்திரன்)" : "Janma Nakshatra (Moon)"}
                      </span>
                      <h4 className="font-serif text-base font-bold text-[#183047]">
                        {language === "ta" ? native_moon_star.name_ta : native_moon_star.name}
                      </h4>
                    </div>
                  </div>
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-purple-50 text-[#69235B] border border-purple-200">
                    {language === "ta" ? `அதிதேவதை: ${native_moon_star.devata}` : `Deity: ${native_moon_star.devata}`}
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-[#8190A6] font-semibold block">
                      {language === "ta" ? "ஆளப்படும் உடல் உறுப்புகள்:" : "Anatomical Organs Ruled:"}
                    </span>
                    <p className="text-[#183047] font-medium">
                      {language === "ta" ? native_moon_star.body_part_ta : native_moon_star.body_part_en}
                    </p>
                  </div>

                  <div>
                    <span className="text-[#8190A6] font-semibold block">
                      {language === "ta" ? "சாத்தியமான உடல்நலக் கூறுகள் (நூல் குறிப்பு):" : "Classical Susceptibility (Treatise):"}
                    </span>
                    <p className="text-rose-900 font-medium">
                      {language === "ta" ? native_moon_star.disease_tendency_ta : native_moon_star.disease_tendency_en}
                    </p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-emerald-50/80 border border-emerald-200 text-emerald-950 text-[11px] space-y-0.5">
                    <span className="font-bold flex items-center gap-1 text-emerald-800">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      {language === "ta" ? "வேத சாந்தி & பரிகாரம்:" : "Vedic Propitiation & Pariharam:"}
                    </span>
                    <p className="leading-relaxed">
                      {language === "ta" ? native_moon_star.propitiation_ta : native_moon_star.propitiation_en}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Lagna Nakshatra Card */}
            {native_lagna_star && (
              <div className="p-4 sm:p-5 rounded-xl border border-indigo-200 bg-white space-y-3 shadow-2xs">
                <div className="flex items-center justify-between border-b border-indigo-100 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="w-7 h-7 rounded-full bg-indigo-100 text-indigo-800 flex items-center justify-center font-bold text-xs">
                      {native_lagna_star.number}
                    </span>
                    <div>
                      <span className="text-[10px] uppercase font-bold text-[#8190A6] block">
                        {language === "ta" ? "லக்ன நட்சத்திரம் (உடலமைப்பு)" : "Lagna Nakshatra (Constitution)"}
                      </span>
                      <h4 className="font-serif text-base font-bold text-[#183047]">
                        {language === "ta" ? native_lagna_star.name_ta : native_lagna_star.name}
                      </h4>
                    </div>
                  </div>
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-800 border border-indigo-200">
                    {language === "ta" ? `அதிதேவதை: ${native_lagna_star.devata}` : `Deity: ${native_lagna_star.devata}`}
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-[#8190A6] font-semibold block">
                      {language === "ta" ? "ஆளப்படும் உடல் உறுப்புகள்:" : "Anatomical Organs Ruled:"}
                    </span>
                    <p className="text-[#183047] font-medium">
                      {language === "ta" ? native_lagna_star.body_part_ta : native_lagna_star.body_part_en}
                    </p>
                  </div>

                  <div>
                    <span className="text-[#8190A6] font-semibold block">
                      {language === "ta" ? "சாத்தியமான உடல்நலக் கூறுகள்:" : "Classical Susceptibility (Treatise):"}
                    </span>
                    <p className="text-indigo-950 font-medium">
                      {language === "ta" ? native_lagna_star.disease_tendency_ta : native_lagna_star.disease_tendency_en}
                    </p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-emerald-50/80 border border-emerald-200 text-emerald-950 text-[11px] space-y-0.5">
                    <span className="font-bold flex items-center gap-1 text-emerald-800">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      {language === "ta" ? "வேத சாந்தி & பரிகாரம்:" : "Vedic Propitiation & Pariharam:"}
                    </span>
                    <p className="leading-relaxed">
                      {language === "ta" ? native_lagna_star.propitiation_ta : native_lagna_star.propitiation_en}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Triggered Yogas in this Chart */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-base font-bold text-[#183047] flex items-center gap-2">
                <Brain className="w-4 h-4 text-[#69235B]" />
                <span>
                  {language === "ta"
                    ? "டாக்டர் எஸ். கிருஷ்ண குமார் நூல் வழி தூண்டப்பட்ட யோகங்கள்"
                    : "Evaluated Medical & Intellectual Yogas (Treatise)"}
                </span>
              </h3>
              <span className="text-xs text-[#8190A6]">
                {allTriggeredRules.length}{" "}
                {language === "ta" ? "யோகங்கள் பொருந்துகின்றன" : "Rules Active"}
              </span>
            </div>

            {allTriggeredRules.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {allTriggeredRules.map((rule: MedicalRule) => {
                  const isIntellectual =
                    rule.category === "vitality" ||
                    rule.name.toLowerCase().includes("buddhi") ||
                    rule.name.toLowerCase().includes("gnana");
                  return (
                    <div
                      key={rule.id}
                      onClick={() => onSelectRule && onSelectRule(rule)}
                      className={`p-4 rounded-xl border transition-all cursor-pointer hover:shadow-xs space-y-2 ${
                        isIntellectual
                          ? "border-emerald-200 bg-emerald-50/40 hover:bg-emerald-50/70"
                          : "border-purple-200 bg-white hover:bg-purple-50/30"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <span
                            className={`text-[10px] font-bold uppercase tracking-wider block ${
                              isIntellectual ? "text-emerald-700" : "text-[#69235B]"
                            }`}
                          >
                            {rule.category.toUpperCase()} • {rule.anatomical_system}
                          </span>
                          <h4 className="font-serif text-sm font-bold text-[#183047]">
                            {language === "ta" ? rule.name_tamil : rule.name}
                          </h4>
                        </div>
                        <span className="text-[10px] font-mono text-[#8190A6] bg-slate-100 px-2 py-0.5 rounded shrink-0">
                          {rule.chapter_verse}
                        </span>
                      </div>

                      <p className="text-xs text-[#52667E] leading-relaxed line-clamp-3">
                        {language === "ta" ? rule.interpretation_tamil : rule.traditional_interpretation}
                      </p>

                      <div className="pt-1 flex items-center justify-between text-[11px]">
                        <span className="text-[#8190A6]">
                          {rule.triggered_positions.join("; ")}
                        </span>
                        <span className="font-semibold text-[#153F6B] flex items-center gap-0.5">
                          {language === "ta" ? "விவரம்" : "Details"} →
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-6 rounded-xl border border-emerald-200 bg-emerald-50/50 text-center space-y-2">
                <CheckCircle2 className="w-6 h-6 text-emerald-600 mx-auto" />
                <h4 className="font-bold text-sm text-emerald-950">
                  {language === "ta"
                    ? "தீவிர நோய்க் குறி யோகங்கள் எதுவும் தூண்டப்படவில்லை"
                    : "No Severe Afflictive Yogas Triggered"}
                </h4>
                <p className="text-xs text-emerald-800 max-w-md mx-auto">
                  {language === "ta"
                    ? "ஜாதகத்தில் தலையாய நோய்களைக் குறிக்கும் விசேஷ யோக அமைப்புகள் (சிரோ வியாதி, கண் பார்வை பாதிப்பு, இருதய கோளாறு போன்றவை) இந்த அட்டவணையில் காணப்படவில்லை."
                    : "No acute afflictive yogas (such as Shiro Vyadhi, acute Nethra Roga, or Hridaya Roga) from Dr. Krishna Kumar's compendium are triggered in this chart."}
                </p>
              </div>
            )}
          </div>

          {/* Special Treatise Observations (Normal delivery vs caesarean & potency) */}
          {(caesarean_vs_normal_delivery_observation || sperm_potency_observation) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {caesarean_vs_normal_delivery_observation && (
                <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/40 space-y-1.5 text-xs">
                  <span className="font-bold text-blue-900 block flex items-center gap-1.5">
                    <HeartPulse className="w-4 h-4 text-blue-700" />
                    {language === "ta" ? "பிரசவ முறை சாஸ்திர ஆய்வு:" : "Delivery Dynamics Observation:"}
                  </span>
                  <p className="text-[#183047] leading-relaxed">
                    {caesarean_vs_normal_delivery_observation}
                  </p>
                </div>
              )}
              {sperm_potency_observation && (
                <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/40 space-y-1.5 text-xs">
                  <span className="font-bold text-amber-900 block flex items-center gap-1.5">
                    <Baby className="w-4 h-4 text-amber-700" />
                    {language === "ta" ? "புத்திர உற்பத்தி காரக நிலை:" : "Fecundity & Progeny Capacity Observation:"}
                  </span>
                  <p className="text-[#183047] leading-relaxed">
                    {sperm_potency_observation}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Active Progeny Curses in this Chart */}
          {activeCurses.length > 0 && (
            <div className="p-4 sm:p-5 rounded-xl border border-rose-300 bg-rose-50/60 space-y-3">
              <div className="flex items-center gap-2 text-rose-900 font-bold text-sm">
                <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
                <span>
                  {language === "ta"
                    ? "ஜாதகத்தில் காணப்படும் புத்திர தோஷ சாபங்கள் (கவனிக்கத்தக்கவை)"
                    : "Classical Progeny Curses Indicated in this Chart"}
                </span>
              </div>
              <p className="text-xs text-rose-800 leading-relaxed">
                {language === "ta"
                  ? "பராசர ஹோரா மற்றும் கிருஷ்ண குமார் விதிகளின்படி இந்த ஜாதகத்தில் பின்வரும் சாபக் கூறுகள் சுட்டிக்காட்டப்பட்டுள்ளன. இதற்கான சாஸ்திர பரிகாரங்களை மேற்கொள்வது நற்பலனைத் தரும்."
                  : "According to Parashara Hora & Dr. Krishna Kumar's compendium, the following progeny curses have planetary indications. Classical remedial shantis are prescribed below:"}
              </p>
              <div className="space-y-2.5">
                {activeCurses.map((c: ProgenyShapaDetail) => (
                  <div key={c.id} className="p-3.5 rounded-lg border border-rose-200 bg-white space-y-1.5">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-xs text-rose-950">
                        {language === "ta" ? c.shapa_name_ta : c.shapa_name}
                      </span>
                      <span className="text-[10px] font-mono text-rose-800 bg-rose-100 px-2 py-0.5 rounded">
                        {c.afflicted_karaka}
                      </span>
                    </div>
                    <p className="text-xs text-[#52667E]">
                      <strong>{language === "ta" ? "சாபக் காரணம்:" : "Karmic Cause:"}</strong>{" "}
                      {language === "ta" ? c.cause_ta : c.cause_en}
                    </p>
                    {c.chart_observation && (
                      <p className="text-xs text-rose-900">
                        <strong>{language === "ta" ? "ஜாதகக் குறிப்பு:" : "Chart Indication:"}</strong>{" "}
                        {c.chart_observation}
                      </p>
                    )}
                    <div className="text-xs text-emerald-900 bg-emerald-50 p-2 rounded border border-emerald-200">
                      <strong>{language === "ta" ? "பரிகார சாந்தி:" : "Prescribed Remedy:"}</strong>{" "}
                      {language === "ta" ? c.remedy_ta : c.remedy_en}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* TAB 2: PROGENY & 9 CURSES */}
      {/* ------------------------------------------------------------------ */}
      {activeTab === "curses" && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl border border-purple-200 bg-purple-50/50 space-y-2">
            <h3 className="font-serif text-base font-bold text-[#183047] flex items-center gap-2">
              <Baby className="w-4 h-4 text-[#69235B]" />
              <span>
                {language === "ta"
                  ? "புத்திர தோஷம் மற்றும் 9 பூர்வ சாபங்கள் - தீர்வுகள்"
                  : "Progeny Obstacles & The 9 Classical Curses (Shapa) with Remedies"}
              </span>
            </h3>
            <p className="text-xs text-[#52667E] leading-relaxed">
              {language === "ta"
                ? "பிரகத் பராசர ஹோரா சாஸ்திரம் மற்றும் டாக்டர் எஸ். கிருஷ்ண குமார் அவர்களின் இரண்டாம் அத்தியாயத்தில் விவரிக்கப்பட்டுள்ளபடி, முற்பிறவி கர்ம வினைகளால் புத்திர பாக்கியத்தில் தடை ஏற்படும் 9 சாபங்களும் அவற்றுக்கான துல்லியமான வேத சாந்தி பரிகாரங்களும் கீழே கொடுக்கப்பட்டுள்ளன."
                : "As enunciated in Brihat Parasara Hora Sastra and Chapter 2 of Dr. S. Krishna Kumar's treatise, the 9 karmic curses hindering progeny and their precise classical remedies are presented below:"}
            </p>
          </div>

          <div className="space-y-3">
            {progeny_shapas.map((curse: ProgenyShapaDetail) => {
              const isExpanded = expandedCurse === curse.id;
              const isActive = curse.is_indicated;

              return (
                <div
                  key={curse.id}
                  className={`rounded-xl border transition-all ${
                    isActive
                      ? "border-rose-300 bg-rose-50/30"
                      : "border-[#D9DEE7] bg-white hover:border-purple-200"
                  }`}
                >
                  <div
                    onClick={() => setExpandedCurse(isExpanded ? null : curse.id)}
                    className="p-4 flex items-center justify-between gap-3 cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                          isActive
                            ? "bg-rose-500 text-white"
                            : "bg-purple-100 text-[#69235B]"
                        }`}
                      >
                        <Baby className="w-4 h-4" />
                      </span>
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4 className="font-serif text-sm font-bold text-[#183047]">
                            {language === "ta" ? curse.shapa_name_ta : curse.shapa_name}
                          </h4>
                          {isActive && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-300">
                              {language === "ta" ? "ஜாதகத்தில் பொருந்துகிறது" : "Active in Chart"}
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-[#8190A6]">
                          {language === "ta" ? "காரக கிரகம்: " : "Afflicted Karaka: "}
                          <span className="font-mono text-[#69235B] font-semibold">{curse.afflicted_karaka}</span>
                        </span>
                      </div>
                    </div>
                    <div className="text-[#8190A6]">
                      {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="px-4 pb-4 pt-1 border-t border-slate-100 space-y-3 text-xs">
                      <div>
                        <span className="text-[#8190A6] font-semibold block">
                          {language === "ta" ? "சாபக் காரணம் (பூர்வ ஜென்ம பாவம்):" : "Karmic Cause (Past-Life Transgression):"}
                        </span>
                        <p className="text-[#183047] leading-relaxed mt-0.5">
                          {language === "ta" ? curse.cause_ta : curse.cause_en}
                        </p>
                      </div>

                      <div>
                        <span className="text-[#8190A6] font-semibold block">
                          {language === "ta" ? "சாஸ்திர கிரக விதிகள் (காரண அமைப்புகள்):" : "Classical Planetary Combinations:"}
                        </span>
                        <ul className="list-disc pl-5 text-[#52667E] space-y-1 mt-1">
                          {curse.combinations.map((comb: string, cIdx: number) => (
                            <li key={`comb-${curse.id}-${cIdx}`}>{comb}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-950 space-y-1">
                        <span className="font-bold flex items-center gap-1.5 text-emerald-800">
                          <ShieldCheck className="w-4 h-4" />
                          {language === "ta" ? "சாஸ்திர வேத பரிகாரம் & சாந்தி:" : "Prescribed Vedic Remedy & Shanti:"}
                        </span>
                        <p className="leading-relaxed">
                          {language === "ta" ? curse.remedy_ta : curse.remedy_en}
                        </p>
                      </div>

                      {curse.chart_observation && (
                        <div className="p-2 rounded bg-rose-50 border border-rose-200 text-rose-900 text-[11px]">
                          <strong>{language === "ta" ? "இந்த ஜாதகத்தில் நிலை:" : "Observation in this Horoscope:"}</strong>{" "}
                          {curse.chart_observation}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* TAB 3: 10 GESTATIONAL MONTHS */}
      {/* ------------------------------------------------------------------ */}
      {activeTab === "pregnancy" && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl border border-purple-200 bg-purple-50/50 space-y-2">
            <h3 className="font-serif text-base font-bold text-[#183047] flex items-center gap-2">
              <Calendar className="w-4 h-4 text-[#69235B]" />
              <span>
                {language === "ta"
                  ? "கர்ப்ப கால 10 மாதங்களும் ஆளும் கிரகங்களும் (பராசர & ஆயுர்வேத முறை)"
                  : "The 10 Gestational Months & Fetal Rulership (Classical Embryology)"}
              </span>
            </h3>
            <p className="text-xs text-[#52667E] leading-relaxed">
              {language === "ta"
                ? "டாக்டர் எஸ். கிருஷ்ண குமார் நூலின் மூன்றாம் அத்தியாயத்தில் கொடுக்கப்பட்டுள்ள கரு வளர்ச்சி மற்றும் மாதந்தோறும் ஆளும் கிரகங்களின் வரிசை. எந்த மாத அதிபதி பலவீனமடைகிறாரோ அந்த மாதத்தில் கருச்சிதைவு அல்லது ஆபத்து ஏற்படலாம் என எச்சரிக்கப்படுகிறது."
                : "From Chapter 3 of Dr. S. Krishna Kumar's treatise: each gestational month is ruled by a specific Graha governing biological morphogenesis. Afflictions to the lord of that month indicate critical vulnerability windows."}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {gestational_months.map((m: GestationalMonthDetail) => (
              <div
                key={`gest-m-${m.month}`}
                className="p-4 rounded-xl border border-[#D9DEE7] bg-white hover:border-purple-300 transition-all space-y-2.5 shadow-2xs"
              >
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <div className="flex items-center gap-2.5">
                    <span className="w-7 h-7 rounded-full bg-purple-100 text-[#69235B] flex items-center justify-center font-bold text-xs">
                      {m.month}
                    </span>
                    <div>
                      <span className="text-[10px] uppercase font-bold text-[#8190A6] block">
                        {language === "ta" ? `${m.month}-ம் மாதம்` : `Month ${m.month}`}
                      </span>
                      <h4 className="font-serif text-sm font-bold text-[#183047]">
                        {m.sanskrit_term}
                      </h4>
                    </div>
                  </div>
                  <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-md bg-purple-50 text-[#69235B] border border-purple-200">
                    {m.ruling_planet}
                  </span>
                </div>

                <div className="space-y-1.5 text-xs">
                  <div>
                    <span className="text-[#8190A6] font-semibold block">
                      {language === "ta" ? "கரு வளர்ச்சி நிலை:" : "Developmental Stage:"}
                    </span>
                    <p className="text-[#183047] font-medium">
                      {language === "ta" ? m.stage_ta : m.stage_en}
                    </p>
                  </div>
                  <div className="pt-1 text-[11px] text-[#52667E] bg-slate-50 p-2 rounded">
                    <strong>{language === "ta" ? "மருத்துவ விளக்கம்:" : "Clinical Description:"}</strong>{" "}
                    {language === "ta" ? m.description_ta : m.description_en}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Delivery principles */}
          <div className="p-4 rounded-xl border border-indigo-200 bg-indigo-50/40 space-y-2">
            <h4 className="font-serif text-sm font-bold text-indigo-950 flex items-center gap-2">
              <HeartPulse className="w-4 h-4 text-indigo-600" />
              <span>
                {language === "ta"
                  ? "சுகப் பிரசவம் மற்றும் அறுவை சிகிச்சை பிரசவ (சிசேரியன்) யோகங்கள்"
                  : "Normal Delivery (Sukha Prasava) vs. Caesarean Operation (Kashta Prasava)"}
              </span>
            </h4>
            <p className="text-xs text-indigo-900 leading-relaxed">
              {language === "ta"
                ? "டாக்டர் கிருஷ்ண குமார் அவர்களின் அத்தியாயம் 7-ல் உள்ளபடி: லக்னம் மற்றும் 5, 9-ம் பாவங்கள் சுபக்கிரகங்களால் பார்க்கப்பட்டால் சுகப் பிரசவம் (சுக பிரசவ யோகம்) நிகழும். செவ்வாய், கேது, அல்லது சனி லக்னம், 8-ம் பாவம் அல்லது சந்திரனைத் தொடர்பு கொண்டால் சஸ்திர பிரசவம் (அறுவை சிகிச்சை சிசேரியன்) தவிர்க்க முடியாததாகிறது."
                : "According to Dr. Krishna Kumar's Chapter 7: Benefic aspects (Jupiter, Venus) to Lagna and 5th/9th bhavas indicate natural safe delivery (Sukha Prasava Yoga). When Mars, Ketu, or Saturn afflict the 1st or 8th house, surgical intervention (Caesarean operation) is indicated."}
            </p>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* TAB 4: 27 NAKSHATRAS MATRIX */}
      {/* ------------------------------------------------------------------ */}
      {activeTab === "nakshatras" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-[#D9DEE7]">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#8190A6]" />
              <input
                type="text"
                placeholder={
                  language === "ta"
                    ? "நட்சத்திரம், அதிதேவதை, அல்லது உடல் உறுப்பைத் தேடுக..."
                    : "Search star by name, deity, ruled organ, or disease..."
                }
                value={starSearch}
                onChange={(e) => setStarSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-[#D9DEE7] text-xs focus:outline-hidden focus:border-[#69235B]"
              />
            </div>
            <span className="text-xs text-[#8190A6] self-center">
              {filteredStars.length} / {all_27_nakshatras.length}{" "}
              {language === "ta" ? "நட்சத்திரங்கள்" : "Stars"}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {filteredStars.map((star: NakshatraMedicalDetail) => {
              const isMoonStar = native_moon_star && star.number === native_moon_star.number;
              const isLagnaStar = native_lagna_star && star.number === native_lagna_star.number;

              return (
                <div
                  key={`star-${star.number}`}
                  className={`p-4 rounded-xl border transition-all space-y-2 shadow-2xs ${
                    isMoonStar
                      ? "border-purple-400 bg-purple-50/50 ring-2 ring-purple-300"
                      : isLagnaStar
                      ? "border-indigo-400 bg-indigo-50/50 ring-2 ring-indigo-300"
                      : "border-[#D9DEE7] bg-white hover:border-purple-200"
                  }`}
                >
                  <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-purple-100 text-[#69235B] flex items-center justify-center font-bold text-[11px]">
                        {star.number}
                      </span>
                      <h4 className="font-serif text-sm font-bold text-[#183047]">
                        {language === "ta" ? star.name_ta : star.name}
                      </h4>
                    </div>
                    {isMoonStar && (
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-600 text-white">
                        {language === "ta" ? "ஜென்ம நட்சத்திரம்" : "Moon Star"}
                      </span>
                    )}
                    {isLagnaStar && !isMoonStar && (
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-600 text-white">
                        {language === "ta" ? "லக்ன நட்சத்திரம்" : "Lagna Star"}
                      </span>
                    )}
                  </div>

                  <div className="space-y-1.5 text-[11px]">
                    <div>
                      <span className="text-[#8190A6] font-semibold">{language === "ta" ? "அதிதேவதை: " : "Deity: "}</span>
                      <span className="text-[#183047] font-medium">{star.devata}</span>
                    </div>

                    <div>
                      <span className="text-[#8190A6] font-semibold block">{language === "ta" ? "உடல் உறுப்புகள்:" : "Organs:"}</span>
                      <span className="text-[#52667E]">{language === "ta" ? star.body_part_ta : star.body_part_en}</span>
                    </div>

                    <div>
                      <span className="text-[#8190A6] font-semibold block">{language === "ta" ? "நோய்க் கூறுகள்:" : "Vulnerability:"}</span>
                      <span className="text-rose-900 font-medium">{language === "ta" ? star.disease_tendency_ta : star.disease_tendency_en}</span>
                    </div>

                    <div className="pt-1 text-emerald-800 bg-emerald-50/70 p-1.5 rounded border border-emerald-100">
                      <strong>{language === "ta" ? "சாந்தி:" : "Propitiation:"}</strong>{" "}
                      {language === "ta" ? star.propitiation_ta : star.propitiation_en}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* TAB 5: TATWAS & NAVADWARAS */}
      {/* ------------------------------------------------------------------ */}
      {activeTab === "tatwas" && (
        <div className="space-y-6">
          {/* Pancha Maha Tatwas */}
          <div className="space-y-3">
            <h3 className="font-serif text-base font-bold text-[#183047] flex items-center gap-2">
              <Flame className="w-4 h-4 text-[#B4872B]" />
              <span>
                {language === "ta"
                  ? "பஞ்ச மகா தத்துவங்கள் (உடலின் ஐந்து மூலக்கூறுகள்)"
                  : "The Pancha Maha Tatwas (Five Biological Elements)"}
              </span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
              {tatwas_and_senses.map((tatwa: TatwaNavadwaraDetail, idx: number) => (
                <div
                  key={`tatwa-${idx}`}
                  className="p-4 rounded-xl border border-amber-200 bg-white space-y-2 shadow-2xs"
                >
                  <div className="flex items-center justify-between border-b border-amber-100 pb-2">
                    <h4 className="font-serif text-sm font-bold text-[#183047]">
                      {language === "ta" ? tatwa.tatwa_ta : tatwa.tatwa_en}
                    </h4>
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200">
                      {tatwa.planet}
                    </span>
                  </div>

                  <div className="space-y-1.5 text-xs">
                    <div>
                      <span className="text-[#8190A6] font-semibold">{language === "ta" ? "தன்மாத்திரை (புலன்): " : "Sense / Tanmatra: "}</span>
                      <span className="text-[#183047]">
                        {language === "ta" ? tatwa.sense_ta : tatwa.sense_en}
                      </span>
                    </div>
                    <div>
                      <span className="text-[#8190A6] font-semibold block">{language === "ta" ? "உடல் அமைப்புகள்:" : "Body Systems:"}</span>
                      <p className="text-[#52667E]">
                        {language === "ta" ? tatwa.body_parts_ta : tatwa.body_parts_en}
                      </p>
                    </div>
                    <div>
                      <span className="text-[#8190A6] font-semibold">{language === "ta" ? "அபிமானி தேவதை: " : "Deity: "}</span>
                      <span className="text-[#69235B] font-medium">{tatwa.abhimani_devata}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* TAB 6: 12 CLINICAL CASE HISTORIES */}
      {/* ------------------------------------------------------------------ */}
      {activeTab === "cases" && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl border border-purple-200 bg-purple-50/50 space-y-2">
            <h3 className="font-serif text-base font-bold text-[#183047] flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#69235B]" />
              <span>
                {language === "ta"
                  ? "டாக்டர் எஸ். கிருஷ்ண குமார் அவர்களின் 12 மருத்துவ ஆய்வு வழக்குகள்"
                  : "Dr. S. Krishna Kumar's 12 Classical Clinical Case Histories (Chapter 7)"}
              </span>
            </h3>
            <p className="text-xs text-[#52667E] leading-relaxed">
              {language === "ta"
                ? "மருத்துவ ஜோதிட நூலின் ஏழாம் அத்தியாயத்தில் இடம்பெற்றுள்ள புகழ்பெற்ற 12 மருத்துவ வரலாற்று ஆய்வுகள். ரத்தப் புற்றுநோய், மூளைக் கட்டி, கண்பார்வை இழப்பு, ஆஸ்துமா, கர்ப்பப்பை மற்றும் பிரசவ சிக்கல்கள் குறித்த ஜாதக அமைப்புகளும் அனுபவப் பாடங்களும்."
                : "The 12 landmark medical case studies from Chapter 7 of the compendium. These real clinical cases illustrate the diagnosis of leukaemia, brain tumours, blindness, gynaecological pathologies, and surgical childbirth."}
            </p>
          </div>

          <div className="space-y-3">
            {case_studies.map((cs: ClinicalCaseStudy, idx: number) => {
              const isExpanded = expandedCase === cs.id;

              return (
                <div
                  key={`case-study-${cs.id}`}
                  className="rounded-xl border border-[#D9DEE7] bg-white transition-all shadow-2xs hover:border-purple-300"
                >
                  <div
                    onClick={() => setExpandedCase(isExpanded ? null : cs.id)}
                    className="p-4 flex items-center justify-between gap-3 cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-7 h-7 rounded-full bg-purple-100 text-[#69235B] flex items-center justify-center font-bold text-xs shrink-0">
                        {idx + 1}
                      </span>
                      <div>
                        <h4 className="font-serif text-sm font-bold text-[#183047]">
                          {language === "ta" ? cs.title_ta : cs.title_en}
                        </h4>
                        <span className="text-[11px] text-rose-900 font-semibold">
                          {cs.disease_diagnosed}
                        </span>
                      </div>
                    </div>
                    <div className="text-[#8190A6]">
                      {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="px-4 pb-4 pt-1 border-t border-slate-100 space-y-3 text-xs">
                      <div>
                        <span className="text-[#8190A6] font-semibold block mb-0.5">
                          {language === "ta" ? "நோயாளி பின்னணி:" : "Patient Profile:"}
                        </span>
                        <p className="text-[#183047] font-medium">{cs.patient_profile}</p>
                      </div>

                      {/* Astrological Indicators */}
                      <div>
                        <span className="text-[#8190A6] font-semibold block mb-1">
                          {language === "ta" ? "ஜாதகக் காரணிகள் & கிரக அமைப்புகள்:" : "Astrological Indicators in Chart:"}
                        </span>
                        <ul className="list-disc pl-5 text-[#52667E] space-y-1 bg-purple-50/40 p-3 rounded-lg border border-purple-100">
                          {cs.astrological_indicators.map((ind: string, iIdx: number) => (
                            <li key={`ind-${cs.id}-${iIdx}`}>{ind}</li>
                          ))}
                        </ul>
                      </div>

                      {/* Dasha Timing */}
                      <div>
                        <span className="text-[#8190A6] font-semibold block">
                          {language === "ta" ? "தசா புக்தி காலக்கட்டம்:" : "Dasha Timing:"}
                        </span>
                        <p className="text-[#183047] font-mono mt-0.5">{cs.dasha_timing}</p>
                      </div>

                      {/* Key Takeaway / Lesson */}
                      <div>
                        <span className="text-[#8190A6] font-semibold block">
                          {language === "ta" ? "மருத்துவ ஜோதிட பாடம் & அனுபவ உண்மை:" : "Clinical Key Takeaway:"}
                        </span>
                        <p className="text-emerald-950 leading-relaxed mt-0.5 bg-emerald-50/60 p-3 rounded-lg border border-emerald-200">
                          {cs.key_takeaway}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
