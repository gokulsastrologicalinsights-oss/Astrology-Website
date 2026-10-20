"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/i18n";
import {
  analyzeNameNumerology,
  suggestNameCorrections,
  saveNumerologyReport,
} from "@/lib/api";
import {
  NameCorrectionResponse,
  NameCandidateResult,
  NameAnalysisResponse,
} from "@/lib/types";
import {
  Sparkles,
  FileText,
  Plus,
  Trash2,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Bookmark,
  Share2,
  Printer,
  Compass,
  ArrowRight,
  Sliders,
  Check,
  Award,
} from "lucide-react";

export function NameCorrectionStudio() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Inputs
  const [originalName, setOriginalName] = useState("Gokul");
  const [birthDate, setBirthDate] = useState("");
  const [systemConvention, setSystemConvention] = useState<"pythagorean" | "chaldean">("chaldean");
  const [reportLang, setReportLang] = useState<"en" | "ta">("en");
  const [targetNumber, setTargetNumber] = useState<number | "auto">("auto");
  const [customVariations, setCustomVariations] = useState<string[]>(["Gokhul"]);
  const [newCustomInput, setNewCustomInput] = useState("");

  // Toggles
  const [allowVowelChanges, setAllowVowelChanges] = useState(true);
  const [allowConsonantDoubling, setAllowConsonantDoubling] = useState(true);
  const [allowPhoneticReplacements, setAllowPhoneticReplacements] = useState(true);
  const [maxCandidates, setMaxCandidates] = useState(25);

  // Results & UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<NameCorrectionResponse | null>(null);
  const [expandedCandidate, setExpandedCandidate] = useState<string | null>(null);
  const [filterTargetOnly, setFilterTargetOnly] = useState(false);
  const [sortBy, setSortBy] = useState<"composite" | "harmony" | "pronunciation" | "expression">("composite");
  const [savedSuccessMsg, setSavedSuccessMsg] = useState<string | null>(null);
  const [savingReport, setSavingReport] = useState(false);
  const [showMethodology, setShowMethodology] = useState(false);

  // Auto-run once on mount for instant visual satisfaction
  useEffect(() => {
    handleRunStudio();
  }, []);

  const handleRunStudio = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!originalName.trim()) {
      setError("Please enter a valid original name.");
      return;
    }

    setLoading(true);
    setError(null);
    setSavedSuccessMsg(null);

    try {
      const response = await suggestNameCorrections({
        original_name: originalName.trim(),
        system_convention: systemConvention,
        target_number: targetNumber === "auto" ? undefined : targetNumber,
        birth_date: birthDate.trim() || undefined,
        custom_variations: customVariations.filter((v) => v.trim()),
        language: reportLang,
        max_candidates: maxCandidates,
        allow_vowel_changes: allowVowelChanges,
        allow_consonant_doubling: allowConsonantDoubling,
        allow_phonetic_replacements: allowPhoneticReplacements,
      });

      setResult(response);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to generate name suggestions.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddCustomVariation = () => {
    const clean = newCustomInput.trim();
    if (clean && !customVariations.includes(clean)) {
      setCustomVariations([...customVariations, clean]);
      setNewCustomInput("");
    }
  };

  const handleRemoveCustomVariation = (index: number) => {
    setCustomVariations(customVariations.filter((_, i) => i !== index));
  };

  const handleSaveToReports = async (candidate?: NameCandidateResult) => {
    if (!isAuthenticated || !session?.access_token) {
      setError("Please log in to save this name correction report to your account.");
      return;
    }
    if (!result) return;

    setSavingReport(true);
    setSavedSuccessMsg(null);

    try {
      const targetCand = candidate || result.candidates[0];
      await saveNumerologyReport(
        {
          person_name: `${result.original_name} -> ${targetCand.name}`,
          birth_date: birthDate || "2000-01-01",
          method: "name_correction",
          system_convention: result.system_convention,
          calculation_data: {
            original_analysis: result.original_analysis,
            selected_candidate: targetCand,
            target_number: result.target_number,
            target_source: result.target_source,
            all_candidates_summary: result.candidates.map((c) => ({
              name: c.name,
              expression: c.expression_number,
              composite_score: c.composite_score,
            })),
          },
          interpretation_data: {
            overall_synthesis: targetCand.vibrational_synthesis,
            harmony_score: targetCand.harmony_score,
            pronunciation_score: targetCand.pronunciation_score,
            simplicity_score: targetCand.simplicity_score,
            formula: result.scoring_explanation.formula,
          },
        },
        session.access_token
      );

      setSavedSuccessMsg(`Successfully saved "${targetCand.name}" reading to your Numerology Reports!`);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to save report.");
    } finally {
      setSavingReport(false);
    }
  };

  // Filtered & Sorted candidates
  const processedCandidates = (result?.candidates || [])
    .filter((c) => (filterTargetOnly ? c.matches_target : true))
    .sort((a, b) => {
      if (sortBy === "composite") return b.composite_score - a.composite_score;
      if (sortBy === "harmony") return b.harmony_score - a.harmony_score;
      if (sortBy === "pronunciation") return b.pronunciation_score - a.pronunciation_score;
      if (sortBy === "expression") return a.expression_number - b.expression_number;
      return 0;
    });

  return (
    <div className="space-y-8">
      {/* Studio Header Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A] text-white shadow-xl relative overflow-hidden border border-slate-800">
        <div className="absolute top-0 right-0 w-80 h-80 bg-[#B8860B]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#B8860B]/20 border border-[#B8860B]/30 text-[#EAB308] text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Name Tuning &amp; Vibrational Optimization Studio</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif font-bold tracking-tight text-white">
              {language === "ta" ? "பெயர் சீரமைப்பு மற்றும் மாற்று எழுத்து ஸ்டுடியோ" : "Name Suggestion & Correction Studio"}
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              Harmonize your name with your Life Path and Mulank vibrations. Generate deterministic spelling variations
              preserving natural phonetics while shifting letter weights under classical Pythagorean and Chaldean traditions.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              type="button"
              onClick={() => setShowMethodology(!showMethodology)}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-xs font-semibold text-slate-200 transition-colors cursor-pointer"
            >
              <HelpCircle className="w-4 h-4 text-[#B8860B]" />
              <span>{showMethodology ? "Hide Methodology" : "Scoring Methodology"}</span>
            </button>
          </div>
        </div>

        {/* Methodology Dropdown */}
        {showMethodology && (
          <div className="mt-6 pt-6 border-t border-slate-700/80 text-xs text-slate-300 grid grid-cols-1 md:grid-cols-3 gap-6 animate-fadeIn">
            <div className="space-y-1.5 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                <Compass className="w-3.5 h-3.5 text-[#B8860B]" />
                1. Numerological Harmony (50%)
              </span>
              <p className="text-[11px] text-slate-400">
                100 pts for exact target expression match. Evaluates ancient planetary friend/enemy relationships (e.g. Sun 1 &amp; Mars 9 friends; Sun 1 &amp; Saturn 8 incompatible).
              </p>
            </div>
            <div className="space-y-1.5 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                <Sliders className="w-3.5 h-3.5 text-blue-400" />
                2. Pronunciation Preservation (30%)
              </span>
              <p className="text-[11px] text-slate-400">
                Normalized Levenshtein edit distance combined with consonant skeleton matching. Geminate doubled consonants share place of articulation and score high.
              </p>
            </div>
            <div className="space-y-1.5 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                3. Spelling Simplicity (20%)
              </span>
              <p className="text-[11px] text-slate-400">
                Penalizes awkward triple-consonants (e.g. `LLL`), excessive length changes, or non-traditional Indic transliteration patterns.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Main Studio Controls Form */}
      <form onSubmit={handleRunStudio} className="p-6 sm:p-8 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Original Name Input */}
          <div className="sm:col-span-2">
            <label className="block text-xs font-bold text-[#102A4C] mb-1.5">
              Original Name / தற்போதைய பெயர் *
            </label>
            <input
              type="text"
              required
              value={originalName}
              onChange={(e) => setOriginalName(e.target.value)}
              placeholder="e.g. Gokul Murugan or கோகுல்"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] text-sm text-[#102A4C] font-semibold focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
            />
          </div>

          {/* Optional Birth Date */}
          <div>
            <label className="block text-xs font-bold text-[#102A4C] mb-1.5">
              Birth Date (Optional for Auto-Target)
            </label>
            <input
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] text-xs text-[#102A4C] focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
            />
          </div>

          {/* Numerology Tradition */}
          <div>
            <label className="block text-xs font-bold text-[#102A4C] mb-1.5">
              Calculation Tradition
            </label>
            <select
              value={systemConvention}
              onChange={(e) => setSystemConvention(e.target.value as any)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] text-xs text-[#102A4C] font-medium focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
            >
              <option value="chaldean">Chaldean (Ancient Cheiro 1-8)</option>
              <option value="pythagorean">Pythagorean (Western 1-9)</option>
            </select>
          </div>
        </div>

        {/* Second Row: Target Number & Rule Toggles */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-4 border-t border-[#F1F5F9]">
          {/* Target Number */}
          <div>
            <label className="block text-xs font-bold text-[#102A4C] mb-1.5">
              Target Expression Number
            </label>
            <select
              value={targetNumber}
              onChange={(e) =>
                setTargetNumber(e.target.value === "auto" ? "auto" : parseInt(e.target.value, 10))
              }
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] text-xs text-[#102A4C] focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
            >
              <option value="auto">Auto (Harmonize with Mulank / Life Path)</option>
              <option value="1">1 — Leadership &amp; Ambition (Sun)</option>
              <option value="2">2 — Diplomacy &amp; Harmony (Moon)</option>
              <option value="3">3 — Creative Expansion &amp; Wisdom (Jupiter)</option>
              <option value="4">4 — Methodical Order &amp; Focus (Rahu)</option>
              <option value="5">5 — Versatility &amp; Commercial Magnetism (Mercury)</option>
              <option value="6">6 — Nurturing, Luxury &amp; Family (Venus)</option>
              <option value="7">7 — Analytical &amp; Spiritual Intellect (Ketu)</option>
              <option value="8">8 — Authority &amp; Material Mastery (Saturn)</option>
              <option value="9">9 — Humanitarian Dynamism &amp; Courage (Mars)</option>
              <option value="11">11 — Master Intuition &amp; Illumination</option>
              <option value="22">22 — Master Architect of Global Projects</option>
              <option value="33">33 — Master Teacher of Compassion</option>
            </select>
          </div>

          {/* Candidate Generation Rules */}
          <div className="sm:col-span-2 space-y-2">
            <span className="block text-xs font-bold text-[#102A4C] mb-1">
              Active Correction Rules
            </span>
            <div className="flex flex-wrap gap-4 pt-1">
              <label className="inline-flex items-center gap-2 text-xs text-[#334155] cursor-pointer">
                <input
                  type="checkbox"
                  checked={allowConsonantDoubling}
                  onChange={(e) => setAllowConsonantDoubling(e.target.checked)}
                  className="rounded text-[#0F172A] focus:ring-[#B8860B]"
                />
                <span>Consonant Doubling (L &rarr; LL, R &rarr; RR)</span>
              </label>

              <label className="inline-flex items-center gap-2 text-xs text-[#334155] cursor-pointer">
                <input
                  type="checkbox"
                  checked={allowVowelChanges}
                  onChange={(e) => setAllowVowelChanges(e.target.checked)}
                  className="rounded text-[#0F172A] focus:ring-[#B8860B]"
                />
                <span>Vowel Tuning (EE &harr; I, OO &harr; U, A &harr; AA)</span>
              </label>

              <label className="inline-flex items-center gap-2 text-xs text-[#334155] cursor-pointer">
                <input
                  type="checkbox"
                  checked={allowPhoneticReplacements}
                  onChange={(e) => setAllowPhoneticReplacements(e.target.checked)}
                  className="rounded text-[#0F172A] focus:ring-[#B8860B]"
                />
                <span>Indic Transliteration (TH &harr; T, D &harr; DH)</span>
              </label>
            </div>
          </div>
        </div>

        {/* Custom Variations Row */}
        <div className="pt-4 border-t border-[#F1F5F9] space-y-3">
          <label className="block text-xs font-bold text-[#102A4C]">
            Custom User Spellings to Benchmark
          </label>
          <div className="flex flex-wrap gap-2 items-center">
            {customVariations.map((v, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[#FAF8F5] border border-[#CBD5E1] text-xs font-semibold text-[#0F172A]"
              >
                <span>{v}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveCustomVariation(idx)}
                  className="text-slate-400 hover:text-rose-600 transition-colors"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </span>
            ))}

            <div className="inline-flex items-center gap-1">
              <input
                type="text"
                value={newCustomInput}
                onChange={(e) => setNewCustomInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddCustomVariation();
                  }
                }}
                placeholder="Type spelling & press +"
                className="px-3 py-1 text-xs rounded-xl border border-[#CBD5E1] bg-white focus:outline-hidden focus:border-[#B8860B]"
              />
              <button
                type="button"
                onClick={handleAddCustomVariation}
                className="p-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Submit Button & Feedback */}
        <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-[#64748B]">
            {result ? (
              <span>
                Target: <strong className="text-[#0F172A]">Number {result.target_number}</strong> ({result.target_source})
              </span>
            ) : (
              <span>Ready to calculate and rank candidate spellings.</span>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-[#B8860B]" />
                <span>Generating &amp; Scoring Candidates...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-[#B8860B]" />
                <span>Analyze &amp; Tune Name</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-center gap-3 text-rose-700 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {savedSuccessMsg && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-3 text-emerald-800 text-xs">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
            <span>{savedSuccessMsg}</span>
          </div>
        )}
      </form>

      {/* Analysis & Results Display */}
      {result && (
        <div className="space-y-8 animate-fadeIn">
          {/* Baseline Analysis Section */}
          <div className="p-6 sm:p-8 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#F1F5F9]">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-[#94A3B8]">
                  Baseline Structural Profile
                </span>
                <h3 className="text-xl font-serif font-bold text-[#102A4C]">
                  {result.original_analysis.full_name}
                </h3>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs px-3 py-1 rounded-full bg-[#FAF8F5] border border-[#CBD5E1] text-[#64748B] font-semibold">
                  Convention: {result.system_convention.toUpperCase()}
                </span>
                <span className="text-xs px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 font-semibold">
                  Target: {result.target_number}
                </span>
              </div>
            </div>

            {/* Component Breakdown Cards (First, Middle, Surname, Initials) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {result.original_analysis.components.map((comp, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E2E8F0] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B]">
                      {comp.component_type}
                    </span>
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-white border border-[#CBD5E1] font-bold text-xs text-[#0F172A]">
                      {comp.expression}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-[#0F172A] truncate">
                    {comp.text || "—"}
                  </h4>
                  <div className="flex items-center justify-between text-[11px] text-[#64748B] pt-2 border-t border-[#E2E8F0]">
                    <span>Vowels (Soul): <strong className="text-[#0F172A]">{comp.soul_urge}</strong></span>
                    <span>Cons (Pers): <strong className="text-[#0F172A]">{comp.personality}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Candidate Variations Comparison Table */}
          <div className="p-6 sm:p-8 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-serif font-bold text-[#102A4C]">
                  Side-by-Side Spelling Candidates
                </h3>
                <p className="text-xs text-[#64748B]">
                  Evaluated across numerological harmony, pronunciation preservation, and simplicity.
                </p>
              </div>

              {/* Sorting & Filtering Controls */}
              <div className="flex flex-wrap items-center gap-3">
                <label className="inline-flex items-center gap-1.5 text-xs text-[#64748B] cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filterTargetOnly}
                    onChange={(e) => setFilterTargetOnly(e.target.checked)}
                    className="rounded text-[#0F172A]"
                  />
                  <span>Target Matches Only</span>
                </label>

                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-1.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-xs text-[#0F172A] font-medium"
                >
                  <option value="composite">Sort by: Overall Rank</option>
                  <option value="harmony">Sort by: Harmony Score</option>
                  <option value="pronunciation">Sort by: Pronunciation</option>
                  <option value="expression">Sort by: Expression Number</option>
                </select>
              </div>
            </div>

            {/* Candidates Table */}
            <div className="overflow-x-auto border border-[#E2E8F0] rounded-2xl">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-[#FAF8F5] text-[#52667E] border-b border-[#E2E8F0]">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Candidate Spelling</th>
                    <th className="py-3 px-3 font-semibold text-center">Expression</th>
                    <th className="py-3 px-3 font-semibold text-center">Soul / Pers</th>
                    <th className="py-3 px-3 font-semibold text-center">Harmony</th>
                    <th className="py-3 px-3 font-semibold text-center">Pronunciation</th>
                    <th className="py-3 px-3 font-semibold text-center">Overall Score</th>
                    <th className="py-3 px-4 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9]">
                  {processedCandidates.map((cand, idx) => {
                    const isExpanded = expandedCandidate === cand.name;
                    const isBaseline = cand.variation_type === "Original Baseline";

                    return (
                      <React.Fragment key={idx}>
                        <tr
                          className={`hover:bg-[#F8FAFC] transition-colors ${
                            cand.matches_target ? "bg-amber-50/40" : ""
                          }`}
                        >
                          {/* Name & Badge */}
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-sm text-[#0F172A] font-serif">
                                {cand.name}
                              </span>
                              {cand.matches_target && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300 text-[10px] font-bold">
                                  <Award className="w-3 h-3 text-amber-700" />
                                  <span>Target Match</span>
                                </span>
                              )}
                              {cand.is_master && (
                                <span className="px-1.5 py-0.5 rounded bg-purple-100 text-purple-800 text-[9px] font-bold">
                                  Master
                                </span>
                              )}
                              {isBaseline && (
                                <span className="px-1.5 py-0.5 rounded bg-slate-200 text-slate-700 text-[9px] font-bold">
                                  Baseline
                                </span>
                              )}
                            </div>
                            <span className="text-[10px] text-[#64748B] block mt-0.5">
                              {cand.variation_type}
                            </span>
                          </td>

                          {/* Expression */}
                          <td className="py-3 px-3 text-center">
                            <span
                              className={`inline-flex items-center justify-center w-8 h-8 rounded-xl font-bold text-xs ${
                                cand.matches_target
                                  ? "bg-[#0F172A] text-white shadow-xs"
                                  : "bg-[#FAF8F5] border border-[#CBD5E1] text-[#0F172A]"
                              }`}
                            >
                              {cand.expression_number}
                            </span>
                            <span className="block text-[9px] text-[#94A3B8] mt-0.5 font-mono">
                              ({cand.compound_expression})
                            </span>
                          </td>

                          {/* Soul Urge & Personality */}
                          <td className="py-3 px-3 text-center font-mono text-[11px] text-[#64748B]">
                            {cand.soul_urge_number} / {cand.personality_number}
                          </td>

                          {/* Harmony */}
                          <td className="py-3 px-3 text-center">
                            <span
                              className={`font-semibold text-xs ${
                                cand.harmony_score >= 90
                                  ? "text-emerald-700"
                                  : cand.harmony_score >= 60
                                  ? "text-blue-700"
                                  : "text-rose-700"
                              }`}
                            >
                              {cand.harmony_score}%
                            </span>
                          </td>

                          {/* Pronunciation */}
                          <td className="py-3 px-3 text-center">
                            <span className="font-semibold text-xs text-[#0F172A]">
                              {cand.pronunciation_score}%
                            </span>
                          </td>

                          {/* Overall Score */}
                          <td className="py-3 px-3 text-center">
                            <div className="flex flex-col items-center gap-1">
                              <span className="font-bold text-xs text-[#0F172A]">
                                {cand.composite_score}
                              </span>
                              <div className="w-16 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${
                                    cand.composite_score >= 80
                                      ? "bg-emerald-500"
                                      : cand.composite_score >= 60
                                      ? "bg-blue-500"
                                      : "bg-amber-500"
                                  }`}
                                  style={{ width: `${cand.composite_score}%` }}
                                />
                              </div>
                            </div>
                          </td>

                          {/* Actions */}
                          <td className="py-3 px-4 text-right">
                            <div className="flex items-center justify-end gap-2">
                              <button
                                type="button"
                                onClick={() =>
                                  setExpandedCandidate(isExpanded ? null : cand.name)
                                }
                                className="p-1.5 rounded-lg border border-[#CBD5E1] hover:bg-slate-100 text-slate-700 transition-colors"
                                title="Calculation Details"
                              >
                                {isExpanded ? (
                                  <ChevronUp className="w-3.5 h-3.5" />
                                ) : (
                                  <ChevronDown className="w-3.5 h-3.5" />
                                )}
                              </button>

                              <button
                                type="button"
                                onClick={() => handleSaveToReports(cand)}
                                disabled={savingReport}
                                className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[#FAF8F5] hover:bg-slate-100 border border-[#CBD5E1] text-[11px] font-semibold text-[#0F172A] transition-colors"
                                title="Save to Reports"
                              >
                                <Bookmark className="w-3 h-3 text-[#B8860B]" />
                                <span>Save</span>
                              </button>
                            </div>
                          </td>
                        </tr>

                        {/* Expandable Calculation Breakdown */}
                        {isExpanded && (
                          <tr className="bg-slate-50/70 border-b border-[#E2E8F0]">
                            <td colSpan={7} className="p-4 sm:p-6 space-y-4">
                              <div className="space-y-1">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B]">
                                  Vibrational Synthesis &amp; Reduction Trail
                                </span>
                                <p className="text-xs text-[#0F172A] font-medium leading-relaxed">
                                  {cand.vibrational_synthesis}
                                </p>
                              </div>

                              {/* Letter Mapping Badges */}
                              <div className="space-y-1.5">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B]">
                                  Letter-by-Letter Sound Values ({result.system_convention.toUpperCase()})
                                </span>
                                <div className="flex flex-wrap gap-1.5 pt-1">
                                  {cand.letter_mappings.map((m, mIdx) => (
                                    <div
                                      key={mIdx}
                                      className={`flex flex-col items-center justify-center w-8 h-10 rounded-lg border ${
                                        m.is_vowel
                                          ? "bg-amber-50 border-amber-200 text-amber-900"
                                          : "bg-white border-slate-200 text-slate-800"
                                      }`}
                                    >
                                      <span className="text-xs font-bold leading-none">{m.char}</span>
                                      <span className="text-[10px] font-mono text-[#64748B] mt-1">{m.value}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>

                              {/* Reduction Steps */}
                              <div className="text-xs text-[#64748B]">
                                <strong>Reduction Steps:</strong>{" "}
                                <span className="font-mono text-[#0F172A]">
                                  {cand.reduction_steps.join(" \u2192 ") || cand.compound_expression}
                                </span>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
