"use client";

import React, { useState, useMemo } from "react";
import {
  JaneRidderPatrickCompendium,
  JaneCellSaltCorrespondence,
  JaneBachFlowerCorrespondence,
  JaneAcupunctureMeridian,
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
} from "lucide-react";

interface JaneRidderPatrickSectionProps {
  compendium: JaneRidderPatrickCompendium;
  language: "en" | "ta";
  onSelectRule?: (rule: MedicalRule) => void;
}

export function JaneRidderPatrickSection({
  compendium,
  language,
  onSelectRule,
}: JaneRidderPatrickSectionProps) {
  const [activeTab, setActiveTab] = useState<
    "alphabet" | "decumbiture" | "crosses_elements" | "materia_medica" | "rules"
  >("alphabet");

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [materiaSubTab, setMateriaSubTab] = useState<"salts" | "bach" | "meridians">("salts");
  const [ruleFilter, setRuleFilter] = useState<"all" | "active">("all");

  const {
    book_title,
    book_title_ta,
    author,
    publisher,
    alphabet_framework = {},
    three_crosses = [],
    decumbiture,
    arabian_parts,
    elemental_analysis,
    culpeper_therapeutic_rules = [],
    stages_of_therapy = [],
    cell_salts = [],
    bach_flowers = [],
    acupuncture_meridians = [],
    matched_rules = [],
  } = compendium;

  const isEn = language === "en";

  // Active rules
  const activeRules = useMemo(() => {
    return matched_rules.filter((r) => r.is_active);
  }, [matched_rules]);

  const displayedRules = useMemo(() => {
    const list = ruleFilter === "active" ? activeRules : matched_rules;
    if (!searchQuery.trim()) return list;
    const q = searchQuery.toLowerCase();
    return list.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.name_tamil.toLowerCase().includes(q) ||
        r.traditional_interpretation.toLowerCase().includes(q) ||
        (r.remedy_en && r.remedy_en.toLowerCase().includes(q))
    );
  }, [ruleFilter, activeRules, matched_rules, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Author and Treatise Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-teal-950 via-slate-900 to-indigo-950 border border-teal-500/30 p-6 shadow-xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/20 border border-teal-500/40 text-teal-300 text-xs font-semibold tracking-wide">
              <BookOpen className="w-3.5 h-3.5" />
              <span>{isEn ? "Classical & Clinical Medical Astrology" : "பாரம்பரிய மற்றும் மருத்துவ ஜோதிட தொகுப்பு"}</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
              <span>{isEn ? book_title : book_title_ta}</span>
            </h2>
            <p className="text-sm text-teal-200/90 font-medium">
              {isEn
                ? `Author: ${author} • Publisher: ${publisher}`
                : `ஆசிரியர்: ${author} • பதிப்பகம்: ${publisher}`}
            </p>
            <p className="text-xs text-slate-400 max-w-3xl leading-relaxed">
              {isEn
                ? "Synthesizing classical Hermetic traditions, William Lilly's decumbiture doctrine, Nicholas Culpeper's therapeutic principles, Dr. Carey's 12 biochemic cell salts, and Peter Damian's 12 Bach flower correspondences with modern naturopathic medicine."
                : "வில்லியம் லில்லியின் நோய்படுக்கை ஜோதிடம், நிக்கோலஸ் கல்பேப்பரின் 7 மருத்துவ விதிகள், டாக்டர் கேரியின் 12 திசு உப்புகள், பீட்டர் டேமியனின் 12 மலர் தீர்வுகள் மற்றும் நவீன இயற்கை மருத்துவத்தின் தொகுப்பு."}
            </p>
          </div>

          <div className="flex flex-row md:flex-col items-start md:items-end gap-2 bg-slate-900/60 p-3 rounded-xl border border-teal-500/20 text-xs text-slate-300">
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <CheckCircle2 className="w-4 h-4" />
              <span>{activeRules.length} {isEn ? "Active Matched Rules" : "பொருந்திய விதிகள்"}</span>
            </div>
            <div className="text-slate-400">
              {matched_rules.length} {isEn ? "Total Treatise Rules Evaluated" : "மொத்த ஆய்வு விதிகள்"}
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mt-6 flex flex-wrap gap-2 border-t border-slate-800/80 pt-4">
          <button
            onClick={() => setActiveTab("alphabet")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "alphabet"
                ? "bg-teal-600 text-white shadow-lg shadow-teal-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{isEn ? "Astrological Alphabet & Therapy" : "ஜோதிட எழுத்துக்கள் & சிகிச்சை"}</span>
          </button>

          <button
            onClick={() => setActiveTab("decumbiture")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "decumbiture"
                ? "bg-teal-600 text-white shadow-lg shadow-teal-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>{isEn ? "Decumbiture & Arabian Parts" : "நோய்படுக்கை & அரேபிய புள்ளிகள்"}</span>
          </button>

          <button
            onClick={() => setActiveTab("crosses_elements")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "crosses_elements"
                ? "bg-teal-600 text-white shadow-lg shadow-teal-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>{isEn ? "3 Crosses & 4 Elements" : "3 சிலுவைகள் & 4 பூதங்கள்"}</span>
          </button>

          <button
            onClick={() => setActiveTab("materia_medica")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "materia_medica"
                ? "bg-teal-600 text-white shadow-lg shadow-teal-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Flower2 className="w-3.5 h-3.5" />
            <span>{isEn ? "Cell Salts, Bach & Meridians" : "திசு உப்புகள், மலர் & மெரிடியன்கள்"}</span>
          </button>

          <button
            onClick={() => setActiveTab("rules")}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 ${
              activeTab === "rules"
                ? "bg-teal-600 text-white shadow-lg shadow-teal-900/40"
                : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{isEn ? "Culpeper & Chart Rules" : "கல்பேப்பர் & ஜாதக விதிகள்"}</span>
            {activeRules.length > 0 && (
              <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-teal-400 text-slate-950 font-bold">
                {activeRules.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* TAB 1: Astrological Alphabet & Stages of Therapy */}
      {activeTab === "alphabet" && (
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
            <h3 className="text-base font-semibold text-teal-300 flex items-center gap-2 mb-3">
              <Layers className="w-4 h-4" />
              <span>{isEn ? "The Astrological Alphabet Framework" : "ஜோதிட எழுத்துக்களின் கட்டமைப்பு"}</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {isEn
                ? "Jane Ridder-Patrick presents astrology as a symbolic diagnostic language composed of five fundamental grammatical elements:"
                : "ஜேன் ரிடர்-பேட்ரிக் மருத்துவ ஜோதிடத்தை 5 அடிப்படை இலக்கணக் கூறுகளாக விளக்குகிறார்:"}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {Object.entries(alphabet_framework).map(([key, desc]) => (
                <div key={key} className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3.5">
                  <div className="text-xs font-bold text-teal-400 uppercase tracking-wider mb-1">
                    {key}
                  </div>
                  <div className="text-xs text-slate-300 leading-relaxed">
                    {desc}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 3 Stages of Astrological Therapy */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
            <h3 className="text-base font-semibold text-emerald-400 flex items-center gap-2 mb-3">
              <Award className="w-4 h-4" />
              <span>{isEn ? "Three Stages of Astrological Therapy" : "ஜோதிட சிகிச்சையின் மூன்று நிலைகள்"}</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {stages_of_therapy.map((s) => (
                <div key={s.stage} className="bg-slate-950/70 border border-emerald-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-xs flex items-center justify-center">
                      {s.stage}
                    </span>
                    <h4 className="text-sm font-semibold text-slate-200">
                      {isEn ? s.title_en : s.title_ta}
                    </h4>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {isEn ? s.description_en : s.description_ta}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Decumbiture Diagnostics & Arabian Parts */}
      {activeTab === "decumbiture" && (
        <div className="space-y-6">
          {/* Arabian Parts Panel */}
          {arabian_parts && (
            <div className="bg-slate-900/80 border border-indigo-500/30 rounded-xl p-5 shadow-lg">
              <h3 className="text-base font-semibold text-indigo-300 flex items-center gap-2 mb-3">
                <Compass className="w-4 h-4" />
                <span>{isEn ? "Classical Hermetic Arabian Parts for Native" : "ஜாதகருக்கான பாரம்பரிய அரேபிய புள்ளிகள்"}</span>
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                {isEn ? arabian_parts.clinical_notes_en : arabian_parts.clinical_notes_ta}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-950/80 border border-amber-500/30 rounded-xl p-4">
                  <div className="text-xs font-semibold text-amber-400 uppercase tracking-wide">
                    {isEn ? "Part of Sickness (Chronic Vulnerability)" : "நோய் புள்ளி (நாள்பட்ட பலவீனம்)"}
                  </div>
                  <div className="text-xl font-bold text-slate-100 mt-2">
                    {arabian_parts.part_of_sickness_coord}
                  </div>
                  <p className="text-xs text-slate-400 mt-2">
                    {isEn
                      ? "Calculated from Asc + Mars - Saturn (Day) or Asc + Saturn - Mars (Night). Represents congenital physiological weakness."
                      : "பகல் பிறப்பிற்கு லக்னம் + செவ்வாய் - சனி; இரவு பிறப்பிற்கு லக்னம் + சனி - செவ்வாய் என கணக்கிடப்படுகிறது."}
                  </p>
                </div>

                <div className="bg-slate-950/80 border border-red-500/30 rounded-xl p-4">
                  <div className="text-xs font-semibold text-red-400 uppercase tracking-wide">
                    {isEn ? "Part of Surgery (Surgical Trauma Point)" : "அறுவைசிகிச்சை புள்ளி"}
                  </div>
                  <div className="text-xl font-bold text-slate-100 mt-2">
                    {arabian_parts.part_of_surgery_coord}
                  </div>
                  <p className="text-xs text-slate-400 mt-2">
                    {isEn
                      ? "Asc + Saturn - Mars. Pinpoints anatomical points where surgical intervention or physical cutting requires maximum antiseptic caution."
                      : "லக்னம் + சனி - செவ்வாய். அறுவை சிகிச்சை அல்லது ஆக்கிரமிப்பு சிகிச்சைகளில் மிகுந்த எச்சரிக்கை தேவைப்படும் புள்ளி."}
                  </p>
                </div>

                <div className="bg-slate-950/80 border border-purple-500/30 rounded-xl p-4">
                  <div className="text-xs font-semibold text-purple-400 uppercase tracking-wide">
                    {isEn ? "Part of Death & Critical Endurance" : "நெருக்கடி & மரண புள்ளி"}
                  </div>
                  <div className="text-xl font-bold text-slate-100 mt-2">
                    {arabian_parts.part_of_death_coord}
                  </div>
                  <p className="text-xs text-slate-400 mt-2">
                    {isEn
                      ? "Asc + 240° - Moon. Marks the native's critical resistance limit and point of maximum constitutional stress."
                      : "லக்னம் + 240° - சந்திரன். ஜாதகரின் உச்சபட்ச உடலியல் தாங்குதிறன் மற்றும் நெருக்கடி அளவை குறிக்கிறது."}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Decumbiture Diagnostic Conditions */}
          {decumbiture && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
              <h3 className="text-base font-semibold text-teal-300 flex items-center gap-2 mb-3">
                <Clock className="w-4 h-4" />
                <span>{isEn ? "William Lilly Decumbiture & Horary Strictures" : "வில்லியம் லில்லியின் நோய்படுக்கை ஜோதிட விதிகள்"}</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs font-bold text-slate-300 mb-1">
                    {isEn ? "Ascendant Radicality Stricture" : "லக்ன ஆரம்ப/முடிவு நிலை"}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {decumbiture.asc_stricture_note}
                  </p>
                </div>

                <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs font-bold text-slate-300 mb-1">
                    {isEn ? "Moon in Via Combusta (15° Libra – 15° Scorpio)" : "எரிந்த பாதையில் சந்திரன் (துலாம் 15° – விருச்சிகம் 15°)"}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {decumbiture.moon_in_via_combusta
                      ? (isEn ? "Active: Moon is traversing Via Combusta. Severe metabolic fluctuation and unpredictable therapeutic response." : "செயலில் உள்ளது: சந்திரன் எரிந்த பாதையில் உள்ளது. மருந்துகளின் எதிர்வினை மாறக்கூடும்.")
                      : (isEn ? "Inactive: Moon is in a safe zodiacal degree." : "செயலில் இல்லை: சந்திரன் பாதுகாப்பான பாகையில் உள்ளது.")}
                  </p>
                </div>

                <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs font-bold text-slate-300 mb-1">
                    {isEn ? "Critical Days Lunar Cycle (Hippocratic Crisis)" : "இப்போக்கிரட்டீஸ் நெருக்கடி நாட்கள் (சந்திர சுழற்சி)"}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {isEn ? decumbiture.critical_days_cycle_en : decumbiture.critical_days_cycle_ta}
                  </p>
                </div>

                <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs font-bold text-slate-300 mb-1">
                    {isEn ? "Anatomical Sidedness Indicator" : "உடல் பக்கவாட்டு சமிக்ஞை (Sidedness)"}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {decumbiture.sidedness_indicator}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: 3 Crosses & 4 Elements */}
      {activeTab === "crosses_elements" && (
        <div className="space-y-6">
          {/* Elemental Analysis Panel */}
          {elemental_analysis && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
              <h3 className="text-base font-semibold text-amber-300 flex items-center gap-2 mb-3">
                <Flame className="w-4 h-4" />
                <span>{isEn ? "Elemental Balance & Constitutional Temperament" : "பூத சமநிலை மற்றும் உடலமைப்பு தன்மை"}</span>
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="bg-slate-950/70 border border-red-500/20 p-3 rounded-lg text-center">
                  <div className="text-xs text-slate-400">{isEn ? "Fire (Pitta / Bilious)" : "நெருப்பு (பித்தம்)"}</div>
                  <div className="text-xl font-bold text-red-400 mt-1">{elemental_analysis.fire_count}</div>
                </div>
                <div className="bg-slate-950/70 border border-amber-500/20 p-3 rounded-lg text-center">
                  <div className="text-xs text-slate-400">{isEn ? "Earth (Melancholic)" : "நிலம் (வாத/கப பிணைப்பு)"}</div>
                  <div className="text-xl font-bold text-amber-400 mt-1">{elemental_analysis.earth_count}</div>
                </div>
                <div className="bg-slate-950/70 border border-cyan-500/20 p-3 rounded-lg text-center">
                  <div className="text-xs text-slate-400">{isEn ? "Air (Vata / Sanguine)" : "காற்று (வாதம்)"}</div>
                  <div className="text-xl font-bold text-cyan-400 mt-1">{elemental_analysis.air_count}</div>
                </div>
                <div className="bg-slate-950/70 border border-blue-500/20 p-3 rounded-lg text-center">
                  <div className="text-xs text-slate-400">{isEn ? "Water (Kapha / Phlegmatic)" : "நீர் (கபம்)"}</div>
                  <div className="text-xl font-bold text-blue-400 mt-1">{elemental_analysis.water_count}</div>
                </div>
              </div>

              <div className="bg-slate-950/80 border border-amber-500/20 p-4 rounded-lg space-y-2">
                <div className="text-xs font-semibold text-amber-400">
                  {isEn
                    ? `Dominant Element: ${elemental_analysis.dominant_element} (Deficient: ${elemental_analysis.deficient_element})`
                    : `முதன்மை பூதம்: ${elemental_analysis.dominant_element} (குறைவு: ${elemental_analysis.deficient_element})`}
                </div>
                <div className="text-xs text-slate-300 leading-relaxed">
                  <strong className="text-teal-400">{isEn ? "Dietary Therapeutics: " : "உணவுமுறை சிகிச்சைகள்: "}</strong>
                  {isEn ? elemental_analysis.dietary_balancing_en : elemental_analysis.dietary_balancing_ta}
                </div>
                <div className="text-xs text-slate-400">
                  <strong className="text-slate-300">{isEn ? "Indicated Herbal Classes: " : "பரிந்துரைக்கப்படும் மூலிகைப் பிரிவுகள்: "}</strong>
                  {elemental_analysis.herbal_classes_indicated.join(", ")}
                </div>
              </div>
            </div>
          )}

          {/* Three Crosses Reflex Dynamics */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
            <h3 className="text-base font-semibold text-teal-300 flex items-center gap-2 mb-3">
              <Compass className="w-4 h-4" />
              <span>{isEn ? "The Three Crosses Reflex Dynamics" : "மூன்று சிலுவைகளின் பிரதிபலிப்பு இயக்கவியல்"}</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {three_crosses.map((c) => (
                <div key={c.cross} className="bg-slate-950/70 border border-teal-500/20 rounded-xl p-4 flex flex-col justify-between">
                  <div className="space-y-2">
                    <h4 className="text-sm font-bold text-slate-200">
                      {isEn ? c.cross : c.cross_ta}
                    </h4>
                    <p className="text-xs font-semibold text-teal-400">
                      {c.theme}
                    </p>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {c.reflex_dynamics}
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-800/80 text-xs text-slate-400">
                    <strong className="text-slate-300">{isEn ? "Therapeutic Focus: " : "சிகிச்சை மையம்: "}</strong>
                    {c.therapeutic_focus}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Materia Medica (Cell Salts, Bach, Meridians) */}
      {activeTab === "materia_medica" && (
        <div className="space-y-6">
          <div className="flex gap-2 border-b border-slate-800 pb-3">
            <button
              onClick={() => setMateriaSubTab("salts")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                materiaSubTab === "salts"
                  ? "bg-teal-500/20 border border-teal-500 text-teal-300 font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {isEn ? "12 Biochemic Cell Salts (Carey/Perry)" : "12 திசு உப்புகள் (கேரி/பெர்ரி)"}
            </button>
            <button
              onClick={() => setMateriaSubTab("bach")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                materiaSubTab === "bach"
                  ? "bg-teal-500/20 border border-teal-500 text-teal-300 font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {isEn ? "12 Bach Flower Remedies (Peter Damian)" : "12 பாச் மலர் தீர்வுகள் (டேமியன்)"}
            </button>
            <button
              onClick={() => setMateriaSubTab("meridians")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                materiaSubTab === "meridians"
                  ? "bg-teal-500/20 border border-teal-500 text-teal-300 font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {isEn ? "12 Acupuncture Meridians" : "12 அக்குபஞ்சர் மெரிடியன்கள்"}
            </button>
          </div>

          {/* Subtab: Cell Salts */}
          {materiaSubTab === "salts" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {cell_salts.map((cs) => (
                <div
                  key={cs.sign}
                  className={`p-4 rounded-xl border transition-all ${
                    cs.is_native_sign
                      ? "bg-teal-950/40 border-teal-500/60 shadow-lg shadow-teal-950/50"
                      : "bg-slate-900/60 border-slate-800"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-300">
                      {isEn ? cs.sign : cs.sign_ta}
                    </span>
                    {cs.is_native_sign && (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-teal-500/20 border border-teal-500/40 text-teal-300 font-bold">
                        {isEn ? "Native Sign" : "ஜாதக ராசி"}
                      </span>
                    )}
                  </div>
                  <div className="text-sm font-semibold text-teal-300">
                    {cs.cell_salt} ({cs.abbreviation})
                  </div>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    {isEn ? cs.physiological_action_en : cs.physiological_action_ta}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Subtab: Bach Flowers */}
          {materiaSubTab === "bach" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {bach_flowers.map((bf) => (
                <div
                  key={bf.sign}
                  className={`p-4 rounded-xl border transition-all ${
                    bf.is_native_sign
                      ? "bg-indigo-950/40 border-indigo-500/60 shadow-lg shadow-indigo-950/50"
                      : "bg-slate-900/60 border-slate-800"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-300">
                      {isEn ? bf.sign : bf.sign_ta}
                    </span>
                    {bf.is_native_sign && (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 font-bold">
                        {isEn ? "Native Sign" : "ஜாதக ராசி"}
                      </span>
                    )}
                  </div>
                  <div className="text-sm font-semibold text-indigo-300">
                    {bf.flower_remedy}
                  </div>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    {isEn ? bf.emotional_archetype_en : bf.emotional_archetype_ta}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Subtab: Meridians */}
          {materiaSubTab === "meridians" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {acupuncture_meridians.map((am) => (
                <div
                  key={am.sign}
                  className={`p-4 rounded-xl border transition-all ${
                    am.is_native_sign
                      ? "bg-emerald-950/40 border-emerald-500/60 shadow-lg shadow-emerald-950/50"
                      : "bg-slate-900/60 border-slate-800"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-300">
                      {isEn ? am.sign : am.sign_ta}
                    </span>
                    {am.is_native_sign && (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold">
                        {isEn ? "Native Ascendant" : "ஜாதக லக்னம்"}
                      </span>
                    )}
                  </div>
                  <div className="text-sm font-semibold text-emerald-300">
                    {isEn ? am.meridian : am.meridian_ta}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 5: Culpeper's 7 Rules & Chart Matched Rules */}
      {activeTab === "rules" && (
        <div className="space-y-6">
          {/* Culpeper's 7 Rules */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
            <h3 className="text-base font-semibold text-teal-300 flex items-center gap-2 mb-3">
              <Stethoscope className="w-4 h-4" />
              <span>{isEn ? "Nicholas Culpeper's 7 Foundational Principles" : "நிக்கோலஸ் கல்பேப்பரின் 7 அடிப்படைக் கோட்பாடுகள்"}</span>
            </h3>
            <div className="space-y-3">
              {culpeper_therapeutic_rules.map((cr) => (
                <div key={cr.rule_number} className="bg-slate-950/70 border border-slate-800/80 p-3.5 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-300 text-xs font-bold flex items-center justify-center">
                      {cr.rule_number}
                    </span>
                    <h4 className="text-xs font-bold text-slate-200">
                      {isEn ? cr.rule_en : cr.rule_ta}
                    </h4>
                  </div>
                  <p className="text-[11px] text-teal-300/80 pl-7 mt-1 font-medium">
                    {cr.application}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Chart-Matched Rules Registry */}
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-teal-400" />
                <span className="text-xs font-semibold text-slate-300">{isEn ? "Filter Rules:" : "வடிகட்டு:"}</span>
                <button
                  onClick={() => setRuleFilter("all")}
                  className={`px-2.5 py-1 rounded text-xs transition-all ${
                    ruleFilter === "all"
                      ? "bg-teal-600 text-white font-bold"
                      : "bg-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {isEn ? `All (${matched_rules.length})` : `அனைத்தும் (${matched_rules.length})`}
                </button>
                <button
                  onClick={() => setRuleFilter("active")}
                  className={`px-2.5 py-1 rounded text-xs transition-all ${
                    ruleFilter === "active"
                      ? "bg-teal-600 text-white font-bold"
                      : "bg-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {isEn ? `Matched to Chart (${activeRules.length})` : `ஜாதகத்தில் பொருந்துபவை (${activeRules.length})`}
                </button>
              </div>

              <div className="relative w-full sm:w-64">
                <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="text"
                  placeholder={isEn ? "Search rules..." : "விதியைத் தேடு..."}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {displayedRules.map((r) => (
                <div
                  key={r.id}
                  onClick={() => onSelectRule && onSelectRule(r)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    r.is_active
                      ? "bg-teal-950/30 border-teal-500/50 hover:border-teal-400 shadow-md"
                      : "bg-slate-900/40 border-slate-800/80 hover:border-slate-700 opacity-75"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                      {r.id}
                    </span>
                    {r.is_active ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>{isEn ? "Matched Native Chart" : "ஜாதகத்தில் பொருந்துகிறது"}</span>
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-500">
                        {isEn ? "Not triggered" : "தூண்டப்படவில்லை"}
                      </span>
                    )}
                  </div>

                  <h4 className="text-sm font-semibold text-slate-100 mb-2">
                    {isEn ? r.name : r.name_tamil}
                  </h4>

                  <p className="text-xs text-slate-300 leading-relaxed mb-3">
                    {isEn ? r.traditional_interpretation : r.interpretation_tamil}
                  </p>

                  {r.remedy_en && (
                    <div className="pt-2 border-t border-slate-800/80">
                      <div className="text-[11px] font-semibold text-teal-400 mb-1 flex items-center gap-1">
                        <Pill className="w-3 h-3" />
                        <span>{isEn ? "Classical Remedial Support:" : "பாரம்பரிய பரிகார முறை:"}</span>
                      </div>
                      <p className="text-xs text-teal-200/90 leading-relaxed">
                        {isEn ? r.remedy_en : r.remedy_ta}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
