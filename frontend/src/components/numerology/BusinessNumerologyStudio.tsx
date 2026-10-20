"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/i18n";
import { analyzeBusinessNumerology, saveNumerologyReport } from "@/lib/api";
import {
  BusinessNumerologyResponse,
  BusinessCandidateResult,
  FounderInput,
  FounderEvaluationResult,
} from "@/lib/types";
import {
  Building2,
  Briefcase,
  Users,
  Sparkles,
  Globe,
  Tag,
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
  Sliders,
  Check,
  Award,
  Layers,
  ArrowRight,
  ShieldCheck,
  Scale,
} from "lucide-react";

const INDUSTRY_OPTIONS = [
  { value: "technology", labelEn: "Technology & Software", labelTa: "தொழில்நுட்பம் & மென்பொருள்", ruler: "Mercury & Uranus", numbers: "5, 1" },
  { value: "retail", labelEn: "Retail & E-Commerce", labelTa: "சில்லறை வணிகம் & இணைய அங்காடி", ruler: "Mercury & Venus", numbers: "5, 6" },
  { value: "education", labelEn: "Education & Coaching", labelTa: "கல்வி & பயிற்சி", ruler: "Jupiter & Mercury", numbers: "3, 5" },
  { value: "healthcare", labelEn: "Healthcare & Pharmaceuticals", labelTa: "மருத்துவம் & நல்வாழ்வு", ruler: "Moon & Jupiter", numbers: "2, 7" },
  { value: "finance", labelEn: "Banking & Financial Services", labelTa: "வங்கி & நிதிச் சேவைகள்", ruler: "Saturn & Mercury", numbers: "4, 8" },
  { value: "manufacturing", labelEn: "Manufacturing & Heavy Industry", labelTa: "உற்பத்தி & கனரகத் தொழில்", ruler: "Mars & Saturn", numbers: "9, 8" },
  { value: "astrology", labelEn: "Astrology & Esoteric Services", labelTa: "ஜோதிடம் & ஆன்மீக சேவைகள்", ruler: "Neptune & Ketu", numbers: "7, 9" },
  { value: "creative", labelEn: "Creative, Media & Entertainment", labelTa: "படைப்பாற்றல், ஊடகம் & கலை", ruler: "Venus & Sun", numbers: "3, 6" },
  { value: "other", labelEn: "General & Diversified Enterprise", labelTa: "பொது & இதர வர்த்தகம்", ruler: "Sun", numbers: "1, 3" },
] as const;

export function BusinessNumerologyStudio() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Core Business Inputs
  const [legalName, setLegalName] = useState("Nexus Tech Innovations Private Limited");
  const [brandName, setBrandName] = useState("");
  const [tagline, setTagline] = useState("Empowering Intelligent Systems");
  const [domainOrHandle, setDomainOrHandle] = useState("nexustech.io");
  const [systemConvention, setSystemConvention] = useState<"pythagorean" | "chaldean">("chaldean");
  const [industryCategory, setIndustryCategory] = useState<
    "technology" | "retail" | "education" | "healthcare" | "finance" | "manufacturing" | "astrology" | "creative" | "other"
  >("technology");
  const [reportLang, setReportLang] = useState<"en" | "ta">("en");

  // Founders State
  const [founders, setFounders] = useState<FounderInput[]>([
    { name: "Gokul Murugan", birth_date: "1994-06-15", role: "Founder & CEO", share_percentage: 60 },
    { name: "Priya Sundaram", birth_date: "1995-11-23", role: "Co-Founder & CTO", share_percentage: 40 },
  ]);

  // Custom Candidates
  const [customCandidates, setCustomCandidates] = useState<string[]>([
    "Nexus AI",
    "Nexus Innovate",
  ]);
  const [newCandidateInput, setNewCandidateInput] = useState("");

  // Results & UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BusinessNumerologyResponse | null>(null);
  const [expandedCandidate, setExpandedCandidate] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<"composite" | "founder" | "industry" | "expression">("composite");
  const [savedSuccessMsg, setSavedSuccessMsg] = useState<string | null>(null);
  const [savingReport, setSavingReport] = useState(false);
  const [showMethodology, setShowMethodology] = useState(false);

  // Auto-run on mount for instant preview
  useEffect(() => {
    handleRunStudio();
  }, []);

  const handleRunStudio = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!legalName.trim()) {
      setError(language === "ta" ? "சட்டப்பூர்வ நிறுவனப் பெயரை உள்ளிடுக." : "Please enter a valid legal business name.");
      return;
    }

    setLoading(true);
    setError(null);
    setSavedSuccessMsg(null);

    try {
      const response = await analyzeBusinessNumerology({
        legal_name: legalName.trim(),
        brand_name: brandName.trim() || undefined,
        tagline: tagline.trim() || undefined,
        domain_or_handle: domainOrHandle.trim() || undefined,
        system_convention: systemConvention,
        industry_category: industryCategory,
        founders: founders.filter((f) => f.name.trim()),
        custom_candidates: customCandidates.filter((c) => c.trim()),
        language: reportLang,
      });

      setResult(response);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to analyze business numerology.");
    } finally {
      setLoading(false);
    }
  };

  // Founder management
  const addFounder = () => {
    setFounders([
      ...founders,
      { name: "", birth_date: "", role: "Partner", share_percentage: 0 },
    ]);
  };

  const updateFounder = (index: number, field: keyof FounderInput, val: any) => {
    const updated = [...founders];
    updated[index] = { ...updated[index], [field]: val };
    setFounders(updated);
  };

  const removeFounder = (index: number) => {
    setFounders(founders.filter((_, idx) => idx !== index));
  };

  // Custom candidate management
  const addCandidate = () => {
    if (newCandidateInput.trim() && !customCandidates.includes(newCandidateInput.trim())) {
      setCustomCandidates([...customCandidates, newCandidateInput.trim()]);
      setNewCandidateInput("");
    }
  };

  const removeCandidate = (cand: string) => {
    setCustomCandidates(customCandidates.filter((c) => c !== cand));
  };

  // Save report
  const handleSaveReport = async () => {
    if (!result) return;
    if (!isAuthenticated || !session?.access_token) {
      setError("Please sign in to save business numerology reports.");
      return;
    }

    setSavingReport(true);
    setSavedSuccessMsg(null);

    try {
      await saveNumerologyReport(
        {
          person_name: result.legal_name,
          birth_date: founders[0]?.birth_date || "2000-01-01",
          system_convention: result.system_convention as any,
          method: "business",
          calculation_data: result,
          interpretation_data: {
            title: `Business Brand Report: ${result.normalized_brand_name}`,
            industry: result.industry_category,
            composite_score: result.candidates[0]?.composite_score || 0,
            founders_count: founders.length,
            partnership_synthesis: result.partnership_matrix.synthesis,
            disclaimer: result.scoring_explanation.disclaimer,
          },
        },
        session.access_token
      );
      setSavedSuccessMsg("Business numerology analysis saved successfully to your profile!");
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to save report.");
    } finally {
      setSavingReport(false);
    }
  };

  // Sort candidate list
  const sortedCandidates = result
    ? [...result.candidates].sort((a, b) => {
        if (sortBy === "composite") return b.composite_score - a.composite_score;
        if (sortBy === "founder") return b.founder_harmony_score - a.founder_harmony_score;
        if (sortBy === "industry") return b.industry_harmony_score - a.industry_harmony_score;
        if (sortBy === "expression") return a.expression_number - b.expression_number;
        return 0;
      })
    : [];

  return (
    <div className="space-y-8">
      {/* 1. Header Banner */}
      <div className="rounded-2xl p-6 sm:p-8 bg-gradient-to-br from-[#0F1E36] via-[#102A4C] to-[#1B365D] text-white shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-[#3478F6]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#3478F6]/20 border border-[#3478F6]/30 text-[#93C5FD] text-xs font-bold uppercase tracking-wider">
            <Building2 className="w-3.5 h-3.5" />
            <span>Corporate & Brand Numerology</span>
          </div>

          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight">
            {language === "ta" ? "வணிக & பிராண்ட் எண் கணித அரங்கம்" : "Business & Brand Numerology Studio"}
          </h1>

          <p className="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
            {language === "ta"
              ? "நிறுவனத்தின் சட்டப்பூர்வ பெயர், பொது பிராண்ட் பெயர், கூட்டாளர் பிறந்த எண்கள் மற்றும் தொழில்துறை அதிர்வுகளை துல்லியமாக ஒப்பிட்டு சாதகமான வர்த்தக அதிர்வை உருவாக்குங்கள்."
              : "Audit statutory legal names versus consumer brand names, evaluate multi-founder equity alignments, test tagline synergy, and score enterprise trade names against planetary industry archetypes."}
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2 text-xs text-slate-300">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Statutory Suffix Stripping</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Users className="w-4 h-4 text-sky-400" />
              <span>Multi-Founder Equity Harmony</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Globe className="w-4 h-4 text-amber-400" />
              <span>Tagline & Domain Vibration</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Scale className="w-4 h-4 text-purple-400" />
              <span>Pythagorean & Chaldean Rigor</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Interactive Input Control Form */}
      <div className="bg-white rounded-2xl border border-[#DDE5F0] p-6 shadow-xs space-y-6">
        <form onSubmit={handleRunStudio} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Legal Business Name */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C]">
                {language === "ta" ? "முழு சட்டப்பூர்வ பெயர் *" : "Full Legal Entity Name *"}
              </label>
              <input
                type="text"
                value={legalName}
                onChange={(e) => setLegalName(e.target.value)}
                placeholder="e.g. Tata Consultancy Services Private Limited"
                className="w-full px-4 py-2.5 rounded-xl border border-[#CBD5E1] text-sm text-[#0F172A] focus:outline-hidden focus:ring-2 focus:ring-[#3478F6] focus:border-transparent font-medium"
                required
              />
              <p className="text-[11px] text-[#64748B]">
                Includes statutory designations like Pvt Ltd, LLP, Inc, Corp, LLC, PLC, GmbH, Co. Ltd.
              </p>
            </div>

            {/* Public Brand Name Override */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C]">
                {language === "ta" ? "பொது பிராண்ட் பெயர் (விருப்பத்திற்குரியது)" : "Public-Facing Brand Name (Optional)"}
              </label>
              <input
                type="text"
                value={brandName}
                onChange={(e) => setBrandName(e.target.value)}
                placeholder="Leave blank to auto-normalize from legal name"
                className="w-full px-4 py-2.5 rounded-xl border border-[#CBD5E1] text-sm text-[#0F172A] focus:outline-hidden focus:ring-2 focus:ring-[#3478F6] focus:border-transparent"
              />
              <p className="text-[11px] text-[#64748B]">
                Consumer-facing identity used in storefronts, ads, and packaging.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Tagline / Slogan */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C] flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-[#3478F6]" />
                <span>{language === "ta" ? "முழக்கம் / விளம்பர வாசகம்" : "Brand Slogan / Tagline"}</span>
              </label>
              <input
                type="text"
                value={tagline}
                onChange={(e) => setTagline(e.target.value)}
                placeholder="e.g. Building Tomorrow's Enterprise"
                className="w-full px-4 py-2.5 rounded-xl border border-[#CBD5E1] text-sm text-[#0F172A] focus:outline-hidden focus:ring-2 focus:ring-[#3478F6] focus:border-transparent"
              />
            </div>

            {/* Domain or Social Handle */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C] flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-[#3478F6]" />
                <span>{language === "ta" ? "வலைத்தள முகவரி / ஹேண்டில்" : "Domain or Social Handle"}</span>
              </label>
              <input
                type="text"
                value={domainOrHandle}
                onChange={(e) => setDomainOrHandle(e.target.value)}
                placeholder="e.g. tataconsultancy.com or @freshworks"
                className="w-full px-4 py-2.5 rounded-xl border border-[#CBD5E1] text-sm text-[#0F172A] focus:outline-hidden focus:ring-2 focus:ring-[#3478F6] focus:border-transparent font-mono"
              />
            </div>
          </div>

          {/* System Convention & Industry Category */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-2">
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C]">
                {language === "ta" ? "கணித மரபு" : "Numerology System"}
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
                  Chaldean (1–8)
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
                  Pythagorean (1–9)
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C]">
                {language === "ta" ? "தொழில்துறை வகை" : "Industry Sector"}
              </label>
              <select
                value={industryCategory}
                onChange={(e) => setIndustryCategory(e.target.value as any)}
                className="w-full px-3 py-2.5 rounded-xl border border-[#CBD5E1] text-xs font-medium text-[#0F172A] bg-white focus:outline-hidden focus:ring-2 focus:ring-[#3478F6]"
              >
                {INDUSTRY_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {language === "ta" ? opt.labelTa : opt.labelEn} (Planets: {opt.ruler})
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C]">
                {language === "ta" ? "விளக்க மொழி" : "Interpretation Language"}
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setReportLang("en")}
                  className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                    reportLang === "en"
                      ? "bg-[#102A4C] text-white border-[#102A4C] shadow-xs"
                      : "bg-[#F8FAFC] text-[#52667E] border-[#E2E8F0] hover:bg-[#F1F5F9]"
                  }`}
                >
                  English
                </button>
                <button
                  type="button"
                  onClick={() => setReportLang("ta")}
                  className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                    reportLang === "ta"
                      ? "bg-[#102A4C] text-white border-[#102A4C] shadow-xs"
                      : "bg-[#F8FAFC] text-[#52667E] border-[#E2E8F0] hover:bg-[#F1F5F9]"
                  }`}
                >
                  தமிழ்
                </button>
              </div>
            </div>
          </div>

          {/* Founders & Partners Manager */}
          <div className="pt-4 border-t border-[#E2E8F0] space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-[#102A4C] flex items-center gap-2">
                  <Users className="w-4 h-4 text-[#3478F6]" />
                  <span>Founders, Partners & Equity Alignment</span>
                </h3>
                <p className="text-xs text-[#64748B]">
                  Add all key promoters. We calculate individual Psychic/Life Path resonance and synthesize a partnership matrix.
                </p>
              </div>
              <button
                type="button"
                onClick={addFounder}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-[#3478F6] bg-[#EFF6FF] border border-[#BFDBFE] hover:bg-[#DBEAFE] transition-colors cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Founder</span>
              </button>
            </div>

            <div className="space-y-3">
              {founders.map((founder, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] grid grid-cols-1 sm:grid-cols-12 gap-3 items-center"
                >
                  <div className="sm:col-span-4 space-y-1">
                    <label className="block text-[10px] font-bold text-[#64748B] uppercase">Founder Name</label>
                    <input
                      type="text"
                      value={founder.name}
                      onChange={(e) => updateFounder(idx, "name", e.target.value)}
                      placeholder="e.g. Founder Name"
                      className="w-full px-3 py-1.5 rounded-lg border border-[#CBD5E1] text-xs font-medium text-[#0F172A] bg-white"
                    />
                  </div>

                  <div className="sm:col-span-3 space-y-1">
                    <label className="block text-[10px] font-bold text-[#64748B] uppercase">Birth Date</label>
                    <input
                      type="date"
                      value={founder.birth_date || ""}
                      onChange={(e) => updateFounder(idx, "birth_date", e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg border border-[#CBD5E1] text-xs font-medium text-[#0F172A] bg-white"
                    />
                  </div>

                  <div className="sm:col-span-3 space-y-1">
                    <label className="block text-[10px] font-bold text-[#64748B] uppercase">Role / Title</label>
                    <input
                      type="text"
                      value={founder.role || ""}
                      onChange={(e) => updateFounder(idx, "role", e.target.value)}
                      placeholder="e.g. CEO / Director"
                      className="w-full px-3 py-1.5 rounded-lg border border-[#CBD5E1] text-xs font-medium text-[#0F172A] bg-white"
                    />
                  </div>

                  <div className="sm:col-span-1 space-y-1">
                    <label className="block text-[10px] font-bold text-[#64748B] uppercase">Equity %</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={founder.share_percentage || 0}
                      onChange={(e) => updateFounder(idx, "share_percentage", parseFloat(e.target.value) || 0)}
                      className="w-full px-2 py-1.5 rounded-lg border border-[#CBD5E1] text-xs font-medium text-[#0F172A] bg-white"
                    />
                  </div>

                  <div className="sm:col-span-1 flex justify-end items-end pt-5">
                    <button
                      type="button"
                      onClick={() => removeFounder(idx)}
                      disabled={founders.length <= 1}
                      className="p-1.5 text-slate-400 hover:text-rose-500 disabled:opacity-30 transition-colors cursor-pointer"
                      title="Remove founder"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Custom Candidate Variations */}
          <div className="pt-4 border-t border-[#E2E8F0] space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wider text-[#102A4C]">
              {language === "ta" ? "மாற்று பிராண்ட் பெயர்கள் (Custom Candidates)" : "Custom Alternative Brand Candidates"}
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
                placeholder="e.g. Nexus Next, Nexura, Nexus Logic"
                className="flex-1 px-4 py-2 rounded-xl border border-[#CBD5E1] text-xs font-medium text-[#0F172A]"
              />
              <button
                type="button"
                onClick={addCandidate}
                className="px-4 py-2 rounded-xl text-xs font-bold text-[#102A4C] bg-[#F1F5F9] border border-[#CBD5E1] hover:bg-[#E2E8F0] transition-colors cursor-pointer"
              >
                Add Candidate
              </button>
            </div>

            {customCandidates.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-1">
                {customCandidates.map((cand, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-[#EFF6FF] text-[#1E40AF] border border-[#BFDBFE]"
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

          {/* Submit Action Button */}
          <div className="pt-4 border-t border-[#E2E8F0] flex flex-col sm:flex-row items-center justify-between gap-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-sm text-white bg-[#102A4C] hover:bg-[#1A365D] transition-all shadow-md cursor-pointer disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Calculating Enterprise Vibrations...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span>Audit & Rank Business Brand</span>
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
                <span>{savingReport ? "Saving Report..." : "Save Business Reading"}</span>
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

      {/* 3. Results Section */}
      {result && (
        <div className="space-y-8">
          {/* Baseline Dual Analysis: Legal Entity vs Clean Brand */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Legal Entity Card */}
            <div className="bg-white rounded-2xl border border-[#DDE5F0] p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                  Statutory Legal Entity
                </span>
                <span className="text-xs font-mono font-bold text-slate-500">
                  Total: {result.legal_analysis.compound_expression}
                </span>
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-[#102A4C] truncate" title={result.legal_name}>
                  {result.legal_name}
                </h4>
                {result.detected_suffixes.length > 0 && (
                  <p className="text-[11px] text-amber-600 font-medium">
                    Detected Suffix: {result.detected_suffixes.join(", ")}
                  </p>
                )}
              </div>
              <div className="flex items-baseline gap-3 pt-2">
                <div className="text-3xl font-serif font-black text-[#102A4C]">
                  {result.legal_analysis.expression_number}
                </div>
                <div className="text-xs text-[#64748B]">
                  <span>Compound: {result.legal_analysis.compound_expression}</span>
                  <p className="text-[10px] font-semibold text-slate-500">
                    Soul: {result.legal_analysis.soul_urge_number} • Personality: {result.legal_analysis.personality_number}
                  </p>
                </div>
              </div>
              <p className="text-xs text-[#52667E] line-clamp-2">
                {result.legal_analysis.vibrational_synthesis}
              </p>
            </div>

            {/* Public Brand Name Card */}
            <div className="bg-gradient-to-br from-[#F8FAFC] to-[#EFF6FF] rounded-2xl border border-[#BFDBFE] p-5 shadow-xs space-y-3 relative overflow-hidden">
              <div className="absolute top-2 right-2">
                <Sparkles className="w-5 h-5 text-[#3478F6]/20" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#3478F6]/10 text-[#3478F6] border border-[#BFDBFE]">
                  Public Brand Identity
                </span>
                {result.brand_analysis.is_master && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                    Master Vibration
                  </span>
                )}
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-[#102A4C]">
                  {result.normalized_brand_name}
                </h4>
                <p className="text-[11px] text-[#3478F6] font-medium">
                  Acronym: {result.acronym}
                </p>
              </div>
              <div className="flex items-baseline gap-3 pt-2">
                <div className="text-3xl font-serif font-black text-[#3478F6]">
                  {result.brand_analysis.expression_number}
                </div>
                <div className="text-xs text-[#64748B]">
                  <span>Compound: {result.brand_analysis.compound_expression}</span>
                  <p className="text-[10px] font-semibold text-[#3478F6]">
                    Composite Score: {result.brand_analysis.composite_score} / 100
                  </p>
                </div>
              </div>
              <p className="text-xs text-[#52667E] line-clamp-2">
                {result.brand_analysis.vibrational_synthesis}
              </p>
            </div>

            {/* Industry Correspondence Profile */}
            <div className="bg-white rounded-2xl border border-[#DDE5F0] p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
                  Industry Correspondence
                </span>
                <span className="text-xs font-bold text-purple-700">
                  Harmony: {result.brand_analysis.industry_harmony_score}%
                </span>
              </div>
              <div>
                <h4 className="font-serif text-base font-bold text-[#102A4C]">
                  {result.industry_vibrations.name}
                </h4>
                <p className="text-[11px] text-[#64748B]">
                  Ruler: {result.industry_vibrations.planetary_ruler}
                </p>
              </div>
              <div className="pt-1 space-y-1">
                <div className="text-xs text-[#102A4C]">
                  <span className="font-bold">Primary Numbers: </span>
                  <span className="font-mono font-bold text-[#3478F6]">
                    {result.industry_vibrations.primary_numbers.join(", ")}
                  </span>
                </div>
                <div className="text-xs text-[#102A4C]">
                  <span className="font-bold">Secondary Numbers: </span>
                  <span className="font-mono text-slate-600">
                    {result.industry_vibrations.secondary_numbers.join(", ")}
                  </span>
                </div>
              </div>
              <p className="text-[11px] text-[#64748B] italic">
                {result.industry_vibrations.traditional_rationale}
              </p>
            </div>
          </div>

          {/* Letter Breakdown Table for Brand Name */}
          <div className="bg-white rounded-2xl border border-[#DDE5F0] p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#102A4C] flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-[#3478F6]" />
                <span>Letter Vibration Breakdown: &ldquo;{result.normalized_brand_name}&rdquo; ({result.system_convention.toUpperCase()})</span>
              </h4>
              <span className="text-xs font-mono text-slate-500">
                Letters: {result.brand_analysis.letter_mappings.length}
              </span>
            </div>

            <div className="overflow-x-auto">
              <div className="flex items-center gap-1.5 py-2">
                {result.brand_analysis.letter_mappings.map((item, idx) => (
                  <div
                    key={idx}
                    className={`flex flex-col items-center justify-center p-2 rounded-lg border min-w-[38px] ${
                      item.is_vowel
                        ? "bg-amber-50 border-amber-200 text-amber-900"
                        : "bg-slate-50 border-slate-200 text-slate-800"
                    }`}
                  >
                    <span className="font-bold text-sm">{item.char}</span>
                    <span className="text-xs font-mono font-bold text-[#3478F6]">{item.value}</span>
                    <span className="text-[9px] uppercase tracking-tighter text-slate-400">
                      {item.is_vowel ? "vow" : "con"}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="text-xs text-[#64748B] pt-2 flex flex-wrap gap-4 border-t border-[#F1F5F9]">
              {result.brand_analysis.reduction_steps.map((step, idx) => (
                <span key={idx} className="font-mono text-[11px] bg-slate-100 px-2 py-0.5 rounded text-slate-700">
                  {step}
                </span>
              ))}
            </div>
          </div>

          {/* Tagline & Domain Synergy Cards */}
          {(result.tagline_analysis || result.domain_analysis) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {result.tagline_analysis && (
                <div className="bg-white rounded-2xl border border-[#DDE5F0] p-5 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                      Tagline Synergy
                    </span>
                    <span className="text-xs font-bold text-emerald-600">
                      Score: {result.tagline_analysis.synergy_score}%
                    </span>
                  </div>
                  <div>
                    <h5 className="text-sm font-bold text-[#102A4C] italic">
                      &ldquo;{result.tagline_analysis.tagline}&rdquo;
                    </h5>
                    <p className="text-xs text-[#64748B] pt-1">
                      Expression: {result.tagline_analysis.expression_number} (Compound: {result.tagline_analysis.compound_expression})
                    </p>
                  </div>
                  <p className="text-xs text-[#52667E]">
                    {result.tagline_analysis.synergy_interpretation}
                  </p>
                </div>
              )}

              {result.domain_analysis && (
                <div className="bg-white rounded-2xl border border-[#DDE5F0] p-5 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-50 text-slate-700 border border-slate-200">
                      Domain / Social Handle Vibration
                    </span>
                    <span className={`text-xs font-bold ${result.domain_analysis.matches_brand ? "text-emerald-600" : "text-amber-600"}`}>
                      {result.domain_analysis.matches_brand ? "Exact Brand Match" : "Variant Vibration"}
                    </span>
                  </div>
                  <div>
                    <h5 className="text-sm font-mono font-bold text-[#102A4C]">
                      {result.domain_analysis.raw_handle}
                    </h5>
                    <p className="text-xs text-[#64748B] pt-1">
                      Sanitized: <span className="font-mono">{result.domain_analysis.clean_handle}</span> • Expression: {result.domain_analysis.expression_number} (Compound: {result.domain_analysis.compound_expression})
                    </p>
                  </div>
                  <p className="text-xs text-[#52667E]">
                    Web and social handles channel initial contact vibrations. A harmony between brand and domain accelerates brand recall and discovery.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Partnership & Multi-Founder Harmony Matrix */}
          <div className="bg-white rounded-2xl border border-[#DDE5F0] p-6 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[#E2E8F0] pb-4">
              <div>
                <h3 className="font-serif text-lg font-bold text-[#102A4C] flex items-center gap-2">
                  <Users className="w-5 h-5 text-[#3478F6]" />
                  <span>Founder Alignment & Partnership Synergy Matrix</span>
                </h3>
                <p className="text-xs text-[#64748B]">
                  Evaluates each founder&rsquo;s Birth/Psychic and Life Path vibrations against the company brand.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs font-bold text-[#64748B] uppercase">Overall Partnership Harmony</div>
                  <div className="text-xl font-black text-[#102A4C]">
                    {result.partnership_matrix.overall_partnership_score}%
                  </div>
                </div>
              </div>
            </div>

            {/* Friction Warning Banner if any */}
            {result.partnership_matrix.has_friction && (
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>Planetary Polarity Tension Detected in Partnership</span>
                </div>
                <p>
                  Tension exists among founders: {result.partnership_matrix.friction_founders.join(", ")}. In traditional numerology, when conflicting polarities (e.g. 1-Sun vs 8-Saturn) co-exist in leadership, establishing distinct operational jurisdictions (e.g., Vision vs Execution) preserves enterprise harmony.
                </p>
              </div>
            )}

            {/* Founder Breakdown Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-[#E2E8F0] text-[#64748B] uppercase text-[10px] tracking-wider">
                    <th className="py-2.5 px-3">Founder & Role</th>
                    <th className="py-2.5 px-3">Equity</th>
                    <th className="py-2.5 px-3">Psychic (Birth)</th>
                    <th className="py-2.5 px-3">Life Path</th>
                    <th className="py-2.5 px-3">Name Expression</th>
                    <th className="py-2.5 px-3">Alignment Score</th>
                    <th className="py-2.5 px-3">Resonance Notes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9]">
                  {result.partnership_matrix.founder_results.map((founder, idx) => (
                    <tr key={idx} className="hover:bg-[#F8FAFC]">
                      <td className="py-3 px-3">
                        <div className="font-bold text-[#102A4C]">{founder.name}</div>
                        <div className="text-[11px] text-[#64748B]">{founder.role || "Partner"}</div>
                      </td>
                      <td className="py-3 px-3 font-mono font-medium text-slate-700">
                        {founder.share_percentage ? `${founder.share_percentage}%` : "—"}
                      </td>
                      <td className="py-3 px-3">
                        {founder.psychic_number ? (
                          <span className="font-mono font-bold text-[#3478F6] px-2 py-0.5 rounded bg-blue-50 border border-blue-100">
                            {founder.psychic_number}
                          </span>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        {founder.life_path_number ? (
                          <span className="font-mono font-bold text-purple-600 px-2 py-0.5 rounded bg-purple-50 border border-purple-100">
                            {founder.life_path_number}
                          </span>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-700">
                        {founder.name_expression}
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`font-bold px-2 py-0.5 rounded-full text-[11px] ${
                            founder.alignment_score >= 80
                              ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                              : founder.alignment_score >= 60
                              ? "bg-blue-50 text-blue-700 border border-blue-200"
                              : "bg-amber-50 text-amber-700 border border-amber-200"
                          }`}
                        >
                          {founder.alignment_score}% ({founder.alignment_level})
                        </span>
                      </td>
                      <td className="py-3 px-3 text-[#52667E] max-w-xs">
                        {founder.notes}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="text-xs text-[#64748B] italic pt-2 border-t border-[#F1F5F9]">
              {result.partnership_matrix.synthesis}
            </p>
          </div>

          {/* Candidate Brand Ranking & Comparative Analysis */}
          <div className="bg-white rounded-2xl border border-[#DDE5F0] p-6 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-[#E2E8F0] pb-4">
              <div>
                <h3 className="font-serif text-lg font-bold text-[#102A4C] flex items-center gap-2">
                  <Award className="w-5 h-5 text-amber-500" />
                  <span>Candidate Brand Rankings & Comparative Audit</span>
                </h3>
                <p className="text-xs text-[#64748B]">
                  Evaluates {sortedCandidates.length} candidate trade names using composite multi-dimensional scoring.
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
                  <option value="founder">Founder Harmony</option>
                  <option value="industry">Industry Alignment</option>
                  <option value="expression">Expression Number</option>
                </select>
              </div>
            </div>

            {/* Candidate List */}
            <div className="space-y-3">
              {sortedCandidates.map((cand, idx) => {
                const isExpanded = expandedCandidate === cand.name;
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
                      onClick={() => setExpandedCandidate(isExpanded ? null : cand.name)}
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
                            <span className="font-serif font-bold text-base text-[#102A4C]">
                              {cand.name}
                            </span>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 uppercase">
                              {cand.candidate_type}
                            </span>
                            {cand.is_master && (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                                Master {cand.expression_number}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-[#64748B]">
                            Compound: <span className="font-mono font-bold text-slate-700">{cand.compound_expression}</span> • Expression: <span className="font-mono font-bold text-[#3478F6]">{cand.expression_number}</span> • Soul: {cand.soul_urge_number} • Personality: {cand.personality_number}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 justify-between sm:justify-end">
                        <div className="flex items-center gap-3 text-right">
                          <div className="hidden sm:block">
                            <div className="text-[10px] font-bold text-[#64748B] uppercase">Founder Harm.</div>
                            <div className="text-xs font-bold text-slate-700">{cand.founder_harmony_score}%</div>
                          </div>
                          <div className="hidden sm:block">
                            <div className="text-[10px] font-bold text-[#64748B] uppercase">Industry</div>
                            <div className="text-xs font-bold text-slate-700">{cand.industry_harmony_score}%</div>
                          </div>
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
                          {cand.vibrational_synthesis}
                        </p>

                        <div className="flex flex-wrap gap-2 text-xs pt-1">
                          <span className="font-mono text-[11px] bg-slate-100 px-2 py-0.5 rounded text-slate-700">
                            Pronunciation Preservation: {cand.pronunciation_score}%
                          </span>
                          <span className="font-mono text-[11px] bg-slate-100 px-2 py-0.5 rounded text-slate-700">
                            Spelling Simplicity: {cand.simplicity_score}%
                          </span>
                          {cand.reduction_steps.map((step, sIdx) => (
                            <span key={sIdx} className="font-mono text-[11px] bg-blue-50 text-blue-800 px-2 py-0.5 rounded">
                              {step}
                            </span>
                          ))}
                        </div>

                        {/* Founder Alignment Sub-table */}
                        {cand.founder_alignments && cand.founder_alignments.length > 0 && (
                          <div className="pt-2">
                            <h6 className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                              Alignment with Individual Promoters
                            </h6>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                              {cand.founder_alignments.map((fa, faIdx) => (
                                <div key={faIdx} className="p-2 rounded-lg bg-slate-50 border border-slate-200 text-[11px]">
                                  <div className="flex justify-between font-bold text-slate-700">
                                    <span>{fa.name}</span>
                                    <span className="text-[#3478F6]">{fa.alignment_score}%</span>
                                  </div>
                                  <div className="text-[10px] text-slate-500">{fa.notes}</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* 4. Methodology & Transparency Section */}
          <div className="bg-slate-50 rounded-2xl border border-slate-200 p-5 space-y-3 text-xs text-slate-600">
            <button
              type="button"
              onClick={() => setShowMethodology(!showMethodology)}
              className="w-full flex items-center justify-between font-bold text-[#102A4C] cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-[#3478F6]" />
                <span>Transparent Scoring Methodology & Cultural Disclaimer</span>
              </div>
              <ChevronDown className={`w-4 h-4 transition-transform ${showMethodology ? "rotate-180" : ""}`} />
            </button>

            {showMethodology && (
              <div className="pt-3 border-t border-slate-200 space-y-3 text-xs leading-relaxed">
                <div>
                  <h5 className="font-bold text-[#102A4C]">Composite Brand Scoring Formula:</h5>
                  <p className="font-mono text-[11px] text-[#3478F6] bg-white p-2 rounded border border-slate-200 my-1">
                    {result.scoring_explanation.formula}
                  </p>
                  <ul className="list-disc list-inside space-y-0.5 text-slate-600 pt-1">
                    <li><strong>35% Founder Harmony:</strong> Evaluates resonance with promoters&rsquo; Psychic and Life Path numbers.</li>
                    <li><strong>25% Industry Alignment:</strong> Assesses alignment with traditional planetary rulers for the sector.</li>
                    <li><strong>20% Pronunciation Preservation:</strong> Ensures brand clarity and phonotactic fluidity.</li>
                    <li><strong>20% Spelling Simplicity:</strong> Rewards clean, non-confusing commercial spelling.</li>
                  </ul>
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
