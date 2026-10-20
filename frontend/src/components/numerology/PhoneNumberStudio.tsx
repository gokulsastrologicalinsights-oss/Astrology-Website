"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/i18n";
import { analyzePhoneNumerology, saveNumerologyReport } from "@/lib/api";
import {
  PhoneNumerologyResponse,
  PhoneCandidateResult,
} from "@/lib/types";
import {
  Phone,
  Smartphone,
  Hash,
  Sparkles,
  Building2,
  User,
  Plus,
  Trash2,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Bookmark,
  Scale,
  Award,
  Layers,
  ShieldCheck,
  Zap,
  Flame,
  BarChart3,
  Sliders,
} from "lucide-react";

const INDUSTRY_OPTIONS = [
  { value: "technology", labelEn: "Technology & Software", labelTa: "தொழில்நுட்பம் & மென்பொருள்", ruler: "Mercury & Uranus", numbers: "5, 1" },
  { value: "retail", labelEn: "Retail & E-Commerce", labelTa: "சில்லறை வணிகம் & இணைய அங்காடி", ruler: "Mercury & Venus", numbers: "5, 6" },
  { value: "education", labelEn: "Education & Coaching", labelTa: "கல்வி & பயிற்சி", ruler: "Jupiter & Mercury", numbers: "3, 5" },
  { value: "healthcare", labelEn: "Healthcare & Pharmaceuticals", labelTa: "மருத்துவம் & நல்வாழ்வு", ruler: "Moon & Jupiter", numbers: "2, 7" },
  { value: "finance", labelEn: "Banking & Financial Services", labelTa: "வங்கி & நிதிச் சேவைகள்", ruler: "Saturn & Mercury", numbers: "4, 8" },
  { value: "manufacturing", labelEn: "Manufacturing & Heavy Industry", labelTa: "உற்பத்தி & கனரகத் தொழில்", ruler: "Mars & Saturn", numbers: "9, 8" },
  { value: "astrology", labelEn: "Astrology & Esoteric Services", labelTa: "ஜோதிடம் & ஆன்மீக சேவைகள்", ruler: "Ketu & Jupiter", numbers: "7, 9" },
  { value: "creative", labelEn: "Creative, Media & Entertainment", labelTa: "படைப்பாற்றல், ஊடகம் & கலை", ruler: "Venus & Sun", numbers: "3, 6" },
  { value: "other", labelEn: "General & Diversified Business", labelTa: "பொது & இதர வர்த்தகம்", ruler: "Sun", numbers: "1, 3" },
] as const;

export function PhoneNumberStudio() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Primary Inputs
  const [phoneNumber, setPhoneNumber] = useState("+91 98765 43210");
  const [systemConvention, setSystemConvention] = useState<"pythagorean" | "chaldean">("chaldean");
  const [includeCountryCode, setIncludeCountryCode] = useState(false);
  const [birthDate, setBirthDate] = useState("1994-06-15");
  const [industryCategory, setIndustryCategory] = useState<string>("technology");
  const [reportLang, setReportLang] = useState<"en" | "ta">("en");

  // Candidate Numbers
  const [candidateNumbers, setCandidateNumbers] = useState<string[]>([
    "98401 23456",
    "99999 88888",
    "+91 98765 43211",
  ]);
  const [newCandidateInput, setNewCandidateInput] = useState("");

  // Results & UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PhoneNumerologyResponse | null>(null);
  const [expandedCandidate, setExpandedCandidate] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<"composite" | "personal" | "vanity" | "root">("composite");
  const [savedSuccessMsg, setSavedSuccessMsg] = useState<string | null>(null);
  const [savingReport, setSavingReport] = useState(false);
  const [showMethodology, setShowMethodology] = useState(false);

  // Auto-run on mount for instant visual feedback
  useEffect(() => {
    handleRunStudio();
  }, []);

  const handleRunStudio = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!phoneNumber.trim()) {
      setError(language === "ta" ? "தொலைபேசி எண்ணை உள்ளிடுக." : "Please enter a valid phone number.");
      return;
    }

    setLoading(true);
    setError(null);
    setSavedSuccessMsg(null);

    try {
      const response = await analyzePhoneNumerology({
        phone_number: phoneNumber.trim(),
        system_convention: systemConvention,
        include_country_code: includeCountryCode,
        birth_date: birthDate.trim() || undefined,
        industry_category: (industryCategory as any) || undefined,
        candidate_numbers: candidateNumbers.filter((c) => c.trim()),
        language: reportLang,
      });

      setResult(response);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to analyze phone number.");
    } finally {
      setLoading(false);
    }
  };

  // Candidate management
  const addCandidate = () => {
    if (newCandidateInput.trim() && !candidateNumbers.includes(newCandidateInput.trim())) {
      setCandidateNumbers([...candidateNumbers, newCandidateInput.trim()]);
      setNewCandidateInput("");
    }
  };

  const removeCandidate = (cand: string) => {
    setCandidateNumbers(candidateNumbers.filter((c) => c !== cand));
  };

  // Save report
  const handleSaveReport = async () => {
    if (!result) return;
    if (!isAuthenticated || !session?.access_token) {
      setError("Please sign in to save phone numerology reports.");
      return;
    }

    setSavingReport(true);
    setSavedSuccessMsg(null);

    try {
      await saveNumerologyReport(
        {
          person_name: `Phone: ${result.formatted_national}`,
          birth_date: birthDate.trim() || "2000-01-01",
          system_convention: result.system_convention,
          method: "phone",
          calculation_data: result,
          interpretation_data: {
            title: `Phone Numerology: ${result.formatted_national}`,
            masked_phone: result.masked_phone,
            root_number: result.primary_analysis.root_number,
            compound_sum: result.primary_analysis.compound_sum,
            vanity_score: result.primary_analysis.patterns.vanity_score,
            personal_resonance: result.personal_compatibility?.level || "Not Evaluated",
            disclaimer: result.scoring_explanation.disclaimer,
          },
        },
        session.access_token
      );
      setSavedSuccessMsg("Phone numerology reading saved successfully to your profile!");
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to save phone report.");
    } finally {
      setSavingReport(false);
    }
  };

  // Candidate sorting
  const sortedCandidates = result
    ? [...result.candidates].sort((a, b) => {
        if (sortBy === "composite") return b.composite_score - a.composite_score;
        if (sortBy === "personal") return (b.personal_score || 0) - (a.personal_score || 0);
        if (sortBy === "vanity") return b.vanity_score - a.vanity_score;
        if (sortBy === "root") return a.root_number - b.root_number;
        return 0;
      })
    : [];

  return (
    <div className="space-y-8">
      {/* 1. Header Banner */}
      <div className="rounded-2xl p-6 sm:p-8 bg-gradient-to-br from-[#0F1E36] via-[#102A4C] to-[#1E3A8A] text-white shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-[#3478F6]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#3478F6]/20 border border-[#3478F6]/30 text-[#93C5FD] text-xs font-bold uppercase tracking-wider">
            <Smartphone className="w-3.5 h-3.5" />
            <span>Mobile & Contact Number Vibration Engine</span>
          </div>

          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight">
            {language === "ta"
              ? "தொலைபேசி & மொபைல் எண் கணித அரங்கம்"
              : "Phone & Mobile Number Numerology Studio"}
          </h1>

          <p className="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
            {language === "ta"
              ? "உங்கள் கைபேசி எண்ணின் கூட்டுத்தொகை, ஆளும் கிரகம், விடுபட்ட எண்கள், மற்றும் பிறந்த தேதியுடனான இணக்கத்தை துல்லியமாக ஆராயுங்கள்."
              : "Analyze SIM card and business hotline vibrations, discover missing digits and zero amplification, evaluate memorability / VIP vanity patterns, and test compatibility with your birth date and industry sector."}
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2 text-xs text-slate-300">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>National vs International Mode</span>
            </div>
            <div className="flex items-center gap-1.5">
              <BarChart3 className="w-4 h-4 text-sky-400" />
              <span>0–9 Digit Frequency Distribution</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Flame className="w-4 h-4 text-amber-400" />
              <span>VIP Vanity & Rhythm Scoring</span>
            </div>
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-purple-400" />
              <span>Privacy-Safe Masked Logging</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Interactive Input Form */}
      <div className="bg-white rounded-2xl border border-[#DDE5F0] p-6 shadow-xs space-y-6">
        <form onSubmit={handleRunStudio} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Phone Number Input */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C] flex items-center justify-between">
                <span>{language === "ta" ? "முக்கிய தொலைபேசி எண் *" : "Primary Phone Number *"}</span>
                {result && result.detected_country_name && (
                  <span className="text-[10px] font-semibold text-[#3478F6] bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
                    {result.detected_country_name} (+{result.detected_country_code})
                  </span>
                )}
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="e.g. +91 98765 43210 or 9876543210"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#CBD5E1] text-sm font-mono font-medium text-[#0F172A] focus:outline-hidden focus:ring-2 focus:ring-[#3478F6]"
                  required
                />
                <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              </div>
              <p className="text-[11px] text-[#64748B]">
                Supports Indian 10-digit mobiles, domestic trunk prefixes (0), and international formats (+91, +1, +44, +65, etc.).
              </p>
            </div>

            {/* Calculation Mode Toggle: National vs International */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C]">
                {language === "ta" ? "கணித அடிப்படை முறை" : "Calculation Dialing Basis"}
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setIncludeCountryCode(false)}
                  className={`px-3 py-2.5 rounded-xl text-xs font-bold border transition-all cursor-pointer text-left ${
                    !includeCountryCode
                      ? "bg-[#102A4C] text-white border-[#102A4C] shadow-xs"
                      : "bg-[#F8FAFC] text-[#52667E] border-[#E2E8F0] hover:bg-[#F1F5F9]"
                  }`}
                >
                  <div className="font-bold">National Digits (Standard)</div>
                  <div className={`text-[10px] ${!includeCountryCode ? "text-slate-300" : "text-slate-400"}`}>
                    Excludes network routing codes
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setIncludeCountryCode(true)}
                  className={`px-3 py-2.5 rounded-xl text-xs font-bold border transition-all cursor-pointer text-left ${
                    includeCountryCode
                      ? "bg-[#102A4C] text-white border-[#102A4C] shadow-xs"
                      : "bg-[#F8FAFC] text-[#52667E] border-[#E2E8F0] hover:bg-[#F1F5F9]"
                  }`}
                >
                  <div className="font-bold">Full with Country Code</div>
                  <div className={`text-[10px] ${includeCountryCode ? "text-slate-300" : "text-slate-400"}`}>
                    Includes international prefix
                  </div>
                </button>
              </div>
            </div>
          </div>

          {/* Profile Resonances: Owner Birth Date & Business Sector */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-2 border-t border-[#E2E8F0]">
            {/* Owner Birth Date */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C] flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-[#3478F6]" />
                <span>{language === "ta" ? "பிறந்த தேதி (தனிநபர் இணக்கம்)" : "Owner Birth Date (Personal Match)"}</span>
              </label>
              <input
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] text-xs font-medium text-[#0F172A] bg-white focus:outline-hidden focus:ring-2 focus:ring-[#3478F6]"
              />
              <p className="text-[10px] text-[#64748B]">
                Compares phone root against Psychic (Day) and Life Path numbers.
              </p>
            </div>

            {/* Business Sector */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C] flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5 text-[#3478F6]" />
                <span>{language === "ta" ? "தொழில்துறை (வணிக இணக்கம்)" : "Business Sector (Commercial Fit)"}</span>
              </label>
              <select
                value={industryCategory}
                onChange={(e) => setIndustryCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] text-xs font-medium text-[#0F172A] bg-white focus:outline-hidden focus:ring-2 focus:ring-[#3478F6]"
              >
                <option value="">-- None (Personal Only) --</option>
                {INDUSTRY_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {language === "ta" ? opt.labelTa : opt.labelEn}
                  </option>
                ))}
              </select>
              <p className="text-[10px] text-[#64748B]">
                Matches sales, banking, and customer service planetary rulers.
              </p>
            </div>

            {/* Numerology Tradition */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C]">
                {language === "ta" ? "கணித மரபு" : "Numerology Tradition"}
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setSystemConvention("chaldean")}
                  className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                    systemConvention === "chaldean"
                      ? "bg-[#102A4C] text-white border-[#102A4C] shadow-xs"
                      : "bg-[#F8FAFC] text-[#52667E] border-[#E2E8F0] hover:bg-[#F1F5F9]"
                  }`}
                >
                  Chaldean
                </button>
                <button
                  type="button"
                  onClick={() => setSystemConvention("pythagorean")}
                  className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                    systemConvention === "pythagorean"
                      ? "bg-[#102A4C] text-white border-[#102A4C] shadow-xs"
                      : "bg-[#F8FAFC] text-[#52667E] border-[#E2E8F0] hover:bg-[#F1F5F9]"
                  }`}
                >
                  Pythagorean
                </button>
              </div>
            </div>
          </div>

          {/* Alternative Candidate Numbers (e.g. for choosing new SIM / VIP number) */}
          <div className="pt-4 border-t border-[#E2E8F0] space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C]">
              {language === "ta"
                ? "ஒப்பீட்டுக்கான பிற எண்கள் (Candidate Numbers to Compare)"
                : "Candidate Numbers to Compare (e.g. SIM Selection / VIP Options)"}
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={newCandidateInput}
                onChange={(e) => setNewCandidateInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addCandidate();
                  }
                }}
                placeholder="e.g. 98401 99999 or +91 98402 12345"
                className="flex-1 px-4 py-2 rounded-xl border border-[#CBD5E1] text-xs font-mono font-medium text-[#0F172A]"
              />
              <button
                type="button"
                onClick={addCandidate}
                className="px-4 py-2 rounded-xl text-xs font-bold text-[#102A4C] bg-[#F1F5F9] border border-[#CBD5E1] hover:bg-[#E2E8F0] transition-colors cursor-pointer"
              >
                Add Candidate
              </button>
            </div>

            {candidateNumbers.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-1">
                {candidateNumbers.map((cand, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-[#EFF6FF] text-[#1E40AF] border border-[#BFDBFE]"
                  >
                    <span>{cand}</span>
                    <button
                      type="button"
                      onClick={() => removeCandidate(cand)}
                      className="hover:text-rose-500 text-slate-400 transition-colors cursor-pointer"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Submit Action */}
          <div className="pt-4 border-t border-[#E2E8F0] flex flex-col sm:flex-row items-center justify-between gap-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-sm text-white bg-[#102A4C] hover:bg-[#1A365D] transition-all shadow-md cursor-pointer disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Auditing Phone Vibrations...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span>Analyze & Rank Phone Numbers</span>
                </>
              )}
            </button>

            {result && isAuthenticated && (
              <button
                type="button"
                onClick={handleSaveReport}
                disabled={savingReport}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-[#102A4C] bg-[#EFF6FF] border border-[#BFDBFE] hover:bg-[#DBEAFE] transition-colors cursor-pointer disabled:opacity-50"
              >
                <Bookmark className="w-3.5 h-3.5 text-[#3478F6]" />
                <span>{savingReport ? "Saving Report..." : "Save Phone Reading"}</span>
              </button>
            )}
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {savedSuccessMsg && (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{savedSuccessMsg}</span>
            </div>
          )}
        </form>
      </div>

      {/* 3. Results Display */}
      {result && (
        <div className="space-y-8">
          {/* Dual Calculation Cards: National Subscriber vs International */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Primary Selected Baseline Card */}
            <div className="bg-gradient-to-br from-[#F8FAFC] to-[#EFF6FF] rounded-2xl border border-[#BFDBFE] p-5 shadow-xs space-y-3 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#3478F6]/10 text-[#3478F6] border border-[#BFDBFE]">
                  Active Vibration Baseline
                </span>
                {result.primary_analysis.is_master && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                    Master {result.primary_analysis.root_number}
                  </span>
                )}
              </div>

              <div>
                <h4 className="font-mono text-xl font-bold text-[#102A4C]">
                  {includeCountryCode ? result.display_international : result.formatted_national}
                </h4>
                <p className="text-[11px] text-[#3478F6] font-medium">
                  Basis: {result.scoring_explanation.selected_basis}
                </p>
              </div>

              <div className="flex items-baseline gap-3 pt-2">
                <div className="text-4xl font-serif font-black text-[#3478F6]">
                  {result.primary_analysis.root_number}
                </div>
                <div className="text-xs text-[#64748B]">
                  <span className="font-bold text-[#102A4C]">Compound Sum: {result.primary_analysis.compound_sum}</span>
                  <p className="text-[10px] font-semibold text-[#3478F6]">
                    Ruler: {result.primary_analysis.ruling_planet}
                  </p>
                </div>
              </div>

              <p className="text-xs text-[#52667E] leading-relaxed">
                {result.primary_analysis.vibrational_meaning}
              </p>
            </div>

            {/* Rhythm, Patterns & VIP Vanity Score Card */}
            <div className="bg-white rounded-2xl border border-[#DDE5F0] p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1">
                  <Flame className="w-3 h-3 text-amber-500" />
                  <span>Rhythm & Vanity Score</span>
                </span>
                <span className="text-xs font-mono font-bold text-amber-600">
                  {result.primary_analysis.patterns.vanity_score} / 100
                </span>
              </div>

              <div>
                <h4 className="font-serif text-base font-bold text-[#102A4C]">
                  {result.primary_analysis.patterns.is_vip_vanity ? "VIP Vanity Number Pattern" : "Standard Dialing Rhythm"}
                </h4>
                <p className="text-[11px] text-[#64748B]">
                  Measures auditory memorability, symmetry, and rapid dialability.
                </p>
              </div>

              <div className="pt-1 space-y-1.5 text-xs">
                {result.primary_analysis.patterns.repeats.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {result.primary_analysis.patterns.repeats.map((r, idx) => (
                      <span key={idx} className="font-mono text-[11px] font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200">
                        {r.pattern} ({r.label})
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-[11px] text-slate-500 italic">No repeated doublets/triplets detected.</p>
                )}

                {result.primary_analysis.patterns.sequences.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {result.primary_analysis.patterns.sequences.map((s, idx) => (
                      <span key={idx} className="font-mono text-[11px] px-2 py-0.5 rounded bg-blue-50 text-blue-900 border border-blue-200">
                        Run: {s.sequence} ({s.type})
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Reduction Steps & Calculation Breakdown */}
            <div className="bg-white rounded-2xl border border-[#DDE5F0] p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                  Reduction Chain
                </span>
                <span className="text-xs font-mono text-slate-500">
                  {result.primary_analysis.digit_count} Digits
                </span>
              </div>

              <div>
                <h4 className="font-serif text-base font-bold text-[#102A4C]">
                  Compound to Root Process
                </h4>
                <p className="text-[11px] text-[#64748B]">
                  Convention: {result.system_convention.toUpperCase()}
                </p>
              </div>

              <div className="space-y-1 pt-1">
                {result.primary_analysis.reduction_steps.map((step, idx) => (
                  <div key={idx} className="font-mono text-[11px] bg-slate-50 px-2.5 py-1 rounded border border-slate-200 text-slate-700">
                    {step}
                  </div>
                ))}
              </div>

              <p className="text-[11px] text-[#64748B] italic">
                Keyword: <strong>{result.primary_analysis.keyword}</strong>
              </p>
            </div>
          </div>

          {/* Digit Frequency Visualizer (0–9 Bar Grid) */}
          <div className="bg-white rounded-2xl border border-[#DDE5F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#102A4C] flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-[#3478F6]" />
                <span>Digit Frequency Distribution (0–9)</span>
              </h4>
              <span className="text-xs text-[#64748B]">
                Dominant: {result.primary_analysis.dominant_digits.length > 0 ? result.primary_analysis.dominant_digits.join(", ") : "Balanced"}
              </span>
            </div>

            <div className="grid grid-cols-5 sm:grid-cols-10 gap-3">
              {Array.from({ length: 10 }).map((_, i) => {
                const count = result.primary_analysis.frequencies[String(i)] || 0;
                const isDominant = result.primary_analysis.dominant_digits.includes(i);
                const isZero = i === 0;

                return (
                  <div
                    key={i}
                    className={`flex flex-col items-center p-3 rounded-xl border text-center transition-all ${
                      count > 0
                        ? isDominant
                          ? "bg-blue-50 border-[#3478F6] text-[#102A4C] shadow-2xs"
                          : "bg-[#F8FAFC] border-[#E2E8F0] text-[#102A4C]"
                        : "bg-slate-50/50 border-slate-200 text-slate-400 opacity-60"
                    }`}
                  >
                    <span className="font-mono text-lg font-bold">{i}</span>
                    <span className="text-xs font-mono font-semibold text-[#3478F6]">
                      {count}×
                    </span>
                    <span className="text-[9px] uppercase tracking-tighter text-slate-400 mt-1">
                      {isZero ? "Cipher" : `Planet ${i}`}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Missing Digits & Zero Significance Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-[#F1F5F9]">
              <div className="space-y-1.5">
                <h5 className="text-[11px] font-bold uppercase tracking-wider text-[#102A4C]">
                  Missing Vibrations (1–9)
                </h5>
                {result.missing_digits_analysis.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {result.missing_digits_analysis.map((item, idx) => (
                      <span
                        key={idx}
                        title={item.lesson}
                        className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-rose-50 text-rose-700 border border-rose-200 cursor-help"
                      >
                        Missing {item.digit}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-emerald-600 font-medium">
                    All numbers 1–9 are represented! Excellent holographic distribution.
                  </p>
                )}
              </div>

              <div className="space-y-1.5">
                <h5 className="text-[11px] font-bold uppercase tracking-wider text-[#102A4C]">
                  Zero (0) Catalyst Analysis
                </h5>
                <p className="text-xs text-[#52667E] leading-relaxed">
                  {result.zero_significance}
                </p>
              </div>
            </div>
          </div>

          {/* Profile Compatibility Cards (Personal DOB & Business Industry) */}
          {(result.personal_compatibility || result.industry_compatibility) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {result.personal_compatibility && (
                <div className="bg-white rounded-2xl border border-[#DDE5F0] p-5 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1">
                      <User className="w-3 h-3" />
                      <span>Owner Personal Match</span>
                    </span>
                    <span className={`text-xs font-bold ${
                      result.personal_compatibility.personal_score >= 80 ? "text-emerald-600" :
                      result.personal_compatibility.personal_score >= 60 ? "text-blue-600" : "text-amber-600"
                    }`}>
                      {result.personal_compatibility.personal_score}% ({result.personal_compatibility.level})
                    </span>
                  </div>

                  <div>
                    <h5 className="text-sm font-bold text-[#102A4C]">
                      Resonance with DOB {result.personal_compatibility.birth_date}
                    </h5>
                    <p className="text-xs text-[#64748B] pt-0.5">
                      Psychic/Day: <span className="font-mono font-bold text-[#3478F6]">{result.personal_compatibility.psychic_number}</span> ({result.personal_compatibility.psychic_harmony_score}%) • Life Path: <span className="font-mono font-bold text-purple-600">{result.personal_compatibility.life_path_number}</span> ({result.personal_compatibility.life_path_harmony_score}%)
                    </p>
                  </div>

                  <p className="text-xs text-[#52667E] leading-relaxed">
                    {result.personal_compatibility.synthesis}
                  </p>
                </div>
              )}

              {result.industry_compatibility && (
                <div className="bg-white rounded-2xl border border-[#DDE5F0] p-5 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 flex items-center gap-1">
                      <Building2 className="w-3 h-3" />
                      <span>Commercial Sector Match</span>
                    </span>
                    <span className={`text-xs font-bold ${
                      result.industry_compatibility.score >= 80 ? "text-emerald-600" : "text-amber-600"
                    }`}>
                      {result.industry_compatibility.score}% ({result.industry_compatibility.level})
                    </span>
                  </div>

                  <div>
                    <h5 className="text-sm font-bold text-[#102A4C]">
                      {result.industry_compatibility.industry_name}
                    </h5>
                    <p className="text-xs text-[#64748B] pt-0.5">
                      Ruler: {result.industry_compatibility.planetary_ruler} • Primary Numbers: {result.industry_compatibility.primary_numbers.join(", ")}
                    </p>
                  </div>

                  <p className="text-xs text-[#52667E] leading-relaxed">
                    {result.industry_compatibility.description}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Candidate Comparison & Ranking Table */}
          <div className="bg-white rounded-2xl border border-[#DDE5F0] p-6 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-[#E2E8F0] pb-4">
              <div>
                <h3 className="font-serif text-lg font-bold text-[#102A4C] flex items-center gap-2">
                  <Award className="w-5 h-5 text-amber-500" />
                  <span>Candidate Number Rankings & Comparative Audit</span>
                </h3>
                <p className="text-xs text-[#64748B]">
                  Evaluates {sortedCandidates.length} candidate phone numbers across personal harmony, industry match, and vanity memorability.
                </p>
              </div>

              {/* Sorter */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-[#64748B]">Sort:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-1.5 rounded-lg border border-[#CBD5E1] text-xs font-semibold text-[#0F172A] bg-white cursor-pointer"
                >
                  <option value="composite">Composite Score (Highest)</option>
                  <option value="personal">Personal Harmony</option>
                  <option value="vanity">Vanity / Memorability</option>
                  <option value="root">Root Number</option>
                </select>
              </div>
            </div>

            {/* Candidate List */}
            <div className="space-y-3">
              {sortedCandidates.map((cand, idx) => {
                const isExpanded = expandedCandidate === cand.national_number;
                return (
                  <div
                    key={idx}
                    className={`rounded-xl border transition-all ${
                      cand.is_favorable
                        ? "border-[#BFDBFE] bg-[#F8FAFC]"
                        : "border-[#E2E8F0] bg-white"
                    }`}
                  >
                    <div
                      onClick={() => setExpandedCandidate(isExpanded ? null : cand.national_number)}
                      className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer select-none"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${
                            idx === 0
                              ? "bg-amber-100 text-amber-900 border border-amber-300 shadow-2xs"
                              : "bg-slate-100 text-slate-700"
                          }`}
                        >
                          #{idx + 1}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-bold text-base text-[#102A4C]">
                              {cand.formatted_national}
                            </span>
                            {cand.country_name && (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 uppercase">
                                {cand.country_name}
                              </span>
                            )}
                            {cand.is_master && (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                                Master {cand.root_number}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-[#64748B]">
                            Compound: <span className="font-mono font-bold text-slate-700">{cand.compound_sum}</span> • Root: <span className="font-mono font-bold text-[#3478F6]">{cand.root_number}</span> ({cand.ruling_planet}) • Vanity: {cand.vanity_score}%
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 justify-between sm:justify-end">
                        <div className="flex items-center gap-3 text-right">
                          {cand.personal_score !== null && cand.personal_score !== undefined && (
                            <div className="hidden sm:block">
                              <div className="text-[10px] font-bold text-[#64748B] uppercase">Personal</div>
                              <div className="text-xs font-bold text-slate-700">{cand.personal_score}%</div>
                            </div>
                          )}
                          {cand.industry_score !== null && cand.industry_score !== undefined && (
                            <div className="hidden sm:block">
                              <div className="text-[10px] font-bold text-[#64748B] uppercase">Industry</div>
                              <div className="text-xs font-bold text-slate-700">{cand.industry_score}%</div>
                            </div>
                          )}
                          <div>
                            <div className="text-[10px] font-bold text-[#64748B] uppercase">Composite</div>
                            <div className="text-base font-black text-[#102A4C]">
                              {cand.composite_score} <span className="text-[10px] font-normal text-slate-400">/ 100</span>
                            </div>
                          </div>
                        </div>

                        <div className="p-1 rounded-lg text-slate-400 hover:text-slate-600">
                          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </div>
                      </div>
                    </div>

                    {/* Expanded Drawer */}
                    {isExpanded && (
                      <div className="px-4 pb-4 pt-2 border-t border-[#E2E8F0] space-y-3 bg-white rounded-b-xl">
                        <p className="text-xs text-[#52667E] leading-relaxed">
                          {cand.vibrational_meaning}
                        </p>

                        <div className="flex flex-wrap gap-2 text-xs pt-1">
                          {cand.reduction_steps.map((step, sIdx) => (
                            <span key={sIdx} className="font-mono text-[11px] bg-blue-50 text-blue-800 px-2 py-0.5 rounded">
                              {step}
                            </span>
                          ))}
                          {cand.missing_digits.length > 0 && (
                            <span className="font-mono text-[11px] bg-slate-100 px-2 py-0.5 rounded text-slate-700">
                              Missing: {cand.missing_digits.join(", ")}
                            </span>
                          )}
                        </div>

                        {cand.personal_compatibility && (
                          <div className="p-2.5 rounded-lg bg-blue-50/60 border border-blue-200 text-xs text-[#1E3A8A]">
                            <strong>Personal Synergy:</strong> {cand.personal_compatibility.synthesis}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* 4. Methodology & Privacy Transparency */}
          <div className="bg-slate-50 rounded-2xl border border-slate-200 p-5 space-y-3 text-xs text-slate-600">
            <button
              type="button"
              onClick={() => setShowMethodology(!showMethodology)}
              className="w-full flex items-center justify-between font-bold text-[#102A4C] cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-[#3478F6]" />
                <span>Transparent Scoring Methodology & Privacy Notice</span>
              </div>
              <ChevronDown className={`w-4 h-4 transition-transform ${showMethodology ? "rotate-180" : ""}`} />
            </button>

            {showMethodology && (
              <div className="pt-3 border-t border-slate-200 space-y-3 text-xs leading-relaxed">
                <div>
                  <h5 className="font-bold text-[#102A4C]">Composite Phone Scoring Formula:</h5>
                  <p className="font-mono text-[11px] text-[#3478F6] bg-white p-2 rounded border border-slate-200 my-1">
                    {result.scoring_explanation.formula}
                  </p>
                  <ul className="list-disc list-inside space-y-0.5 text-slate-600 pt-1">
                    <li><strong>Personal Harmony:</strong> Evaluates resonance with owner&rsquo;s Psychic (Day) and Life Path numbers.</li>
                    <li><strong>Industry Alignment:</strong> Matches primary and secondary planetary rulers of the commercial sector.</li>
                    <li><strong>Vanity & Rhythm Score:</strong> Analyzes repeated digit clusters, numerical sequences, and memorability.</li>
                  </ul>
                </div>

                <div className="p-3 rounded-xl bg-purple-50/70 border border-purple-200 text-purple-900 text-[11px]">
                  <strong>Privacy Safeguard:</strong> {result.scoring_explanation.privacy_notice}
                </div>

                <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 text-[11px]">
                  <strong>System Notice & Disclaimer:</strong> {result.scoring_explanation.disclaimer}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
