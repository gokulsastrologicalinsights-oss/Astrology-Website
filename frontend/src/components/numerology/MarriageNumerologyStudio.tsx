"use client";

import React, { useState } from "react";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { analyzeMarriageNumerology, saveNumerologyReport, exportNumerologyPdf } from "@/lib/api";
import {
  MarriageNumerologyRequest,
  MarriageNumerologyResponse,
  MarriagePersonProfile,
  MarriageComponentComparison,
} from "@/lib/types";
import {
  Heart,
  Sparkles,
  Users,
  Compass,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Save,
  Download,
  Loader2,
  Calendar,
  MessageSquare,
  ShieldCheck,
  Flame,
  ArrowRight,
  BookOpen,
} from "lucide-react";

export function MarriageNumerologyStudio() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Convention & Language
  const [convention, setConvention] = useState<"pythagorean" | "chaldean">("pythagorean");
  const [reportLang, setReportLang] = useState<"en" | "ta">("en");
  const [relationshipStatus, setRelationshipStatus] = useState<string>("considering_marriage");

  // Person A inputs
  const [personAName, setPersonAName] = useState<string>("Sundar Raman");
  const [personADob, setPersonADob] = useState<string>("1995-06-15");
  const [personAPreferred, setPersonAPreferred] = useState<string>("Sundar");
  const [personAInitials, setPersonAInitials] = useState<string>("R");

  // Person B inputs
  const [personBName, setPersonBName] = useState<string>("Meenakshi Sundaram");
  const [personBDob, setPersonBDob] = useState<string>("1996-09-22");
  const [personBPreferred, setPersonBPreferred] = useState<string>("Meena");
  const [personBInitials, setPersonBInitials] = useState<string>("S");

  // State
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MarriageNumerologyResponse | null>(null);

  // Saving state
  const [saving, setSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [pdfDownloading, setPdfDownloading] = useState<boolean>(false);

  const handleAnalyze = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!personADob || !personBDob) {
      setError(
        language === "ta"
          ? "தயவுசெய்து இருவரின் பிறந்த தேதிகளையும் உள்ளிடவும்."
          : "Please enter birth dates for both partners."
      );
      return;
    }

    setLoading(true);
    setError(null);
    setSaveSuccess(null);
    setSaveError(null);

    const payload: MarriageNumerologyRequest = {
      person_a: {
        full_name: personAName.trim() || undefined,
        birth_date: personADob.trim(),
        preferred_name: personAPreferred.trim() || undefined,
        surname_initials: personAInitials.trim() || undefined,
        relationship_status: relationshipStatus,
        language: reportLang,
      },
      person_b: {
        full_name: personBName.trim() || undefined,
        birth_date: personBDob.trim(),
        preferred_name: personBPreferred.trim() || undefined,
        surname_initials: personBInitials.trim() || undefined,
        relationship_status: relationshipStatus,
        language: reportLang,
      },
      system_convention: convention,
      language: reportLang,
    };

    try {
      const res = await analyzeMarriageNumerology(payload, session?.access_token);
      setResult(res);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to analyze marriage compatibility.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveReport = async () => {
    if (!result) return;
    if (!isAuthenticated || !session?.access_token) {
      setSaveError(
        language === "ta"
          ? "அறிக்கையைச் சேமிக்க உள்நுழையவும்."
          : "Please log in to save this numerology report."
      );
      return;
    }

    setSaving(true);
    setSaveSuccess(null);
    setSaveError(null);

    const nameA = result.person_a_profile.full_name || result.person_a_profile.preferred_name || "Partner A";
    const nameB = result.person_b_profile.full_name || result.person_b_profile.preferred_name || "Partner B";

    try {
      await saveNumerologyReport(
        {
          person_name: `${nameA} & ${nameB}`,
          birth_date: result.person_a_profile.birth_date,
          method: "marriage",
          system_convention: result.system_convention,
          calculation_data: result as any,
          interpretation_data: {
            overall_score: result.overall_score,
            overall_harmony_level: result.overall_harmony_level,
            synthesis: result.overall_synthesis,
            emotional_themes: result.emotional_themes,
            shared_strengths: result.shared_strengths,
            potential_challenges: result.potential_challenges,
          },
        },
        session.access_token
      );
      setSaveSuccess(
        language === "ta"
          ? "திருமணப் பொருத்த அறிக்கை வெற்றிகரமாகச் சேமிக்கப்பட்டது!"
          : "Marriage numerology compatibility report saved successfully!"
      );
    } catch (err: any) {
      setSaveError(err?.data?.detail || err?.message || "Failed to save report.");
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!result) return;
    setPdfDownloading(true);
    setSaveError(null);
    try {
      const nameA = result.person_a_profile.full_name || result.person_a_profile.preferred_name || "Partner A";
      const nameB = result.person_b_profile.full_name || result.person_b_profile.preferred_name || "Partner B";
      const blob = await exportNumerologyPdf(
        {
          person_name: `${nameA} & ${nameB}`,
          birth_date: `${result.person_a_profile.birth_date} / ${result.person_b_profile.birth_date}`,
          method: "marriage",
          system_convention: result.system_convention,
          language: language === "ta" ? "ta" : "en",
          calculation_data: result as any,
          interpretation_data: {
            overall_synthesis: result.overall_synthesis,
            shared_strengths: result.shared_strengths,
            challenges: result.potential_challenges,
          },
        },
        session?.access_token
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeName = `${nameA}_${nameB}`.replace(/\s+/g, "_");
      a.download = `Marriage_Numerology_${safeName}_${language}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setSaveError(err?.message || "Failed to generate marriage PDF report.");
    } finally {
      setPdfDownloading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* 1. Header Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-rose-50 via-white to-amber-50/40 border border-rose-200/70 shadow-xs relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-48 h-48 bg-rose-200/20 rounded-full blur-2xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-100/80 border border-rose-200 text-rose-800 text-xs font-semibold mb-3">
            <Heart className="w-3.5 h-3.5 fill-rose-500 text-rose-500" />
            <span>
              {language === "ta" ? "எண் கணித திருமண இணக்க அரங்கம்" : "Numerology Marriage Compatibility Studio"}
            </span>
          </div>
          <h2 className="font-serif text-2xl sm:text-3xl font-bold text-[#102A4C]">
            {language === "ta" ? "திருமண & கூட்டாண்மை எண் கணிதப் பொருத்தம்" : "Marriage & Couple Numerology Compatibility"}
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-[#52667E] leading-relaxed">
            {language === "ta"
              ? "பித்தகோரியன் மற்றும் கால்டியன் மரபுகளைப் பயன்படுத்தி பிறந்த எண், விதி எண், பெயர் எண், மற்றும் ஆன்ம விருப்ப இணக்கத்தை ஒப்பிடுங்கள்."
              : "Compare Birth Numbers (Mulank), Life Path trajectories (Bhagyank), Expression numbers, and Soul Urge emotional longings under classical Pythagorean and Chaldean traditions."}
          </p>
        </div>
      </div>

      {/* 2. Couple Inputs Form */}
      <form onSubmit={handleAnalyze} className="p-6 sm:p-8 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#F1F5F9]">
          <h3 className="text-sm font-bold text-[#102A4C] flex items-center gap-2">
            <Users className="w-4 h-4 text-rose-500" />
            <span>{language === "ta" ? "தம்பதியர் விவரங்கள்" : "Enter Couple Details"}</span>
          </h3>

          <div className="flex items-center gap-2">
            {/* System Convention Toggle */}
            <div className="flex items-center p-1 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs font-semibold">
              <button
                type="button"
                onClick={() => setConvention("pythagorean")}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  convention === "pythagorean" ? "bg-[#102A4C] text-white shadow-2xs" : "text-[#52667E] hover:text-[#102A4C]"
                }`}
              >
                Pythagorean (1–9)
              </button>
              <button
                type="button"
                onClick={() => setConvention("chaldean")}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  convention === "chaldean" ? "bg-[#102A4C] text-white shadow-2xs" : "text-[#52667E] hover:text-[#102A4C]"
                }`}
              >
                Chaldean (1–8)
              </button>
            </div>

            {/* Language */}
            <div className="flex items-center p-1 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs font-semibold">
              <button
                type="button"
                onClick={() => setReportLang("en")}
                className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                  reportLang === "en" ? "bg-[#102A4C] text-white shadow-2xs" : "text-[#52667E]"
                }`}
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => setReportLang("ta")}
                className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                  reportLang === "ta" ? "bg-[#102A4C] text-white shadow-2xs" : "text-[#52667E]"
                }`}
              >
                தமிழ்
              </button>
            </div>
          </div>
        </div>

        {/* Side-by-Side Partner Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Partner 1 (Person A) */}
          <div className="p-5 rounded-2xl bg-gradient-to-b from-[#FBFDFF] to-white border border-[#BFDBFE]/60 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-[#EBF2FE]">
              <span className="text-xs font-bold text-[#102A4C] flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#3478F6]" />
                <span>{language === "ta" ? "முதல் நபர் (Person A)" : "Person A / Groom / Partner 1"}</span>
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 border border-blue-200">
                Primary
              </span>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                {language === "ta" ? "முழு பெயர் (விருப்பத்திற்குரியது)" : "Full Name (Optional for Name Numbers)"}
              </label>
              <input
                type="text"
                value={personAName}
                onChange={(e) => setPersonAName(e.target.value)}
                placeholder="e.g. Sundar Raman"
                className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] text-xs text-[#102A4C] bg-white focus:outline-none focus:ring-2 focus:ring-[#3478F6]/20"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                  {language === "ta" ? "பிறந்த தேதி *" : "Birth Date *"}
                </label>
                <input
                  type="date"
                  required
                  value={personADob}
                  onChange={(e) => setPersonADob(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] text-xs text-[#102A4C] bg-white focus:outline-none focus:ring-2 focus:ring-[#3478F6]/20"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                  {language === "ta" ? "விருப்பப் பெயர்" : "Preferred Name"}
                </label>
                <input
                  type="text"
                  value={personAPreferred}
                  onChange={(e) => setPersonAPreferred(e.target.value)}
                  placeholder="e.g. Sundar"
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] text-xs text-[#102A4C] bg-white"
                />
              </div>
            </div>
          </div>

          {/* Partner 2 (Person B) */}
          <div className="p-5 rounded-2xl bg-gradient-to-b from-[#FFFDFD] to-white border border-rose-200/70 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-rose-100">
              <span className="text-xs font-bold text-[#102A4C] flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <span>{language === "ta" ? "இரண்டாம் நபர் (Person B)" : "Person B / Bride / Partner 2"}</span>
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-600 border border-rose-200">
                Partner
              </span>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                {language === "ta" ? "முழு பெயர் (விருப்பத்திற்குரியது)" : "Full Name (Optional for Name Numbers)"}
              </label>
              <input
                type="text"
                value={personBName}
                onChange={(e) => setPersonBName(e.target.value)}
                placeholder="e.g. Meenakshi Sundaram"
                className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] text-xs text-[#102A4C] bg-white focus:outline-none focus:ring-2 focus:ring-rose-400/20"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                  {language === "ta" ? "பிறந்த தேதி *" : "Birth Date *"}
                </label>
                <input
                  type="date"
                  required
                  value={personBDob}
                  onChange={(e) => setPersonBDob(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] text-xs text-[#102A4C] bg-white focus:outline-none focus:ring-2 focus:ring-rose-400/20"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                  {language === "ta" ? "விருப்பப் பெயர்" : "Preferred Name"}
                </label>
                <input
                  type="text"
                  value={personBPreferred}
                  onChange={(e) => setPersonBPreferred(e.target.value)}
                  placeholder="e.g. Meena"
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] text-xs text-[#102A4C] bg-white"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Relationship Status Selector */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
          <div className="flex items-center gap-3">
            <label className="text-xs font-semibold text-[#52667E] whitespace-nowrap">
              {language === "ta" ? "உறவு நிலை:" : "Relationship Context:"}
            </label>
            <select
              value={relationshipStatus}
              onChange={(e) => setRelationshipStatus(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-[#DDE5F0] text-xs text-[#102A4C] bg-white cursor-pointer"
            >
              <option value="considering_marriage">{language === "ta" ? "திருமணப் பேச்சுவார்த்தை" : "Considering Marriage / Alliance"}</option>
              <option value="dating">{language === "ta" ? "காதல் / அறிமுக நிலை" : "Dating / Courtship"}</option>
              <option value="engaged">{language === "ta" ? "நிச்சயதார்த்தம் ஆனது" : "Engaged"}</option>
              <option value="married">{language === "ta" ? "திருமணமான தம்பதியர்" : "Married Couple"}</option>
              <option value="partnership">{language === "ta" ? "நீண்ட கால வாழ்க்கை துணை" : "Long-Term Life Partnership"}</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-rose-500 to-[#102A4C] text-white text-xs font-bold hover:shadow-md transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Heart className="w-4 h-4 fill-white text-white" />}
            <span>
              {language === "ta"
                ? (loading ? "கணக்கிடப்படுகிறது..." : "பொருத்தத்தைக் காண்க")
                : (loading ? "Evaluating Synergy..." : "Analyze Couple Compatibility")}
            </span>
          </button>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </form>

      {/* 3. Analysis Results */}
      {result && (
        <div className="space-y-8 animate-fadeIn">
          {/* Top Score Banner */}
          <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-[#102A4C] to-[#1E3A8A] text-white shadow-md relative overflow-hidden">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
              <div className="space-y-2 max-w-2xl">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-xs font-semibold">
                  <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                  <span>{result.overall_harmony_level}</span>
                </div>
                <h3 className="font-serif text-2xl sm:text-3xl font-bold">
                  {result.person_a_profile.preferred_name || result.person_a_profile.full_name || "Partner A"} &amp;{" "}
                  {result.person_b_profile.preferred_name || result.person_b_profile.full_name || "Partner B"}
                </h3>
                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                  {result.overall_synthesis}
                </p>
                <div className="pt-2 text-[11px] text-slate-300 font-mono">
                  Formula: {result.scoring_formula_explanation.formula}
                </div>
              </div>

              {/* Big Circular Score */}
              <div className="flex flex-col items-center justify-center p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 shrink-0 text-center min-w-[160px]">
                <div className="text-4xl sm:text-5xl font-black text-amber-300">
                  {result.overall_score}
                </div>
                <div className="text-[11px] uppercase tracking-wider text-slate-200 font-bold mt-1">
                  Composite Score / 100
                </div>
                <div className="text-[10px] text-slate-300 mt-0.5">
                  {result.system_convention.toUpperCase()} Tradition
                </div>
              </div>
            </div>
          </div>

          {/* Action Bar (Save Report) */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs">
            <div className="text-xs text-[#52667E]">
              {language === "ta"
                ? "இந்த பகுப்பாய்வை உங்கள் கணக்கில் பாதுகாப்பாக சேமித்து எப்போது வேண்டுமானாலும் அணுகலாம்."
                : "Persist this numerology reading to your account dashboard with full component breakdowns."}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={handleDownloadPdf}
                disabled={pdfDownloading}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-[#B8860B] bg-[#FAF2DE] hover:bg-[#F3E5C2] text-[#8C6D23] text-xs font-bold transition-all cursor-pointer disabled:opacity-50"
              >
                {pdfDownloading ? <Loader2 className="w-3.5 h-3.5 animate-spin text-[#B8860B]" /> : <Download className="w-3.5 h-3.5 text-[#B8860B]" />}
                <span>
                  {language === "ta"
                    ? (pdfDownloading ? "PDF தயாராகிறது..." : "PDF பதிவிறக்கம்")
                    : (pdfDownloading ? "Generating PDF..." : "Download PDF")}
                </span>
              </button>

              <button
                type="button"
                onClick={handleSaveReport}
                disabled={saving}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#102A4C] text-white text-xs font-bold hover:bg-[#1E293B] transition-all cursor-pointer disabled:opacity-50"
              >
                {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                <span>
                  {language === "ta" ? (saving ? "சேமிக்கப்படுகிறது..." : "அறிக்கையை சேமிக்க") : (saving ? "Saving..." : "Save Report")}
                </span>
              </button>
            </div>
          </div>

          {saveSuccess && (
            <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{saveSuccess}</span>
            </div>
          )}

          {saveError && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{saveError}</span>
            </div>
          )}

          {/* Side-by-Side Individual Profiles */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ProfileCard profile={result.person_a_profile} badgeColor="border-blue-200 bg-blue-50 text-blue-700" isPartnerA />
            <ProfileCard profile={result.person_b_profile} badgeColor="border-rose-200 bg-rose-50 text-rose-700" />
          </div>

          {/* Component-by-Component Compatibility Breakdown */}
          <div className="space-y-4">
            <h4 className="font-serif text-lg font-bold text-[#102A4C] flex items-center gap-2">
              <Compass className="w-5 h-5 text-[#3478F6]" />
              <span>{language === "ta" ? "கூறுவாரியான பொருத்தம்" : "Component-by-Component Synergy"}</span>
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Life Path */}
              <ComponentCard comparison={result.life_path_compatibility} icon={<Compass className="w-4 h-4 text-emerald-600" />} />
              {/* Psychic */}
              <ComponentCard comparison={result.psychic_compatibility} icon={<Calendar className="w-4 h-4 text-blue-600" />} />
              {/* Expression */}
              {result.expression_compatibility && (
                <ComponentCard comparison={result.expression_compatibility} icon={<Sparkles className="w-4 h-4 text-amber-600" />} />
              )}
              {/* Soul Urge */}
              {result.soul_urge_compatibility && (
                <ComponentCard comparison={result.soul_urge_compatibility} icon={<Heart className="w-4 h-4 text-rose-500" />} />
              )}
            </div>
          </div>

          {/* Dynamic Themes: Emotional & Communication */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Emotional Themes */}
            <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-3">
              <h4 className="text-xs font-bold text-[#102A4C] flex items-center gap-2">
                <Heart className="w-4 h-4 text-rose-500" />
                <span>{language === "ta" ? "உணர்ச்சிபூர்வ அலைவரிசை" : "Emotional Resonance & Vulnerability"}</span>
              </h4>
              <ul className="space-y-2 text-xs text-[#52667E]">
                {result.emotional_themes.map((theme, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                    <span>{theme}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Communication Themes */}
            <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-3">
              <h4 className="text-xs font-bold text-[#102A4C] flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-blue-500" />
                <span>{language === "ta" ? "தொடர்பு & உரையாடல் பாணி" : "Communication Rhythms & Dialogue"}</span>
              </h4>
              <ul className="space-y-2 text-xs text-[#52667E]">
                {result.communication_themes.map((theme, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0" />
                    <span>{theme}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Strengths & Challenges */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Shared Strengths */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-emerald-50/50 to-white border border-emerald-200/80 shadow-xs space-y-3">
              <h4 className="text-xs font-bold text-emerald-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>{language === "ta" ? "இணைந்த பலங்கள்" : "Mutual Strengths & Natural Flow"}</span>
              </h4>
              <ul className="space-y-2 text-xs text-[#52667E]">
                {result.shared_strengths.map((str, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mt-0.5 shrink-0" />
                    <span>{str}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Potential Challenges */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-amber-50/50 to-white border border-amber-200/80 shadow-xs space-y-3">
              <h4 className="text-xs font-bold text-amber-900 flex items-center gap-2">
                <Flame className="w-4 h-4 text-amber-600" />
                <span>{language === "ta" ? "கவனிக்க வேண்டிய வளர்ச்சிப் பகுதிகள்" : "Growth Points & Friction Watch"}</span>
              </h4>
              <ul className="space-y-2 text-xs text-[#52667E]">
                {result.potential_challenges.map((chal, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500 mt-0.5 shrink-0" />
                    <span>{chal}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Practical Conversation Prompts */}
          <div className="p-6 sm:p-8 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
            <h4 className="font-serif text-base font-bold text-[#102A4C] flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-purple-600" />
              <span>{language === "ta" ? "தம்பதியர் கலந்துரையாடலுக்கான கேள்விகள்" : "Practical Conversation Prompts for the Couple"}</span>
            </h4>
            <p className="text-xs text-[#52667E]">
              {language === "ta"
                ? "இருவரும் மனம் திறந்து பேசி பரஸ்பர எல்லைகளையும் எதிர்கால திட்டங்களையும் ஆழப்படுத்த உதவும் கேள்விகள்:"
                : "Use these thoughtfully crafted prompts during relaxed moments to deepen emotional understanding and align long-term expectations:"}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              {result.conversation_prompts.map((prompt, i) => (
                <div key={i} className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs text-[#102A4C] flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-purple-100 text-purple-700 font-bold text-[10px] flex items-center justify-center shrink-0">
                    {i + 1}
                  </span>
                  <span className="leading-relaxed">{prompt}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Growth Recommendations */}
          <div className="p-6 rounded-2xl bg-blue-50/40 border border-blue-200/70 shadow-xs space-y-3">
            <h4 className="text-xs font-bold text-blue-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              <span>{language === "ta" ? "நீண்ட கால நல்லுறவுக்கான வழிகாட்டல்" : "Cultivating Long-Term Partnership Resonance"}</span>
            </h4>
            <div className="space-y-2 text-xs text-[#52667E]">
              {result.growth_recommendations.map((rec, i) => (
                <div key={i} className="flex items-start gap-2">
                  <ArrowRight className="w-3.5 h-3.5 text-blue-500 mt-0.5 shrink-0" />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Ethical Disclaimer */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-slate-500 text-[11px] leading-relaxed flex items-start gap-2.5">
            <HelpCircle className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
            <div>
              <span className="font-bold text-slate-700">Ethical Numerology Disclaimer: </span>
              {result.disclaimer}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Subcomponents

function ProfileCard({
  profile,
  badgeColor,
  isPartnerA,
}: {
  profile: MarriagePersonProfile;
  badgeColor: string;
  isPartnerA?: boolean;
}) {
  return (
    <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
        <div>
          <h4 className="font-serif text-lg font-bold text-[#102A4C]">
            {profile.full_name || profile.preferred_name || profile.person_label}
          </h4>
          <p className="text-xs text-[#52667E]">
            DOB: {profile.birth_date} • {profile.person_label}
          </p>
        </div>
        <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${badgeColor}`}>
          {isPartnerA ? "Primary" : "Partner"}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        {/* Psychic Number */}
        <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
          <div className="text-[10px] text-[#52667E] uppercase font-bold">Birth / Psychic (Mulank)</div>
          <div className="text-xl font-bold text-[#102A4C] mt-0.5">{profile.birth_psychic_number}</div>
          <div className="text-[10px] text-blue-600 font-semibold">{profile.birth_psychic_planet}</div>
        </div>

        {/* Life Path Number */}
        <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
          <div className="text-[10px] text-[#52667E] uppercase font-bold flex items-center justify-between">
            <span>Life Path (Bhagyank)</span>
            {profile.is_life_path_master && (
              <span className="text-[9px] bg-amber-100 text-amber-800 px-1 rounded font-bold">Master</span>
            )}
          </div>
          <div className="text-xl font-bold text-[#102A4C] mt-0.5">{profile.life_path_number}</div>
          <div className="text-[10px] text-emerald-600 font-semibold">{profile.life_path_planet}</div>
        </div>

        {/* Expression */}
        {profile.expression_number !== null && profile.expression_number !== undefined && (
          <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
            <div className="text-[10px] text-[#52667E] uppercase font-bold">Expression (Destiny)</div>
            <div className="text-xl font-bold text-[#102A4C] mt-0.5">{profile.expression_number}</div>
            <div className="text-[10px] text-purple-600 font-semibold">
              Compound {profile.expression_compound}
            </div>
          </div>
        )}

        {/* Soul Urge */}
        {profile.soul_urge_number !== null && profile.soul_urge_number !== undefined && (
          <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
            <div className="text-[10px] text-[#52667E] uppercase font-bold">Soul Urge (Vowels)</div>
            <div className="text-xl font-bold text-[#102A4C] mt-0.5">{profile.soul_urge_number}</div>
            <div className="text-[10px] text-rose-600 font-semibold">Inner Desire</div>
          </div>
        )}
      </div>

      {profile.master_numbers.length > 0 && (
        <div className="pt-1 flex items-center gap-1.5 flex-wrap">
          <span className="text-[10px] text-[#52667E] font-semibold">Master Energies:</span>
          {profile.master_numbers.map((m) => (
            <span key={m} className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-bold">
              {m}
            </span>
          ))}
        </div>
      )}

      {profile.karmic_debts.length > 0 && (
        <div className="pt-1 flex items-center gap-1.5 flex-wrap">
          <span className="text-[10px] text-rose-600 font-semibold">Karmic Debts:</span>
          {profile.karmic_debts.map((kd) => (
            <span key={kd.number} className="px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 text-[10px] font-bold">
              {kd.number} ({kd.source})
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function ComponentCard({
  comparison,
  icon,
}: {
  comparison: MarriageComponentComparison;
  icon: React.ReactNode;
}) {
  return (
    <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-[#F1F5F9]">
        <div className="flex items-center gap-2">
          {icon}
          <h5 className="text-xs font-bold text-[#102A4C]">{comparison.component_name}</h5>
        </div>
        <span className="text-xs font-black text-[#102A4C] bg-[#F8FAFC] px-2 py-0.5 rounded-lg border border-[#E2E8F0]">
          {comparison.score}%
        </span>
      </div>

      <div className="flex items-center justify-between text-xs text-[#52667E]">
        <div>
          <span className="font-bold text-[#102A4C]">{comparison.person_a_label}:</span> Number {comparison.person_a_number}
        </div>
        <div className="text-rose-500 font-bold">&bull;</div>
        <div>
          <span className="font-bold text-[#102A4C]">{comparison.person_b_label}:</span> Number {comparison.person_b_number}
        </div>
      </div>

      <div className="text-[11px] text-[#52667E] leading-relaxed">
        {comparison.interpretation}
      </div>

      <div className="pt-1 flex items-center justify-between text-[10px] text-slate-400">
        <span>Planets: {comparison.planetary_dynamic}</span>
        <span className="font-semibold text-emerald-600">{comparison.harmony_level}</span>
      </div>
    </div>
  );
}
