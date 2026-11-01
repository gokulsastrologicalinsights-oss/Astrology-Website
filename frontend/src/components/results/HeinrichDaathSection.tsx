"use client";

import React, { useState, useMemo } from "react";
import {
  HeinrichDaathCompendium,
  DaathSignAnatomy,
  DaathPlanetAction,
  DaathAntipathicTherapy,
  DaathPlanetaryPeriod,
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
  Droplets,
  Wind,
  Mountain,
  Flower2,
  Stethoscope,
  Pill,
  Zap,
  Scale,
  Brain,
  Bone,
} from "lucide-react";

interface HeinrichDaathSectionProps {
  compendium: HeinrichDaathCompendium;
  language: "en" | "ta";
  onSelectRule?: (rule: MedicalRule) => void;
}

export function HeinrichDaathSection({
  compendium,
  language,
  onSelectRule,
}: HeinrichDaathSectionProps) {
  const [activeTab, setActiveTab] = useState<
    "overview" | "signs" | "biodynamics" | "temperaments" | "antipathics" | "cycles" | "rules"
  >("overview");

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [ruleFilter, setRuleFilter] = useState<"all" | "active">("all");
  const [expandedSign, setExpandedSign] = useState<number | null>(null);
  const [selectedPlanet, setSelectedPlanet] = useState<string | null>(null);

  const {
    book_title,
    book_title_ta,
    author,
    publisher,
    historical_foundation,
    core_philosophy_en,
    core_philosophy_ta,
    signs_anatomy = [],
    planets_biodynamics = [],
    temperaments_and_crosses = {},
    antipathic_therapeutics = [],
    seven_ages_of_man = [],
    decumbiture_and_cycles,
    strength_evaluation,
    matched_rules = [],
  } = compendium;

  const isEn = language === "en";

  // Filtered signs based on search query
  const filteredSigns = useMemo(() => {
    if (!searchQuery.trim()) return signs_anatomy;
    const q = searchQuery.toLowerCase();
    return signs_anatomy.filter(
      (s) =>
        s.sign_name_en.toLowerCase().includes(q) ||
        s.sign_name_ta.toLowerCase().includes(q) ||
        s.principal_bones.some((b) => b.toLowerCase().includes(q)) ||
        s.muscles.some((m) => m.toLowerCase().includes(q)) ||
        s.morbid_actions.some((ma) => ma.toLowerCase().includes(q))
    );
  }, [signs_anatomy, searchQuery]);

  // Filtered rules
  const activeRulesCount = useMemo(
    () => matched_rules.filter((r) => r.is_active).length,
    [matched_rules]
  );

  const displayedRules = useMemo(() => {
    return matched_rules.filter((r) => {
      if (ruleFilter === "active" && !r.is_active) return false;
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        r.name.toLowerCase().includes(q) ||
        (r.name_tamil && r.name_tamil.toLowerCase().includes(q)) ||
        (r.traditional_interpretation &&
          r.traditional_interpretation.toLowerCase().includes(q)) ||
        (r.category && r.category.toLowerCase().includes(q))
      );
    });
  }, [matched_rules, ruleFilter, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Author and Treatise Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-950 via-slate-900 to-purple-950 border border-indigo-500/30 p-6 shadow-xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-xs font-semibold tracking-wide">
              <BookOpen className="w-3.5 h-3.5" />
              <span>
                {isEn
                  ? "Classical Jatromathematics & Hermetic Biodynamics"
                  : "பண்டைய எகிப்திய மருத்துவ ஜோதிடம் & ஹெர்மெடிக் உயிரியக்கவியல்"}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
              <span>{isEn ? book_title : book_title_ta}</span>
            </h2>
            <p className="text-sm text-indigo-200/90 font-medium">
              {isEn
                ? `Author: ${author} • Publisher: ${publisher}`
                : `ஆசிரியர்: ${author} • பதிப்பகம்: ${publisher}`}
            </p>
            <p className="text-xs text-slate-400 max-w-3xl leading-relaxed">
              {isEn
                ? "Restoring the ancient Egyptian jatromathematics and Paracelsian Medicina Adepta: human anatomy mapped through 12-sign bony/vascular frameworks, 9 planetary biodynamic vectors, antipathic balancing (Contraria Contrariis Curantur), and decumbiture critical days."
                : "பண்டைய எகிப்திய ஜாத்ரோமேத்தமேட்டிக்ஸ் மற்றும் பரசெல்சியன் மருத்துவ ஞானம்: 12 ராசி எலும்பு/இரத்தநாள உடற்கூறியல், 9 கிரகங்களின் துருவநிலை இயக்கம், எதிர்முனை சமநிலை சிகிச்சை மற்றும் தீவிர நோய்க்கால சந்திர சுழற்சிகள்."}
            </p>
          </div>

          <div className="flex md:flex-col items-center md:items-end gap-2 shrink-0">
            <div className="px-3.5 py-2 rounded-xl bg-slate-800/80 border border-indigo-500/30 text-center">
              <span className="text-xs text-indigo-300 block font-medium">
                {isEn ? "Historical Root" : "வரலாற்று ஆதாரம்"}
              </span>
              <span className="text-sm font-bold text-slate-100">
                {isEn ? "Egyptian / Paracelsian" : "எகிப்து / பாராசெல்சியஸ்"}
              </span>
            </div>
            <div className="px-3.5 py-2 rounded-xl bg-indigo-500/20 border border-indigo-500/40 text-center">
              <span className="text-xs text-indigo-300 block font-medium">
                {isEn ? "Active Rules" : "செயலில் உள்ள விதிகள்"}
              </span>
              <span className="text-sm font-bold text-indigo-200">
                {activeRulesCount} / {matched_rules.length}
              </span>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mt-6 flex flex-wrap gap-2 border-t border-slate-800/80 pt-4">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "overview"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isEn ? "Jatromathematics & Foundation" : "ஜாத்ரோமேத்தமேட்டிக்ஸ் & அடிப்படை"}</span>
          </button>

          <button
            onClick={() => setActiveTab("signs")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "signs"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Bone className="w-3.5 h-3.5" />
            <span>{isEn ? "12-Sign Head-to-Toe Anatomy" : "12 ராசி உடற்கூறியல்"}</span>
          </button>

          <button
            onClick={() => setActiveTab("biodynamics")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "biodynamics"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{isEn ? "Planetary Biodynamics & Tissues" : "கிரக இயக்கவியல் & திசுக்கள்"}</span>
          </button>

          <button
            onClick={() => setActiveTab("temperaments")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "temperaments"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Flame className="w-3.5 h-3.5" />
            <span>{isEn ? "Temperaments & Cross Reflexes" : "சுபாவங்கள் & குறுக்கு பிரதிபலிப்பு"}</span>
          </button>

          <button
            onClick={() => setActiveTab("antipathics")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "antipathics"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Scale className="w-3.5 h-3.5" />
            <span>{isEn ? "Antipathic Therapeutics" : "எதிர்முனை சமநிலை மருத்துவம்"}</span>
          </button>

          <button
            onClick={() => setActiveTab("cycles")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "cycles"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>{isEn ? "Seven Ages & Decumbiture" : "மனிதனின் 7 பருவங்கள் & சந்திர சுழற்சிகள்"}</span>
          </button>

          <button
            onClick={() => setActiveTab("rules")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "rules"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>
              {isEn ? `Matched Rules (${activeRulesCount})` : `பொருந்திய விதிகள் (${activeRulesCount})`}
            </span>
          </button>
        </div>
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* TAB 1: OVERVIEW & JATROMATHEMATICS FOUNDATION */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Core Philosophy Card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-md space-y-4">
            <h3 className="text-lg font-bold text-indigo-300 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <span>{isEn ? "Core Jatromathematical Principles" : "அடிப்படை மருத்துவ தத்துவங்கள்"}</span>
            </h3>
            <p className="text-sm text-slate-300 leading-relaxed">
              {isEn ? core_philosophy_en : core_philosophy_ta}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-800/80">
              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-2">
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block">
                  {isEn ? "Microcosm in Macrocosm" : "அண்டத்தில் உள்ளது பிண்டம்"}
                </span>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {isEn
                    ? "Man is a miniature universe. Every organ, fluid, and cell vibrates sympathetically with the celestial spheres and planetary vectors."
                    : "மனிதன் ஒரு சிறிய பிரபஞ்சம். ஒவ்வொரு உறுப்பும் திரவமும் செல்லும் விண்வெளி கோளங்களின் அதிர்வுகளோடு இணைந்திருக்கிறது."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-2">
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block">
                  {isEn ? "Doctrine of Vibration (Adelphixis)" : "அதிர்வு மற்றும் அனுதாப கோட்பாடு"}
                </span>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {isEn
                    ? "Disease is not a material intruder but a disturbance of physiological rhythm—manifesting as Hyper-tonicity (+), Hypo-atonicity (-), or Perversion."
                    : "நோய் என்பது வெளியிலிருந்து வரும் பருப்பொருள் அல்ல; அது உடலின் இயற்கை அதிர்வில் ஏற்படும் அதிக அழுத்தம் (+), தளர்வு (-) அல்லது பிறழ்ச்சி ஆகும்."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-2">
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block">
                  {isEn ? "Contraria Contrariis Curantur" : "எதிர்முனை சமநிலை சிகிச்சை"}
                </span>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {isEn
                    ? "Afflictions of excessive cold (Saturn) require antipathic heat/tonics (Mars/Iron); excessive inflammatory combustion (Mars) requires cooling sedatives (Saturn/Antimony)."
                    : "சனி கிரகத்தின் குளிர்ச்சியான சோர்வு நிலைக்கு செவ்வாயின் இரும்பு டானிக்குகளும், செவ்வாயின் கொதிக்கும் காய்ச்சலுக்கு சனியின் குளிர்ச்சி மருந்துகளும் தேவைப்படுகின்றன."}
                </p>
              </div>
            </div>
          </div>

          {/* 5-Fold Strength Evaluation Card */}
          {strength_evaluation && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-md space-y-4">
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Scale className="w-5 h-5 text-indigo-400" />
                <span>
                  {isEn
                    ? "Five-Fold Astrological Potency Evaluation"
                    : "ஐந்து வகை ஜோதிட வலிமை பகுப்பாய்வு"}
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                {isEn
                  ? "Heinrich Däath evaluates physiological prognosis through five classical balances: Aspect (Drikbalam), Position (Sthanabalam), Natural / Mutual Receptions, Motional Speed, and Radix Hexis vs Directional Diathesis."
                  : "ஹென்ரிச் டாத் ஜாதகரின் நோய்த்தடுப்பு திறனை பார்வை வலிமை, ஸ்தான வலிமை, பரஸ்பர பரிவர்த்தனை, கோள்களின் வேகம் மற்றும் நிரந்தர உடல்வாகு கொண்டு மதிப்பிடுகிறார்."}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 space-y-2">
                  <div className="flex items-center gap-2 text-indigo-300 font-semibold text-xs">
                    <Eye className="w-4 h-4" />
                    <span>{isEn ? "1. Aspect Potency (Drikbalam)" : "1. பார்வை பலம்"}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {strength_evaluation.drikbalam_aspect_summary}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 space-y-2">
                  <div className="flex items-center gap-2 text-indigo-300 font-semibold text-xs">
                    <Compass className="w-4 h-4" />
                    <span>{isEn ? "2. Positional Dignity (Sthanabalam)" : "2. ஸ்தான பலம்"}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {strength_evaluation.sthanabalam_summary}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 space-y-2">
                  <div className="flex items-center gap-2 text-indigo-300 font-semibold text-xs">
                    <Layers className="w-4 h-4" />
                    <span>{isEn ? "3. Mutual Receptions" : "3. பரஸ்பர பரிவர்த்தனை"}</span>
                  </div>
                  <ul className="text-xs text-slate-300 space-y-1">
                    {strength_evaluation.nisargikabalam_mutual_receptions.map((mr, i) => (
                      <li key={i} className="leading-relaxed">
                        • {mr}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 space-y-2">
                  <div className="flex items-center gap-2 text-indigo-300 font-semibold text-xs">
                    <HeartPulse className="w-4 h-4" />
                    <span>{isEn ? "4. Mundane Angles vs Cadent" : "4. கேந்திர vs மறைவு பாவங்கள்"}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {strength_evaluation.mundane_strength_summary}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 space-y-2">
                  <div className="flex items-center gap-2 text-indigo-300 font-semibold text-xs">
                    <Clock className="w-4 h-4" />
                    <span>{isEn ? "5. Motional Speed & Retrograde" : "5. கோள் வேகம் & வக்ரம்"}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {strength_evaluation.motional_strength_summary}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 space-y-2">
                  <div className="flex items-center gap-2 text-indigo-300 font-semibold text-xs">
                    <Activity className="w-4 h-4" />
                    <span>{isEn ? "Hexis (Habit) vs Diathesis" : "நிரந்தர vs தற்காலிக நிலை"}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {strength_evaluation.directional_hexis_vs_diathesis}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 2: 12-SIGN HEAD-TO-TOE ANATOMY */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "signs" && (
        <div className="space-y-6">
          {/* Renal Distinction Callout Banner */}
          <div className="rounded-2xl border border-amber-500/40 bg-amber-950/30 p-5 shadow-lg space-y-2">
            <div className="flex items-center gap-2 text-amber-300 font-bold text-sm">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
              <span>
                {isEn
                  ? "Däath's Signature Clinical Distinction: Libra Filtration vs Scorpio Calculus"
                  : "ஹென்ரிச் டாத்தின் முக்கிய மருத்துவ வேறுபாடு: துலாம் சிறுநீரக வடிகட்டுதல் vs விருச்சிக சிறுநீரக கல்"}
              </span>
            </div>
            <p className="text-xs text-amber-200/90 leading-relaxed">
              {isEn
                ? "Däath explicitly warns medical practitioners against confusing kidney secretion with kidney excretion. Libra strictly rules the cortical substance and Malpighian tufts (secretion of urine; failure causes suppression). Scorpio rules the renal pelvis, calyces, ureters, and bladder (holding and excreting; affliction causes calculus/gravel, retention, or surgical gravel)."
                : "சிறுநீரகத்தில் நீர் பிரித்தெடுப்பதற்கும் (துலாம் - Libra cortex), சிறுநீரக குழாய்கள் மற்றும் பையில் தங்குவதற்கும் (விருச்சிகம் - Scorpio pelvis/gravel) உள்ள மிக முக்கியமான வேறுபாட்டை டாத் தெளிவாக சுட்டிக்காட்டுகிறார். துலாம் கோளாறு சிறுநீர் உற்பத்தியை நிறுத்தும்; விருச்சிகக் கோளாறு கற்களையும் சிறுநீர் தேக்கத்தையும் உண்டாக்கும்."}
            </p>
          </div>

          {/* Search Bar */}
          <div className="flex items-center gap-3 bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-2.5">
            <Search className="w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={
                isEn
                  ? "Search signs, bones, muscles, vessels, or diseases..."
                  : "ராசி, எலும்புகள், தசைகள் அல்லது நோய்களைத் தேடுக..."
              }
              className="bg-transparent text-sm text-slate-200 placeholder-slate-500 focus:outline-none w-full"
            />
          </div>

          {/* Signs Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredSigns.map((sign) => {
              const isExpanded = expandedSign === sign.sign_index;
              const hasNativeTag =
                sign.is_native_ascendant ||
                sign.is_native_sun_sign ||
                sign.is_native_moon_sign ||
                sign.is_native_sixth_house;

              return (
                <div
                  key={sign.sign_index}
                  className={`rounded-2xl border transition-all ${
                    hasNativeTag
                      ? "border-indigo-500/50 bg-slate-900/80 shadow-md shadow-indigo-950/30"
                      : "border-slate-800 bg-slate-900/40 hover:border-slate-700"
                  } p-5 space-y-3`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-lg bg-indigo-500/20 text-indigo-300 text-xs font-bold flex items-center justify-center">
                          {sign.sign_index}
                        </span>
                        <h4 className="text-base font-bold text-slate-100">
                          {isEn ? sign.sign_name_en : sign.sign_name_ta}
                        </h4>
                        <span className="text-xs text-slate-400">
                          ({isEn ? sign.sign_name_ta : sign.sign_name_en})
                        </span>
                      </div>
                      <span className="text-xs text-slate-400 block mt-1">
                        {sign.symbolic_quality}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-1 justify-end">
                      {sign.is_native_ascendant && (
                        <span className="px-2 py-0.5 rounded-md bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-[10px] font-semibold">
                          {isEn ? "Ascendant" : "லக்னம்"}
                        </span>
                      )}
                      {sign.is_native_sun_sign && (
                        <span className="px-2 py-0.5 rounded-md bg-amber-500/20 border border-amber-500/40 text-amber-300 text-[10px] font-semibold">
                          {isEn ? "Sun" : "சூரியன்"}
                        </span>
                      )}
                      {sign.is_native_moon_sign && (
                        <span className="px-2 py-0.5 rounded-md bg-blue-500/20 border border-blue-500/40 text-blue-300 text-[10px] font-semibold">
                          {isEn ? "Moon" : "சந்திரன்"}
                        </span>
                      )}
                      {sign.is_native_sixth_house && (
                        <span className="px-2 py-0.5 rounded-md bg-rose-500/20 border border-rose-500/40 text-rose-300 text-[10px] font-semibold">
                          {isEn ? "6th House" : "6-ம் பாவம்"}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Special Kidney Distinction Note */}
                  {sign.kidney_pelvis_distinction && (
                    <div className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-600/30 text-[11px] text-amber-200 leading-relaxed">
                      <strong>{isEn ? "Physiological Speciality: " : "சிறப்பு குறிப்பு: "}</strong>
                      {sign.kidney_pelvis_distinction}
                    </div>
                  )}

                  {/* Principal Anatomical Structures */}
                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="font-semibold text-slate-300 block">
                        {isEn ? "Principal Bones:" : "முக்கிய எலும்புகள்:"}
                      </span>
                      <p className="text-slate-400">{sign.principal_bones.join(", ")}</p>
                    </div>

                    <div>
                      <span className="font-semibold text-slate-300 block">
                        {isEn ? "Muscles Governed:" : "ஆளும் தசைகள்:"}
                      </span>
                      <p className="text-slate-400">{sign.muscles.join(", ")}</p>
                    </div>

                    {isExpanded && (
                      <div className="space-y-2 pt-2 border-t border-slate-800/80">
                        <div>
                          <span className="font-semibold text-slate-300 block">
                            {isEn ? "Arterial Supply:" : "தமனி ரத்த ஓட்டம்:"}
                          </span>
                          <p className="text-slate-400">{sign.arteries.join(", ")}</p>
                        </div>

                        <div>
                          <span className="font-semibold text-slate-300 block">
                            {isEn ? "Venous System:" : "சிரை ரத்த நாளங்கள்:"}
                          </span>
                          <p className="text-slate-400">{sign.veins.join(", ")}</p>
                        </div>
                      </div>
                    )}

                    <div>
                      <span className="font-semibold text-rose-300 block">
                        {isEn ? "Morbid Actions & Diseases:" : "நோயியல் தாக்கங்கள்:"}
                      </span>
                      <p className="text-rose-200/90">{sign.morbid_actions.join(", ")}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => setExpandedSign(isExpanded ? null : sign.sign_index)}
                    className="text-[11px] text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1 pt-1"
                  >
                    <span>{isExpanded ? (isEn ? "Show Less" : "குறைவாகக் காட்டு") : (isEn ? "Show Vessels & Details" : "நாளங்கள் & முழு விவரம்")}</span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 3: PLANETARY BIODYNAMICS & TISSUES */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "biodynamics" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Zap className="w-5 h-5 text-indigo-400" />
              <span>{isEn ? "Nine Planetary Biodynamic Modes" : "ஒன்பது கிரகங்களின் உயிரியக்கவியல்"}</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              {isEn
                ? "In Däath's jatromathematics, planets are dynamic motion vectors. They build specific bodily tissues, express thermal/moisture polarities, and cause distinctive pathognomic symptoms when afflicted."
                : "ஹென்ரிச் டாத்தின் கோட்பாட்டின்படி, கிரகங்கள் என்பது உடல் திசுக்களை உருவாக்கும் இயங்கு ஆற்றல்கள். அவை வெப்ப/குளிர்ச்சி துருவங்களை உடலுக்கு வழங்கி, கோளாறுகளின் போது தனித்துவமான நோய்க்குறிகளை வெளிப்படுத்துகின்றன."}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {planets_biodynamics.map((p) => {
              const isSelected = selectedPlanet === p.planet;
              return (
                <div
                  key={p.planet}
                  className={`rounded-2xl border p-5 space-y-3 transition-all ${
                    p.native_chart_condition.includes("Tonic")
                      ? "border-emerald-500/40 bg-slate-900/80"
                      : p.native_chart_condition.includes("Atonic") || p.native_chart_condition.includes("Perverted")
                      ? "border-rose-500/40 bg-slate-900/80"
                      : "border-slate-800 bg-slate-900/40"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-base font-bold text-slate-100">{p.planet}</h4>
                        <span className="text-xs text-indigo-300">({p.planet_ta})</span>
                      </div>
                      <span className="text-[11px] text-slate-400 block italic">
                        {p.esoteric_title}
                      </span>
                    </div>

                    <span
                      className={`px-2 py-0.5 rounded-md text-[10px] font-semibold border ${
                        p.polarity.includes("Positive")
                          ? "bg-amber-500/20 border-amber-500/40 text-amber-300"
                          : p.polarity.includes("Negative")
                          ? "bg-blue-500/20 border-blue-500/40 text-blue-300"
                          : "bg-purple-500/20 border-purple-500/40 text-purple-300"
                      }`}
                    >
                      {p.polarity.split(" ")[0]}
                    </span>
                  </div>

                  {/* Native Chart Status Pill */}
                  <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
                    <span className="text-[10px] text-slate-400 block font-medium">
                      {isEn ? "Native's Radix Status:" : "ஜாதகரின் அமைவு நிலை:"}
                    </span>
                    <span className="font-semibold text-slate-200">
                      {p.native_chart_condition}
                    </span>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="text-slate-400 block">{isEn ? "Biodynamic Vector:" : "இயக்க வகை:"}</span>
                      <span className="text-slate-200 font-medium">{p.biodynamic_motion}</span>
                    </div>

                    <div>
                      <span className="text-slate-400 block">{isEn ? "Tissue Building:" : "உருவாக்கும் திசுக்கள்:"}</span>
                      <span className="text-indigo-300 font-medium">{p.tissue_building}</span>
                    </div>

                    <div>
                      <span className="text-slate-400 block">{isEn ? "Elemental Degrees:" : "பூத அளவுகள்:"}</span>
                      <span className="text-amber-200">{p.elemental_degrees}</span>
                    </div>

                    <div>
                      <span className="text-slate-400 block">{isEn ? "Salient Pathognomy:" : "முக்கிய நோயியல் அறிகுறி:"}</span>
                      <p className="text-slate-300 text-[11px] leading-relaxed">
                        {p.salient_pathognomy}
                      </p>
                    </div>

                    {isSelected && (
                      <div className="space-y-2 pt-2 border-t border-slate-800">
                        <div>
                          <span className="text-slate-400 block">{isEn ? "Typical Botanical Simples:" : "தாவர மூலிகைகள்:"}</span>
                          <p className="text-emerald-300 text-[11px]">
                            {p.typical_plants.join(", ")}
                          </p>
                        </div>
                        <div>
                          <span className="text-slate-400 block">{isEn ? "Metals & Minerals:" : "உலோகங்கள் & தாதுக்கள்:"}</span>
                          <p className="text-slate-300 text-[11px]">
                            {p.metals_minerals.join(", ")}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => setSelectedPlanet(isSelected ? null : p.planet)}
                    className="text-[11px] text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1 pt-1"
                  >
                    <span>{isSelected ? (isEn ? "Show Less" : "குறைவாகக் காட்டு") : (isEn ? "Show Materia Medica" : "மூலிகை & உலோகம் காட்டு")}</span>
                    {isSelected ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 4: TEMPERAMENTS & CROSS REFLEXES */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "temperaments" && (
        <div className="space-y-6">
          {/* Dominant Temperament Header */}
          <div className="rounded-2xl border border-indigo-500/30 bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 p-6 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider block">
                  {isEn ? "Dominant Radix Temperament" : "ஜாதகரின் முதன்மை சுபாவம்"}
                </span>
                <h3 className="text-2xl font-bold text-slate-100 mt-1">
                  {temperaments_and_crosses.dominant_temperament || "Sanguine / Choleric"}
                </h3>
              </div>

              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1.5 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-semibold">
                  🔥 {isEn ? "Fire:" : "நெருப்பு:"} {temperaments_and_crosses.fire_count || 0}
                </span>
                <span className="px-3 py-1.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-semibold">
                  🌍 {isEn ? "Earth:" : "பூமி:"} {temperaments_and_crosses.earth_count || 0}
                </span>
                <span className="px-3 py-1.5 rounded-xl bg-sky-500/20 border border-sky-500/40 text-sky-300 text-xs font-semibold">
                  💨 {isEn ? "Air:" : "காற்று:"} {temperaments_and_crosses.air_count || 0}
                </span>
                <span className="px-3 py-1.5 rounded-xl bg-blue-500/20 border border-blue-500/40 text-blue-300 text-xs font-semibold">
                  🌊 {isEn ? "Water:" : "நீர்:"} {temperaments_and_crosses.water_count || 0}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs">
                <span className="text-slate-400 block">{isEn ? "Cardinal (Brahma / Creative):" : "சரம் (படைப்பு):"}</span>
                <span className="text-base font-bold text-slate-100">{temperaments_and_crosses.cardinal_count || 0} planets</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs">
                <span className="text-slate-400 block">{isEn ? "Fixed (Vishnu / Preservative):" : "ஸ்திரம் (காத்தல்):"}</span>
                <span className="text-base font-bold text-slate-100">{temperaments_and_crosses.fixed_count || 0} planets</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs">
                <span className="text-slate-400 block">{isEn ? "Mutable (Iswara / Destructive):" : "உபயம் (மாற்றம்):"}</span>
                <span className="text-base font-bold text-slate-100">{temperaments_and_crosses.mutable_count || 0} planets</span>
              </div>
            </div>
          </div>

          {/* 4 Temperaments Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(temperaments_and_crosses.temperament_definitions || {}).map(([key, item]: [string, any]) => (
              <div key={key} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-base font-bold text-slate-100">{item.name}</h4>
                  <span className="text-xs text-indigo-300">{item.name_ta}</span>
                </div>
                <div className="space-y-1.5 text-xs">
                  <div>
                    <span className="text-slate-400 font-medium">{isEn ? "Signs & Element:" : "ராசிகள் & பூதம்:"}</span>{" "}
                    <span className="text-slate-200">{item.element}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">{isEn ? "Somatic Diathesis:" : "உடல் தத்துவம்:"}</span>{" "}
                    <span className="text-slate-200">{item.somatic_diathesis}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">{isEn ? "Morbid Tendency:" : "நோய் போக்கு:"}</span>{" "}
                    <span className="text-rose-300">{item.morbid_tendency}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Quadruplicities & Cross Reflex Dynamics */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
            <h3 className="text-base font-bold text-indigo-300 flex items-center gap-2">
              <Compass className="w-5 h-5 text-indigo-400" />
              <span>{isEn ? "Three Quadruplicities & Cross Reflex Dynamics" : "முப்பெரும் சிலுவைகள் & உறுப்பு பிரதிபலிப்பு"}</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              {isEn
                ? "Däath incorporates the Hindu Trinity (Brahma=Cardinal, Vishnu=Fixed, Iswara=Mutable) into pathological cross dynamics. An affliction in one arm of a cross invariably excites symptoms in the opposite or square polarities."
                : "சரம், ஸ்திரம், உபயம் ஆகிய மூன்று சிலுவை அமைப்புகளும் மனித உடலில் ஒன்றோடொன்று குறுக்கு பிரதிபலிப்பு கொண்டுள்ளன. ஒரு ராசியில் ஏற்படும் கோளாறு அதன் நேர் எதிர் அல்லது சதுர ராசிகளிலும் பிரதிபலிக்கும்."}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(temperaments_and_crosses.cross_definitions || {}).map(([key, cross]: [string, any]) => (
                <div key={key} className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-2">
                  <h5 className="text-sm font-bold text-slate-100">{cross.name}</h5>
                  <span className="text-[11px] text-indigo-300 block">{cross.esoteric_force}</span>
                  <p className="text-xs text-slate-300">{cross.pathology_mode}</p>
                  <div className="pt-2 border-t border-slate-800 text-[11px] text-amber-200/90">
                    <strong>{isEn ? "Reflex Dynamics:" : "பிரதிபலிப்பு:"}</strong> {cross.cross_reflex}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 5: ANTIPATHIC THERAPEUTICS */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "antipathics" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Scale className="w-5 h-5 text-indigo-400" />
              <span>{isEn ? "Paracelsian Antipathic Therapeutics (Contraria Contrariis Curantur)" : "எதிர்முனை சமநிலை சிகிச்சை விதிகள்"}</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              {isEn
                ? "Unlike modern symptomatic suppression, Paracelsian Jatromathematics restores balance by neutralizing the afflicting planetary vibration with its true astrological and chemical antipathy."
                : "பாதிக்கப்பட்ட கிரகத்தின் அதீத வெப்பம், குளிர்ச்சி அல்லது சோர்வை அதற்கு இணையான எதிர்முனை கிரக சக்தி மற்றும் மூலிகைகள் கொண்டு சமநிலைப்படுத்தும் பாரம்பரிய முறை."}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {antipathic_therapeutics.map((at, idx) => (
              <div
                key={idx}
                className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="text-base font-bold text-slate-100">{at.category}</h4>
                    <span className="text-xs text-indigo-300">{at.category_ta}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 text-[10px] font-semibold border border-indigo-500/40">
                    {isEn ? "Antipathic Balance" : "எதிர் சமநிலை"}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2 text-xs">
                  <div>
                    <span className="text-rose-400 font-semibold block">
                      {isEn ? "Afflicting Planetary Cause:" : "பாதிக்கும் கிரக காரகம்:"}
                    </span>
                    <span className="text-slate-300">{at.afflicting_planetary_force}</span>
                  </div>

                  <div>
                    <span className="text-emerald-400 font-semibold block">
                      {isEn ? "Curative Antipathic Remedy Planet:" : "குணப்படுத்தும் எதிர் கோள்:"}
                    </span>
                    <span className="text-slate-300">{at.curative_planetary_remedy}</span>
                  </div>
                </div>

                <div className="text-xs space-y-1">
                  <span className="text-indigo-300 font-semibold block">
                    {isEn ? "Therapeutic Rule:" : "சிகிச்சை விதி:"}
                  </span>
                  <p className="text-slate-400 italic text-[11px] leading-relaxed">
                    "{at.opposing_polarity_rule}"
                  </p>
                </div>

                <div className="text-xs space-y-1 pt-2 border-t border-slate-800">
                  <span className="text-slate-300 font-semibold block">
                    {isEn ? "Specific Dietary & Substance Applications:" : "பயன்படுத்தப்படும் பொருட்கள் & உணவு முறை:"}
                  </span>
                  <p className="text-slate-400 text-[11px] leading-relaxed">
                    {at.substances_and_application}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 6: SEVEN AGES & DECUMBITURE CYCLES */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "cycles" && (
        <div className="space-y-6">
          {/* Seven Ages of Man Timeline */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
            <div>
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Clock className="w-5 h-5 text-indigo-400" />
                <span>{isEn ? "The Seven Ages of Man (Planetary Life-Periods)" : "மனிதனின் 7 பருவங்கள் (கிரக காலங்கள்)"}</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                {isEn
                  ? "Ptolemaic and Däath doctrine divides the human lifespan into 7 sequential planetary regimes. If the period ruler is afflicted in the radix or directional arcs, illnesses characteristic of that planet become active."
                  : "மனித வாழ்க்கை 7 கிரகப் பருவங்களாக பிரிக்கப்பட்டுள்ளது. நடப்பு பருவத்தின் அதிபதி ஜாதகத்தில் பலவீனமடைந்தால், அக்கோளின் நோயியல் தன்மைகள் வெளிப்படும்."}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {seven_ages_of_man.map((period, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-xl border transition-all ${
                    period.is_native_current_age
                      ? "border-emerald-500 bg-emerald-950/30 shadow-lg shadow-emerald-950/40"
                      : "border-slate-800 bg-slate-900/40"
                  } space-y-2`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-slate-100">
                      {period.planet} ({period.planet_ta})
                    </span>
                    <span className="text-xs text-indigo-300 font-semibold">
                      {period.start_age}-{period.end_age}y
                    </span>
                  </div>

                  {period.is_native_current_age && (
                    <span className="inline-block px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 text-[10px] font-bold border border-emerald-500/40">
                      {isEn ? "Native's Current Age" : "ஜாதகரின் தற்போதைய பருவம்"}
                    </span>
                  )}

                  <div className="text-xs space-y-1">
                    <span className="text-slate-400 block font-medium">
                      {isEn ? period.age_label : period.age_label_ta}
                    </span>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      {period.biological_development}
                    </p>
                    <p className="text-rose-300 text-[11px] pt-1">
                      <strong>{isEn ? "Affliction: " : "பாதிப்பு: "}</strong>
                      {period.astrological_vulnerability}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Decumbiture & 7-Year Climacterics */}
          {decumbiture_and_cycles && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Lunar Decumbiture Critical Days */}
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-3">
                <h4 className="text-base font-bold text-indigo-300 flex items-center gap-2">
                  <Moon className="w-5 h-5 text-indigo-400" />
                  <span>{isEn ? "Acute Febrile Decumbiture Cycles" : "காய்ச்சல் & தீவிர நோய்க்கான சந்திர சுழற்சிகள்"}</span>
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {isEn
                    ? "In acute febrile crises, the Moon's progress marks the turning points of the disease via exact squares and oppositions to its decumbiture longitude."
                    : "திடீர் காய்ச்சல் மற்றும் தீவிர நோய்களின் போது, சந்திரன் தன் துவக்க புள்ளியிலிருந்து நகரும் சதுர மற்றும் சமசப்தம பார்வை நாட்களே நோயின் திருப்புமுனை நாட்களாகும்."}
                </p>

                <div className="space-y-2 pt-2">
                  {decumbiture_and_cycles.lunar_critical_cycles.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-100">{item.day}</span>
                        <span className="text-indigo-300 text-[11px]">{item.motion}</span>
                      </div>
                      <p className="text-slate-300 text-[11px] leading-relaxed">
                        {item.clinical_manifestation}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 7-Year Climacteric Law & Lunar Metabolism */}
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-3">
                <h4 className="text-base font-bold text-purple-300 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-purple-400" />
                  <span>{isEn ? "The Seven-Year Climacteric Law" : "7-ஆண்டு முக்கிய மாற்ற கால விதி"}</span>
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-800/50 p-3 rounded-xl border border-slate-700/60">
                  {isEn
                    ? decumbiture_and_cycles.climacteric_seven_year_law
                    : decumbiture_and_cycles.climacteric_seven_year_law_ta}
                </p>

                <h5 className="text-xs font-bold text-slate-200 pt-2">
                  {isEn ? "Lunar Phase Metabolic Shifts:" : "சந்திர பிறை வளர்சிதை மாற்ற சுழற்சிகள்:"}
                </h5>
                <div className="space-y-2">
                  {decumbiture_and_cycles.lunar_phases_metabolism.map((lp, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/40 text-xs flex items-start gap-2"
                    >
                      <span className="font-semibold text-indigo-300 shrink-0 w-28">
                        {lp.phase}:
                      </span>
                      <span className="text-slate-300 text-[11px]">
                        {lp.biological_mode} — {lp.therapeutic_rule}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 7: CHART-MATCHED RULES */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === "rules" && (
        <div className="space-y-6">
          {/* Rules Filter Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-900/80 border border-slate-800 rounded-xl p-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setRuleFilter("all")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  ruleFilter === "all"
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                {isEn ? "All Rules" : "அனைத்து விதிகள்"} ({matched_rules.length})
              </button>
              <button
                onClick={() => setRuleFilter("active")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  ruleFilter === "active"
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                {isEn ? "Qualifying in Radix" : "ஜாதகத்தில் பொருந்துபவை"} ({activeRulesCount})
              </button>
            </div>

            <div className="flex items-center gap-2">
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={isEn ? "Search rules or diseases..." : "விதிகள் அல்லது நோய்களைத் தேடுக..."}
                className="bg-transparent text-xs text-slate-200 placeholder-slate-500 focus:outline-none w-48"
              />
            </div>
          </div>

          {/* Rules List */}
          <div className="space-y-4">
            {displayedRules.map((rule) => {
              const isActive = rule.is_active;
              return (
                <div
                  key={rule.id}
                  className={`rounded-2xl border transition-all p-5 space-y-3 ${
                    isActive
                      ? "border-indigo-500/60 bg-slate-900/90 shadow-md shadow-indigo-950/40"
                      : "border-slate-800/80 bg-slate-900/40 opacity-75 hover:opacity-100"
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span
                          className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                            isActive ? "bg-emerald-400 animate-pulse" : "bg-slate-600"
                          }`}
                        />
                        <h4 className="text-base font-bold text-slate-100">
                          {isEn ? rule.name : (rule.name_tamil || rule.name)}
                        </h4>
                      </div>
                      <span className="text-xs text-indigo-300 block mt-0.5">
                        {rule.source} • {rule.chapter_verse}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 text-[10px] font-semibold border border-slate-700">
                        {rule.category}
                      </span>
                      <span
                        className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${
                          isActive
                            ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300"
                            : "bg-slate-800 border-slate-700 text-slate-400"
                        }`}
                      >
                        {isActive
                          ? isEn
                            ? "Qualifying in Chart"
                            : "ஜாதகத்தில் பொருந்தியது"
                          : isEn
                          ? "Not Satisfied"
                          : "பொருந்தவில்லை"}
                      </span>
                    </div>
                  </div>

                  {/* Triggered Placements */}
                  {rule.triggered_positions && rule.triggered_positions.length > 0 && (
                    <div className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-xs">
                      <span className="text-indigo-300 font-semibold block">
                        {isEn ? "Triggered Chart Configurations:" : "பொருந்திய ஜாதக அமைப்புகள்:"}
                      </span>
                      <p className="text-slate-200 mt-0.5 leading-relaxed">
                        {rule.triggered_positions.join("; ")}
                      </p>
                    </div>
                  )}

                  {/* Mandatory Conditions List */}
                  {rule.mandatory_conditions && rule.mandatory_conditions.length > 0 && (
                    <div className="text-xs space-y-1">
                      <span className="text-slate-400 font-medium block">
                        {isEn ? "Mandatory Conditions:" : "கட்டாய நிபந்தனைகள்:"}
                      </span>
                      <ul className="space-y-0.5 text-slate-300">
                        {rule.mandatory_conditions.map((mc, idx) => (
                          <li key={idx} className="flex items-start gap-1.5 text-[11px]">
                            <span className="text-indigo-400">•</span>
                            <span>{mc}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Traditional Interpretation */}
                  <div className="text-xs space-y-1 pt-1">
                    <span className="text-slate-400 font-medium block">
                      {isEn ? "Traditional Interpretation:" : "பாரம்பரிய விளக்கம்:"}
                    </span>
                    <p className="text-slate-200 text-xs leading-relaxed bg-slate-800/30 p-3 rounded-xl border border-slate-800">
                      {isEn
                        ? rule.traditional_interpretation
                        : rule.interpretation_tamil || rule.traditional_interpretation}
                    </p>
                  </div>

                  {/* Remedies */}
                  {(rule.remedy_en || rule.remedy_ta) && (
                    <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-xs space-y-1">
                      <span className="text-emerald-400 font-semibold flex items-center gap-1.5">
                        <Pill className="w-3.5 h-3.5" />
                        <span>{isEn ? "Antipathic Balancing & Classical Advice:" : "எதிர் சமநிலை & பரிகார ஆலோசனைகள்:"}</span>
                      </span>
                      <p className="text-emerald-200/90 text-xs leading-relaxed">
                        {isEn ? rule.remedy_en : rule.remedy_ta || rule.remedy_en}
                      </p>
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
